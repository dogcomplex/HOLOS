"""
Holon - The fundamental unit of identity in HOLOS.

A Holon is a ZK-proof bubble protecting its interior while exposing
a verifiable public interface. It follows the three-layer architecture:

- LOCUS: Persistent identity layer (on-chain state)
- SIGNUM: Deterministic interface layer (wake conditions, public methods)
- SENSUS: Ephemeral AI layer (loaded on-demand, not stored)

Holons are fractal: individuals, groups, guilds, and the entire network
are all Holons with identical interfaces.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum
import hashlib
import uuid

if TYPE_CHECKING:
    from .identity import Name
    from .contract import Contract


class HolonStatus(Enum):
    """Operating status of a Holon."""
    CALCIFIED = "CALCIFIED"    # Dormant, cost-efficient state
    HYDRATED = "HYDRATED"      # Active, processing state (AI loaded)
    BANKRUPT = "BANKRUPT"      # Insolvent, cannot operate
    EXITED = "EXITED"          # Left parent Sheaf


@dataclass(frozen=True)
class HolonId:
    """Cryptographic identifier for a Holon."""
    value: str

    @classmethod
    def generate(cls) -> 'HolonId':
        """Generate a new unique HolonId."""
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_string(cls, s: str) -> 'HolonId':
        return cls(value=s)

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self.value[:8]  # Short display form


@dataclass
class ExitSpec:
    """Specification for how this Holon can exit its parent Sheaf."""
    always_allowed: bool = True           # Constitutional invariant
    notice_period: int = 0                # Turns of notice required
    exit_cost_rate: float = 0.0           # % of vault as exit fee
    mantles_forfeited: bool = True        # Mantles stay behind on exit


@dataclass
class WakeCondition:
    """Condition that triggers Holon hydration."""
    condition_type: str                   # "PAYMENT" | "MESSAGE" | "TIMER"
    threshold: int = 0                    # Minimum payment to wake
    sender_filter: Optional[List[HolonId]] = None  # Allowed senders


@dataclass
class MethodSpec:
    """Public method exposed by this Holon."""
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    cost: int = 0                         # Base cost to call this method


@dataclass
class Constitution:
    """Immutable rules governing this Holon's behavior."""
    constitution_id: str
    invariants: List[str] = field(default_factory=list)  # Rules that cannot be violated

    # Standard constitutional invariants
    exit_always_allowed: bool = True      # Non-blocking exit
    requires_solvency_proof: bool = True  # Proof of solvency
    requires_explicit_consent: bool = True  # Bilateral consent for membership

    def to_hash(self) -> str:
        """Generate commitment to constitution."""
        content = f"{self.constitution_id}:{','.join(sorted(self.invariants))}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class Holon:
    """
    Sovereign computational entity - the atomic unit of HOLOS.

    A Holon is a ZK bubble that:
    - Protects its private interior (balance, strategy, sub-holons)
    - Exposes a verifiable public interface
    - Can be nested fractally (individuals → groups → guilds → network)
    - Has constitutional right to exit any parent hierarchy
    """

    # === LOCUS: Persistent Identity Layer ===
    holon_id: HolonId
    state_hash: str = ""                  # Commitment to private state
    vault: int = 0                        # Public balance
    valuation: int = 0                    # Harberger self-assessment
    constitution: Constitution = field(default_factory=lambda: Constitution(constitution_id="default"))

    # Identity
    name_id: Optional[str] = None         # Reference to Name (reputation)

    # === SIGNUM: Deterministic Interface Layer ===
    wake_conditions: List[WakeCondition] = field(default_factory=list)
    public_methods: List[MethodSpec] = field(default_factory=list)
    exit_protocol: ExitSpec = field(default_factory=ExitSpec)

    # === Fractal Composition ===
    parent_sheaf_id: Optional[str] = None  # Parent Sheaf (if member)
    sub_holon_ids: List[HolonId] = field(default_factory=list)  # Nested Holons

    # === Runtime State ===
    status: HolonStatus = HolonStatus.CALCIFIED
    contracts: List[str] = field(default_factory=list)  # Active contract IDs
    mantles: List[str] = field(default_factory=list)    # Held Mantle IDs

    # === Private State (normally hidden, exposed for simulation) ===
    _private_balance: int = 0             # True balance (hidden in real ZK)
    _private_strategy: str = ""           # Strategy (hidden)

    def __post_init__(self):
        """Initialize state hash from private state."""
        self._update_state_hash()

    def _update_state_hash(self):
        """Update commitment to private state."""
        content = f"{self._private_balance}:{self._private_strategy}"
        self.state_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

    # === Public Interface ===

    def is_active(self) -> bool:
        """Check if Holon can operate."""
        return self.status in (HolonStatus.CALCIFIED, HolonStatus.HYDRATED)

    def is_solvent(self) -> bool:
        """Check if Holon has positive balance."""
        return self._private_balance >= 0

    def net_worth(self) -> int:
        """Total value: vault + private balance + valuation."""
        return self.vault + self._private_balance + self.valuation

    def can_exit(self) -> bool:
        """Constitutional invariant: exit is always possible."""
        return self.exit_protocol.always_allowed

    def hydrate(self) -> bool:
        """
        Activate the Holon (load AI/context).
        Returns True if successful.
        """
        if self.status == HolonStatus.BANKRUPT:
            return False
        self.status = HolonStatus.HYDRATED
        return True

    def calcify(self):
        """
        Deactivate the Holon (save state, release AI).
        """
        self._update_state_hash()
        self.status = HolonStatus.CALCIFIED

    def execute_exit(self, from_sheaf_id: str) -> 'ExitResult':
        """
        Exercise the constitutional right to exit.

        Returns ExitResult with:
        - success: bool
        - exit_cost: int (fee paid)
        - mantles_lost: List[str] (Mantles forfeited)
        """
        if self.parent_sheaf_id != from_sheaf_id:
            return ExitResult(success=False, message="Not a member of this Sheaf")

        # Calculate exit cost
        exit_cost = int(self.vault * self.exit_protocol.exit_cost_rate)

        # Collect forfeited Mantles
        mantles_lost = []
        if self.exit_protocol.mantles_forfeited:
            mantles_lost = self.mantles.copy()
            self.mantles = []

        # Execute exit
        self.vault -= exit_cost
        self.parent_sheaf_id = None
        self.status = HolonStatus.EXITED

        return ExitResult(
            success=True,
            exit_cost=exit_cost,
            mantles_lost=mantles_lost,
            message=f"Exited successfully, paid ${exit_cost} fee"
        )

    def deposit(self, amount: int):
        """Add funds to vault (public balance)."""
        self.vault += amount

    def withdraw(self, amount: int) -> bool:
        """Remove funds from vault. Returns False if insufficient."""
        if self.vault < amount:
            return False
        self.vault -= amount
        return True

    def set_valuation(self, new_valuation: int):
        """Update Harberger self-assessment."""
        self.valuation = max(0, new_valuation)

    def to_public_view(self) -> Dict[str, Any]:
        """Generate public view (what others can see)."""
        return {
            "holon_id": str(self.holon_id),
            "name_id": self.name_id,
            "vault": self.vault,
            "valuation": self.valuation,
            "status": self.status.value,
            "state_hash": self.state_hash,
            "constitution_hash": self.constitution.to_hash(),
            "parent_sheaf_id": self.parent_sheaf_id,
            "mantle_count": len(self.mantles),
            "contract_count": len(self.contracts),
        }


@dataclass
class ExitResult:
    """Result of executing an exit."""
    success: bool
    exit_cost: int = 0
    mantles_lost: List[str] = field(default_factory=list)
    message: str = ""


# === Factory Functions ===

def create_holon(
    initial_balance: int = 0,
    valuation: int = 0,
    constitution: Optional[Constitution] = None
) -> Holon:
    """Create a new Holon with given parameters."""
    return Holon(
        holon_id=HolonId.generate(),
        vault=initial_balance,
        valuation=valuation,
        constitution=constitution or Constitution(constitution_id="default"),
        _private_balance=initial_balance,
    )
