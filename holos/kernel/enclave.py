"""
Enclave - Compositional Governance Layer

An Enclave is a group of Holons that IS itself a Holon (fractal composition).
This enables nested sovereignty: individuals → groups → guilds → network.

Taxonomy by scale:
- Enclave: Base grouping (any size)
- Collective: 100+ members - mid-scale coordination
- Kingdom: 1000+ members - large-scale governance

Constitutional invariant: An Enclave CANNOT block a sub-Holon's exit request.
The right to exit is fundamental and cannot be overridden by majority vote.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import time

from .holon import Holon, HolonId, HolonStatus, Constitution, ExitSpec, create_holon


class EnclaveType(Enum):
    """Classification of Enclave by purpose."""
    TERRITORIAL = "TERRITORIAL"    # Geographic/spatial grouping
    IMPERIAL = "IMPERIAL"          # Hierarchical structure
    FUNCTIONAL = "FUNCTIONAL"      # Task/skill-based grouping
    TEMPORARY = "TEMPORARY"        # Time-bounded coalition


class EnclaveScale(Enum):
    """Taxonomy by member count."""
    ENCLAVE = "ENCLAVE"        # Any size (base)
    COLLECTIVE = "COLLECTIVE"  # 100+ members
    KINGDOM = "KINGDOM"        # 1000+ members

    @classmethod
    def from_member_count(cls, count: int) -> 'EnclaveScale':
        if count >= 1000:
            return cls.KINGDOM
        elif count >= 100:
            return cls.COLLECTIVE
        return cls.ENCLAVE


class VotingMechanism(Enum):
    """How decisions are made in the Enclave."""
    ONE_HOLON_ONE_VOTE = "ONE_HOLON_ONE_VOTE"
    STAKE_WEIGHTED = "STAKE_WEIGHTED"          # Votes proportional to valuation
    QUADRATIC = "QUADRATIC"                     # sqrt(stake) voting power
    LIQUID_DEMOCRACY = "LIQUID_DEMOCRACY"       # Delegatable votes


class MembershipStatus(Enum):
    """Status of a Holon's membership in an Enclave."""
    PENDING = "PENDING"        # Requested, not yet approved
    ACTIVE = "ACTIVE"          # Full member
    SUSPENDED = "SUSPENDED"    # Temporarily inactive
    EXITED = "EXITED"          # Voluntarily left


@dataclass
class MembershipRecord:
    """Record of a Holon's membership in an Enclave."""
    holon_id: HolonId
    status: MembershipStatus = MembershipStatus.PENDING
    joined_at: int = 0

    # Stake (Sybil-resistant weight for UBI distribution)
    # Prevents infinite node creation to farm UBI
    stake: int = 0

    # Voting
    voting_weight: float = 1.0
    delegate_to: Optional[HolonId] = None  # For liquid democracy

    # Economics
    contribution_total: int = 0   # Total taxes/fees paid
    ubi_received: int = 0         # Total UBI received (renamed from dividend_received)

    def __hash__(self):
        return hash(self.holon_id)


class DistributionMethod(Enum):
    """How UBI is distributed among members."""
    EQUAL = "EQUAL"                    # Equal shares regardless of stake
    STAKE_WEIGHTED = "STAKE_WEIGHTED"  # Proportional to stake (Sybil-resistant)


@dataclass
class FlowRouter:
    """
    Routes tax payments directly to members as UBI. NO STORAGE.

    Key insight: Tax collection and UBI distribution are the SAME EVENT.
    There is no treasury to accumulate, no pot to capture, no attack target.

    Taxes flow DOWN, not UP:
        Tax paid → Immediately split as UBI → Members receive
    """
    tax_rate: float = 0.10           # Tax on transactions
    harberger_rate: float = 0.10     # Tax on valuations
    distribution_method: DistributionMethod = DistributionMethod.STAKE_WEIGHTED

    # Accounting (for transparency, no balance stored)
    total_routed: int = 0

    def route_tax(
        self,
        amount: int,
        members: List[MembershipRecord]
    ) -> Dict[HolonId, int]:
        """
        Route a tax payment immediately to all active members as UBI.

        This is the core flow-through mechanism:
        - NO balance accumulation
        - Tax in = UBI out (same event)
        - Stake-weighted to prevent Sybil attacks

        Returns dict of holon_id -> amount received.
        """
        active_members = [m for m in members if m.status == MembershipStatus.ACTIVE]
        if not active_members or amount <= 0:
            return {}

        distributions = {}

        if self.distribution_method == DistributionMethod.EQUAL:
            per_member = amount // len(active_members)
            for member in active_members:
                distributions[member.holon_id] = per_member
                member.ubi_received += per_member

        elif self.distribution_method == DistributionMethod.STAKE_WEIGHTED:
            total_stake = sum(m.stake for m in active_members)
            if total_stake > 0:
                for member in active_members:
                    share = int(amount * member.stake / total_stake) if member.stake > 0 else 0
                    distributions[member.holon_id] = share
                    member.ubi_received += share
            else:
                # Fallback to equal if no stakes
                per_member = amount // len(active_members)
                for member in active_members:
                    distributions[member.holon_id] = per_member
                    member.ubi_received += per_member

        self.total_routed += sum(distributions.values())
        return distributions

    def calculate_harberger_tax(self, valuation: int) -> int:
        """Calculate Harberger tax on a valuation."""
        return int(valuation * self.harberger_rate)

    def calculate_transaction_tax(self, amount: int) -> int:
        """Calculate tax on a transaction amount."""
        return int(amount * self.tax_rate)


# Legacy alias for backward compatibility
Treasury = FlowRouter
DividendPolicy = None  # Removed - no longer needed


@dataclass
class Vote:
    """A vote on a proposal."""
    voter_id: HolonId
    choice: str                    # "YES" | "NO" | "ABSTAIN"
    weight: float = 1.0
    delegated_from: List[HolonId] = field(default_factory=list)
    timestamp: int = field(default_factory=lambda: int(time.time()))


@dataclass
class Proposal:
    """A governance proposal for Enclave decision-making."""
    proposal_id: str
    proposer_id: HolonId
    proposal_type: str             # "PARAMETER_CHANGE" | "MEMBERSHIP" | "TREASURY" | "CUSTOM"
    description: str

    # Voting
    votes: Dict[str, Vote] = field(default_factory=dict)  # voter_id -> Vote
    threshold: float = 0.5         # Fraction needed to pass

    # Timing
    created_at: int = field(default_factory=lambda: int(time.time()))
    deadline: int = 0              # Voting ends at this turn

    # Resolution
    resolved: bool = False
    passed: bool = False

    def tally(self) -> Dict[str, float]:
        """Tally votes, respecting delegation weights."""
        yes_weight = sum(v.weight for v in self.votes.values() if v.choice == "YES")
        no_weight = sum(v.weight for v in self.votes.values() if v.choice == "NO")
        abstain_weight = sum(v.weight for v in self.votes.values() if v.choice == "ABSTAIN")
        total = yes_weight + no_weight + abstain_weight

        return {
            "yes": yes_weight,
            "no": no_weight,
            "abstain": abstain_weight,
            "total": total,
            "yes_ratio": yes_weight / total if total > 0 else 0,
        }

    def resolve(self) -> bool:
        """Resolve the proposal. Returns True if passed."""
        tally = self.tally()
        self.passed = tally["yes_ratio"] >= self.threshold
        self.resolved = True
        return self.passed


@dataclass
class Enclave:
    """
    A group of Holons with shared governance - itself a Holon (fractal).

    Constitutional invariant: An Enclave CANNOT block sub-Holon exit.
    Members can always leave; the only question is what they take with them.

    Taxonomy:
    - Enclave: Base grouping (any size)
    - Collective: 100+ members
    - Kingdom: 1000+ members
    """

    # The Enclave IS a Holon
    holon: Holon

    # Classification
    enclave_type: EnclaveType = EnclaveType.FUNCTIONAL

    # Membership
    members: Dict[str, MembershipRecord] = field(default_factory=dict)  # holon_id -> record
    pending_applications: List[HolonId] = field(default_factory=list)

    # Economics (Flow-through - no treasury accumulation)
    flow_router: FlowRouter = field(default_factory=FlowRouter)

    # Legacy alias
    @property
    def treasury(self) -> FlowRouter:
        """Legacy alias for flow_router."""
        return self.flow_router

    # Governance
    voting_mechanism: VotingMechanism = VotingMechanism.ONE_HOLON_ONE_VOTE
    delegation_graph: Dict[str, str] = field(default_factory=dict)  # delegator -> delegate
    active_proposals: Dict[str, Proposal] = field(default_factory=dict)

    # Mantles owned by the Enclave (can be assigned to members)
    enclave_mantles: List[str] = field(default_factory=list)

    @property
    def enclave_id(self) -> str:
        """Enclave is identified by its Holon's ID."""
        return str(self.holon.holon_id.value)

    @property
    def member_count(self) -> int:
        """Number of active members."""
        return sum(1 for m in self.members.values() if m.status == MembershipStatus.ACTIVE)

    @property
    def scale(self) -> EnclaveScale:
        """Get taxonomy classification based on size."""
        return EnclaveScale.from_member_count(self.member_count)

    @property
    def is_collective(self) -> bool:
        """True if 100+ members."""
        return self.member_count >= 100

    @property
    def is_kingdom(self) -> bool:
        """True if 1000+ members."""
        return self.member_count >= 1000

    # === Membership Management ===

    def apply_for_membership(self, holon: Holon) -> bool:
        """
        Holon requests to join. Returns True if application submitted.
        Requires bilateral consent - Enclave must also approve.
        """
        holon_id_str = str(holon.holon_id.value)

        if holon_id_str in self.members:
            return False  # Already a member

        if holon.holon_id in self.pending_applications:
            return False  # Already applied

        self.pending_applications.append(holon.holon_id)
        return True

    def approve_membership(self, holon_id: HolonId, holon: Holon) -> bool:
        """
        Enclave approves membership application.
        Bilateral consent complete - membership activated.
        """
        if holon_id not in self.pending_applications:
            return False

        holon_id_str = str(holon_id.value)

        # Create membership record
        # Stake = vault + valuation (proof-of-skin-in-the-game)
        member_stake = holon.vault + holon.valuation

        record = MembershipRecord(
            holon_id=holon_id,
            status=MembershipStatus.ACTIVE,
            joined_at=int(time.time()),
            stake=member_stake,
        )

        # Calculate voting weight based on mechanism
        if self.voting_mechanism == VotingMechanism.STAKE_WEIGHTED:
            record.voting_weight = float(member_stake)
        elif self.voting_mechanism == VotingMechanism.QUADRATIC:
            record.voting_weight = float(member_stake) ** 0.5

        self.members[holon_id_str] = record
        self.pending_applications.remove(holon_id)

        # Update Holon's parent reference
        holon.parent_sheaf_id = self.enclave_id  # TODO: rename to parent_enclave_id

        return True

    def process_exit(self, holon: Holon) -> Dict[str, Any]:
        """
        Process a Holon's exit request.

        CONSTITUTIONAL INVARIANT: Exit CANNOT be blocked.
        The Enclave can only determine:
        - Exit cost (within constitutional limits)
        - Which Mantles stay behind
        """
        holon_id_str = str(holon.holon_id.value)

        if holon_id_str not in self.members:
            return {"success": False, "reason": "Not a member"}

        record = self.members[holon_id_str]

        # Exit always succeeds (constitutional invariant)
        exit_result = holon.execute_exit(self.enclave_id)

        if exit_result.success:
            # Update membership record
            record.status = MembershipStatus.EXITED

            # Remove from delegation graph
            if holon_id_str in self.delegation_graph:
                del self.delegation_graph[holon_id_str]

            # Re-route any delegations TO this holon
            for delegator, delegate in list(self.delegation_graph.items()):
                if delegate == holon_id_str:
                    del self.delegation_graph[delegator]

            return {
                "success": True,
                "exit_cost": exit_result.exit_cost,
                "mantles_lost": exit_result.mantles_lost,
            }

        return {"success": False, "reason": exit_result.message}

    # === Governance ===

    def create_proposal(
        self,
        proposer_id: HolonId,
        proposal_type: str,
        description: str,
        deadline: int = 0,
        threshold: float = 0.5
    ) -> Optional[Proposal]:
        """Create a new governance proposal."""
        proposer_str = str(proposer_id.value)

        if proposer_str not in self.members:
            return None

        if self.members[proposer_str].status != MembershipStatus.ACTIVE:
            return None

        proposal = Proposal(
            proposal_id=f"prop_{len(self.active_proposals)}",
            proposer_id=proposer_id,
            proposal_type=proposal_type,
            description=description,
            deadline=deadline,
            threshold=threshold,
        )

        self.active_proposals[proposal.proposal_id] = proposal
        return proposal

    def cast_vote(
        self,
        voter_id: HolonId,
        proposal_id: str,
        choice: str
    ) -> bool:
        """Cast a vote on a proposal."""
        voter_str = str(voter_id.value)

        if proposal_id not in self.active_proposals:
            return False

        if voter_str not in self.members:
            return False

        record = self.members[voter_str]
        if record.status != MembershipStatus.ACTIVE:
            return False

        proposal = self.active_proposals[proposal_id]

        # Calculate effective weight (including delegated votes)
        weight = record.voting_weight
        delegated_from = []

        if self.voting_mechanism == VotingMechanism.LIQUID_DEMOCRACY:
            # Collect delegations
            for delegator_str, delegate_str in self.delegation_graph.items():
                if delegate_str == voter_str:
                    delegator_record = self.members.get(delegator_str)
                    if delegator_record and delegator_record.status == MembershipStatus.ACTIVE:
                        weight += delegator_record.voting_weight
                        delegated_from.append(HolonId.from_string(delegator_str))

        vote = Vote(
            voter_id=voter_id,
            choice=choice,
            weight=weight,
            delegated_from=delegated_from,
        )

        proposal.votes[voter_str] = vote
        return True

    def delegate_vote(self, delegator_id: HolonId, delegate_id: HolonId) -> bool:
        """Delegate voting power to another member (liquid democracy)."""
        delegator_str = str(delegator_id.value)
        delegate_str = str(delegate_id.value)

        if delegator_str not in self.members or delegate_str not in self.members:
            return False

        # Prevent delegation loops
        current = delegate_str
        visited = {delegator_str}
        while current in self.delegation_graph:
            if current in visited:
                return False  # Would create a loop
            visited.add(current)
            current = self.delegation_graph[current]

        self.delegation_graph[delegator_str] = delegate_str
        return True

    # === Economics (Flow-Through) ===

    def collect_and_distribute_taxes(self, holons: Dict[str, Holon]) -> Dict[str, Any]:
        """
        Collect Harberger taxes and IMMEDIATELY distribute as UBI.

        This is the core flow-through mechanism:
        - Tax collection and UBI distribution are the SAME EVENT
        - No treasury accumulation, no pot to capture
        - Stake-weighted to prevent Sybil attacks

        Returns dict with:
        - total_collected: int
        - distributions: Dict[HolonId, int] (UBI received per member)
        """
        total_collected = 0
        all_distributions: Dict[HolonId, int] = {}

        active_members = [m for m in self.members.values() if m.status == MembershipStatus.ACTIVE]

        for holon_id_str, record in self.members.items():
            if record.status != MembershipStatus.ACTIVE:
                continue

            holon = holons.get(holon_id_str)
            if not holon:
                continue

            # Calculate tax
            tax = self.flow_router.calculate_harberger_tax(holon.valuation)
            if tax <= 0:
                continue

            # Withdraw from payer
            if holon.withdraw(tax):
                record.contribution_total += tax
                total_collected += tax

                # IMMEDIATELY route as UBI to all members (same event!)
                distributions = self.flow_router.route_tax(tax, active_members)

                # Merge distributions
                for h_id, amount in distributions.items():
                    all_distributions[h_id] = all_distributions.get(h_id, 0) + amount

                    # Credit to recipient's vault
                    recipient_holon = holons.get(str(h_id.value))
                    if recipient_holon:
                        recipient_holon.deposit(amount)

                # Update payer's stake (they just paid tax)
                record.stake = holon.vault + holon.valuation

        return {
            "total_collected": total_collected,
            "distributions": all_distributions,
        }

    def update_member_stakes(self, holons: Dict[str, Holon]):
        """Update all member stakes based on current vault + valuation."""
        for holon_id_str, record in self.members.items():
            if record.status != MembershipStatus.ACTIVE:
                continue
            holon = holons.get(holon_id_str)
            if holon:
                record.stake = holon.vault + holon.valuation

    # Legacy method - redirects to new flow-through method
    def collect_member_taxes(self, holons: Dict[str, Holon]) -> int:
        """Legacy method. Use collect_and_distribute_taxes() instead."""
        result = self.collect_and_distribute_taxes(holons)
        return result["total_collected"]

    def distribute_dividends(self) -> Dict[HolonId, int]:
        """
        Legacy method - no longer needed with flow-through economics.
        Taxes are distributed as UBI at collection time.
        """
        return {}  # No-op - distribution happens at collection

    # === Public View ===

    def to_public_view(self) -> Dict[str, Any]:
        """Generate public view of the Enclave."""
        return {
            "enclave_id": self.enclave_id,
            "enclave_type": self.enclave_type.value,
            "scale": self.scale.value,
            "member_count": self.member_count,
            "is_collective": self.is_collective,
            "is_kingdom": self.is_kingdom,
            "total_routed": self.flow_router.total_routed,  # No balance - flow-through
            "distribution_method": self.flow_router.distribution_method.value,
            "voting_mechanism": self.voting_mechanism.value,
            "active_proposals": len(self.active_proposals),
            "holon_view": self.holon.to_public_view(),
        }


# === Factory Functions ===

def create_enclave(
    enclave_type: EnclaveType = EnclaveType.FUNCTIONAL,
    initial_balance: int = 0,
    tax_rate: float = 0.10,
    harberger_rate: float = 0.10,
    distribution_method: DistributionMethod = DistributionMethod.STAKE_WEIGHTED,
    voting_mechanism: VotingMechanism = VotingMechanism.ONE_HOLON_ONE_VOTE,
    constitution: Optional[Constitution] = None
) -> Enclave:
    """
    Create a new Enclave with flow-through economics.

    Note: initial_balance goes to the Enclave's Holon vault, not a treasury.
    There is no treasury accumulation - taxes flow directly to members as UBI.
    """
    holon = create_holon(
        initial_balance=initial_balance,
        constitution=constitution,
    )

    flow_router = FlowRouter(
        tax_rate=tax_rate,
        harberger_rate=harberger_rate,
        distribution_method=distribution_method,
    )

    return Enclave(
        holon=holon,
        enclave_type=enclave_type,
        flow_router=flow_router,
        voting_mechanism=voting_mechanism,
    )
