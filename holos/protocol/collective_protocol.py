"""
HOLOS Collective Protocol - Fractal Economic Sovereignty

A protocol for building enclaves that:
1. Start small (10-100 members) and scale fractally
2. Use ZK proofs for privacy-preserving wealth tracking
3. Implement progressive extraction without central authority
4. Create network value through liquidity and information sharing

Core insight: The protocol must make joining MORE attractive than staying
outside at EVERY scale level, while extracting wealth progressively.

Protocol Layers:
1. Identity - ZK membership proofs, reputation (aligned with kernel Name/Holon)
2. Value - Staking, progressive fees, flow-through UBI
3. Trading - AMM liquidity pools, atomic swaps
4. Information - Encrypted sharing, prediction markets
5. Governance - Quadratic voting, parameter adjustment

Naming Convention (aligned with holos/kernel):
- Enclave: Base group of Holons (any size, <100)
- Collective: 100+ members - mid-scale coordination
- Kingdom: 1000+ members - large-scale governance

Constitutional Invariants (from holos/kernel/constitution.py):
1. Non-Blocking Exit - Sub-Holon can detach without parent permission
2. Proof of Solvency - SUM(Inputs) >= SUM(Outputs), provable via ZK
3. Explicit Consent - Membership requires bilateral cryptographic consent
4. Sybil Resistance - Voting weight proportional to proven root
5. Legible Interface - Public methods standardized; interior private
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Callable
from enum import Enum, auto
from abc import ABC, abstractmethod
import hashlib
import secrets
import time


# =============================================================================
# SCALE TAXONOMY (aligned with holos/kernel/enclave.py)
# =============================================================================

class EnclaveScale(Enum):
    """Scale taxonomy for fractal groups."""
    ENCLAVE = auto()     # < 100 members - small group
    COLLECTIVE = auto()  # 100-999 members - mid-scale
    KINGDOM = auto()     # 1000+ members - large-scale

    @classmethod
    def from_member_count(cls, count: int) -> 'EnclaveScale':
        if count >= 1000:
            return cls.KINGDOM
        elif count >= 100:
            return cls.COLLECTIVE
        return cls.ENCLAVE


# =============================================================================
# ZK PRIMITIVES - Aligned with holos/kernel/zk/mock_proof.py
# =============================================================================

class StatementType(Enum):
    """
    Types of ZK statements (aligned with kernel).

    From holos/kernel/zk/mock_proof.py:
    - SOLVENCY: Balance >= threshold
    - RANGE: Value in [min, max]
    - MEMBERSHIP: Member of set
    - CONSTITUTIONAL: Transition obeys constitution
    - EXIT_RIGHT: Has right to exit contract
    - CREDENTIAL: Possesses credential
    """
    SOLVENCY = "solvency"
    RANGE = "range"
    MEMBERSHIP = "membership"
    CONSTITUTIONAL = "constitutional"
    EXIT_RIGHT = "exit_right"
    CREDENTIAL = "credential"
    WEALTH_BRACKET = "wealth_bracket"  # Protocol-specific
    REPUTATION = "reputation"          # Protocol-specific


@dataclass
class ZKProof:
    """
    Zero-knowledge proof stub (aligned with kernel's MockZKProof).

    In production, this would be a real ZK proof (e.g., Groth16, PLONK).
    For simulation, we use commitments with hidden values.

    Aligned with holos/kernel/zk/mock_proof.py:MockZKProof
    """
    commitment: bytes           # Hash commitment to hidden value
    statement_type: StatementType  # What this proves (aligned with kernel)
    public_inputs: Dict[str, Any] = field(default_factory=dict)

    # Witness data (private - only for simulation)
    _witness: Any = field(default=None, repr=False)

    # Cost model (aligned with kernel - expensive to create, cheap to verify)
    creation_cost: int = 100   # Prover pays
    verification_cost: int = 1  # Cheap to verify

    # Backward compatibility alias
    @property
    def proof_type(self) -> str:
        return self.statement_type.value


class ZKProofSystem:
    """
    ZK proof generation and verification.

    Aligned with holos/kernel/zk/mock_proof.py:MockProver/MockVerifier

    Supports proofs for:
    - Membership: "I am a member" without revealing identity
    - Wealth bracket: "My wealth is in range [a,b]" without revealing exact amount
    - Reputation: "My reputation > threshold" without revealing score
    - Solvency: "My balance >= X"
    - Constitutional: "My transition obeys constitution"
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
    def prove_membership(member_id: str, enclave_merkle_root: bytes) -> ZKProof:
        """
        Prove membership in an enclave without revealing identity.

        In production: Merkle proof that member_id is in the member tree.
        """
        commitment, _ = ZKProofSystem.commit(member_id)
        return ZKProof(
            commitment=commitment,
            statement_type=StatementType.MEMBERSHIP,
            public_inputs={"enclave_root": enclave_merkle_root.hex()},
            _witness=member_id,
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
            statement_type=StatementType.WEALTH_BRACKET,
            public_inputs={
                "bracket_min": bracket_min,
                "bracket_max": bracket_max,
            },
            _witness=actual_wealth,
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
            statement_type=StatementType.REPUTATION,
            public_inputs={"threshold": threshold},
            _witness=actual_rep,
        )

    @staticmethod
    def prove_solvency(balance: float, threshold: float) -> ZKProof:
        """Prove balance >= threshold (aligned with kernel)."""
        assert balance >= threshold, "Balance below threshold"

        commitment, _ = ZKProofSystem.commit(balance)
        return ZKProof(
            commitment=commitment,
            statement_type=StatementType.SOLVENCY,
            public_inputs={"threshold": threshold},
            _witness=balance,
        )

    @staticmethod
    def prove_exit_right(holon_id: str, contract_id: str) -> ZKProof:
        """Prove right to exit a contract (constitutional invariant)."""
        commitment, _ = ZKProofSystem.commit(f"{holon_id}:{contract_id}")
        return ZKProof(
            commitment=commitment,
            statement_type=StatementType.EXIT_RIGHT,
            public_inputs={"contract_id": contract_id},
            _witness=holon_id,
        )

    @staticmethod
    def verify(proof: ZKProof) -> bool:
        """
        Verify a ZK proof.

        In production: Full cryptographic verification.
        For simulation: Always returns True (proofs are honestly generated).

        Aligned with holos/kernel/zk/mock_proof.py:MockVerifier
        """
        # In real implementation, this would verify the cryptographic proof
        return True


# =============================================================================
# IDENTITY LAYER - Aligned with holos/kernel/identity.py and holon.py
# =============================================================================

class RootType(Enum):
    """
    Root of trust for identity (aligned with kernel).

    From holos/kernel/identity.py:
    Determines Sybil resistance weight.
    """
    HUMAN = "human"      # Proof of personhood
    AI = "ai"           # Verified AI agent
    CAPITAL = "capital"  # Capital-backed (can be purchased)
    PROTOCOL = "protocol"  # System-generated


@dataclass
class SovereignIdentity:
    """
    A sovereign identity in the enclave.

    Aligned with holos/kernel concepts:
    - Holon: Fundamental computational entity with LOCUS (persistent) layer
    - Name: Reputation-bearing identity that travels on exit

    Properties:
    - Self-sovereign: Only owner controls
    - Privacy-preserving: Can prove properties without revealing identity
    - Portable: Reputation transfers across enclaves (like kernel Name)
    - Exit-guaranteed: Can always leave (constitutional invariant)
    """
    # Core identity (private) - analogous to Holon.private_key
    private_key: bytes = field(default_factory=lambda: secrets.token_bytes(32))

    # Public commitment (derived from private key) - analogous to Holon.holon_id
    public_commitment: bytes = field(default=None)

    # Root of trust (aligned with kernel Name.root_type)
    root_type: RootType = RootType.HUMAN

    # Display name (optional, aligned with kernel Name.display_name)
    display_name: str = ""

    # Reputation scores (encrypted, self-attested with proofs)
    # Aligned with kernel Name reputation fields
    reputation_commitment: bytes = field(default=None)
    _reputation: float = field(default=0.5, repr=False)

    # Transaction history (aligned with kernel Name fields)
    contracts_completed: int = 0
    contracts_breached: int = 0
    exit_count: int = 0  # Times exercised exit right

    # Membership proofs for various enclaves
    memberships: Dict[str, ZKProof] = field(default_factory=dict)

    # History hash (aligned with kernel Name.history_hash)
    history_hash: bytes = field(default_factory=lambda: b'\x00' * 32)

    def __post_init__(self):
        if self.public_commitment is None:
            self.public_commitment = hashlib.sha256(self.private_key).digest()
        if self.reputation_commitment is None:
            self.reputation_commitment, _ = ZKProofSystem.commit(self._reputation)

    @property
    def holon_id(self) -> bytes:
        """Alias for public_commitment (kernel compatibility)."""
        return self.public_commitment

    def prove_membership(self, enclave_id: str) -> Optional[ZKProof]:
        """Generate proof of membership in an enclave."""
        return self.memberships.get(enclave_id)

    def prove_reputation(self, threshold: float) -> Optional[ZKProof]:
        """Prove reputation exceeds threshold."""
        if self._reputation >= threshold:
            return ZKProofSystem.prove_reputation_threshold(self._reputation, threshold)
        return None

    def prove_solvency(self, balance: float, threshold: float) -> Optional[ZKProof]:
        """Prove balance >= threshold (kernel alignment)."""
        if balance >= threshold:
            return ZKProofSystem.prove_solvency(balance, threshold)
        return None

    def update_reputation(self, delta: float):
        """Update reputation (would require proof in production)."""
        self._reputation = max(0, min(1, self._reputation + delta))
        self.reputation_commitment, _ = ZKProofSystem.commit(self._reputation)
        # Update history hash
        self._update_history()

    def record_contract_completion(self, success: bool):
        """Record contract completion (aligned with kernel Name)."""
        if success:
            self.contracts_completed += 1
            self.update_reputation(0.01)
        else:
            self.contracts_breached += 1
            self.update_reputation(-0.05)

    def record_exit(self):
        """Record exercise of exit right."""
        self.exit_count += 1
        self._update_history()

    def _update_history(self):
        """Update history hash commitment."""
        data = f"{self.contracts_completed}:{self.contracts_breached}:{self.exit_count}:{self._reputation}"
        self.history_hash = hashlib.sha256(data.encode()).digest()


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
class FlowRouter:
    """
    Flow-through UBI distribution (aligned with holos/kernel/enclave.py).

    KEY DESIGN: No treasury accumulation - taxes flow immediately as UBI.
    This eliminates the treasury as an attack target.

    From the plan:
    > "The 'treasury' becomes a **routing function**, not a storage account."

    Traditional:  Holon pays tax → Treasury accumulates → Later distributes
                                           ↑ (Attack target!)

    Flow-Through: Holon pays tax ═══════════════> Immediately split as UBI
                                   (Same event, no storage)
    """
    distribution_method: str = "STAKE_WEIGHTED"  # or "EQUAL"
    distribution_rate: float = 1.0  # 100% flow-through (no reserve)

    # Merkle root of eligible recipients (for verification)
    recipients_root: bytes = field(default_factory=lambda: b'\x00' * 32)

    # Tracking (no balance stored!)
    total_routed: float = 0.0
    last_distribution: float = 0.0

    def route_tax(
        self,
        amount: float,
        members: Dict[bytes, 'StakePosition'],
    ) -> Dict[bytes, float]:
        """
        Route tax payment immediately as UBI. Returns distribution per member.

        Key: No self.balance - nothing is stored, everything flows through.

        Args:
            amount: Tax amount to distribute
            members: Dict of member commitment -> stake position

        Returns:
            Dict of member commitment -> UBI amount received
        """
        if not members:
            return {}

        distributions = {}
        distributable = amount * self.distribution_rate

        if self.distribution_method == "STAKE_WEIGHTED":
            # Stake-weighted distribution (Sybil-resistant)
            total_stake = sum(pos.amount for pos in members.values())
            if total_stake == 0:
                # Fall back to equal distribution
                per_member = distributable / len(members)
                return {commitment: per_member for commitment in members}

            for commitment, position in members.items():
                share = position.amount / total_stake
                distributions[commitment] = distributable * share
        else:
            # Equal distribution
            per_member = distributable / len(members)
            distributions = {commitment: per_member for commitment in members}

        self.total_routed += distributable
        self.last_distribution = time.time()

        return distributions

    def update_recipients(self, members_root: bytes):
        """Update merkle root of eligible recipients."""
        self.recipients_root = members_root


# Backward compatibility alias
class UBIPool(FlowRouter):
    """
    Backward compatibility wrapper for FlowRouter.

    DEPRECATED: Use FlowRouter directly. UBIPool is kept for
    compatibility with existing simulations.
    """
    # Additional tracking for backward compatibility
    _pending: float = 0.0  # Accumulates until distribution triggered
    recipient_count: int = 0
    claims: Dict[bytes, bool] = field(default_factory=dict)

    @property
    def balance(self) -> float:
        """Backward compat: returns pending amount (not a real treasury)."""
        return self._pending

    def deposit(self, amount: float):
        """Accumulate pending (will be distributed on next cycle)."""
        self._pending += amount

    def calculate_distribution(self) -> float:
        """Calculate per-member distribution amount."""
        if self.recipient_count == 0:
            return 0.0
        distributable = self._pending * self.distribution_rate
        return distributable / self.recipient_count

    def claim(self, member_commitment: bytes, membership_proof: ZKProof) -> float:
        """Claim UBI distribution (backward compat interface)."""
        if not ZKProofSystem.verify(membership_proof):
            return 0.0
        if self.claims.get(member_commitment, False):
            return 0.0

        amount = self.calculate_distribution()
        self.claims[member_commitment] = True
        self._pending -= amount
        self.total_routed += amount

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
# CONSTITUTIONAL INVARIANTS (from holos/kernel/constitution.py)
# =============================================================================

class ConstitutionalInvariant(Enum):
    """
    The five constitutional invariants that cannot be violated.

    From holos/kernel/constitution.py - these define HOLOS identity.
    """
    NON_BLOCKING_EXIT = "non_blocking_exit"     # Sub-Holon can detach without parent permission
    PROOF_OF_SOLVENCY = "proof_of_solvency"     # SUM(Inputs) >= SUM(Outputs)
    EXPLICIT_CONSENT = "explicit_consent"       # Membership requires bilateral consent
    SYBIL_RESISTANCE = "sybil_resistance"       # Voting weight proportional to proven root
    LEGIBLE_INTERFACE = "legible_interface"     # Public methods standardized


@dataclass
class ConstitutionalChecker:
    """
    Checks that operations respect constitutional invariants.

    Enforced through reputation contagion, not authority.
    Violations result in reputation hits and exclusion.
    """

    def check_exit_allowed(self, holon_id: bytes, enclave: 'Enclave') -> Tuple[bool, str]:
        """
        Check NON_BLOCKING_EXIT: Exit can never be blocked.

        This is THE core right - without this, it's just another trap.
        """
        # Exit is ALWAYS allowed - this is a constitutional invariant
        return True, "Exit always permitted (constitutional guarantee)"

    def check_solvency(self, balance: float, withdrawal: float) -> Tuple[bool, str]:
        """Check PROOF_OF_SOLVENCY: Outputs cannot exceed inputs."""
        if withdrawal > balance:
            return False, f"Withdrawal {withdrawal} exceeds balance {balance}"
        return True, "Solvency maintained"

    def check_consent(self, proposer: bytes, acceptor: bytes) -> Tuple[bool, str]:
        """Check EXPLICIT_CONSENT: Both parties must agree."""
        # In production, verify signatures from both parties
        if proposer is None or acceptor is None:
            return False, "Missing consent signature"
        return True, "Bilateral consent verified"

    def check_sybil_resistance(self, voter: SovereignIdentity, enclave: 'Enclave') -> Tuple[bool, float]:
        """
        Check SYBIL_RESISTANCE: Voting weight based on proven root.

        Returns (valid, weight_multiplier).
        """
        # Root type determines weight
        weights = {
            RootType.HUMAN: 1.0,      # Full weight
            RootType.AI: 0.5,         # Reduced (can be spawned)
            RootType.CAPITAL: 0.25,   # Can be purchased
            RootType.PROTOCOL: 0.1,   # System-generated
        }
        weight = weights.get(voter.root_type, 0.1)
        return True, weight


# =============================================================================
# ENCLAVE - The Full Protocol (renamed from Collective for kernel alignment)
# =============================================================================

@dataclass
class Enclave:
    """
    A HOLOS enclave implementing the full protocol.

    This is the fractal unit that scales from 10 people to global.

    Aligned with holos/kernel/enclave.py:
    - Enclave: Base group (<100 members)
    - Collective: Mid-scale (100-999 members)
    - Kingdom: Large-scale (1000+ members)

    Constitutional guarantees:
    1. Non-Blocking Exit - Members can always leave
    2. Proof of Solvency - No hidden insolvency
    3. Explicit Consent - No forced membership
    4. Sybil Resistance - Weighted voting
    5. Legible Interface - Standardized methods
    """
    enclave_id: str  # Renamed from collective_id

    # Parameters (governable)
    params: CollectiveParameters = field(default_factory=CollectiveParameters)

    # Members (commitment -> stake position)
    members: Dict[bytes, StakePosition] = field(default_factory=dict)
    member_count: int = 0

    # Financial infrastructure
    fee_schedule: ProgressiveFeeSchedule = field(default_factory=ProgressiveFeeSchedule)
    flow_router: FlowRouter = field(default_factory=FlowRouter)  # Renamed from ubi_pool

    # Backward compatibility alias
    @property
    def ubi_pool(self) -> FlowRouter:
        return self.flow_router

    # Liquidity pools (pair_id -> pool)
    liquidity_pools: Dict[str, LiquidityPool] = field(default_factory=dict)

    # Information sharing
    shared_info: Dict[str, EncryptedInfoPacket] = field(default_factory=dict)
    prediction_markets: Dict[str, PredictionMarket] = field(default_factory=dict)

    # Governance
    active_proposals: Dict[str, QuadraticVote] = field(default_factory=dict)

    # Merkle root of members (for ZK proofs)
    members_root: bytes = field(default_factory=lambda: b'\x00' * 32)

    # Parent/child enclaves (fractal structure)
    parent_enclave: Optional[str] = None  # Renamed from parent_collective
    child_enclaves: List[str] = field(default_factory=list)  # Renamed from child_collectives

    # Constitutional checker
    constitution: ConstitutionalChecker = field(default_factory=ConstitutionalChecker)

    # Backward compatibility aliases
    @property
    def collective_id(self) -> str:
        return self.enclave_id

    @property
    def parent_collective(self) -> Optional[str]:
        return self.parent_enclave

    @property
    def child_collectives(self) -> List[str]:
        return self.child_enclaves

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
        Join the enclave.

        Constitutional requirements (EXPLICIT_CONSENT):
        - Minimum stake (bilateral agreement on terms)
        - Stake is locked for vesting period

        Returns True if join successful.
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
        identity.memberships[self.enclave_id] = proof

        return True

    def leave(self, identity: SovereignIdentity) -> float:
        """
        Leave the enclave.

        Constitutional guarantee (NON_BLOCKING_EXIT):
        Exit can NEVER be blocked - this is the core right.

        Returns stake minus any early exit penalty.
        Penalty goes to flow-through UBI.
        """
        commitment = identity.public_commitment

        if commitment not in self.members:
            return 0.0

        # Constitutional check: exit always allowed
        allowed, _ = self.constitution.check_exit_allowed(commitment, self)
        assert allowed, "Constitutional violation: exit must always be allowed"

        position = self.members[commitment]
        current_time = time.time()

        penalty = position.early_exit_penalty(current_time, self.params.early_exit_penalty)
        refund = position.amount - penalty

        # Penalty flows through to UBI
        self.ubi_pool.deposit(penalty)
        self.total_value_locked -= position.amount

        del self.members[commitment]
        self.member_count -= 1
        self._update_merkle_root()

        # Revoke membership proof and record exit
        if self.enclave_id in identity.memberships:
            del identity.memberships[self.enclave_id]
        identity.record_exit()

        return refund

    # =========================================================================
    # FEES AND UBI (Flow-Through Pattern)
    # =========================================================================

    def collect_fees(self, member_wealth: Dict[bytes, float]) -> float:
        """
        Collect progressive fees from all members.

        Flow-through pattern: Fees are NOT accumulated in a treasury.
        They are held temporarily for the next distribute_ubi call.
        """
        total_fees = 0.0

        for commitment, wealth in member_wealth.items():
            if commitment not in self.members:
                continue

            fee, proof = self.fee_schedule.calculate_fee(wealth)

            # In production: verify proof before accepting fee
            if ZKProofSystem.verify(proof):
                total_fees += fee

        # Store temporarily for distribution (flow-through means no long-term storage)
        self._pending_fees = getattr(self, '_pending_fees', 0.0) + total_fees
        self.total_fees_collected += total_fees

        return total_fees

    def distribute_ubi(self) -> Dict[bytes, float]:
        """
        Distribute UBI to all members using flow-through pattern.

        KEY: Taxes collected flow IMMEDIATELY as UBI - no treasury accumulation.
        This eliminates the treasury as an attack target.

        Returns mapping of member -> distribution amount.
        """
        pending = getattr(self, '_pending_fees', 0.0)
        if pending <= 0 or not self.members:
            return {}

        # Update flow router's recipient root
        self.flow_router.update_recipients(self.members_root)

        # Route all pending fees immediately through to members
        distributions = self.flow_router.route_tax(pending, self.members)

        # Update tracking
        for amount in distributions.values():
            self.total_ubi_distributed += amount

        # Clear pending (flow-through complete)
        self._pending_fees = 0.0

        return distributions

    def collect_and_distribute(self, member_wealth: Dict[bytes, float]) -> Dict[bytes, float]:
        """
        Single-step fee collection and UBI distribution.

        This is the recommended flow-through pattern:
        Tax payment → Immediate UBI distribution (same event)

        Returns mapping of member -> net change (UBI received - fee paid).
        """
        # Calculate fees
        fees_by_member = {}
        for commitment, wealth in member_wealth.items():
            if commitment not in self.members:
                continue
            fee, _ = self.fee_schedule.calculate_fee(wealth)
            fees_by_member[commitment] = fee

        total_fees = sum(fees_by_member.values())
        self.total_fees_collected += total_fees

        # Immediately route as UBI (no storage!)
        self.flow_router.update_recipients(self.members_root)
        ubi_distributions = self.flow_router.route_tax(total_fees, self.members)

        # Track UBI
        for amount in ubi_distributions.values():
            self.total_ubi_distributed += amount

        # Return net change per member
        net_changes = {}
        for commitment in self.members:
            fee_paid = fees_by_member.get(commitment, 0.0)
            ubi_received = ubi_distributions.get(commitment, 0.0)
            net_changes[commitment] = ubi_received - fee_paid

        return net_changes

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

    @property
    def scale(self) -> EnclaveScale:
        """Get current scale taxonomy based on member count."""
        return EnclaveScale.from_member_count(self.member_count)

    def create_child_enclave(self, child_id: str) -> 'Enclave':
        """Create a child enclave (fractal scaling down)."""
        child = Enclave(
            enclave_id=child_id,
            params=CollectiveParameters(**vars(self.params)),  # Copy params
            parent_enclave=self.enclave_id,
        )
        self.child_enclaves.append(child_id)
        return child

    # Backward compatibility alias
    def create_child_collective(self, child_id: str) -> 'Enclave':
        """Deprecated: Use create_child_enclave instead."""
        return self.create_child_enclave(child_id)

    def join_parent(self, parent: 'Enclave') -> bool:
        """Join a parent enclave (fractal scaling up)."""
        # The enclave itself becomes a member of the parent
        # This allows nested enclaves
        self.parent_enclave = parent.enclave_id
        return True


# =============================================================================
# BACKWARD COMPATIBILITY - Collective alias for Enclave
# =============================================================================

# Collective is now an alias for Enclave (kernel naming convention)
Collective = Enclave


# =============================================================================
# PROTOCOL VALUE CALCULATION
# =============================================================================

def calculate_enclave_value(enclave: Enclave) -> Dict[str, float]:
    """
    Calculate the value proposition of joining an enclave.

    This determines whether rational actors will join.

    Factors considered:
    - Liquidity value (trading depth)
    - Information value (shared knowledge, prediction markets)
    - Network value (member count, network effects)

    Returns dict with value breakdown and should_join recommendation.
    """
    # Liquidity value
    total_liquidity = sum(
        pool.token_a_reserve + pool.token_b_reserve
        for pool in enclave.liquidity_pools.values()
    )
    liquidity_value = (total_liquidity / 10000) ** 0.5  # Sqrt for network effects

    # Information value
    info_count = len(enclave.shared_info)
    prediction_count = len(enclave.prediction_markets)
    info_value = (info_count + prediction_count) * 0.01

    # Network value (scale-aware)
    network_value = (enclave.member_count / 100) ** 0.8

    # Total value
    total_value = 0.4 * liquidity_value + 0.35 * info_value + 0.25 * network_value

    # Cost (fees + staking)
    avg_fee = enclave.params.base_fee_rate * 1.5  # Assume middle bracket
    stake_cost = enclave.params.min_stake * 0.05  # Opportunity cost
    total_cost = avg_fee + stake_cost / 100

    return {
        "liquidity_value": liquidity_value,
        "info_value": info_value,
        "network_value": network_value,
        "total_value": total_value,
        "total_cost": total_cost,
        "net_value": total_value - total_cost,
        "should_join": total_value > total_cost,
        "scale": enclave.scale.name,  # Scale taxonomy
    }


# Backward compatibility alias
def calculate_collective_value(collective: Enclave) -> Dict[str, float]:
    """Deprecated: Use calculate_enclave_value instead."""
    return calculate_enclave_value(collective)
