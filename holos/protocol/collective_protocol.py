"""
HOLOS Collective Protocol - Fractal Economic Sovereignty

A protocol for building collectives that:
1. Start small (10-100 members) and scale fractally
2. Use ZK proofs for privacy-preserving wealth tracking
3. Implement progressive extraction without central authority
4. Create network value through liquidity and information sharing

Core insight: The protocol must make joining MORE attractive than staying
outside at EVERY scale level, while extracting wealth progressively.

Protocol Layers:
1. Identity - ZK membership proofs, reputation
2. Value - Staking, progressive fees, UBI
3. Trading - AMM liquidity pools, atomic swaps
4. Information - Encrypted sharing, prediction markets
5. Governance - Quadratic voting, parameter adjustment
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Callable
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import secrets
import time


# =============================================================================
# ZK PRIMITIVES - Privacy-Preserving Proofs
# =============================================================================

@dataclass
class ZKProof:
    """
    Zero-knowledge proof stub.

    In production, this would be a real ZK proof (e.g., Groth16, PLONK).
    For simulation, we use commitments with hidden values.
    """
    commitment: bytes  # Hash commitment to hidden value
    proof_type: str    # What this proves
    public_inputs: Dict[str, Any] = field(default_factory=dict)

    # In real implementation: proof bytes, verification key, etc.


class ZKProofSystem:
    """
    ZK proof generation and verification.

    Supports proofs for:
    - Membership: "I am a member" without revealing identity
    - Wealth bracket: "My wealth is in range [a,b]" without revealing exact amount
    - Reputation: "My reputation > threshold" without revealing score
    - Trade validity: "This trade is valid" without revealing details
    """

    @staticmethod
    def commit(value: Any, blinding: bytes = None) -> Tuple[bytes, bytes]:
        """Create a hiding commitment to a value."""
        if blinding is None:
            blinding = secrets.token_bytes(32)

        # Pedersen-style commitment: H(value || blinding)
        data = str(value).encode() + blinding
        commitment = hashlib.sha256(data).digest()

        return commitment, blinding

    @staticmethod
    def prove_membership(member_id: str, guild_merkle_root: bytes) -> ZKProof:
        """
        Prove membership in a guild without revealing identity.

        In production: Merkle proof that member_id is in the member tree.
        """
        commitment, _ = ZKProofSystem.commit(member_id)
        return ZKProof(
            commitment=commitment,
            proof_type="membership",
            public_inputs={"guild_root": guild_merkle_root.hex()},
        )

    @staticmethod
    def prove_wealth_bracket(
        actual_wealth: float,
        bracket_min: float,
        bracket_max: float,
    ) -> ZKProof:
        """
        Prove wealth is within a bracket without revealing exact amount.

        Used for progressive fee calculation - prove you're in bracket X
        without revealing if you're at the low or high end.
        """
        assert bracket_min <= actual_wealth <= bracket_max, "Wealth not in bracket"

        commitment, _ = ZKProofSystem.commit(actual_wealth)
        return ZKProof(
            commitment=commitment,
            proof_type="wealth_bracket",
            public_inputs={
                "bracket_min": bracket_min,
                "bracket_max": bracket_max,
            },
        )

    @staticmethod
    def prove_reputation_threshold(
        actual_rep: float,
        threshold: float,
    ) -> ZKProof:
        """Prove reputation exceeds threshold without revealing exact score."""
        assert actual_rep >= threshold, "Reputation below threshold"

        commitment, _ = ZKProofSystem.commit(actual_rep)
        return ZKProof(
            commitment=commitment,
            proof_type="reputation_threshold",
            public_inputs={"threshold": threshold},
        )

    @staticmethod
    def verify(proof: ZKProof) -> bool:
        """
        Verify a ZK proof.

        In production: Full cryptographic verification.
        For simulation: Always returns True (proofs are honestly generated).
        """
        # In real implementation, this would verify the cryptographic proof
        return True


# =============================================================================
# IDENTITY LAYER - Sovereign Identity with Reputation
# =============================================================================

@dataclass
class SovereignIdentity:
    """
    A sovereign identity in the collective.

    Properties:
    - Self-sovereign: Only owner controls
    - Privacy-preserving: Can prove properties without revealing identity
    - Portable: Reputation transfers across collectives
    """
    # Core identity (private)
    private_key: bytes = field(default_factory=lambda: secrets.token_bytes(32))

    # Public commitment (derived from private key)
    public_commitment: bytes = field(default=None)

    # Reputation scores (encrypted, self-attested with proofs)
    reputation_commitment: bytes = field(default=None)
    _reputation: float = field(default=0.5, repr=False)

    # Membership proofs for various collectives
    memberships: Dict[str, ZKProof] = field(default_factory=dict)

    def __post_init__(self):
        if self.public_commitment is None:
            self.public_commitment = hashlib.sha256(self.private_key).digest()
        if self.reputation_commitment is None:
            self.reputation_commitment, _ = ZKProofSystem.commit(self._reputation)

    def prove_membership(self, collective_id: str) -> Optional[ZKProof]:
        """Generate proof of membership in a collective."""
        return self.memberships.get(collective_id)

    def prove_reputation(self, threshold: float) -> Optional[ZKProof]:
        """Prove reputation exceeds threshold."""
        if self._reputation >= threshold:
            return ZKProofSystem.prove_reputation_threshold(self._reputation, threshold)
        return None

    def update_reputation(self, delta: float):
        """Update reputation (would require proof in production)."""
        self._reputation = max(0, min(1, self._reputation + delta))
        self.reputation_commitment, _ = ZKProofSystem.commit(self._reputation)


# =============================================================================
# VALUE LAYER - Staking, Fees, and UBI
# =============================================================================

@dataclass
class StakePosition:
    """A staked position in the collective."""
    owner_commitment: bytes
    amount: float
    stake_time: float
    vesting_periods: int
    unlock_time: float

    def is_vested(self, current_time: float) -> bool:
        return current_time >= self.unlock_time

    def early_exit_penalty(self, current_time: float, penalty_rate: float) -> float:
        """Calculate penalty for early exit."""
        if self.is_vested(current_time):
            return 0.0

        # Linear penalty based on time remaining
        time_remaining = self.unlock_time - current_time
        total_time = self.unlock_time - self.stake_time
        remaining_ratio = time_remaining / total_time if total_time > 0 else 0

        return self.amount * penalty_rate * remaining_ratio


class WealthBracket(Enum):
    """Wealth brackets for progressive fees."""
    TIER_1 = (0, 1000)           # Bottom tier
    TIER_2 = (1000, 10000)       # Lower middle
    TIER_3 = (10000, 100000)     # Upper middle
    TIER_4 = (100000, 1000000)   # Wealthy
    TIER_5 = (1000000, float('inf'))  # Whale


@dataclass
class ProgressiveFeeSchedule:
    """
    Progressive fee schedule based on wealth brackets.

    Higher wealth = higher fee rate.
    Uses ZK proofs so exact wealth is never revealed.
    """
    # Fee rates by bracket (as multiplier of base rate)
    bracket_multipliers: Dict[WealthBracket, float] = field(default_factory=lambda: {
        WealthBracket.TIER_1: 0.5,   # 50% of base
        WealthBracket.TIER_2: 1.0,   # 100% of base
        WealthBracket.TIER_3: 1.5,   # 150% of base
        WealthBracket.TIER_4: 2.5,   # 250% of base
        WealthBracket.TIER_5: 4.0,   # 400% of base (whales)
    })

    base_fee_rate: float = 0.02  # 2% base rate

    def get_bracket(self, wealth: float) -> WealthBracket:
        """Determine wealth bracket."""
        for bracket in WealthBracket:
            min_val, max_val = bracket.value
            if min_val <= wealth < max_val:
                return bracket
        return WealthBracket.TIER_5

    def calculate_fee(self, wealth: float) -> Tuple[float, ZKProof]:
        """
        Calculate fee and generate ZK proof of bracket.

        Returns fee amount and proof that wealth is in claimed bracket.
        """
        bracket = self.get_bracket(wealth)
        multiplier = self.bracket_multipliers[bracket]
        fee = wealth * self.base_fee_rate * multiplier

        # Generate proof of bracket membership
        min_val, max_val = bracket.value
        proof = ZKProofSystem.prove_wealth_bracket(wealth, min_val, max_val)

        return fee, proof


@dataclass
class UBIPool:
    """
    Universal Basic Income distribution pool.

    Collects fees and distributes equally to all members.
    Uses merkle trees for efficient distribution claims.
    """
    balance: float = 0.0
    distribution_interval: float = 100.0  # Time units between distributions
    last_distribution: float = 0.0

    # Merkle root of eligible recipients
    recipients_root: bytes = field(default_factory=lambda: b'\x00' * 32)
    recipient_count: int = 0

    # Claimed distributions (commitment -> claimed)
    claims: Dict[bytes, bool] = field(default_factory=dict)

    def deposit(self, amount: float):
        """Deposit fees into pool."""
        self.balance += amount

    def calculate_distribution(self) -> float:
        """Calculate per-member distribution amount."""
        if self.recipient_count == 0:
            return 0.0

        # Distribute 80% of pool, keep 20% as reserve
        distributable = self.balance * 0.8
        return distributable / self.recipient_count

    def claim(self, member_commitment: bytes, membership_proof: ZKProof) -> float:
        """
        Claim UBI distribution.

        Requires proof of membership. Each member can claim once per period.
        """
        if not ZKProofSystem.verify(membership_proof):
            return 0.0

        if self.claims.get(member_commitment, False):
            return 0.0  # Already claimed

        amount = self.calculate_distribution()
        self.claims[member_commitment] = True
        self.balance -= amount

        return amount

    def reset_period(self, new_recipients_root: bytes, count: int):
        """Start new distribution period."""
        self.recipients_root = new_recipients_root
        self.recipient_count = count
        self.claims = {}
        self.last_distribution = time.time()


# =============================================================================
# TRADING LAYER - Liquidity Pools and Atomic Swaps
# =============================================================================

@dataclass
class LiquidityPool:
    """
    Automated Market Maker (AMM) liquidity pool.

    Provides instant liquidity for any trade size.
    Uses constant product formula: x * y = k
    """
    token_a_reserve: float
    token_b_reserve: float
    total_lp_tokens: float = 0.0

    # LP token balances (commitment -> balance)
    lp_balances: Dict[bytes, float] = field(default_factory=dict)

    # Fee parameters
    swap_fee: float = 0.003  # 0.3% swap fee

    @property
    def k(self) -> float:
        """Constant product."""
        return self.token_a_reserve * self.token_b_reserve

    def get_price(self) -> float:
        """Current price of A in terms of B."""
        return self.token_b_reserve / self.token_a_reserve

    def get_output_amount(self, input_amount: float, input_is_a: bool) -> float:
        """Calculate output amount for a swap."""
        if input_is_a:
            input_reserve = self.token_a_reserve
            output_reserve = self.token_b_reserve
        else:
            input_reserve = self.token_b_reserve
            output_reserve = self.token_a_reserve

        # Apply fee
        input_with_fee = input_amount * (1 - self.swap_fee)

        # Constant product formula
        new_input_reserve = input_reserve + input_with_fee
        new_output_reserve = self.k / new_input_reserve
        output_amount = output_reserve - new_output_reserve

        return output_amount

    def swap(self, input_amount: float, input_is_a: bool) -> float:
        """Execute a swap."""
        output_amount = self.get_output_amount(input_amount, input_is_a)

        if input_is_a:
            self.token_a_reserve += input_amount
            self.token_b_reserve -= output_amount
        else:
            self.token_b_reserve += input_amount
            self.token_a_reserve -= output_amount

        return output_amount

    def add_liquidity(
        self,
        provider_commitment: bytes,
        amount_a: float,
        amount_b: float,
    ) -> float:
        """Add liquidity and receive LP tokens."""
        if self.total_lp_tokens == 0:
            # Initial liquidity
            lp_tokens = (amount_a * amount_b) ** 0.5
        else:
            # Proportional to existing liquidity
            share_a = amount_a / self.token_a_reserve
            share_b = amount_b / self.token_b_reserve
            lp_tokens = min(share_a, share_b) * self.total_lp_tokens

        self.token_a_reserve += amount_a
        self.token_b_reserve += amount_b
        self.total_lp_tokens += lp_tokens

        self.lp_balances[provider_commitment] = self.lp_balances.get(provider_commitment, 0) + lp_tokens

        return lp_tokens


@dataclass
class AtomicSwap:
    """
    Hash Time-Locked Contract for trustless swaps.

    Enables cross-collective trading without trusted intermediary.
    """
    initiator_commitment: bytes
    responder_commitment: bytes

    # Swap details
    initiator_amount: float
    responder_amount: float

    # Hash lock
    hash_lock: bytes  # H(secret)

    # Time lock
    timeout: float

    # State (has default)
    secret: Optional[bytes] = None
    state: str = "pending"  # pending, completed, refunded

    @classmethod
    def create(
        cls,
        initiator: bytes,
        responder: bytes,
        init_amount: float,
        resp_amount: float,
        timeout: float,
    ) -> Tuple['AtomicSwap', bytes]:
        """Create a new atomic swap with secret."""
        secret = secrets.token_bytes(32)
        hash_lock = hashlib.sha256(secret).digest()

        swap = cls(
            initiator_commitment=initiator,
            responder_commitment=responder,
            initiator_amount=init_amount,
            responder_amount=resp_amount,
            hash_lock=hash_lock,
            timeout=timeout,
        )

        return swap, secret

    def complete(self, secret: bytes) -> bool:
        """Complete swap by revealing secret."""
        if hashlib.sha256(secret).digest() != self.hash_lock:
            return False

        self.secret = secret
        self.state = "completed"
        return True

    def refund(self, current_time: float) -> bool:
        """Refund if timeout reached."""
        if current_time < self.timeout:
            return False

        self.state = "refunded"
        return True


# =============================================================================
# INFORMATION LAYER - Encrypted Sharing and Prediction Markets
# =============================================================================

@dataclass
class EncryptedInfoPacket:
    """
    Encrypted information for selective sharing.

    Uses threshold encryption - N of M members can decrypt.
    """
    ciphertext: bytes
    metadata: Dict[str, Any]  # Public metadata

    # Access control
    required_reputation: float = 0.0
    required_stake: float = 0.0

    # Decryption shares (in production: threshold crypto)
    decryption_threshold: int = 1
    decryption_shares: List[bytes] = field(default_factory=list)


@dataclass
class PredictionMarket:
    """
    Prediction market for collective intelligence.

    Members stake on outcomes, accurate predictors earn rewards.
    """
    question: str
    outcomes: List[str]
    resolution_time: float

    # Stakes by outcome (commitment -> amount)
    stakes: Dict[str, Dict[bytes, float]] = field(default_factory=dict)

    # Total staked per outcome
    outcome_totals: Dict[str, float] = field(default_factory=dict)

    resolved: bool = False
    winning_outcome: Optional[str] = None

    def __post_init__(self):
        for outcome in self.outcomes:
            self.stakes[outcome] = {}
            self.outcome_totals[outcome] = 0.0

    def stake(self, member_commitment: bytes, outcome: str, amount: float):
        """Stake on an outcome."""
        if outcome not in self.outcomes:
            return

        self.stakes[outcome][member_commitment] = self.stakes[outcome].get(member_commitment, 0) + amount
        self.outcome_totals[outcome] += amount

    def get_odds(self, outcome: str) -> float:
        """Get current implied odds for an outcome."""
        total = sum(self.outcome_totals.values())
        if total == 0:
            return 1.0 / len(self.outcomes)
        return self.outcome_totals.get(outcome, 0) / total

    def resolve(self, winning: str) -> Dict[bytes, float]:
        """Resolve market and calculate payouts."""
        if winning not in self.outcomes:
            return {}

        self.resolved = True
        self.winning_outcome = winning

        total_pool = sum(self.outcome_totals.values())
        winning_pool = self.outcome_totals[winning]

        if winning_pool == 0:
            return {}

        # Distribute total pool to winners proportionally
        payouts = {}
        for commitment, stake in self.stakes[winning].items():
            share = stake / winning_pool
            payouts[commitment] = total_pool * share

        return payouts


# =============================================================================
# GOVERNANCE LAYER - Quadratic Voting and Parameters
# =============================================================================

@dataclass
class QuadraticVote:
    """
    Quadratic voting for democratic decisions.

    Cost of votes scales quadratically: 1 vote = 1 credit, 2 votes = 4 credits, etc.
    This prevents plutocracy - whales can't simply buy outcomes.
    """
    proposal_id: str
    options: List[str]

    # Votes by option (commitment -> vote_count)
    votes: Dict[str, Dict[bytes, int]] = field(default_factory=dict)

    # Credits spent by voter
    credits_spent: Dict[bytes, float] = field(default_factory=dict)

    # Total votes per option
    vote_totals: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        for option in self.options:
            self.votes[option] = {}
            self.vote_totals[option] = 0

    @staticmethod
    def vote_cost(num_votes: int) -> float:
        """Quadratic cost: n votes costs n^2 credits."""
        return num_votes ** 2

    def cast_votes(self, voter: bytes, option: str, num_votes: int, available_credits: float) -> bool:
        """Cast votes on an option."""
        if option not in self.options:
            return False

        cost = self.vote_cost(num_votes)
        if cost > available_credits:
            return False

        self.votes[option][voter] = self.votes[option].get(voter, 0) + num_votes
        self.vote_totals[option] += num_votes
        self.credits_spent[voter] = self.credits_spent.get(voter, 0) + cost

        return True

    def get_result(self) -> str:
        """Get winning option."""
        return max(self.options, key=lambda o: self.vote_totals.get(o, 0))


@dataclass
class CollectiveParameters:
    """
    Governable parameters of the collective.

    All parameters can be adjusted through quadratic voting.
    """
    # Fee parameters
    base_fee_rate: float = 0.02
    progressive_exponent: float = 1.5

    # Staking parameters
    min_stake: float = 100.0
    vesting_periods: int = 10
    early_exit_penalty: float = 0.5

    # UBI parameters
    ubi_distribution_rate: float = 0.8  # % of pool distributed

    # Trading parameters
    swap_fee: float = 0.003
    min_liquidity: float = 1000.0

    # Reputation parameters
    min_reputation_to_trade: float = 0.3
    reputation_decay: float = 0.01

    # Governance parameters
    proposal_threshold: float = 0.05  # 5% of members to propose
    quorum: float = 0.20  # 20% participation required


# =============================================================================
# COLLECTIVE - The Full Protocol
# =============================================================================

@dataclass
class Collective:
    """
    A HOLOS collective implementing the full protocol.

    This is the fractal unit that scales from 10 people to global.
    """
    collective_id: str

    # Parameters (governable)
    params: CollectiveParameters = field(default_factory=CollectiveParameters)

    # Members (commitment -> stake position)
    members: Dict[bytes, StakePosition] = field(default_factory=dict)
    member_count: int = 0

    # Financial infrastructure
    fee_schedule: ProgressiveFeeSchedule = field(default_factory=ProgressiveFeeSchedule)
    ubi_pool: UBIPool = field(default_factory=UBIPool)

    # Liquidity pools (pair_id -> pool)
    liquidity_pools: Dict[str, LiquidityPool] = field(default_factory=dict)

    # Information sharing
    shared_info: Dict[str, EncryptedInfoPacket] = field(default_factory=dict)
    prediction_markets: Dict[str, PredictionMarket] = field(default_factory=dict)

    # Governance
    active_proposals: Dict[str, QuadraticVote] = field(default_factory=dict)

    # Merkle root of members (for ZK proofs)
    members_root: bytes = field(default_factory=lambda: b'\x00' * 32)

    # Parent/child collectives (fractal structure)
    parent_collective: Optional[str] = None
    child_collectives: List[str] = field(default_factory=list)

    # Metrics
    total_value_locked: float = 0.0
    total_fees_collected: float = 0.0
    total_ubi_distributed: float = 0.0

    def _update_merkle_root(self):
        """Update merkle root of members."""
        # Simplified: hash all member commitments
        data = b''.join(sorted(self.members.keys()))
        self.members_root = hashlib.sha256(data).digest()

    # =========================================================================
    # MEMBERSHIP
    # =========================================================================

    def join(self, identity: SovereignIdentity, stake_amount: float) -> bool:
        """
        Join the collective.

        Requires:
        - Minimum stake
        - Stake is locked for vesting period
        """
        if stake_amount < self.params.min_stake:
            return False

        commitment = identity.public_commitment

        if commitment in self.members:
            return False  # Already a member

        # Create stake position
        current_time = time.time()
        position = StakePosition(
            owner_commitment=commitment,
            amount=stake_amount,
            stake_time=current_time,
            vesting_periods=self.params.vesting_periods,
            unlock_time=current_time + self.params.vesting_periods * 100,  # 100 time units per period
        )

        self.members[commitment] = position
        self.member_count += 1
        self.total_value_locked += stake_amount

        # Generate membership proof
        self._update_merkle_root()
        proof = ZKProofSystem.prove_membership(str(commitment), self.members_root)
        identity.memberships[self.collective_id] = proof

        return True

    def leave(self, identity: SovereignIdentity) -> float:
        """
        Leave the collective.

        Returns stake minus any early exit penalty.
        """
        commitment = identity.public_commitment

        if commitment not in self.members:
            return 0.0

        position = self.members[commitment]
        current_time = time.time()

        penalty = position.early_exit_penalty(current_time, self.params.early_exit_penalty)
        refund = position.amount - penalty

        # Penalty goes to UBI pool
        self.ubi_pool.deposit(penalty)
        self.total_value_locked -= position.amount

        del self.members[commitment]
        self.member_count -= 1
        self._update_merkle_root()

        # Revoke membership proof
        if self.collective_id in identity.memberships:
            del identity.memberships[self.collective_id]

        return refund

    # =========================================================================
    # FEES AND UBI
    # =========================================================================

    def collect_fees(self, member_wealth: Dict[bytes, float]):
        """
        Collect progressive fees from all members.

        Fees go to UBI pool for redistribution.
        """
        total_fees = 0.0

        for commitment, wealth in member_wealth.items():
            if commitment not in self.members:
                continue

            fee, proof = self.fee_schedule.calculate_fee(wealth)

            # In production: verify proof before accepting fee
            if ZKProofSystem.verify(proof):
                total_fees += fee

        self.ubi_pool.deposit(total_fees)
        self.total_fees_collected += total_fees

        return total_fees

    def distribute_ubi(self) -> Dict[bytes, float]:
        """
        Distribute UBI to all members.

        Returns mapping of member -> distribution amount.
        """
        self.ubi_pool.reset_period(self.members_root, self.member_count)

        distributions = {}
        per_member = self.ubi_pool.calculate_distribution()

        for commitment in self.members:
            proof = ZKProofSystem.prove_membership(str(commitment), self.members_root)
            amount = self.ubi_pool.claim(commitment, proof)
            distributions[commitment] = amount
            self.total_ubi_distributed += amount

        return distributions

    # =========================================================================
    # TRADING
    # =========================================================================

    def create_pool(self, pair_id: str, amount_a: float, amount_b: float, creator: bytes) -> bool:
        """Create a new liquidity pool."""
        if pair_id in self.liquidity_pools:
            return False

        pool = LiquidityPool(
            token_a_reserve=amount_a,
            token_b_reserve=amount_b,
            swap_fee=self.params.swap_fee,
        )
        pool.add_liquidity(creator, amount_a, amount_b)

        self.liquidity_pools[pair_id] = pool
        return True

    def swap(self, pair_id: str, input_amount: float, input_is_a: bool, trader: bytes) -> float:
        """Execute a swap in a liquidity pool."""
        if pair_id not in self.liquidity_pools:
            return 0.0

        # Check membership and reputation
        if trader not in self.members:
            return 0.0  # Must be member to trade

        pool = self.liquidity_pools[pair_id]
        return pool.swap(input_amount, input_is_a)

    # =========================================================================
    # INFORMATION
    # =========================================================================

    def share_info(self, info_id: str, packet: EncryptedInfoPacket):
        """Share encrypted information with the collective."""
        self.shared_info[info_id] = packet

    def create_prediction_market(self, market_id: str, question: str, outcomes: List[str], resolution_time: float):
        """Create a new prediction market."""
        market = PredictionMarket(
            question=question,
            outcomes=outcomes,
            resolution_time=resolution_time,
        )
        self.prediction_markets[market_id] = market

    # =========================================================================
    # GOVERNANCE
    # =========================================================================

    def create_proposal(self, proposal_id: str, options: List[str], proposer: bytes) -> bool:
        """Create a new governance proposal."""
        if proposer not in self.members:
            return False

        vote = QuadraticVote(
            proposal_id=proposal_id,
            options=options,
        )
        self.active_proposals[proposal_id] = vote
        return True

    def vote(self, proposal_id: str, voter: bytes, option: str, num_votes: int, credits: float) -> bool:
        """Vote on a proposal."""
        if proposal_id not in self.active_proposals:
            return False

        if voter not in self.members:
            return False

        return self.active_proposals[proposal_id].cast_votes(voter, option, num_votes, credits)

    # =========================================================================
    # FRACTAL OPERATIONS
    # =========================================================================

    def create_child_collective(self, child_id: str) -> 'Collective':
        """Create a child collective (fractal scaling)."""
        child = Collective(
            collective_id=child_id,
            params=CollectiveParameters(**vars(self.params)),  # Copy params
            parent_collective=self.collective_id,
        )
        self.child_collectives.append(child_id)
        return child

    def join_parent(self, parent: 'Collective') -> bool:
        """Join a parent collective (fractal scaling up)."""
        # The collective itself becomes a member of the parent
        # This allows nested collectives
        self.parent_collective = parent.collective_id
        return True


# =============================================================================
# PROTOCOL VALUE CALCULATION
# =============================================================================

def calculate_collective_value(collective: Collective) -> Dict[str, float]:
    """
    Calculate the value proposition of joining a collective.

    This determines whether rational actors will join.
    """
    # Liquidity value
    total_liquidity = sum(
        pool.token_a_reserve + pool.token_b_reserve
        for pool in collective.liquidity_pools.values()
    )
    liquidity_value = (total_liquidity / 10000) ** 0.5  # Sqrt for network effects

    # Information value
    info_count = len(collective.shared_info)
    prediction_count = len(collective.prediction_markets)
    info_value = (info_count + prediction_count) * 0.01

    # Network value
    network_value = (collective.member_count / 100) ** 0.8

    # Total value
    total_value = 0.4 * liquidity_value + 0.35 * info_value + 0.25 * network_value

    # Cost (fees + staking)
    avg_fee = collective.params.base_fee_rate * 1.5  # Assume middle bracket
    stake_cost = collective.params.min_stake * 0.05  # Opportunity cost
    total_cost = avg_fee + stake_cost / 100

    return {
        "liquidity_value": liquidity_value,
        "info_value": info_value,
        "network_value": network_value,
        "total_value": total_value,
        "total_cost": total_cost,
        "net_value": total_value - total_cost,
        "should_join": total_value > total_cost,
    }
