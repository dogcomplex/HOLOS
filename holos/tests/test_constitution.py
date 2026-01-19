"""
Tests for Constitutional invariants.

The five constitutional invariants that CANNOT be violated:
1. Non-Blocking Exit - Sub-Holon can detach without parent permission
2. Proof of Solvency - SUM(Inputs) >= SUM(Outputs)
3. Explicit Consent - Membership requires bilateral consent
4. Sybil Resistance - Voting weight proportional to proven root
5. Legible Interface - Public methods standardized; interior private
"""

import pytest
from holos.kernel import (
    create_holon, create_checker,
    InvariantType, ViolationSeverity
)
from holos.kernel.contract import ExitCondition


class TestNonBlockingExit:
    """Invariant 1: Exit cannot be blocked."""

    def test_exit_always_passes_with_unconditional_exit(self):
        """Exit check passes when ALWAYS exit condition exists."""
        checker = create_checker()

        exit_conditions = [
            ExitCondition(
                condition_id="always",
                condition_type="ALWAYS",
                description="Exit always allowed",
            )
        ]

        result = checker.check_non_blocking_exit(
            holon_id="holon_1",
            parent_sheaf_id="enclave_1",
            exit_conditions=exit_conditions,
        )

        assert result.passed is True
        assert result.invariant_type == InvariantType.NON_BLOCKING_EXIT

    def test_exit_fails_without_unconditional_exit(self):
        """Exit check fails when no ALWAYS exit condition."""
        checker = create_checker()

        exit_conditions = [
            ExitCondition(
                condition_id="notice",
                condition_type="NOTICE_PERIOD",
                description="30 day notice required",
            )
        ]

        result = checker.check_non_blocking_exit(
            holon_id="holon_1",
            parent_sheaf_id="enclave_1",
            exit_conditions=exit_conditions,
        )

        assert result.passed is False

    def test_exit_fails_with_empty_conditions(self):
        """Exit check fails with no exit conditions."""
        checker = create_checker()

        result = checker.check_non_blocking_exit(
            holon_id="holon_1",
            parent_sheaf_id="enclave_1",
            exit_conditions=[],
        )

        assert result.passed is False


class TestProofOfSolvency:
    """Invariant 2: Inputs >= Outputs."""

    def test_solvency_passes_when_balanced(self):
        """Solvency check passes when inputs >= outputs."""
        checker = create_checker()

        result = checker.check_proof_of_solvency(
            entity_id="holon_1",
            total_inputs=1000,
            total_outputs=800,
            claimed_balance=200,
            actual_balance=200,
        )

        assert result.passed is True
        assert result.invariant_type == InvariantType.PROOF_OF_SOLVENCY

    def test_solvency_fails_when_outputs_exceed_inputs(self):
        """Solvency check fails when outputs > inputs."""
        checker = create_checker()

        result = checker.check_proof_of_solvency(
            entity_id="holon_1",
            total_inputs=500,
            total_outputs=800,
            claimed_balance=0,
            actual_balance=0,
        )

        assert result.passed is False
        assert "exceed" in result.message.lower()

    def test_solvency_fails_when_claimed_exceeds_actual(self):
        """Solvency fails when claimed balance > actual."""
        checker = create_checker()

        result = checker.check_proof_of_solvency(
            entity_id="holon_1",
            total_inputs=1000,
            total_outputs=500,
            claimed_balance=600,  # Claims 600
            actual_balance=500,   # Only has 500
        )

        assert result.passed is False


class TestExplicitConsent:
    """Invariant 3: Bilateral consent required."""

    def test_consent_passes_when_both_signed(self):
        """Consent check passes when both parties sign."""
        checker = create_checker()

        result = checker.check_explicit_consent(
            relationship_type="MEMBERSHIP",
            party_a_id="holon_1",
            party_b_id="enclave_1",
            party_a_signed=True,
            party_b_signed=True,
        )

        assert result.passed is True
        assert result.invariant_type == InvariantType.EXPLICIT_CONSENT

    def test_consent_fails_without_party_a(self):
        """Consent fails when party A hasn't signed."""
        checker = create_checker()

        result = checker.check_explicit_consent(
            relationship_type="CONTRACT",
            party_a_id="holon_1",
            party_b_id="holon_2",
            party_a_signed=False,
            party_b_signed=True,
        )

        assert result.passed is False
        assert "holon_1" in result.message

    def test_consent_fails_without_party_b(self):
        """Consent fails when party B hasn't signed."""
        checker = create_checker()

        result = checker.check_explicit_consent(
            relationship_type="CONTRACT",
            party_a_id="holon_1",
            party_b_id="holon_2",
            party_a_signed=True,
            party_b_signed=False,
        )

        assert result.passed is False
        assert "holon_2" in result.message


class TestSybilResistance:
    """Invariant 4: Voting weight bounded by proven root."""

    def test_sybil_passes_when_weight_backed(self):
        """Sybil check passes when claimed weight <= proven root."""
        checker = create_checker()

        result = checker.check_sybil_resistance(
            voter_id="holon_1",
            claimed_voting_weight=10.0,
            proven_root_weight=15.0,  # Has more backing than claimed
            root_type="CAPITAL",
        )

        assert result.passed is True
        assert result.invariant_type == InvariantType.SYBIL_RESISTANCE

    def test_sybil_fails_when_weight_exceeds_root(self):
        """Sybil check fails when claiming more weight than proven."""
        checker = create_checker()

        result = checker.check_sybil_resistance(
            voter_id="holon_1",
            claimed_voting_weight=20.0,  # Claims 20
            proven_root_weight=10.0,     # Only proves 10
            root_type="AI",
        )

        assert result.passed is False
        assert "exceeds" in result.message.lower()


class TestLegibleInterface:
    """Invariant 5: Standardized public interface."""

    def test_legible_passes_with_good_interface(self):
        """Legible check passes with proper interface."""
        checker = create_checker()

        result = checker.check_legible_interface(
            entity_id="holon_1",
            has_standard_interface=True,
            exposes_private_state=False,
            public_methods_documented=True,
        )

        assert result.passed is True
        assert result.invariant_type == InvariantType.LEGIBLE_INTERFACE

    def test_legible_fails_without_standard_interface(self):
        """Legible check fails without standard interface."""
        checker = create_checker()

        result = checker.check_legible_interface(
            entity_id="holon_1",
            has_standard_interface=False,
            exposes_private_state=False,
            public_methods_documented=True,
        )

        assert result.passed is False

    def test_legible_fails_when_exposing_private(self):
        """Legible check fails when private state exposed."""
        checker = create_checker()

        result = checker.check_legible_interface(
            entity_id="holon_1",
            has_standard_interface=True,
            exposes_private_state=True,  # Bad!
            public_methods_documented=True,
        )

        assert result.passed is False


class TestHolonCompliance:
    """Test full Holon compliance checking."""

    def test_holon_compliance_report(self):
        """Generate compliance report for a Holon."""
        checker = create_checker()
        holon = create_holon(initial_balance=100)

        report = checker.check_holon_compliance(holon)

        assert report.entity_id == str(holon.holon_id.value)
        assert len(report.checks) > 0
        # Default Holon should be compliant
        assert report.is_compliant is True

    def test_holon_violation_recorded(self):
        """Violations are recorded in checker history."""
        checker = create_checker()

        # Create a violation
        checker.record_violation(
            invariant_type=InvariantType.PROOF_OF_SOLVENCY,
            severity=ViolationSeverity.VIOLATION,
            description="Holon spent more than it had",
            violating_entity_id="holon_1",
        )

        history = checker.get_violation_history(entity_id="holon_1")

        assert len(history) == 1
        assert history[0].invariant_type == InvariantType.PROOF_OF_SOLVENCY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
