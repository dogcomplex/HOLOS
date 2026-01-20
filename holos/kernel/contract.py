"""
Contract System - Cooperation Primitive

Contracts are the fundamental unit of cooperation between Holons.
Everything is ultimately a contract: exchanges, memberships, services.

Key principle: EXIT CONDITIONS MUST ALWAYS BE SATISFIABLE
This is a constitutional invariant - contracts cannot trap parties.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import time
import hashlib


class ContractType(Enum):
    """Types of contracts."""
    EXCHANGE = "EXCHANGE"         # Simple swap (A gives X, B gives Y)
    SERVICE = "SERVICE"           # Work contract (A does work, B pays)
    MEMBERSHIP = "MEMBERSHIP"     # Sheaf membership
    PROPERTY = "PROPERTY"         # Property/Mantle holding
    CUSTOM = "CUSTOM"             # Arbitrary terms


class ContractStatus(Enum):
    """Lifecycle status of a contract."""
    PROPOSED = "PROPOSED"         # Awaiting signatures
    ACTIVE = "ACTIVE"             # All parties signed, in effect
    COMPLETED = "COMPLETED"       # All obligations fulfilled
    BREACHED = "BREACHED"         # One or more parties violated terms
    EXITED = "EXITED"             # Party exercised exit right
    EXPIRED = "EXPIRED"           # Duration elapsed
    CANCELLED = "CANCELLED"       # Cancelled before activation


class EnforcementType(Enum):
    """How contract terms are enforced."""
    BOND = "BOND"                 # Parties stake tokens, slashed on breach
    REPUTATION = "REPUTATION"     # Breach damages Name reputation
    ZK_PROOF = "ZK_PROOF"         # Automated verification via ZK
    ARBITRATION = "ARBITRATION"   # Third-party dispute resolution
    AUTOMATIC = "AUTOMATIC"       # Smart contract enforcement


class ObligationType(Enum):
    """Types of obligations."""
    PAYMENT = "PAYMENT"           # Transfer tokens
    DELIVERY = "DELIVERY"         # Provide goods/services
    ACTION = "ACTION"             # Perform specific action
    RESTRAINT = "RESTRAINT"       # Refrain from action
    CONTINUOUS = "CONTINUOUS"     # Ongoing obligation


@dataclass
class Obligation:
    """A specific obligation within a contract."""
    obligation_id: str
    obligor_id: str               # Who must fulfill this
    obligation_type: ObligationType
    description: str

    # What must be done
    action: str
    amount: int = 0               # For PAYMENT obligations
    target_id: Optional[str] = None  # Recipient for PAYMENT

    # Timing
    due_by: Optional[int] = None  # Turn/timestamp deadline
    frequency: str = "once"       # "once" | "per_turn" | "on_demand"

    # Status
    fulfilled: bool = False
    fulfilled_at: Optional[int] = None

    def mark_fulfilled(self, turn: int):
        """Mark obligation as fulfilled."""
        self.fulfilled = True
        self.fulfilled_at = turn

    def is_overdue(self, current_turn: int) -> bool:
        """Check if obligation is past due."""
        if self.fulfilled:
            return False
        if self.due_by is None:
            return False
        return current_turn > self.due_by


@dataclass
class ExitCondition:
    """
    Condition under which a party can exit the contract.

    CONSTITUTIONAL INVARIANT: At least one exit condition must always
    be satisfiable without requiring permission from other parties.
    """
    condition_id: str
    description: str

    # What triggers this exit
    condition_type: str           # "ALWAYS" | "AFTER_DURATION" | "ON_BREACH" | "MUTUAL"
    trigger_value: int = 0        # E.g., turn count for AFTER_DURATION

    # Cost of exercising this exit
    exit_cost_rate: float = 0.0   # % of contract value as fee
    exit_cost_fixed: int = 0      # Fixed fee

    # Consequences
    bond_forfeiture_rate: float = 0.0  # % of bond forfeited
    reputation_impact: float = 0.0     # Impact on Name reputation

    def is_satisfiable(self, current_turn: int, contract_value: int) -> bool:
        """Check if this exit condition can be exercised."""
        if self.condition_type == "ALWAYS":
            return True
        elif self.condition_type == "AFTER_DURATION":
            return current_turn >= self.trigger_value
        elif self.condition_type == "ON_BREACH":
            return False  # Requires breach detection
        elif self.condition_type == "MUTUAL":
            return False  # Requires all-party consent
        return False

    def calculate_exit_cost(self, contract_value: int) -> int:
        """Calculate total cost to exit via this condition."""
        return self.exit_cost_fixed + int(contract_value * self.exit_cost_rate)


# Standard exit conditions
ALWAYS_EXIT = ExitCondition(
    condition_id="always_exit",
    description="Can exit at any time (constitutional right)",
    condition_type="ALWAYS",
    exit_cost_rate=0.0,
)

GRACEFUL_EXIT = ExitCondition(
    condition_id="graceful_exit",
    description="Exit with notice period",
    condition_type="ALWAYS",
    exit_cost_rate=0.05,  # 5% fee for immediate exit
)


@dataclass
class Signature:
    """Cryptographic signature on a contract."""
    signer_id: str
    signed_at: int
    signature_hash: str           # In real system: actual signature

    @classmethod
    def create(cls, signer_id: str, contract_hash: str, turn: int) -> 'Signature':
        """Create a new signature."""
        content = f"{signer_id}:{contract_hash}:{turn}"
        sig_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return cls(signer_id=signer_id, signed_at=turn, signature_hash=sig_hash)


@dataclass
class Contract:
    """
    Agreement between Holons with enforcement.

    A Contract specifies:
    - Parties: Who is involved (bilateral consent required)
    - Obligations: What each party must do
    - Rights: What each party gains
    - Enforcement: How violations are handled
    - Exit: How parties can leave (must always be possible)
    """
    contract_id: str
    contract_type: ContractType

    # Parties (bilateral consent required - constitutional invariant)
    parties: List[str]                    # HolonIds
    signatures: Dict[str, Signature] = field(default_factory=dict)

    # Terms
    obligations: List[Obligation] = field(default_factory=list)
    description: str = ""
    value: int = 0                        # Total contract value
    duration: Optional[int] = None        # Turns until expiry

    # Enforcement
    enforcement_type: EnforcementType = EnforcementType.BOND
    bond_amounts: Dict[str, int] = field(default_factory=dict)  # Party -> bond

    # Exit conditions (must always include at least one satisfiable option)
    exit_conditions: List[ExitCondition] = field(default_factory=list)
    exit_costs: Dict[str, int] = field(default_factory=dict)    # Paid exit fees

    # Lifecycle
    status: ContractStatus = ContractStatus.PROPOSED
    created_at: int = field(default_factory=lambda: int(time.time()))
    activated_at: Optional[int] = None
    completed_at: Optional[int] = None

    # History
    breach_count: int = 0
    breaching_parties: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Ensure constitutional invariants."""
        # Must have at least one always-satisfiable exit condition
        if not any(ec.condition_type == "ALWAYS" for ec in self.exit_conditions):
            self.exit_conditions.append(ALWAYS_EXIT)

    def is_fully_signed(self) -> bool:
        """Check if all parties have signed."""
        return all(party in self.signatures for party in self.parties)

    def sign(self, party_id: str, turn: int) -> bool:
        """Add party's signature to contract."""
        if party_id not in self.parties:
            return False
        if party_id in self.signatures:
            return False  # Already signed

        contract_hash = self._compute_hash()
        self.signatures[party_id] = Signature.create(party_id, contract_hash, turn)

        # Auto-activate if all parties signed
        if self.is_fully_signed():
            self.activate(turn)

        return True

    def activate(self, turn: int):
        """Activate the contract (all signatures received)."""
        if not self.is_fully_signed():
            return False
        self.status = ContractStatus.ACTIVE
        self.activated_at = turn
        return True

    def check_obligations(self, current_turn: int) -> List[Obligation]:
        """Return list of unfulfilled, overdue obligations."""
        return [
            ob for ob in self.obligations
            if not ob.fulfilled and ob.is_overdue(current_turn)
        ]

    def fulfill_obligation(self, obligation_id: str, turn: int) -> bool:
        """Mark an obligation as fulfilled."""
        for ob in self.obligations:
            if ob.obligation_id == obligation_id:
                ob.mark_fulfilled(turn)
                self._check_completion()
                return True
        return False

    def _check_completion(self):
        """Check if all obligations are fulfilled."""
        if all(ob.fulfilled for ob in self.obligations):
            self.status = ContractStatus.COMPLETED
            self.completed_at = int(time.time())

    def record_breach(self, breaching_party_id: str):
        """Record a contract breach."""
        self.breach_count += 1
        if breaching_party_id not in self.breaching_parties:
            self.breaching_parties.append(breaching_party_id)
        self.status = ContractStatus.BREACHED

    def can_exit(self, party_id: str, current_turn: int) -> bool:
        """Check if party can exercise exit right."""
        if party_id not in self.parties:
            return False

        # Constitutional invariant: at least one exit must be satisfiable
        return any(
            ec.is_satisfiable(current_turn, self.value)
            for ec in self.exit_conditions
        )

    def execute_exit(self, party_id: str, current_turn: int) -> 'ExitResult':
        """Party exercises exit right."""
        if party_id not in self.parties:
            return ExitResult(success=False, message="Not a party to this contract")

        # Find cheapest satisfiable exit condition
        satisfiable = [
            ec for ec in self.exit_conditions
            if ec.is_satisfiable(current_turn, self.value)
        ]

        if not satisfiable:
            # This should never happen due to constitutional invariant
            return ExitResult(success=False, message="No satisfiable exit condition")

        # Use cheapest option
        chosen_exit = min(satisfiable, key=lambda ec: ec.calculate_exit_cost(self.value))
        exit_cost = chosen_exit.calculate_exit_cost(self.value)

        # Execute exit
        self.exit_costs[party_id] = exit_cost
        self.status = ContractStatus.EXITED

        return ExitResult(
            success=True,
            exit_cost=exit_cost,
            exit_condition=chosen_exit,
            message=f"Exited via {chosen_exit.description}, cost: ${exit_cost}"
        )

    def get_party_obligations(self, party_id: str) -> List[Obligation]:
        """Get all obligations for a specific party."""
        return [ob for ob in self.obligations if ob.obligor_id == party_id]

    def _compute_hash(self) -> str:
        """Compute hash of contract terms."""
        content = f"{self.contract_id}:{self.contract_type.value}:{','.join(sorted(self.parties))}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_public_view(self) -> Dict[str, Any]:
        """Public view of contract."""
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type.value,
            "parties": self.parties,
            "status": self.status.value,
            "value": self.value,
            "obligations_count": len(self.obligations),
            "fulfilled_count": sum(1 for ob in self.obligations if ob.fulfilled),
            "exit_conditions_count": len(self.exit_conditions),
            "is_fully_signed": self.is_fully_signed(),
        }


@dataclass
class ExitResult:
    """Result of executing an exit."""
    success: bool
    exit_cost: int = 0
    exit_condition: Optional[ExitCondition] = None
    bond_returned: int = 0
    message: str = ""


# === Factory Functions ===

def create_exchange_contract(
    party_a: str,
    party_b: str,
    a_gives: int,
    b_gives: int,
    description: str = "Simple exchange"
) -> Contract:
    """Create a simple exchange contract."""
    contract_id = f"exchange_{int(time.time())}"

    obligations = [
        Obligation(
            obligation_id=f"{contract_id}_a",
            obligor_id=party_a,
            obligation_type=ObligationType.PAYMENT,
            description=f"{party_a} pays {a_gives}",
            action="pay",
            amount=a_gives,
            target_id=party_b,
        ),
        Obligation(
            obligation_id=f"{contract_id}_b",
            obligor_id=party_b,
            obligation_type=ObligationType.PAYMENT,
            description=f"{party_b} pays {b_gives}",
            action="pay",
            amount=b_gives,
            target_id=party_a,
        ),
    ]

    return Contract(
        contract_id=contract_id,
        contract_type=ContractType.EXCHANGE,
        parties=[party_a, party_b],
        obligations=obligations,
        description=description,
        value=a_gives + b_gives,
        exit_conditions=[ALWAYS_EXIT, GRACEFUL_EXIT],
    )


def create_membership_contract(
    holon_id: str,
    sheaf_id: str,
    membership_fee: int = 0,
    exit_cost_rate: float = 0.0,
) -> Contract:
    """Create a Sheaf membership contract."""
    contract_id = f"membership_{holon_id}_{sheaf_id}"

    obligations = []
    if membership_fee > 0:
        obligations.append(Obligation(
            obligation_id=f"{contract_id}_fee",
            obligor_id=holon_id,
            obligation_type=ObligationType.PAYMENT,
            description=f"Membership fee",
            action="pay",
            amount=membership_fee,
            target_id=sheaf_id,
        ))

    exit_conditions = [
        ALWAYS_EXIT,
        ExitCondition(
            condition_id="membership_exit",
            description="Exit membership with fee",
            condition_type="ALWAYS",
            exit_cost_rate=exit_cost_rate,
        ),
    ]

    return Contract(
        contract_id=contract_id,
        contract_type=ContractType.MEMBERSHIP,
        parties=[holon_id, sheaf_id],
        obligations=obligations,
        description=f"Membership of {holon_id} in Sheaf {sheaf_id}",
        value=membership_fee,
        exit_conditions=exit_conditions,
    )
