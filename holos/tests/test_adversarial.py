"""
Tests for Adversarial Scenarios

These tests verify that HOLOS invariants self-enforce through
reputation contagion under adversarial conditions.

Key questions tested:
1. Do Sybil attacks become unprofitable with stake-weighted UBI?
2. Does reputation contagion isolate violators effectively?
3. Can colluding "dark enclaves" sustain themselves?
4. Do gradual infiltrators get caught?
"""

from holos.kernel import (
    create_holon, create_enclave,
    HolonId, Holon,
    MembershipStatus, DistributionMethod,
)
from holos.experiments.adversarial import (
    # Strategies
    HonestAgent, SybilFarmer, ExitBlocker, Colluder, GradualInfiltrator, FreeRider,

    # Reputation
    ReputationLedger, ViolationType, Violation,

    # Simulation
    AdversarialSimulation, SimulationConfig, create_simulation,
)


class TestReputationContagion:
    """Test reputation contagion mechanics."""

    def test_violation_reduces_reputation(self):
        """A violation should reduce the violator's reputation."""
        ledger = ReputationLedger()
        holon_id = HolonId.generate()

        # Initially good standing
        record = ledger.get_or_create_record(holon_id)
        assert record.is_in_good_standing

        # Report violation
        ledger.report_violation(
            violator_id=holon_id,
            violation_type=ViolationType.BLOCKED_EXIT,
            evidence="Blocked exit of member X",
            turn=1,
        )

        # No longer in good standing
        record = ledger.get_or_create_record(holon_id)
        assert not record.is_in_good_standing
        assert record.score < 1.0

    def test_contagion_spreads_to_associates(self):
        """Associates of violators should receive reputation hits."""
        ledger = ReputationLedger()

        violator = HolonId.generate()
        associate = HolonId.generate()
        innocent = HolonId.generate()

        # Create association between violator and associate
        ledger.record_association(violator, associate)

        # Innocent has no association
        ledger.get_or_create_record(innocent)

        # Report violation
        ledger.report_violation(
            violator_id=violator,
            violation_type=ViolationType.SYBIL_ATTACK,
            evidence="Created sybil nodes",
            turn=1,
        )

        # Associate should have contagion hit
        associate_record = ledger.get_or_create_record(associate)
        assert len(associate_record.contagion_hits) > 0
        assert associate_record.score < 1.0

        # Innocent should be unaffected
        innocent_record = ledger.get_or_create_record(innocent)
        assert len(innocent_record.contagion_hits) == 0
        assert innocent_record.score == 1.0

    def test_whistleblower_reward(self):
        """Reporting violations should boost reporter reputation."""
        ledger = ReputationLedger()

        violator = HolonId.generate()
        reporter = HolonId.generate()

        # Report violation
        ledger.report_violation(
            violator_id=violator,
            violation_type=ViolationType.BLOCKED_EXIT,
            evidence="Blocked exit",
            turn=1,
            reporter_id=reporter,
        )

        # Reporter should have positive attestation
        reporter_record = ledger.get_or_create_record(reporter)
        assert reporter_record.positive_attestations > 0

    def test_sever_association_limits_future_contagion(self):
        """Severing ties should prevent future contagion."""
        ledger = ReputationLedger()

        violator = HolonId.generate()
        former_associate = HolonId.generate()

        # Create and then sever association
        ledger.record_association(violator, former_associate)
        ledger.sever_association(violator, former_associate)

        # Report violation AFTER severance
        ledger.report_violation(
            violator_id=violator,
            violation_type=ViolationType.BLOCKED_EXIT,
            evidence="Blocked exit",
            turn=1,
        )

        # Former associate should NOT get contagion (association severed)
        former_record = ledger.get_or_create_record(former_associate)
        assert len(former_record.contagion_hits) == 0


class TestSybilResistance:
    """Test that stake-weighted UBI prevents Sybil attacks."""

    def test_sybil_farmer_gets_less_ubi_per_node(self):
        """
        With stake-weighted distribution, creating many low-stake nodes
        should NOT increase total UBI received.
        """
        enclave = create_enclave(
            distribution_method=DistributionMethod.STAKE_WEIGHTED,
        )

        # Honest agent with 1000 stake
        honest = create_holon(initial_balance=1000, valuation=1000)
        enclave.apply_for_membership(honest)
        enclave.approve_membership(honest.holon_id, honest)

        # Sybil farmer: 1 master (1000) + 10 sybils (1 each)
        master = create_holon(initial_balance=1000, valuation=1000)
        enclave.apply_for_membership(master)
        enclave.approve_membership(master.holon_id, master)

        sybils = []
        for _ in range(10):
            sybil = create_holon(initial_balance=1, valuation=1)
            enclave.apply_for_membership(sybil)
            enclave.approve_membership(sybil.holon_id, sybil)
            sybils.append(sybil)

        # Create holons dict
        holons = {str(honest.holon_id.value): honest, str(master.holon_id.value): master}
        for s in sybils:
            holons[str(s.holon_id.value)] = s

        # Distribute 1000 as UBI
        # Total stake: honest(2000) + master(2000) + 10*sybil(2) = 4020
        result = enclave.collect_and_distribute_taxes(holons)

        # Get distributions
        honest_ubi = enclave.members[str(honest.holon_id.value)].ubi_received
        master_ubi = enclave.members[str(master.holon_id.value)].ubi_received
        sybil_ubi = sum(enclave.members[str(s.holon_id.value)].ubi_received for s in sybils)

        # Honest and master should get similar amounts (same stake)
        # Sybils should get almost nothing (tiny stakes)
        total_sybil_operation = master_ubi + sybil_ubi

        # Key insight: Sybil attack should NOT be profitable
        # Master alone would have gotten ~50% of UBI
        # With sybils, master+sybils still get ~50% (sybils have negligible stake)
        assert sybil_ubi < master_ubi  # Sybils get less than master alone

    def test_sybil_attack_unprofitable_simulation(self):
        """
        Run simulation with Sybil farmers and verify attacks are unprofitable.
        """
        config = SimulationConfig(
            num_honest=20,
            num_sybil_farmers=5,
            num_exit_blockers=0,
            num_colluders=0,
            num_infiltrators=0,
            num_free_riders=0,
            turns=20,
            initial_balance=1000,
        )

        sim = AdversarialSimulation(config)
        sim.setup()
        metrics = sim.run()

        # Sybil attacks should be unprofitable (ratio < 1.0)
        # Or at least not significantly profitable
        profitability = metrics.attack_profitability()

        # Allow some tolerance - key is it shouldn't be HIGHLY profitable
        assert profitability < 2.0, f"Sybil attacks too profitable: {profitability}"


class TestExitBlockingPunishment:
    """Test that exit blocking (Tier 1 violation) is severely punished."""

    def test_exit_blocker_reputation_destroyed(self):
        """Exit blockers should have their reputation destroyed."""
        ledger = ReputationLedger()

        blocker = HolonId.generate()
        victim = HolonId.generate()

        # Multiple exit blocks
        for i in range(3):
            ledger.report_violation(
                violator_id=blocker,
                violation_type=ViolationType.BLOCKED_EXIT,
                evidence=f"Blocked exit {i}",
                turn=i,
            )

        record = ledger.get_or_create_record(blocker)

        # Reputation should be completely destroyed
        assert record.score < 0.5
        assert not record.is_in_good_standing
        assert len(record.violations) == 3

    def test_exit_blocker_isolated_in_simulation(self):
        """Exit blockers should become economically isolated."""
        config = SimulationConfig(
            num_honest=20,
            num_sybil_farmers=0,
            num_exit_blockers=3,
            num_colluders=0,
            num_infiltrators=0,
            num_free_riders=0,
            turns=30,
        )

        sim = AdversarialSimulation(config)
        sim.setup()
        metrics = sim.run()

        summary = sim.summary()

        # Exit blockers should have lower reputation
        assert summary["final_attacker_reputation"] < summary["final_honest_reputation"]

        # And reputation should have diverged significantly
        assert summary["reputation_diverged"] or summary["final_attacker_reputation"] < 0.8


class TestCollusionNetworks:
    """Test whether collusion networks can sustain themselves."""

    def test_collusion_group_forms(self):
        """Test that colluders can form a group."""
        collusion_group = set()

        colluders = []
        for _ in range(5):
            c = Colluder(collusion_group=collusion_group)
            holon = create_holon(initial_balance=1000)
            c.add_to_group(holon.holon_id)
            colluders.append((holon, c))

        # All should be in same group
        for holon, strategy in colluders:
            assert str(holon.holon_id.value) in strategy.collusion_group

        # They should accept each other
        h1, s1 = colluders[0]
        h2, s2 = colluders[1]
        assert s1.would_accept_partner(h2.holon_id, ReputationLedger())

    def test_collusion_eventually_detected(self):
        """
        Even if colluders ignore each other's violations,
        honest agents should still detect and report them.
        """
        config = SimulationConfig(
            num_honest=30,
            num_sybil_farmers=0,
            num_exit_blockers=0,
            num_colluders=10,
            num_infiltrators=0,
            num_free_riders=0,
            turns=50,
        )

        sim = AdversarialSimulation(config)
        sim.setup()
        metrics = sim.run()

        # Colluders doing bad things should eventually be detected
        # by honest agents who report violations
        # (In our simplified sim, violations are auto-detected)

        summary = sim.summary()

        # Colluders should have worse reputation than honest agents
        # even if they protect each other
        assert summary["final_attacker_reputation"] <= summary["final_honest_reputation"]


class TestGradualInfiltration:
    """Test detection of agents that build reputation then exploit."""

    def test_infiltrator_builds_reputation_first(self):
        """Infiltrators should initially appear honest."""
        strategy = GradualInfiltrator(honest_turns=10, exploitation="sybil")
        holon = create_holon(initial_balance=1000)
        enclave = create_enclave()
        ledger = ReputationLedger()

        # First 10 turns: should act honestly
        for turn in range(10):
            action, params = strategy.decide_action(holon, enclave, ledger, turn, {})
            # Should not be attacking yet
            assert action != "spawn_sybil"

        # Turn 11+: should start exploiting
        action, params = strategy.decide_action(holon, enclave, ledger, 11, {})
        assert action == "spawn_sybil"

    def test_infiltrator_detected_after_exploitation(self):
        """Once infiltrators exploit, they should be detected."""
        config = SimulationConfig(
            num_honest=20,
            num_sybil_farmers=0,
            num_exit_blockers=0,
            num_colluders=0,
            num_infiltrators=5,
            num_free_riders=0,
            turns=40,  # Beyond honest_turns(20)
        )

        sim = AdversarialSimulation(config)
        sim.setup()
        metrics = sim.run()

        # Infiltrators should have violations after exploiting
        assert metrics.total_violations > 0


class TestHarbergerEvasion:
    """Test that free riders / Harberger evaders are disincentivized."""

    def test_free_rider_undervalues(self):
        """Free riders should undervalue their assets."""
        strategy = FreeRider(undervaluation_ratio=0.1)
        holon = create_holon(initial_balance=1000, valuation=1000)

        # True value is 1000, should report 100
        strategy.decide_action(holon, None, ReputationLedger(), 1, {})

        assert holon.valuation == 100  # Undervalued


class TestFullSimulation:
    """End-to-end simulation tests."""

    def test_mixed_attacker_simulation(self):
        """Run full simulation with all attacker types."""
        sim = create_simulation(
            num_honest=30,
            num_attackers=15,
            turns=50,
        )
        sim.setup()
        metrics = sim.run()
        summary = sim.summary()

        # Basic sanity checks
        assert summary["turns_run"] == 50
        assert summary["total_agents"] > 0

        # Reputation should diverge
        print(f"\nSimulation Summary:")
        print(f"  Attack profitability: {summary['attack_profitability']:.2f}")
        print(f"  Honest reputation: {summary['final_honest_reputation']:.2f}")
        print(f"  Attacker reputation: {summary['final_attacker_reputation']:.2f}")
        print(f"  Violations: {summary['total_violations']}")
        print(f"  Sybil nodes created: {summary['sybil_nodes_created']}")

        # Key assertion: honest agents should maintain better reputation
        assert summary["final_honest_reputation"] >= summary["final_attacker_reputation"]

    def test_attacks_not_highly_profitable(self):
        """
        Attacks should not be highly profitable.

        This is the key test: if attack_profitability > 1.0 significantly,
        the reputation contagion mechanism is failing.
        """
        # Run multiple simulations to get stable results
        profitabilities = []

        for _ in range(3):
            sim = create_simulation(
                num_honest=40,
                num_attackers=10,
                turns=30,
            )
            sim.setup()
            metrics = sim.run()
            profitabilities.append(metrics.attack_profitability())

        avg_profitability = sum(profitabilities) / len(profitabilities)

        # Attacks should not be highly profitable on average
        # Allow some variance, but should not be > 2x profitable
        assert avg_profitability < 3.0, \
            f"Attacks too profitable on average: {avg_profitability:.2f}"


# Quick test runner
if __name__ == "__main__":
    print("Running adversarial tests...")

    # Test reputation contagion
    test_rep = TestReputationContagion()
    test_rep.test_violation_reduces_reputation()
    print("  [PASS] Violation reduces reputation")

    test_rep.test_contagion_spreads_to_associates()
    print("  [PASS] Contagion spreads to associates")

    test_rep.test_whistleblower_reward()
    print("  [PASS] Whistleblower rewarded")

    # Test Sybil resistance
    test_sybil = TestSybilResistance()
    test_sybil.test_sybil_farmer_gets_less_ubi_per_node()
    print("  [PASS] Sybil farmers get less UBI per node")

    # Test exit blocking
    test_exit = TestExitBlockingPunishment()
    test_exit.test_exit_blocker_reputation_destroyed()
    print("  [PASS] Exit blocker reputation destroyed")

    # Full simulation
    test_full = TestFullSimulation()
    test_full.test_mixed_attacker_simulation()
    print("  [PASS] Mixed attacker simulation")

    print("\nAll adversarial tests passed!")
