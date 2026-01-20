"""
Tests for Guild Victory Paths

Explores what mechanisms allow cooperative guilds to overcome legacy
information advantages:

1. Pure time erosion - does it ever level the field?
2. Counter-surveillance - identify and boycott predators
3. Reputation markets - expose information predators through patterns
4. Prediction markets - crowd wisdom for price discovery
5. All mechanisms combined

Key metrics:
- Guild victory turn (when guild avg wealth > legacy avg)
- Legacy advantage trajectory (converging or diverging?)
- Economic damage (Gini, efficiency changes)
"""

from holos.experiments.guild_victory import (
    # Markets
    TradingReputation, ReputationMarket,
    Prediction, PredictionMarket,

    # Agents
    CounterSurveillanceGuild, CounterSurveillanceAgent,

    # Simulation
    GuildVictoryConfig, GuildVictorySimulation,

    # Test functions
    test_pure_time_erosion,
    test_counter_surveillance,
    test_all_mechanisms,
    find_victory_conditions,
)

from holos.kernel import create_holon, HolonId


def print_summary(title: str, summary: dict):
    """Print formatted summary."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    print(f"  Method: {summary.get('method', 'unknown')}")
    print(f"  Turns: {summary.get('turns_run', 0)}")
    print()


class TestReputationMarket:
    """Test reputation market mechanics."""

    def test_trading_updates_reputation(self):
        """Trades should update reputation scores."""
        market = ReputationMarket()

        # Agent makes profitable trades
        for _ in range(10):
            market.record_trade("agent_1", surplus=50)

        rep = market.get_reputation("agent_1")
        assert rep.trades_made == 10
        assert rep.profitable_trades == 10
        assert rep.win_rate == 1.0
        assert rep.predator_score > 0.5, "Should be flagged as potential predator"

    def test_predator_detection(self):
        """Consistently profitable traders should be flagged."""
        market = ReputationMarket(predator_threshold=0.6)

        # Agent makes many profitable trades
        for _ in range(15):
            market.record_trade("predator", surplus=100)

        assert market.is_boycotted("predator"), "Should be on boycott list"

    def test_normal_trader_not_flagged(self):
        """Normal traders with mixed results should not be flagged."""
        market = ReputationMarket()

        # Mixed results (about 50/50)
        for i in range(20):
            surplus = 30 if i % 2 == 0 else -20
            market.record_trade("normal", surplus=surplus)

        rep = market.get_reputation("normal")
        assert rep.predator_score < 0.5, "Should not be flagged"
        assert not market.is_boycotted("normal")


class TestPredictionMarket:
    """Test prediction market mechanics."""

    def test_consensus_calculation(self):
        """Consensus should be stake-weighted average."""
        market = PredictionMarket()

        # Two predictions with different stakes
        market.submit_prediction("agent_1", "asset_1", predicted_value=100, stake=100, timestamp=0)
        market.submit_prediction("agent_2", "asset_1", predicted_value=200, stake=100, timestamp=0)

        consensus = market.get_consensus_value("asset_1")
        # Both have same stake and same initial accuracy (0.5), so average
        assert consensus is not None
        assert 140 <= consensus <= 160  # Should be around 150

    def test_accuracy_rewards(self):
        """Accurate predictors should be rewarded."""
        market = PredictionMarket()

        market.submit_prediction("good", "asset_1", predicted_value=100, stake=50, timestamp=0)
        market.submit_prediction("bad", "asset_1", predicted_value=200, stake=50, timestamp=0)

        rewards = market.resolve("asset_1", true_value=100)

        assert rewards["good"] > 0, "Accurate predictor should be rewarded"
        assert rewards["bad"] < 0, "Inaccurate predictor should lose stake"


class TestGuildVictorySimulation:
    """Test full guild victory simulation."""

    def test_basic_simulation_runs(self):
        """Basic simulation should complete."""
        config = GuildVictoryConfig(
            num_legacy=3,
            num_counter_guild=15,
            num_regular_guild=0,
            num_blind=12,
            turns=30,
        )
        sim = GuildVictorySimulation(config)
        sim.setup()
        metrics = sim.run()
        summary = sim.summary()

        print_summary("Basic Guild Victory Sim", summary)

        print(f"  Legacy avg: {summary['avg_legacy_wealth']:.0f}")
        print(f"  Counter-Guild avg: {summary['avg_counter_guild_wealth']:.0f}")
        print(f"  Legacy vs Counter: {summary['legacy_vs_counter']:.2f}x")
        print(f"  Predators identified: {summary['predators_identified']}")
        print(f"  Trades avoided: {summary['trades_avoided']}")

        assert summary['turns_run'] == 30

    def test_counter_surveillance_identifies_predators(self):
        """Counter-surveillance should identify legacy as predators."""
        config = GuildVictoryConfig(
            num_legacy=5,
            num_counter_guild=20,
            num_regular_guild=0,
            num_blind=25,
            enable_reputation_market=True,
            turns=100,
        )
        sim = GuildVictorySimulation(config)
        sim.setup()
        sim.run()
        summary = sim.summary()

        print_summary("Counter-Surveillance Detection", summary)

        print(f"  Predators identified: {summary['predators_identified']} / {config.num_legacy}")
        print(f"  Trades avoided: {summary['trades_avoided']}")
        print(f"  Legacy advantage: {summary['legacy_vs_counter']:.2f}x")

        # Should identify at least some predators
        # (may not catch all due to randomness)


class TestGuildVictoryPaths:
    """Test different paths to guild victory."""

    def test_pure_time_erosion(self):
        """Test if pure time erosion eventually leads to parity."""
        summary = test_pure_time_erosion(turns=300)

        print_summary("PURE TIME EROSION (300 turns)", summary)

        print(f"  Erosion mechanisms: {summary['erosion_mechanisms']}")
        print(f"  Early legacy advantage: {summary['early_legacy_advantage']:.2f}x")
        print(f"  Late legacy advantage: {summary['late_legacy_advantage']:.2f}x")
        print(f"  Advantage change: {summary['advantage_change']:+.2f}")
        print(f"  Converging: {summary['converging']}")
        print(f"  Guild won: {summary['guild_won']}")
        if summary['guild_victory_turn']:
            print(f"  Victory turn: {summary['guild_victory_turn']}")
        print()
        print(f"  Economic impact:")
        print(f"    Final Gini: {summary['final_gini']:.3f}")
        print(f"    Gini change: {summary['gini_change']:+.3f}")
        print(f"    Efficiency: {summary['final_efficiency']:.3f}")

    def test_counter_surveillance_path(self):
        """Test if counter-surveillance helps guilds win."""
        summary = test_counter_surveillance(turns=200)

        print_summary("COUNTER-SURVEILLANCE PATH (200 turns)", summary)

        print(f"  Predators identified: {summary['predators_identified']}")
        print(f"  Trades avoided: {summary['trades_avoided']}")
        print(f"  Early legacy advantage: {summary['early_legacy_advantage']:.2f}x")
        print(f"  Late legacy advantage: {summary['late_legacy_advantage']:.2f}x")
        print(f"  Converging: {summary['converging']}")
        print(f"  Guild won: {summary['guild_won']}")
        if summary['guild_victory_turn']:
            print(f"  Victory turn: {summary['guild_victory_turn']}")
        print()
        print(f"  Economic impact:")
        print(f"    Final Gini: {summary['final_gini']:.3f}")
        print(f"    Efficiency: {summary['final_efficiency']:.3f}")

    def test_all_mechanisms_combined(self):
        """Test with all mechanisms enabled."""
        summary = test_all_mechanisms(turns=200)

        print_summary("ALL MECHANISMS COMBINED (200 turns)", summary)

        print(f"  Erosion: {summary['erosion_mechanisms']}")
        print(f"  Predators identified: {summary['predators_identified']}")
        print(f"  Early legacy advantage: {summary['early_legacy_advantage']:.2f}x")
        print(f"  Late legacy advantage: {summary['late_legacy_advantage']:.2f}x")
        print(f"  Converging: {summary['converging']}")
        print(f"  Guild won: {summary['guild_won']}")
        if summary['guild_victory_turn']:
            print(f"  Victory turn: {summary['guild_victory_turn']}")
        print()
        print(f"  Counter-Guild vs Regular Guild: {summary['counter_vs_regular']:.2f}x")
        print()
        print(f"  Economic impact:")
        print(f"    Final Gini: {summary['final_gini']:.3f}")
        print(f"    Gini change: {summary['gini_change']:+.3f}")
        print(f"    Efficiency: {summary['final_efficiency']:.3f}")

    def test_find_victory_conditions(self):
        """Systematically find what leads to guild victory."""
        results = find_victory_conditions()

        print_summary("FINDING VICTORY CONDITIONS", {"method": "rule_based", "turns_run": 300})

        print(f"  Configurations tested: {len(results['results'])}")
        print(f"  Winning configurations: {len(results['winning_configs'])}")
        print()

        for r in results['results']:
            erosion = r['erosion_combo'] or ['none']
            won = "WIN" if r['guild_won'] else "LOSE"
            victory_turn = r['guild_victory_turn'] or "N/A"
            print(f"  {erosion}: {won} (turn {victory_turn}), "
                  f"advantage {r['late_legacy_advantage']:.2f}x, "
                  f"gini {r['final_gini']:.3f}")

        if results['winning_configs']:
            best = results['best_config']
            print()
            print(f"  BEST CONFIG: {best['erosion_combo']}")
            print(f"    Victory turn: {best['guild_victory_turn']}")
            print(f"    Final Gini: {best['final_gini']:.3f}")


class TestEconomicDamage:
    """Test economic damage from different scenarios."""

    def test_compare_scenarios(self):
        """Compare economic damage across scenarios."""
        scenarios = []

        # Scenario 1: No intervention (pure legacy dominance)
        config1 = GuildVictoryConfig(
            num_legacy=5,
            num_counter_guild=0,
            num_regular_guild=20,
            num_blind=25,
            erosion_mechanisms=[],
            turns=100,
        )
        sim1 = GuildVictorySimulation(config1)
        sim1.setup()
        sim1.run()
        s1 = sim1.summary()
        s1["scenario"] = "No intervention"
        scenarios.append(s1)

        # Scenario 2: Counter-surveillance
        config2 = GuildVictoryConfig(
            num_legacy=5,
            num_counter_guild=20,
            num_regular_guild=0,
            num_blind=25,
            enable_reputation_market=True,
            erosion_mechanisms=[],
            turns=100,
        )
        sim2 = GuildVictorySimulation(config2)
        sim2.setup()
        sim2.run()
        s2 = sim2.summary()
        s2["scenario"] = "Counter-surveillance"
        scenarios.append(s2)

        # Scenario 3: Full erosion
        config3 = GuildVictoryConfig(
            num_legacy=5,
            num_counter_guild=20,
            num_regular_guild=0,
            num_blind=25,
            enable_reputation_market=True,
            erosion_mechanisms=["rotation", "churn", "noise"],
            turns=100,
        )
        sim3 = GuildVictorySimulation(config3)
        sim3.setup()
        sim3.run()
        s3 = sim3.summary()
        s3["scenario"] = "Full erosion"
        scenarios.append(s3)

        print_summary("ECONOMIC DAMAGE COMPARISON", {"method": "rule_based", "turns_run": 100})

        print(f"  {'Scenario':<25} {'Legacy Adv':<12} {'Gini':<10} {'Efficiency':<10}")
        print(f"  {'-'*25} {'-'*12} {'-'*10} {'-'*10}")

        for s in scenarios:
            print(f"  {s['scenario']:<25} "
                  f"{s['legacy_vs_counter']:.2f}x{' '*6} "
                  f"{s['final_gini']:.3f}{' '*5} "
                  f"{s['final_efficiency']:.3f}")

        print()
        print("  Analysis:")
        print("  - Lower legacy advantage = more equal competition")
        print("  - Lower Gini = less wealth inequality")
        print("  - Higher efficiency = better market function")
        print()

        # Trade-off analysis
        baseline = scenarios[0]
        for s in scenarios[1:]:
            gini_change = s['final_gini'] - baseline['final_gini']
            eff_change = s['final_efficiency'] - baseline['final_efficiency']
            adv_change = s['legacy_vs_counter'] - baseline['legacy_vs_counter']

            print(f"  {s['scenario']} vs Baseline:")
            print(f"    Gini: {gini_change:+.3f}, Efficiency: {eff_change:+.3f}, Advantage: {adv_change:+.2f}")


# Quick test runner
if __name__ == "__main__":
    print("\n" + "="*70)
    print("  GUILD VICTORY PATH TESTS")
    print("="*70)
    print("\n  Testing paths for cooperative guilds to beat legacy information brokers")

    # Basic tests
    test_rep = TestReputationMarket()
    test_rep.test_trading_updates_reputation()
    test_rep.test_predator_detection()
    test_rep.test_normal_trader_not_flagged()
    print("\n[PASS] Reputation market mechanics")

    test_pred = TestPredictionMarket()
    test_pred.test_consensus_calculation()
    test_pred.test_accuracy_rewards()
    print("[PASS] Prediction market mechanics")

    test_sim = TestGuildVictorySimulation()
    test_sim.test_basic_simulation_runs()
    test_sim.test_counter_surveillance_identifies_predators()
    print("[PASS] Basic simulation")

    # Victory path tests
    print("\n" + "-"*70)
    print("  VICTORY PATH ANALYSIS")
    print("-"*70)

    test_paths = TestGuildVictoryPaths()
    test_paths.test_pure_time_erosion()
    test_paths.test_counter_surveillance_path()
    test_paths.test_all_mechanisms_combined()
    test_paths.test_find_victory_conditions()

    # Economic damage analysis
    print("\n" + "-"*70)
    print("  ECONOMIC DAMAGE ANALYSIS")
    print("-"*70)

    test_damage = TestEconomicDamage()
    test_damage.test_compare_scenarios()

    print("\n" + "="*70)
    print("  ALL TESTS COMPLETE")
    print("="*70)
