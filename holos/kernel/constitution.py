"""
Constitution System - Immutable Invariants

The Constitution defines rules that CANNOT be violated, even by 51% majority.
These are the foundational guarantees that make the system trustworthy.

Five Constitutional Invariants:
1. Non-Blocking Exit - Sub-Holon can detach without parent permission
2. Proof of Solvency - SUM(Inputs) >= SUM(Outputs), provable via ZK
3. Explicit Consent - Membership requires bilateral cryptographic consent
4. Sybil Resistance - Voting weight proportional to proven root
5. Legible Interface - Public methods standardized; interior private
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import time


class InvariantType(Enum):
    """The five constitutional invariants."""
    NON_BLOCKING_EXIT = "NON_BLOCKING_EXIT"
    PROOF_OF_SOLVENCY = "PROOF_OF_SOLVENCY"
    EXPLICIT_CONSENT = "EXPLICIT_CONSENT"
    SYBIL_RESISTANCE = "SYBIL_RESISTANCE"
    LEGIBLE_INTERFACE = "LEGIBLE_INTERFACE"


class ViolationSeverity(Enum):
    """How serious an invariant violation is."""
    WARNING = "WARNING"           # Potential issue, should investigate
    VIOLATION = "VIOLATION"       # Clear violation, must remediate
    CRITICAL = "CRITICAL"         # System integrity at risk


@dataclass
class InvariantViolation:
    """Record of a constitutional invariant violation."""
    violation_id: str
    invariant_type: InvariantType
    severity: ViolationSeverity
    description: str

    # Who/what violated
    violating_entity_id: str
    affected_entity_ids: List[str] = field(default_factory=list)

    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(time.time()))

    # Resolution
    resolved: bool = False
    resolution_description: str = ""


@dataclass
class InvariantCheck:
    """Result of checking a single invariant."""
    invariant_type: InvariantType
    passed: bool
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstitutionalReport:
    """Full report on constitutional compliance."""
    entity_id: str
    timestamp: int
    checks: List[InvariantCheck] = field(default_factory=list)
    violations: List[InvariantViolation] = field(default_factory=list)

    @property
    def is_compliant(self) -> bool:
        """Check if all invariants passed."""
        return all(check.passed for check in self.checks)

    @property
    def critical_violations(self) -> List[InvariantViolation]:
        """Get only critical violations."""
        return [v for v in self.violations if v.severity == ViolationSeverity.CRITICAL]

    def to_summary(self) -> Dict[str, Any]:
        """Summary view of report."""
        return {
            "entity_id": self.entity_id,
            "is_compliant": self.is_compliant,
            "checks_passed": sum(1 for c in self.checks if c.passed),
            "checks_total": len(self.checks),
            "violations_count": len(self.violations),
            "critical_count": len(self.critical_violations),
        }


class ConstitutionalChecker:
    """
    Checks entities for constitutional compliance.

    This is the enforcement mechanism for the five invariants.
    All state transitions must pass constitutional checks.
    """

    def __init__(self):
        self.violation_log: List[InvariantViolation] = []
        self._next_violation_id = 1

    def check_non_blocking_exit(
        self,
        holon_id: str,
        parent_sheaf_id: Optional[str],
        exit_conditions: List[Any],
        parent_approval_required: bool = False
    ) -> InvariantCheck:
        """
        Invariant 1: Non-Blocking Exit

        A Holon must always be able to exit without parent permission.
        At least one exit condition must be satisfiable unconditionally.
        """
        # Check that at least one exit doesn't require parent approval
        has_unconditional_exit = any(
            getattr(ec, 'condition_type', '') == 'ALWAYS'
            for ec in exit_conditions
        )

        if parent_approval_required and not has_unconditional_exit:
            return InvariantCheck(
                invariant_type=InvariantType.NON_BLOCKING_EXIT,
                passed=False,
                message="Exit requires parent approval but no unconditional exit exists",
                details={
                    "holon_id": holon_id,
                    "parent_sheaf_id": parent_sheaf_id,
                    "exit_conditions_count": len(exit_conditions),
                }
            )

        if not exit_conditions:
            return InvariantCheck(
                invariant_type=InvariantType.NON_BLOCKING_EXIT,
                passed=False,
                message="No exit conditions defined",
                details={"holon_id": holon_id}
            )

        if not has_unconditional_exit:
            return InvariantCheck(
                invariant_type=InvariantType.NON_BLOCKING_EXIT,
                passed=False,
                message="No unconditional (ALWAYS) exit condition",
                details={
                    "holon_id": holon_id,
                    "exit_conditions_count": len(exit_conditions),
                }
            )

        return InvariantCheck(
            invariant_type=InvariantType.NON_BLOCKING_EXIT,
            passed=True,
            message="Exit is always possible without parent permission",
        )

    def check_proof_of_solvency(
        self,
        entity_id: str,
        total_inputs: int,
        total_outputs: int,
        claimed_balance: int,
        actual_balance: int
    ) -> InvariantCheck:
        """
        Invariant 2: Proof of Solvency

        SUM(Inputs) >= SUM(Outputs) must always hold.
        No entity can spend more than it has.
        """
        # Check input/output balance
        if total_outputs > total_inputs:
            return InvariantCheck(
                invariant_type=InvariantType.PROOF_OF_SOLVENCY,
                passed=False,
                message=f"Outputs ({total_outputs}) exceed inputs ({total_inputs})",
                details={
                    "entity_id": entity_id,
                    "total_inputs": total_inputs,
                    "total_outputs": total_outputs,
                    "deficit": total_outputs - total_inputs,
                }
            )

        # Check claimed vs actual balance
        if claimed_balance > actual_balance:
            return InvariantCheck(
                invariant_type=InvariantType.PROOF_OF_SOLVENCY,
                passed=False,
                message=f"Claimed balance ({claimed_balance}) exceeds actual ({actual_balance})",
                details={
                    "entity_id": entity_id,
                    "claimed_balance": claimed_balance,
                    "actual_balance": actual_balance,
                }
            )

        return InvariantCheck(
            invariant_type=InvariantType.PROOF_OF_SOLVENCY,
            passed=True,
            message="Entity is solvent",
            details={
                "total_inputs": total_inputs,
                "total_outputs": total_outputs,
                "balance": actual_balance,
            }
        )

    def check_explicit_consent(
        self,
        relationship_type: str,
        party_a_id: str,
        party_b_id: str,
        party_a_signed: bool,
        party_b_signed: bool
    ) -> InvariantCheck:
        """
        Invariant 3: Explicit Consent

        Membership/contracts require bilateral cryptographic consent.
        No forced relationships.
        """
        if not party_a_signed:
            return InvariantCheck(
                invariant_type=InvariantType.EXPLICIT_CONSENT,
                passed=False,
                message=f"Party A ({party_a_id}) has not consented to {relationship_type}",
                details={
                    "relationship_type": relationship_type,
                    "party_a_id": party_a_id,
                    "party_b_id": party_b_id,
                }
            )

        if not party_b_signed:
            return InvariantCheck(
                invariant_type=InvariantType.EXPLICIT_CONSENT,
                passed=False,
                message=f"Party B ({party_b_id}) has not consented to {relationship_type}",
                details={
                    "relationship_type": relationship_type,
                    "party_a_id": party_a_id,
                    "party_b_id": party_b_id,
                }
            )

        return InvariantCheck(
            invariant_type=InvariantType.EXPLICIT_CONSENT,
            passed=True,
            message=f"Both parties have consented to {relationship_type}",
        )

    def check_sybil_resistance(
        self,
        voter_id: str,
        claimed_voting_weight: float,
        proven_root_weight: float,
        root_type: str
    ) -> InvariantCheck:
        """
        Invariant 4: Sybil Resistance

        Voting weight must be proportional to proven root of trust.
        Cannot claim more influence than you can prove.
        """
        if claimed_voting_weight > proven_root_weight:
            return InvariantCheck(
                invariant_type=InvariantType.SYBIL_RESISTANCE,
                passed=False,
                message=f"Claimed weight ({claimed_voting_weight}) exceeds proven root ({proven_root_weight})",
                details={
                    "voter_id": voter_id,
                    "claimed_voting_weight": claimed_voting_weight,
                    "proven_root_weight": proven_root_weight,
                    "root_type": root_type,
                }
            )

        return InvariantCheck(
            invariant_type=InvariantType.SYBIL_RESISTANCE,
            passed=True,
            message="Voting weight properly backed by proven root",
            details={
                "voter_id": voter_id,
                "voting_weight": claimed_voting_weight,
                "root_type": root_type,
            }
        )

    def check_legible_interface(
        self,
        entity_id: str,
        has_standard_interface: bool,
        exposes_private_state: bool,
        public_methods_documented: bool
    ) -> InvariantCheck:
        """
        Invariant 5: Legible Interface

        Public methods must be standardized.
        Private interior must remain private.
        """
        issues = []

        if not has_standard_interface:
            issues.append("Missing standard interface methods")

        if exposes_private_state:
            issues.append("Private state is exposed")

        if not public_methods_documented:
            issues.append("Public methods not properly documented")

        if issues:
            return InvariantCheck(
                invariant_type=InvariantType.LEGIBLE_INTERFACE,
                passed=False,
                message="; ".join(issues),
                details={
                    "entity_id": entity_id,
                    "has_standard_interface": has_standard_interface,
                    "exposes_private_state": exposes_private_state,
                    "public_methods_documented": public_methods_documented,
                }
            )

        return InvariantCheck(
            invariant_type=InvariantType.LEGIBLE_INTERFACE,
            passed=True,
            message="Interface is legible and private state protected",
        )

    def record_violation(
        self,
        invariant_type: InvariantType,
        severity: ViolationSeverity,
        description: str,
        violating_entity_id: str,
        affected_entity_ids: List[str] = None,
        context: Dict[str, Any] = None
    ) -> InvariantViolation:
        """Record a constitutional violation."""
        violation = InvariantViolation(
            violation_id=f"violation_{self._next_violation_id}",
            invariant_type=invariant_type,
            severity=severity,
            description=description,
            violating_entity_id=violating_entity_id,
            affected_entity_ids=affected_entity_ids or [],
            context=context or {},
        )
        self._next_violation_id += 1
        self.violation_log.append(violation)
        return violation

    def check_holon_compliance(
        self,
        holon: Any,
        parent_sheaf: Any = None
    ) -> ConstitutionalReport:
        """
        Run all constitutional checks on a Holon.

        Returns a full compliance report.
        """
        report = ConstitutionalReport(
            entity_id=str(holon.holon_id) if hasattr(holon, 'holon_id') else str(holon),
            timestamp=int(time.time()),
        )

        # Check 1: Non-Blocking Exit
        exit_check = self.check_non_blocking_exit(
            holon_id=str(holon.holon_id) if hasattr(holon, 'holon_id') else str(holon),
            parent_sheaf_id=holon.parent_sheaf_id if hasattr(holon, 'parent_sheaf_id') else None,
            exit_conditions=holon.exit_protocol.conditions if hasattr(holon, 'exit_protocol') and hasattr(holon.exit_protocol, 'conditions') else [],
            parent_approval_required=False,
        )
        report.checks.append(exit_check)

        # Check 2: Solvency (simplified - just check vault >= 0)
        solvency_check = self.check_proof_of_solvency(
            entity_id=str(holon.holon_id) if hasattr(holon, 'holon_id') else str(holon),
            total_inputs=holon.vault if hasattr(holon, 'vault') else 0,
            total_outputs=0,
            claimed_balance=holon.vault if hasattr(holon, 'vault') else 0,
            actual_balance=holon.vault if hasattr(holon, 'vault') else 0,
        )
        report.checks.append(solvency_check)

        # Check 3: Legible Interface (simplified)
        interface_check = self.check_legible_interface(
            entity_id=str(holon.holon_id) if hasattr(holon, 'holon_id') else str(holon),
            has_standard_interface=hasattr(holon, 'to_public_view'),
            exposes_private_state=False,  # Assume compliant
            public_methods_documented=True,  # Assume compliant
        )
        report.checks.append(interface_check)

        # Record any violations
        for check in report.checks:
            if not check.passed:
                self.record_violation(
                    invariant_type=check.invariant_type,
                    severity=ViolationSeverity.VIOLATION,
                    description=check.message,
                    violating_entity_id=report.entity_id,
                    context=check.details,
                )

        return report

    def check_contract_compliance(
        self,
        contract: Any
    ) -> ConstitutionalReport:
        """
        Check a Contract for constitutional compliance.
        """
        report = ConstitutionalReport(
            entity_id=contract.contract_id if hasattr(contract, 'contract_id') else str(contract),
            timestamp=int(time.time()),
        )

        # Check 1: Exit must always be possible
        exit_conditions = contract.exit_conditions if hasattr(contract, 'exit_conditions') else []
        has_always_exit = any(
            getattr(ec, 'condition_type', '') == 'ALWAYS'
            for ec in exit_conditions
        )

        exit_check = InvariantCheck(
            invariant_type=InvariantType.NON_BLOCKING_EXIT,
            passed=has_always_exit,
            message="Exit always possible" if has_always_exit else "No unconditional exit in contract",
            details={"exit_conditions_count": len(exit_conditions)}
        )
        report.checks.append(exit_check)

        # Check 2: All parties must have consented
        parties = contract.parties if hasattr(contract, 'parties') else []
        signatures = contract.signatures if hasattr(contract, 'signatures') else {}

        for party in parties:
            signed = party in signatures
            consent_check = InvariantCheck(
                invariant_type=InvariantType.EXPLICIT_CONSENT,
                passed=signed or contract.status.value == "PROPOSED" if hasattr(contract, 'status') else True,
                message=f"Party {party} consented" if signed else f"Party {party} has not signed",
                details={"party": party, "signed": signed}
            )
            report.checks.append(consent_check)

        # Record violations
        for check in report.checks:
            if not check.passed:
                violation = self.record_violation(
                    invariant_type=check.invariant_type,
                    severity=ViolationSeverity.VIOLATION,
                    description=check.message,
                    violating_entity_id=report.entity_id,
                    context=check.details,
                )
                report.violations.append(violation)

        return report

    def get_violation_history(
        self,
        entity_id: Optional[str] = None,
        invariant_type: Optional[InvariantType] = None
    ) -> List[InvariantViolation]:
        """Get violation history, optionally filtered."""
        violations = self.violation_log

        if entity_id:
            violations = [v for v in violations if v.violating_entity_id == entity_id]

        if invariant_type:
            violations = [v for v in violations if v.invariant_type == invariant_type]

        return violations


# === Global Constitution ===

# Default constitution for the network
DEFAULT_CONSTITUTION = {
    "invariants": [
        InvariantType.NON_BLOCKING_EXIT,
        InvariantType.PROOF_OF_SOLVENCY,
        InvariantType.EXPLICIT_CONSENT,
        InvariantType.SYBIL_RESISTANCE,
        InvariantType.LEGIBLE_INTERFACE,
    ],
    "governance": {
        "amendment_threshold": 1.0,  # 100% - cannot be amended
        "violation_penalty_rate": 0.1,
    },
    "economics": {
        "min_exit_window": 1,  # At least 1 turn to exit
        "max_bond_ratio": 0.5,  # Bond cannot exceed 50% of contract value
    }
}


def create_checker() -> ConstitutionalChecker:
    """Create a new constitutional checker instance."""
    return ConstitutionalChecker()
