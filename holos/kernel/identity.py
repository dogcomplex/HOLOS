"""
Identity System - Names and Mantles

Names: Persistent identity with reputation that travels with the Holon on exit.
Mantles: Transferable authority with rights and responsibilities that stays behind.

This separation allows:
- Reputation to be portable (you keep your Name when you leave)
- Roles to be stable (the Mantle stays with the organization)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import hashlib
import time


class RootType(Enum):
    """Root of trust for identity verification."""
    HUMAN = "HUMAN"           # Biometric/government verified human
    AI = "AI"                 # Verified AI agent
    CAPITAL = "CAPITAL"       # Proof-of-stake/work/burn
    PROTOCOL = "PROTOCOL"     # Smart contract / protocol


@dataclass
class Name:
    """
    Persistent identity with reputation history.

    A Name is attached to a Holon and accumulates reputation over time.
    When a Holon exits a Sheaf, their Name (and reputation) travels with them.

    Names are the "who you are" - your history and trustworthiness.
    """
    name_id: str
    display_name: str
    owner_holon_id: str           # Current owner's HolonId

    # Root of trust
    root_type: RootType = RootType.AI
    created_at: int = field(default_factory=lambda: int(time.time()))

    # Reputation metrics (accumulate over time, portable)
    reputation_score: float = 0.0
    contracts_completed: int = 0
    contracts_breached: int = 0
    total_value_transacted: int = 0

    # Exit history (tracks voluntary departures)
    exit_count: int = 0
    sheafs_joined: int = 0

    # History commitment (ZK proof of full history)
    history_hash: str = ""

    def __post_init__(self):
        self._update_history_hash()

    def _update_history_hash(self):
        """Update commitment to reputation history."""
        content = f"{self.name_id}:{self.reputation_score}:{self.contracts_completed}:{self.contracts_breached}"
        self.history_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

    def record_contract_completion(self, value: int = 0):
        """Record successful contract completion."""
        self.contracts_completed += 1
        self.total_value_transacted += value
        self._update_reputation()
        self._update_history_hash()

    def record_contract_breach(self, severity: float = 1.0):
        """Record contract breach (damages reputation)."""
        self.contracts_breached += 1
        self.reputation_score -= severity * 10
        self._update_history_hash()

    def record_exit(self):
        """Record exercising exit right (neutral to reputation)."""
        self.exit_count += 1
        self._update_history_hash()

    def record_join(self):
        """Record joining a Sheaf."""
        self.sheafs_joined += 1
        self._update_history_hash()

    def _update_reputation(self):
        """Recalculate reputation score."""
        if self.contracts_completed + self.contracts_breached == 0:
            self.reputation_score = 0.0
        else:
            completion_rate = self.contracts_completed / (self.contracts_completed + self.contracts_breached)
            self.reputation_score = completion_rate * 100 * (1 + self.contracts_completed / 100)

    def transfer_to(self, new_owner_holon_id: str):
        """Transfer Name ownership (rare - usually Names stay with Holon)."""
        self.owner_holon_id = new_owner_holon_id

    def get_trust_level(self) -> str:
        """Human-readable trust assessment."""
        if self.contracts_completed < 5:
            return "NEW"
        elif self.reputation_score < 50:
            return "LOW"
        elif self.reputation_score < 80:
            return "MEDIUM"
        elif self.reputation_score < 95:
            return "HIGH"
        else:
            return "EXCELLENT"

    def to_public_view(self) -> Dict[str, Any]:
        """Public view of Name (what others can see)."""
        return {
            "name_id": self.name_id,
            "display_name": self.display_name,
            "root_type": self.root_type.value,
            "reputation_score": round(self.reputation_score, 2),
            "contracts_completed": self.contracts_completed,
            "contracts_breached": self.contracts_breached,
            "trust_level": self.get_trust_level(),
            "history_hash": self.history_hash,
        }


@dataclass
class Right:
    """A specific right granted by a Mantle."""
    right_id: str
    description: str
    action_type: str              # What action this permits
    resource_scope: str = "*"     # What resources it applies to
    conditions: List[str] = field(default_factory=list)  # Conditions for exercise


@dataclass
class Responsibility:
    """A specific responsibility required by a Mantle."""
    responsibility_id: str
    description: str
    action_type: str              # What must be done
    frequency: str = "continuous"  # "continuous" | "periodic" | "on_demand"
    penalty_for_failure: int = 0  # Cost of failing this responsibility


@dataclass
class Mantle:
    """
    Transferable authority with rights and responsibilities.

    A Mantle is a role or position that grants specific rights and requires
    specific responsibilities. When a Holon exits, their Mantles stay behind
    (either returned to issuer or transferred).

    Mantles are the "what you can do" - your authority and obligations.

    Examples:
    - Property ownership (right to collect rent, responsibility to pay tax)
    - Treasury manager (right to move funds, responsibility to report)
    - Validator node (right to earn fees, responsibility to stay online)
    """
    mantle_id: str
    name: str                     # Human-readable name
    description: str = ""

    # Issuer
    issuing_sheaf_id: str = ""    # Who created this Mantle

    # Current holder
    holder_holon_id: Optional[str] = None

    # What this Mantle grants
    rights: List[Right] = field(default_factory=list)
    access_keys: List[str] = field(default_factory=list)  # Resource access

    # What this Mantle requires
    responsibilities: List[Responsibility] = field(default_factory=list)
    bond_required: int = 0        # Stake required to hold this Mantle

    # Harberger properties (for transferable Mantles)
    valuation: int = 0            # Self-assessed value
    transferable: bool = True     # Can be bought/sold
    harberger_enabled: bool = True  # Subject to forced sale at valuation

    # Transfer history
    transfer_count: int = 0
    created_at: int = field(default_factory=lambda: int(time.time()))

    def is_held(self) -> bool:
        """Check if Mantle is currently held."""
        return self.holder_holon_id is not None

    def assign_to(self, holon_id: str) -> bool:
        """Assign Mantle to a Holon."""
        if self.is_held():
            return False
        self.holder_holon_id = holon_id
        return True

    def transfer_to(self, new_holder_id: str, price: int = 0) -> bool:
        """Transfer Mantle to new holder."""
        if not self.transferable:
            return False
        self.holder_holon_id = new_holder_id
        self.transfer_count += 1
        return True

    def release(self) -> bool:
        """Release Mantle (return to unassigned state)."""
        if not self.is_held():
            return False
        self.holder_holon_id = None
        return True

    def set_valuation(self, new_valuation: int):
        """Update Harberger self-assessment."""
        self.valuation = max(0, new_valuation)

    def calculate_tax(self, tax_rate: float) -> int:
        """Calculate Harberger tax owed."""
        return int(self.valuation * tax_rate)

    def to_public_view(self) -> Dict[str, Any]:
        """Public view of Mantle."""
        return {
            "mantle_id": self.mantle_id,
            "name": self.name,
            "issuing_sheaf_id": self.issuing_sheaf_id,
            "holder_holon_id": self.holder_holon_id,
            "valuation": self.valuation,
            "transferable": self.transferable,
            "harberger_enabled": self.harberger_enabled,
            "bond_required": self.bond_required,
            "rights_count": len(self.rights),
            "responsibilities_count": len(self.responsibilities),
        }


# === Registries ===

class NameRegistry:
    """Registry tracking all Names in the system."""

    def __init__(self):
        self.names: Dict[str, Name] = {}
        self._next_id = 1

    def create_name(
        self,
        display_name: str,
        owner_holon_id: str,
        root_type: RootType = RootType.AI
    ) -> Name:
        """Create and register a new Name."""
        name_id = f"name_{self._next_id}"
        self._next_id += 1

        name = Name(
            name_id=name_id,
            display_name=display_name,
            owner_holon_id=owner_holon_id,
            root_type=root_type,
        )
        self.names[name_id] = name
        return name

    def get(self, name_id: str) -> Optional[Name]:
        return self.names.get(name_id)

    def get_by_owner(self, holon_id: str) -> List[Name]:
        return [n for n in self.names.values() if n.owner_holon_id == holon_id]


class MantleRegistry:
    """Registry tracking all Mantles in the system."""

    def __init__(self):
        self.mantles: Dict[str, Mantle] = {}
        self._next_id = 1

    def create_mantle(
        self,
        name: str,
        issuing_sheaf_id: str,
        rights: List[Right] = None,
        responsibilities: List[Responsibility] = None,
        bond_required: int = 0,
        transferable: bool = True,
    ) -> Mantle:
        """Create and register a new Mantle."""
        mantle_id = f"mantle_{self._next_id}"
        self._next_id += 1

        mantle = Mantle(
            mantle_id=mantle_id,
            name=name,
            issuing_sheaf_id=issuing_sheaf_id,
            rights=rights or [],
            responsibilities=responsibilities or [],
            bond_required=bond_required,
            transferable=transferable,
        )
        self.mantles[mantle_id] = mantle
        return mantle

    def get(self, mantle_id: str) -> Optional[Mantle]:
        return self.mantles.get(mantle_id)

    def get_by_holder(self, holon_id: str) -> List[Mantle]:
        return [m for m in self.mantles.values() if m.holder_holon_id == holon_id]

    def get_by_issuer(self, sheaf_id: str) -> List[Mantle]:
        return [m for m in self.mantles.values() if m.issuing_sheaf_id == sheaf_id]

    def get_available(self) -> List[Mantle]:
        """Get all unassigned Mantles."""
        return [m for m in self.mantles.values() if not m.is_held()]
