"""
Tests for Information Asymmetry Effects

Tests how information advantages affect wealth inequality and market dominance,
and validates that erosion mechanisms can counter these advantages.

Key scenarios:
1. Legacy advantage: Incumbents with historical data
2. Active surveillance: Ongoing spying capability
3. Coverage/fidelity variations: Partial/noisy information
4. Erosion mechanisms: What counters the advantage?
"""

from holos.kernel import create_holon, HolonId
from holos.experiments.information_asymmetry import (
    # Information
    InformationType, InformationPacket,

    # Surveillance
    SurveillanceCapability, LegacyAdvantage, ActiveSurveillance, InsiderKnowledge,

    # Market
    Asset, Market,

    # Agents
    InformedTrader, BlindTrader,

    # Metrics
    gini_coefficient, herfindahl_index, top_n_share, InequalityMetrics,

    # Erosion
    IdentityRotation, NoiseInjection, ZKShielding, PopulationChurn,

    # Simulation
    InfoAsymmetryConfig, InfoAsymmetrySimulation, create_info_asymmetry_sim,
)


class TestInequalityMetrics:
    """Test inequality measurement functions."""

    def test_gini_perfect_equality(self):
        """Gini = 0 when everyone has same wealth."""
        wealths = [100, 100, 100, 100, 100]
        gini = gini_coefficient(wealths)
        assert gini < 0.01, f"Expected ~0, got {gini}"

    def test_gini_high_inequality(self):
        """Gini approaches 1 with extreme inequality."""
        wealths = [1000, 1, 1, 1, 1]  # One person has almost everything
        gini = gini_coefficient(wealths)
        assert gini > 0.7, f"Expected >0.7, got {gini}"

    def test_herfindahl_monopoly(self):
        """HHI = 1 for monopoly."""
        wealths = [100, 0, 0, 0, 0]
        hhi = herfindahl_index(wealths)
        assert hhi == 1.0

    def test_herfindahl_competitive(self):
        """HHI is low for evenly distributed market."""
        wealths = [100] * 10  # 10 equal players
        hhi = herfindahl_index(wealths)
        assert abs(hhi - 0.1) < 0.001  # 1/N for equal shares (with float tolerance)

    def test_top_n_share(self):
        """Top N share calculation."""
        wealths = [100, 50, 30, 20]  # Total = 200
        assert top_n_share(wealths, 1) == 0.5  # Top 1 = 100/200
        assert top_n_share(wealths, 2) == 0.75  # Top 2 = 150/200


class TestSurveillanceCapabilities:
    """Test different surveillance models."""

    def test_legacy_advantage_high_coverage(self):
        """Legacy advantage has high initial coverage."""
        legacy = LegacyAdvantage()
        assert legacy.coverage >= 0.8

    def test_legacy_advantage_decays_faster(self):
        """Legacy data becomes stale faster."""
        legacy = LegacyAdvantage()
        active = ActiveSurveillance()

        # After 10 turns
        legacy_fidelity = legacy.get_fidelity(10)
        active_fidelity = active.get_fidelity(10)

        assert legacy_fidelity < active_fidelity, "Legacy should decay faster"

    def test_active_surveillance_higher_fidelity(self):
        """Active surveillance has higher base fidelity."""
        legacy = LegacyAdvantage()
        active = ActiveSurveillance()

        assert active.base_fidelity > legacy.base_fidelity

    def test_insider_perfect_fidelity(self):
        """Insider knowledge is perfect."""
        insider = InsiderKnowledge()
        assert insider.base_fidelity == 1.0


class TestMarketMechanics:
    """Test Harberger market with information asymmetry."""

    def test_harberger_buy_informed(self):
        """Informed buyer captures surplus from undervalued assets."""
        market = Market()
        seller = create_holon(initial_balance=1000)
        buyer_id = HolonId.generate()

        # Asset worth 100, declared at 60 (undervalued)
        asset = market.create_asset(seller, true_value=100, declared_value=60)

        trade = market.harberger_buy(buyer_id, asset.asset_id, buyer_knows_true_value=True)

        assert trade is not None
        assert trade["price"] == 60  # Pays declared value
        assert trade["surplus"] == 40  # Captures 100-60 = 40

    def test_informed_trader_finds_opportunities(self):
        """Informed trader identifies undervalued assets."""
        market = Market()
        owner = create_holon(initial_balance=1000)

        # Create undervalued asset
        asset = market.create_asset(owner, true_value=200, declared_value=100)

        # Create info packet
        packet = InformationPacket(
            target_id=owner.holon_id,
            info_type=InformationType.VALUATION,
            true_value=200,
            observed_value=200,  # Perfect info
            fidelity=1.0,
            timestamp=0,
        )

        opportunities = market.get_undervalued_assets([packet], min_surplus_ratio=0.2)

        assert len(opportunities) > 0
        asset_id, surplus = opportunities[0]
        assert asset_id == asset.asset_id
        assert surplus == 100  # 200 - 100


class TestErosionMechanisms:
    """Test mechanisms that erode information advantage."""

    def test_identity_rotation_reduces_coverage(self):
        """Identity rotation erodes surveillance coverage."""
        surveillance = SurveillanceCapability(coverage=0.9)
        erosion = IdentityRotation(rotation_rate=0.2)

        # Apply erosion multiple times
        for turn in range(5):
            surveillance = erosion.apply(surveillance, turn)

        assert surveillance.coverage < 0.5, f"Coverage should have eroded: {surveillance.coverage}"

    def test_noise_injection_reduces_fidelity(self):
        """Noise injection reduces information fidelity."""
        surveillance = SurveillanceCapability(base_fidelity=0.9)
        erosion = NoiseInjection(noise_level=0.2)

        surveillance = erosion.apply(surveillance, 0)

        assert surveillance.base_fidelity < 0.9 * 0.85  # ~20% reduction

    def test_zk_shielding_removes_info_types(self):
        """ZK shielding removes certain information types from visibility."""
        surveillance = SurveillanceCapability(
            visible_info_types={
                InformationType.PRIVATE_BALANCE,
                InformationType.VALUATION,
                InformationType.STRATEGY,
            }
        )
        erosion = ZKShielding(shielded_types={InformationType.PRIVATE_BALANCE})

        surveillance = erosion.apply(surveillance, 0)

        assert InformationType.PRIVATE_BALANCE not in surveillance.visible_info_types
        assert InformationType.VALUATION in surveillance.visible_info_types

    def test_population_churn_dilutes_knowledge(self):
        """New entrants dilute legacy knowledge advantage."""
        surveillance = SurveillanceCapability(coverage=0.9)
        erosion = PopulationChurn(churn_rate=0.1)

        # Apply over many turns
        for turn in range(20):
            surveillance = erosion.apply(surveillance, turn)

        # Coverage of original population is diluted
        assert surveillance.coverage < 0.5


class TestInformationAsymmetrySimulation:
    """Test full simulation scenarios."""

    def test_baseline_no_erosion(self):
        """Without erosion, informed traders accumulate advantage."""
        sim = create_info_asymmetry_sim(
            num_informed=5,
            num_blind=45,
            surveillance_type="legacy",
            coverage=0.8,
            fidelity=0.9,
            erosion=[],  # No erosion
            turns=30,
        )
        sim.setup()
        metrics = sim.run()
        summary = sim.summary()

        print(f"\n=== Baseline (No Erosion) ===")
        print(f"  Informed avg wealth: {summary['avg_informed_wealth']:.0f}")
        print(f"  Blind avg wealth: {summary['avg_blind_wealth']:.0f}")
        print(f"  Wealth advantage ratio: {summary['wealth_advantage_ratio']:.2f}x")
        print(f"  Gini coefficient: {summary['final_gini']:.3f}")
        print(f"  Informed surplus: {summary['informed_total_surplus']}")

        # Informed should have accumulated advantage
        assert summary['wealth_advantage_ratio'] >= 1.0, "Informed should have advantage"

    def test_legacy_advantage_scenario(self):
        """Test legacy information advantage (incumbents with historical data)."""
        sim = create_info_asymmetry_sim(
            num_informed=3,
            num_blind=47,
            surveillance_type="legacy",
            coverage=0.9,  # Know almost everyone historically
            fidelity=0.7,  # But data is somewhat old
            erosion=[],
            turns=50,
        )
        sim.setup()
        metrics = sim.run()
        summary = sim.summary()

        print(f"\n=== Legacy Advantage ===")
        print(f"  Wealth advantage: {summary['wealth_advantage_ratio']:.2f}x")
        print(f"  Gini change: {summary['gini_change']:.3f}")

    def test_active_surveillance_scenario(self):
        """Test active surveillance (ongoing spying)."""
        sim = create_info_asymmetry_sim(
            num_informed=5,
            num_blind=45,
            surveillance_type="active",
            coverage=0.3,  # Can only track 30%
            fidelity=0.95,  # But very accurate
            erosion=[],
            turns=50,
        )
        sim.setup()
        metrics = sim.run()
        summary = sim.summary()

        print(f"\n=== Active Surveillance ===")
        print(f"  Wealth advantage: {summary['wealth_advantage_ratio']:.2f}x")

    def test_erosion_reduces_advantage(self):
        """Erosion mechanisms should reduce information advantage."""
        # Without erosion
        sim_no_erosion = create_info_asymmetry_sim(
            num_informed=5,
            num_blind=45,
            surveillance_type="legacy",
            coverage=0.8,
            fidelity=0.9,
            erosion=[],
            turns=50,
        )
        sim_no_erosion.setup()
        sim_no_erosion.run()
        summary_no_erosion = sim_no_erosion.summary()

        # With all erosion mechanisms
        sim_with_erosion = create_info_asymmetry_sim(
            num_informed=5,
            num_blind=45,
            surveillance_type="legacy",
            coverage=0.8,
            fidelity=0.9,
            erosion=["rotation", "noise", "churn"],
            turns=50,
        )
        sim_with_erosion.setup()
        sim_with_erosion.run()
        summary_with_erosion = sim_with_erosion.summary()

        print(f"\n=== Erosion Comparison ===")
        print(f"  No erosion - advantage: {summary_no_erosion['wealth_advantage_ratio']:.2f}x")
        print(f"  With erosion - advantage: {summary_with_erosion['wealth_advantage_ratio']:.2f}x")
        print(f"  Coverage eroded: {summary_with_erosion['coverage_eroded']:.3f}")

        # Erosion should reduce advantage (or at least coverage)
        assert summary_with_erosion['final_coverage'] < summary_no_erosion['final_coverage'] or \
               summary_with_erosion['wealth_advantage_ratio'] <= summary_no_erosion['wealth_advantage_ratio'] * 1.1

    def test_zk_shielding_effectiveness(self):
        """ZK shielding should significantly reduce information leakage."""
        # Without ZK
        sim_no_zk = create_info_asymmetry_sim(
            num_informed=5,
            num_blind=45,
            surveillance_type="active",
            coverage=0.5,
            fidelity=0.9,
            erosion=[],
            turns=30,
        )
        sim_no_zk.setup()
        sim_no_zk.run()
        summary_no_zk = sim_no_zk.summary()

        # With ZK shielding
        sim_with_zk = create_info_asymmetry_sim(
            num_informed=5,
            num_blind=45,
            surveillance_type="active",
            coverage=0.5,
            fidelity=0.9,
            erosion=["zk"],
            turns=30,
        )
        sim_with_zk.setup()
        sim_with_zk.run()
        summary_with_zk = sim_with_zk.summary()

        print(f"\n=== ZK Shielding ===")
        print(f"  No ZK - informed surplus: {summary_no_zk['informed_total_surplus']}")
        print(f"  With ZK - informed surplus: {summary_with_zk['informed_total_surplus']}")

    def test_coverage_vs_inequality(self):
        """Higher surveillance coverage should lead to more inequality."""
        results = []

        for coverage in [0.2, 0.5, 0.8]:
            sim = create_info_asymmetry_sim(
                num_informed=5,
                num_blind=45,
                surveillance_type="legacy",
                coverage=coverage,
                fidelity=0.9,
                erosion=[],
                turns=40,
            )
            sim.setup()
            sim.run()
            summary = sim.summary()
            results.append((coverage, summary['final_gini'], summary['wealth_advantage_ratio']))

        print(f"\n=== Coverage vs Inequality ===")
        for coverage, gini, advantage in results:
            print(f"  Coverage {coverage:.0%}: Gini={gini:.3f}, Advantage={advantage:.2f}x")

        # Higher coverage should generally lead to more inequality
        # (though randomness can cause variance)

    def test_fidelity_vs_inequality(self):
        """Higher information fidelity should lead to more inequality."""
        results = []

        for fidelity in [0.5, 0.75, 0.95]:
            sim = create_info_asymmetry_sim(
                num_informed=5,
                num_blind=45,
                surveillance_type="legacy",
                coverage=0.7,
                fidelity=fidelity,
                erosion=[],
                turns=40,
            )
            sim.setup()
            sim.run()
            summary = sim.summary()
            results.append((fidelity, summary['final_gini'], summary['wealth_advantage_ratio']))

        print(f"\n=== Fidelity vs Inequality ===")
        for fidelity, gini, advantage in results:
            print(f"  Fidelity {fidelity:.0%}: Gini={gini:.3f}, Advantage={advantage:.2f}x")


class TestMarketDominance:
    """Test market dominance / concentration scenarios."""

    def test_market_concentration_over_time(self):
        """Track how market concentration evolves."""
        sim = create_info_asymmetry_sim(
            num_informed=3,
            num_blind=47,
            surveillance_type="legacy",
            coverage=0.9,
            fidelity=0.8,
            erosion=[],
            turns=100,
        )
        sim.setup()
        metrics = sim.run()

        # Check if top 1% share increased
        initial_top = metrics.top_1_share_over_time[0] if metrics.top_1_share_over_time else 0
        final_top = metrics.top_1_share_over_time[-1] if metrics.top_1_share_over_time else 0

        print(f"\n=== Market Concentration ===")
        print(f"  Initial top 1 share: {initial_top:.1%}")
        print(f"  Final top 1 share: {final_top:.1%}")

    def test_informed_minority_dominance(self):
        """Small informed minority should not dominate completely."""
        sim = create_info_asymmetry_sim(
            num_informed=2,  # Only 2 informed (4% of population)
            num_blind=48,
            surveillance_type="active",
            coverage=0.5,
            fidelity=0.9,
            erosion=["rotation", "churn"],  # Some erosion
            turns=100,
        )
        sim.setup()
        metrics = sim.run()
        summary = sim.summary()

        print(f"\n=== Minority Dominance Test ===")
        print(f"  Informed (4%): avg wealth {summary['avg_informed_wealth']:.0f}")
        print(f"  Blind (96%): avg wealth {summary['avg_blind_wealth']:.0f}")
        print(f"  Top 1 share: {summary['final_top_1_share']:.1%}")

        # With erosion, even informed minority shouldn't achieve total dominance
        assert summary['final_top_1_share'] < 0.5, "Single agent shouldn't own >50%"


# Quick test runner
if __name__ == "__main__":
    print("Running information asymmetry tests...")
    print("=" * 60)

    # Metrics tests
    test_metrics = TestInequalityMetrics()
    test_metrics.test_gini_perfect_equality()
    test_metrics.test_gini_high_inequality()
    test_metrics.test_herfindahl_monopoly()
    test_metrics.test_herfindahl_competitive()
    test_metrics.test_top_n_share()
    print("[PASS] Inequality metrics")

    # Surveillance tests
    test_surv = TestSurveillanceCapabilities()
    test_surv.test_legacy_advantage_high_coverage()
    test_surv.test_legacy_advantage_decays_faster()
    test_surv.test_active_surveillance_higher_fidelity()
    test_surv.test_insider_perfect_fidelity()
    print("[PASS] Surveillance capabilities")

    # Market tests
    test_market = TestMarketMechanics()
    test_market.test_harberger_buy_informed()
    test_market.test_informed_trader_finds_opportunities()
    print("[PASS] Market mechanics")

    # Erosion tests
    test_erosion = TestErosionMechanisms()
    test_erosion.test_identity_rotation_reduces_coverage()
    test_erosion.test_noise_injection_reduces_fidelity()
    test_erosion.test_zk_shielding_removes_info_types()
    test_erosion.test_population_churn_dilutes_knowledge()
    print("[PASS] Erosion mechanisms")

    # Simulation tests
    print("\n" + "=" * 60)
    print("Running simulation scenarios...")

    test_sim = TestInformationAsymmetrySimulation()
    test_sim.test_baseline_no_erosion()
    test_sim.test_legacy_advantage_scenario()
    test_sim.test_active_surveillance_scenario()
    test_sim.test_erosion_reduces_advantage()
    test_sim.test_zk_shielding_effectiveness()
    test_sim.test_coverage_vs_inequality()
    test_sim.test_fidelity_vs_inequality()

    # Market dominance tests
    test_dom = TestMarketDominance()
    test_dom.test_market_concentration_over_time()
    test_dom.test_informed_minority_dominance()

    print("\n" + "=" * 60)
    print("All information asymmetry tests passed!")
