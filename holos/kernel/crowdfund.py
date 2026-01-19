"""
Crowdfunding Pools - Voluntary Funding for Large Projects

With flow-through economics, there is no treasury to fund large projects.
Instead, individuals receive UBI first, then VOLUNTARILY invest in pools.

Key principles:
- All pooling is voluntary and downstream of individual receipt
- Pools compete for contributions (accountable or get no funding)
- Contributors can track their investment and pool progress
- Failed pools can refund contributors (depending on pool type)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import time
import uuid

from .holon import HolonId


class PoolStatus(Enum):
    """Status of a crowdfund pool."""
    OPEN = "OPEN"              # Accepting contributions
    FUNDED = "FUNDED"          # Goal reached
    EXECUTING = "EXECUTING"    # Project in progress
    COMPLETED = "COMPLETED"    # Project delivered
    FAILED = "FAILED"          # Goal not reached by deadline
    CANCELLED = "CANCELLED"    # Cancelled by creator


class PoolType(Enum):
    """Type of crowdfund pool - determines refund policy."""
    ALL_OR_NOTHING = "ALL_OR_NOTHING"  # Full refund if goal not reached
    KEEP_WHAT_YOU_RAISE = "KEEP_WHAT_YOU_RAISE"  # No refunds
    MILESTONE_BASED = "MILESTONE_BASED"  # Funds released in stages


@dataclass
class Contribution:
    """A contribution to a crowdfund pool."""
    contributor_id: HolonId
    amount: int
    timestamp: int = field(default_factory=lambda: int(time.time()))
    refunded: bool = False


@dataclass
class Milestone:
    """A milestone in a milestone-based pool."""
    milestone_id: str
    description: str
    funding_release: int       # Amount released when achieved
    achieved: bool = False
    achieved_at: Optional[int] = None


@dataclass
class CrowdfundPool:
    """
    Voluntary pool for large projects.

    Individuals receive UBI first, then choose to invest here.
    This is the coordination mechanism that replaces treasury-funded projects.

    Design:
    - Pools compete for contributions (accountability through market)
    - Contributors retain ownership claims
    - Different pool types for different risk/reward profiles
    """
    pool_id: str
    name: str
    description: str
    creator_id: HolonId

    # Funding
    goal: int                  # Target amount
    deadline: int              # Timestamp or turn number

    # Pool type determines refund policy
    pool_type: PoolType = PoolType.ALL_OR_NOTHING

    # Contributions
    contributions: Dict[str, Contribution] = field(default_factory=dict)  # contributor_id -> Contribution

    # Milestones (for MILESTONE_BASED pools)
    milestones: List[Milestone] = field(default_factory=list)

    # Status
    status: PoolStatus = PoolStatus.OPEN
    created_at: int = field(default_factory=lambda: int(time.time()))

    # Execution
    funds_released: int = 0
    deliverables: List[str] = field(default_factory=list)

    @property
    def total_raised(self) -> int:
        """Total amount contributed (excluding refunds)."""
        return sum(
            c.amount for c in self.contributions.values()
            if not c.refunded
        )

    @property
    def contributor_count(self) -> int:
        """Number of unique contributors."""
        return len([c for c in self.contributions.values() if not c.refunded])

    @property
    def funding_percentage(self) -> float:
        """Percentage of goal reached."""
        return (self.total_raised / self.goal * 100) if self.goal > 0 else 0

    @property
    def is_funded(self) -> bool:
        """Whether the pool has reached its goal."""
        return self.total_raised >= self.goal

    def contribute(self, contributor_id: HolonId, amount: int) -> bool:
        """
        Make a voluntary contribution to the pool.

        Returns True if contribution accepted.
        """
        if self.status != PoolStatus.OPEN:
            return False

        if amount <= 0:
            return False

        contributor_key = str(contributor_id.value)

        # Add to existing contribution or create new
        if contributor_key in self.contributions:
            existing = self.contributions[contributor_key]
            if not existing.refunded:
                existing.amount += amount
        else:
            self.contributions[contributor_key] = Contribution(
                contributor_id=contributor_id,
                amount=amount,
            )

        # Check if now funded
        if self.is_funded and self.status == PoolStatus.OPEN:
            self.status = PoolStatus.FUNDED

        return True

    def get_contribution(self, contributor_id: HolonId) -> int:
        """Get total contribution from a specific contributor."""
        contributor_key = str(contributor_id.value)
        if contributor_key in self.contributions:
            c = self.contributions[contributor_key]
            return c.amount if not c.refunded else 0
        return 0

    def request_refund(self, contributor_id: HolonId) -> Optional[int]:
        """
        Request a refund. Only works for ALL_OR_NOTHING pools that haven't funded.

        Returns refund amount, or None if not eligible.
        """
        if self.pool_type != PoolType.ALL_OR_NOTHING:
            return None

        if self.status not in (PoolStatus.OPEN, PoolStatus.FAILED):
            return None

        contributor_key = str(contributor_id.value)
        if contributor_key not in self.contributions:
            return None

        contribution = self.contributions[contributor_key]
        if contribution.refunded:
            return None

        # Process refund
        refund_amount = contribution.amount
        contribution.refunded = True
        contribution.amount = 0

        return refund_amount

    def check_deadline(self, current_time: int) -> bool:
        """
        Check if deadline has passed and update status accordingly.

        Returns True if status changed.
        """
        if self.status != PoolStatus.OPEN:
            return False

        if current_time >= self.deadline:
            if self.is_funded:
                self.status = PoolStatus.FUNDED
            else:
                self.status = PoolStatus.FAILED
            return True

        return False

    def start_execution(self) -> bool:
        """Start project execution after funding."""
        if self.status != PoolStatus.FUNDED:
            return False

        self.status = PoolStatus.EXECUTING
        return True

    def achieve_milestone(self, milestone_id: str) -> Optional[int]:
        """
        Mark a milestone as achieved and release associated funds.

        Returns amount released, or None if not applicable.
        """
        if self.pool_type != PoolType.MILESTONE_BASED:
            return None

        if self.status != PoolStatus.EXECUTING:
            return None

        for milestone in self.milestones:
            if milestone.milestone_id == milestone_id and not milestone.achieved:
                milestone.achieved = True
                milestone.achieved_at = int(time.time())
                self.funds_released += milestone.funding_release
                return milestone.funding_release

        return None

    def complete(self, deliverable: str = "") -> bool:
        """Mark pool as completed with deliverable."""
        if self.status != PoolStatus.EXECUTING:
            return False

        if deliverable:
            self.deliverables.append(deliverable)

        self.status = PoolStatus.COMPLETED
        return True

    def cancel(self) -> bool:
        """Cancel the pool (creator only). Triggers refunds for ALL_OR_NOTHING."""
        if self.status not in (PoolStatus.OPEN, PoolStatus.FUNDED):
            return False

        self.status = PoolStatus.CANCELLED
        return True

    def get_refund_amounts(self) -> Dict[HolonId, int]:
        """
        Get refund amounts for all contributors.

        Only applicable for ALL_OR_NOTHING pools that failed or were cancelled.
        """
        if self.pool_type != PoolType.ALL_OR_NOTHING:
            return {}

        if self.status not in (PoolStatus.FAILED, PoolStatus.CANCELLED):
            return {}

        refunds = {}
        for contribution in self.contributions.values():
            if not contribution.refunded and contribution.amount > 0:
                refunds[contribution.contributor_id] = contribution.amount

        return refunds

    def to_public_view(self) -> Dict[str, Any]:
        """Generate public view of the pool."""
        return {
            "pool_id": self.pool_id,
            "name": self.name,
            "description": self.description,
            "creator_id": str(self.creator_id.value),
            "goal": self.goal,
            "total_raised": self.total_raised,
            "funding_percentage": self.funding_percentage,
            "contributor_count": self.contributor_count,
            "status": self.status.value,
            "pool_type": self.pool_type.value,
            "deadline": self.deadline,
            "is_funded": self.is_funded,
        }


# === Factory Functions ===

def create_pool(
    name: str,
    description: str,
    creator_id: HolonId,
    goal: int,
    deadline: int,
    pool_type: PoolType = PoolType.ALL_OR_NOTHING,
    milestones: List[Dict[str, Any]] = None
) -> CrowdfundPool:
    """Create a new crowdfund pool."""
    pool = CrowdfundPool(
        pool_id=f"pool_{uuid.uuid4().hex[:8]}",
        name=name,
        description=description,
        creator_id=creator_id,
        goal=goal,
        deadline=deadline,
        pool_type=pool_type,
    )

    if milestones and pool_type == PoolType.MILESTONE_BASED:
        for i, m in enumerate(milestones):
            pool.milestones.append(Milestone(
                milestone_id=f"ms_{i}",
                description=m.get("description", ""),
                funding_release=m.get("funding_release", 0),
            ))

    return pool


@dataclass
class PoolRegistry:
    """Registry tracking all crowdfund pools in an Enclave."""
    pools: Dict[str, CrowdfundPool] = field(default_factory=dict)

    def register(self, pool: CrowdfundPool):
        """Register a new pool."""
        self.pools[pool.pool_id] = pool

    def get(self, pool_id: str) -> Optional[CrowdfundPool]:
        """Get pool by ID."""
        return self.pools.get(pool_id)

    def get_open_pools(self) -> List[CrowdfundPool]:
        """Get all open pools accepting contributions."""
        return [p for p in self.pools.values() if p.status == PoolStatus.OPEN]

    def get_pools_by_creator(self, creator_id: HolonId) -> List[CrowdfundPool]:
        """Get all pools created by a specific Holon."""
        creator_key = str(creator_id.value)
        return [
            p for p in self.pools.values()
            if str(p.creator_id.value) == creator_key
        ]

    def get_pools_by_contributor(self, contributor_id: HolonId) -> List[CrowdfundPool]:
        """Get all pools a Holon has contributed to."""
        contributor_key = str(contributor_id.value)
        return [
            p for p in self.pools.values()
            if contributor_key in p.contributions
        ]

    def check_all_deadlines(self, current_time: int) -> List[CrowdfundPool]:
        """Check deadlines for all open pools. Returns list of pools that changed status."""
        changed = []
        for pool in self.pools.values():
            if pool.check_deadline(current_time):
                changed.append(pool)
        return changed
