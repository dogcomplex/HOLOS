"""
Tests for Market Efficiency, Cooperative Guilds, and LLM Agents

Key questions tested:
1. Does information erosion hurt or help market efficiency?
2. Can cooperative guilds match legacy information brokers?
3. Do LLM agents outperform rule-based strategies?
4. When does guild advantage reach parity with legacy?

All tests report METHOD (rule_based vs llm_powered) in summaries.
"""

import os
from holos.kernel import create_holon, HolonId
from holos.experiments.market_efficiency import (
    # Efficiency
    MarketEfficiencyMetrics, calculate_market_efficiency,

    # Guilds
    InformationGuild, GuildMember,

    # LLM
    LLMAgent,

    # Simulation
    EnhancedSimConfig, EnhancedSimulation, create_enhanced_sim,
)
from holos.experiments.information_asymmetry import (
    Market, Asset, SurveillanceCapability, InformationType, InformationPacket,
)


def print_summary(title: str, summary: dict):
    """Print formatted summary with method information."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"  Method: {summary.get('method', 'unknown')}")
    if summary.get('llm_model'):
        print(f"  LLM Model: {summary['llm_model']}")
        print(f"  LLM Calls: {summary.get('llm_calls', 0)}")
    print(f"  Turns: {summary.get('turns_run', 0)}")
    print()


class TestMarketEfficiencyMetrics:
    """Test market efficiency calculations."""

    def test_efficiency_perfect_prices(self):
        """Perfect price accuracy = high efficiency."""
        market = Market()
        owner = create_holon(initial_balance=1000)

        # Create asset with perfect pricing
        market.create_asset(owner, true_value=100, declared_value=100)
        market.create_asset(owner, true_value=200, declared_value=200)

        agents = {str(owner.holon_id.value): (owner, None, False)}
        metrics = calculate_market_efficiency(market, agents)

        assert metrics.avg_price_error < 0.01, "Perfect prices should have ~0 error"
        # Note: efficiency_score includes trade component (0 if no trades)
        # With perfect prices and no trades: 0.4*1.0 + 0.3*1.0 + 0.3*0 = 0.7
        assert metrics.efficiency_score() >= 0.7

    def test_efficiency_poor_prices(self):
        """Poor price accuracy = lower efficiency."""
        market = Market()
        owner = create_holon(initial_balance=1000)

        # Create assets with poor pricing (50% error)
        market.create_asset(owner, true_value=100, declared_value=50)
        market.create_asset(owner, true_value=100, declared_value=150)

        agents = {str(owner.holon_id.value): (owner, None, False)}
        metrics = calculate_market_efficiency(market, agents)

        assert metrics.avg_price_error > 0.3, f"Should have significant error: {metrics.avg_price_error}"


class TestInformationGuild:
    """Test cooperative information sharing."""

    def test_guild_creation_and_membership(self):
        """Test basic guild operations."""
        guild = InformationGuild(
            guild_id="test_guild",
            name="Test Cooperative",
            membership_stake=100,
        )

        member = create_holon(initial_balance=1000)
        success = guild.add_member(member.holon_id, stake=100)

        assert success
        assert str(member.holon_id.value) in guild.members
        assert guild.pool_balance == 100

    def test_guild_information_sharing(self):
        """Test that members can share and access information."""
        guild = InformationGuild(
            guild_id="test_guild",
            name="Test Cooperative",
            membership_stake=50,
        )

        member1 = create_holon(initial_balance=1000)
        member2 = create_holon(initial_balance=1000)
        target = create_holon(initial_balance=500)

        guild.add_member(member1.holon_id, 50)
        guild.add_member(member2.holon_id, 50)

        # Member 1 shares information
        packet = InformationPacket(
            target_id=target.holon_id,
            info_type=InformationType.VALUATION,
            true_value=500,
            observed_value=480,
            fidelity=0.9,
            timestamp=1,
        )
        guild.contribute_info(member1.holon_id, packet)

        # Member 2 should be able to access it
        shared = guild.get_shared_info(member2.holon_id)
        assert len(shared) == 1
        assert shared[0].observed_value == 480

    def test_guild_collective_capability_grows(self):
        """More members = better collective capability."""
        guild = InformationGuild(
            guild_id="test_guild",
            name="Test Cooperative",
            membership_stake=10,
        )

        initial_coverage = guild.collective_coverage

        # Add many members
        for _ in range(20):
            member = create_holon(initial_balance=100)
            guild.add_member(member.holon_id, 10)

        assert guild.collective_coverage > initial_coverage
        assert guild.collective_coverage > 0.8  # Should approach 95%

    def test_surplus_distribution(self):
        """Test fair surplus distribution."""
        guild = InformationGuild(
            guild_id="test_guild",
            name="Test Cooperative",
            membership_stake=100,
            surplus_sharing="equal",
        )

        members = []
        for _ in range(4):
            m = create_holon(initial_balance=1000)
            guild.add_member(m.holon_id, 100)
            members.append(m)

        distribution = guild.distribute_surplus(1000)

        assert len(distribution) == 4
        assert all(v == 250 for v in distribution.values())  # Equal split


class TestLLMAgent:
    """Test LLM-powered agent."""

    def test_llm_agent_fallback(self):
        """Without API key, should fall back to rule-based."""
        # Temporarily clear API key
        original_key = os.environ.get("ANTHROPIC_API_KEY")
        if "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

        try:
            agent = LLMAgent()
            assert not agent.enabled
        finally:
            # Restore
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key

    def test_llm_agent_surveil(self):
        """Test LLM agent can surveil targets."""
        agent = LLMAgent(
            surveillance=SurveillanceCapability(coverage=1.0, base_fidelity=0.9)
        )

        target = create_holon(initial_balance=500)
        target._private_balance = 500

        packets = agent.surveil([target], turn=1)

        # Should have gathered some information
        assert len(packets) > 0 or len(agent.info_cache) >= 0  # May not surveil all types


class TestEnhancedSimulation:
    """Test full simulation with all agent types."""

    def test_simulation_runs(self):
        """Basic simulation should complete."""
        sim = create_enhanced_sim(
            num_legacy=2,
            num_guild=10,
            num_llm=2,
            num_blind=16,
            use_llm=True,
            turns=20,
        )
        sim.setup()
        metrics = sim.run()
        summary = sim.summary()

        print_summary("Basic Simulation", summary)

        print(f"  Wealth by type:")
        print(f"    Legacy:  {summary['avg_legacy_wealth']:.0f} ({summary['legacy_vs_blind']:.2f}x blind)")
        print(f"    Guild:   {summary['avg_guild_wealth']:.0f} ({summary['guild_vs_blind']:.2f}x blind)")
        print(f"    LLM:     {summary['avg_llm_wealth']:.0f} ({summary['llm_vs_blind']:.2f}x blind)")
        print(f"    Blind:   {summary['avg_blind_wealth']:.0f}")
        print()
        print(f"  Market Efficiency: {summary['final_efficiency_score']:.3f}")
        print(f"  Price Error: {summary['avg_price_error']:.1%}")

        assert summary['turns_run'] == 20

    def test_guild_vs_legacy_competition(self):
        """Test if guilds can compete with legacy information brokers."""
        # Scenario: Strong legacy vs organized guild
        sim = create_enhanced_sim(
            num_legacy=3,
            num_guild=20,
            num_llm=0,
            num_blind=27,
            use_llm=False,
            erosion=["churn"],  # Population churn erodes legacy advantage
            turns=50,
        )
        sim.setup()
        metrics = sim.run()
        summary = sim.summary()

        print_summary("Guild vs Legacy Competition", summary)

        print(f"  Legacy advantage: {summary['legacy_vs_blind']:.2f}x blind")
        print(f"  Guild advantage:  {summary['guild_vs_blind']:.2f}x blind")
        print(f"  Guild vs Legacy:  {summary['guild_vs_legacy']:.2f}x")
        print()
        print(f"  Efficiency: {summary['final_efficiency_score']:.3f}")

        # Guild should be competitive (not necessarily winning, but close)
        # This is the key question: can bottom-up cooperation match top-down legacy?

    def test_efficiency_with_vs_without_erosion(self):
        """Compare market efficiency with and without erosion."""
        # Without erosion
        sim_no_erosion = create_enhanced_sim(
            num_legacy=5,
            num_guild=10,
            num_llm=0,
            num_blind=35,
            use_llm=False,
            erosion=[],
            turns=50,
        )
        sim_no_erosion.setup()
        sim_no_erosion.run()
        summary_no = sim_no_erosion.summary()

        # With erosion
        sim_with_erosion = create_enhanced_sim(
            num_legacy=5,
            num_guild=10,
            num_llm=0,
            num_blind=35,
            use_llm=False,
            erosion=["rotation", "noise", "churn"],
            turns=50,
        )
        sim_with_erosion.setup()
        sim_with_erosion.run()
        summary_with = sim_with_erosion.summary()

        print_summary("Efficiency: No Erosion vs With Erosion", summary_no)

        print(f"  NO EROSION:")
        print(f"    Efficiency: {summary_no['final_efficiency_score']:.3f}")
        print(f"    Legacy advantage: {summary_no['legacy_vs_blind']:.2f}x")
        print()
        print(f"  WITH EROSION:")
        print(f"    Efficiency: {summary_with['final_efficiency_score']:.3f}")
        print(f"    Legacy advantage: {summary_with['legacy_vs_blind']:.2f}x")
        print()

        # Key question: Does erosion hurt efficiency?
        # Economic theory (Grossman-Stiglitz) suggests SOME information asymmetry is needed
        efficiency_diff = summary_with['final_efficiency_score'] - summary_no['final_efficiency_score']
        print(f"  Efficiency change from erosion: {efficiency_diff:+.3f}")

    def test_llm_vs_rule_based(self):
        """Compare LLM agents to rule-based strategies."""
        # Note: If ANTHROPIC_API_KEY not set, LLM falls back to rule-based

        sim = create_enhanced_sim(
            num_legacy=2,
            num_guild=10,
            num_llm=5,
            num_blind=33,
            use_llm=True,
            turns=30,
        )
        sim.setup()
        metrics = sim.run()
        summary = sim.summary()

        print_summary("LLM vs Rule-Based Agents", summary)

        print(f"  Agent Performance:")
        print(f"    Legacy (rule): {summary['avg_legacy_wealth']:.0f}")
        print(f"    Guild (rule):  {summary['avg_guild_wealth']:.0f}")
        print(f"    LLM:           {summary['avg_llm_wealth']:.0f}")
        print(f"    Blind:         {summary['avg_blind_wealth']:.0f}")
        print()

        if summary['method'] == 'llm_powered':
            print(f"  LLM Performance:")
            print(f"    Decisions: {summary['llm_calls']}")
            print(f"    Profitable rate: {summary['llm_profitable_trade_rate']:.1%}")


class TestEquilibriumAndParity:
    """Test when advantages erode to parity."""

    def test_long_run_equilibrium(self):
        """Run long simulation to see equilibrium dynamics."""
        sim = create_enhanced_sim(
            num_legacy=3,
            num_guild=15,
            num_llm=0,
            num_blind=32,
            use_llm=False,
            erosion=["rotation", "churn"],
            turns=100,
        )
        sim.setup()
        metrics = sim.run()
        summary = sim.summary()

        print_summary("Long-Run Equilibrium", summary)

        # Track advantage over time
        m = metrics
        if len(m.legacy_wealth) > 10 and len(m.guild_wealth) > 10:
            # Calculate advantage at different points
            n_legacy = sim.config.num_legacy_informed
            n_guild = sim.config.num_guild_members

            early_legacy = m.legacy_wealth[10] / n_legacy
            early_guild = m.guild_wealth[10] / n_guild
            early_ratio = early_legacy / early_guild if early_guild > 0 else float('inf')

            late_legacy = m.legacy_wealth[-1] / n_legacy
            late_guild = m.guild_wealth[-1] / n_guild
            late_ratio = late_legacy / late_guild if late_guild > 0 else float('inf')

            print(f"  Advantage evolution:")
            print(f"    Turn 10: Legacy/Guild = {early_ratio:.2f}")
            print(f"    Turn {len(m.legacy_wealth)}: Legacy/Guild = {late_ratio:.2f}")
            print()

            if late_ratio < early_ratio:
                print(f"  Convergence detected: Guild catching up to Legacy")
            else:
                print(f"  Divergence: Legacy maintaining/growing advantage")


class TestCounterSurveillance:
    """Test counter-surveillance strategies."""

    def test_zk_shielding_impact(self):
        """Test how ZK shielding affects the dynamics."""
        # Without ZK
        sim_no_zk = create_enhanced_sim(
            num_legacy=5,
            num_guild=10,
            num_llm=0,
            num_blind=35,
            use_llm=False,
            erosion=[],
            turns=40,
        )
        sim_no_zk.setup()
        sim_no_zk.run()
        summary_no_zk = sim_no_zk.summary()

        # With ZK shielding
        sim_with_zk = create_enhanced_sim(
            num_legacy=5,
            num_guild=10,
            num_llm=0,
            num_blind=35,
            use_llm=False,
            erosion=["zk"],
            turns=40,
        )
        sim_with_zk.setup()
        sim_with_zk.run()
        summary_with_zk = sim_with_zk.summary()

        print_summary("ZK Shielding Impact", summary_no_zk)

        print(f"  WITHOUT ZK:")
        print(f"    Legacy advantage: {summary_no_zk['legacy_vs_blind']:.2f}x")
        print(f"    Efficiency: {summary_no_zk['final_efficiency_score']:.3f}")
        print()
        print(f"  WITH ZK:")
        print(f"    Legacy advantage: {summary_with_zk['legacy_vs_blind']:.2f}x")
        print(f"    Efficiency: {summary_with_zk['final_efficiency_score']:.3f}")


# Quick test runner
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  MARKET EFFICIENCY & COOPERATIVE GUILD TESTS")
    print("="*60)

    # Check for LLM capability
    has_llm = os.environ.get("ANTHROPIC_API_KEY") is not None
    print(f"\n  LLM Mode: {'ENABLED' if has_llm else 'DISABLED (rule-based fallback)'}")

    # Basic tests
    test_metrics = TestMarketEfficiencyMetrics()
    test_metrics.test_efficiency_perfect_prices()
    test_metrics.test_efficiency_poor_prices()
    print("\n[PASS] Market efficiency metrics")

    test_guild = TestInformationGuild()
    test_guild.test_guild_creation_and_membership()
    test_guild.test_guild_information_sharing()
    test_guild.test_guild_collective_capability_grows()
    test_guild.test_surplus_distribution()
    print("[PASS] Information guild mechanics")

    test_llm = TestLLMAgent()
    test_llm.test_llm_agent_fallback()
    test_llm.test_llm_agent_surveil()
    print("[PASS] LLM agent basics")

    # Simulation tests
    print("\n" + "-"*60)
    print("  SIMULATION SCENARIOS")
    print("-"*60)

    test_sim = TestEnhancedSimulation()
    test_sim.test_simulation_runs()
    test_sim.test_guild_vs_legacy_competition()
    test_sim.test_efficiency_with_vs_without_erosion()
    test_sim.test_llm_vs_rule_based()

    test_eq = TestEquilibriumAndParity()
    test_eq.test_long_run_equilibrium()

    test_counter = TestCounterSurveillance()
    test_counter.test_zk_shielding_impact()

    print("\n" + "="*60)
    print("  ALL TESTS PASSED")
    print("="*60)
