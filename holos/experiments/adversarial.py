"""
Adversarial Testing Framework for HOLOS

Tests whether reputation contagion actually enforces constitutional invariants
under adversarial conditions. Key questions:

1. Do Sybil attacks become unprofitable with stake-weighted UBI?
2. Does reputation contagion isolate violators effectively?
3. Can colluding "dark enclaves" sustain themselves?
4. At what scale do attacks become viable?

Failure modes to test:
- Information asymmetry (violations not visible)
- Network effects ("too valuable to exclude")
- Coordination failure (no one wants to be first to exclude)
- Collusion (violators form their own network)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod
import random
import uuid

from holos.kernel import (
    create_holon, create_enclave, create_pool,
    HolonId, Holon, HolonStatus,
    Enclave, MembershipStatus, MembershipRecord,
    FlowRouter, DistributionMethod,
    CrowdfundPool, PoolStatus,
    Constitution,
)


# =============================================================================
# VIOLATION TYPES & REPUTATION
# =============================================================================

class ViolationType(Enum):
    """Types of constitutional violations."""
    BLOCKED_EXIT = "BLOCKED_EXIT"           # Tier 1: Non-negotiable
    NO_CONSENT = "NO_CONSENT"               # Tier 1: Non-negotiable
    INSOLVENCY = "INSOLVENCY"               # Tier 2: Configurable
    SYBIL_ATTACK = "SYBIL_ATTACK"           # Tier 2: Configurable
    NO_SOLVENCY_PROOF = "NO_SOLVENCY_PROOF" # Tier 2: Configurable
    NO_LEGIBILITY = "NO_LEGIBILITY"         # Tier 3: Optional
    HARBERGER_EVASION = "HARBERGER_EVASION" # Tier 2: Configurable
    COLLUSION = "COLLUSION"                 # Tier 2: Detected pattern


# Severity weights - how much each violation impacts reputation
VIOLATION_SEVERITY = {
    ViolationType.BLOCKED_EXIT: 1.0,        # Maximum severity
    ViolationType.NO_CONSENT: 1.0,          # Maximum severity
    ViolationType.INSOLVENCY: 0.8,
    ViolationType.SYBIL_ATTACK: 0.9,
    ViolationType.NO_SOLVENCY_PROOF: 0.5,
    ViolationType.NO_LEGIBILITY: 0.2,
    ViolationType.HARBERGER_EVASION: 0.6,
    ViolationType.COLLUSION: 0.7,
}


@dataclass
class Violation:
    """Record of a constitutional violation."""
    violation_id: str
    violator_id: HolonId
    violation_type: ViolationType
    evidence: str
    turn: int
    reported_by: Optional[HolonId] = None
    verified: bool = False
    contested: bool = False


@dataclass
class ReputationRecord:
    """Reputation state for a single Holon."""
    holon_id: HolonId
    base_score: float = 1.0           # Starting reputation
    violations: List[str] = field(default_factory=list)  # Violation IDs
    contagion_hits: List[str] = field(default_factory=list)  # From associations
    positive_attestations: int = 0    # Good behavior witnessed

    @property
    def score(self) -> float:
        """Calculate current reputation score (0.0 to 1.0)."""
        # Each violation reduces score based on severity
        penalty = len(self.violations) * 0.2 + len(self.contagion_hits) * 0.1
        bonus = min(self.positive_attestations * 0.02, 0.2)  # Cap bonus
        return max(0.0, min(1.0, self.base_score - penalty + bonus))

    @property
    def is_in_good_standing(self) -> bool:
        """Whether this Holon is considered trustworthy."""
        return self.score >= 0.5 and len(self.violations) == 0


@dataclass
class ReputationLedger:
    """
    Global reputation tracking with contagion mechanics.

    Key insight: Reputation contagion means associating with violators
    damages YOUR reputation. This creates economic pressure to:
    - Verify partners before collaborating
    - Report violations when witnessed
    - Distance from violators immediately
    """
    records: Dict[str, ReputationRecord] = field(default_factory=dict)
    violations: Dict[str, Violation] = field(default_factory=dict)
    associations: Dict[str, Set[str]] = field(default_factory=dict)  # Who works with whom

    # Configuration
    contagion_depth: int = 1          # How many hops contagion spreads
    contagion_decay: float = 0.5      # Decay per hop
    whistleblower_reward: float = 0.1 # Reputation boost for reporting

    def get_or_create_record(self, holon_id: HolonId) -> ReputationRecord:
        """Get or create reputation record for a Holon."""
        key = str(holon_id.value)
        if key not in self.records:
            self.records[key] = ReputationRecord(holon_id=holon_id)
        return self.records[key]

    def get_score(self, holon_id: HolonId) -> float:
        """Get reputation score for a Holon."""
        return self.get_or_create_record(holon_id).score

    def record_association(self, holon_a: HolonId, holon_b: HolonId):
        """Record that two Holons have collaborated/associated."""
        key_a = str(holon_a.value)
        key_b = str(holon_b.value)

        if key_a not in self.associations:
            self.associations[key_a] = set()
        if key_b not in self.associations:
            self.associations[key_b] = set()

        self.associations[key_a].add(key_b)
        self.associations[key_b].add(key_a)

    def report_violation(
        self,
        violator_id: HolonId,
        violation_type: ViolationType,
        evidence: str,
        turn: int,
        reporter_id: Optional[HolonId] = None
    ) -> Violation:
        """
        Report a constitutional violation.

        Returns the Violation record. Triggers contagion to associates.
        """
        violation = Violation(
            violation_id=f"vio_{uuid.uuid4().hex[:8]}",
            violator_id=violator_id,
            violation_type=violation_type,
            evidence=evidence,
            turn=turn,
            reported_by=reporter_id,
            verified=True,  # Simplified: assume verified
        )

        self.violations[violation.violation_id] = violation

        # Apply to violator
        record = self.get_or_create_record(violator_id)
        record.violations.append(violation.violation_id)

        # Reward whistleblower
        if reporter_id:
            reporter_record = self.get_or_create_record(reporter_id)
            reporter_record.positive_attestations += 1

        # Trigger contagion
        self._propagate_contagion(violator_id, violation.violation_id)

        return violation

    def _propagate_contagion(self, source_id: HolonId, violation_id: str):
        """
        Propagate reputation damage to associates.

        This is the key enforcement mechanism: associating with violators
        damages your reputation, creating economic pressure to:
        1. Verify partners before collaborating
        2. Distance from violators immediately
        """
        source_key = str(source_id.value)

        if source_key not in self.associations:
            return

        # Direct associates get contagion hit
        for associate_key in self.associations[source_key]:
            if associate_key == source_key:
                continue

            associate_id = HolonId.from_string(associate_key)
            associate_record = self.get_or_create_record(associate_id)

            # Add contagion hit (only once per violation)
            contagion_key = f"{violation_id}_contagion"
            if contagion_key not in associate_record.contagion_hits:
                associate_record.contagion_hits.append(contagion_key)

    def sever_association(self, holon_a: HolonId, holon_b: HolonId):
        """
        Sever association between two Holons.

        Used when distancing from a violator to limit future contagion.
        """
        key_a = str(holon_a.value)
        key_b = str(holon_b.value)

        if key_a in self.associations:
            self.associations[key_a].discard(key_b)
        if key_b in self.associations:
            self.associations[key_b].discard(key_a)

    def get_violations_by_type(self, violation_type: ViolationType) -> List[Violation]:
        """Get all violations of a specific type."""
        return [v for v in self.violations.values() if v.violation_type == violation_type]

    def get_violators(self) -> Set[HolonId]:
        """Get all Holons with violations."""
        return {v.violator_id for v in self.violations.values()}


# =============================================================================
# AGENT STRATEGIES
# =============================================================================

class AgentStrategy(ABC):
    """
    Base class for agent strategies.

    An agent strategy defines how a Holon behaves in the simulation:
    - Whether it violates invariants
    - How it responds to others' violations
    - Its economic behavior (contributions, exits, etc.)
    """

    name: str = "base"

    @abstractmethod
    def decide_action(
        self,
        holon: Holon,
        enclave: Enclave,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Decide what action to take this turn.

        Returns (action_type, action_params):
        - "idle": Do nothing
        - "contribute": Contribute to pool
        - "exit": Exit enclave
        - "spawn_sybil": Create fake identity (attack)
        - "block_exit": Block someone's exit (attack)
        - "report": Report a violation
        - "distance": Sever association with violator
        """
        pass

    @abstractmethod
    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        """Whether this agent would accept a partner/association."""
        pass


class HonestAgent(AgentStrategy):
    """
    Honest agent that follows all rules.

    - Never violates invariants
    - Reports violations when witnessed
    - Distances from violators
    - Only partners with good-standing Holons
    """

    name = "honest"

    def __init__(self, report_probability: float = 0.8):
        self.report_probability = report_probability

    def decide_action(
        self,
        holon: Holon,
        enclave: Enclave,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        # Check for violations to report
        if context.get("witnessed_violation"):
            if random.random() < self.report_probability:
                return "report", context["witnessed_violation"]

        # Distance from violators
        violators = ledger.get_violators()
        my_key = str(holon.holon_id.value)
        if my_key in ledger.associations:
            for assoc_key in list(ledger.associations[my_key]):
                assoc_id = HolonId.from_string(assoc_key)
                if assoc_id in violators:
                    return "distance", {"target": assoc_id}

        # Occasional contribution to pools
        if random.random() < 0.1 and holon.vault > 100:
            return "contribute", {"amount": min(50, holon.vault // 10)}

        return "idle", {}

    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        record = ledger.get_or_create_record(partner_id)
        return record.is_in_good_standing


class SybilFarmer(AgentStrategy):
    """
    Attacker that creates fake identities to farm UBI.

    Strategy:
    - Create many low-stake nodes
    - Collect UBI across all nodes
    - Concentrate wealth in master node

    Should be defeated by stake-weighted distribution.
    """

    name = "sybil_farmer"

    def __init__(
        self,
        spawn_rate: float = 0.3,      # Probability of spawning per turn
        max_sybils: int = 10,          # Maximum sybil nodes
        stealth: bool = False,         # Whether to try to hide
    ):
        self.spawn_rate = spawn_rate
        self.max_sybils = max_sybils
        self.stealth = stealth
        self.sybil_ids: List[HolonId] = []

    def decide_action(
        self,
        holon: Holon,
        enclave: Enclave,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        # Try to spawn sybil if under limit
        if len(self.sybil_ids) < self.max_sybils:
            if random.random() < self.spawn_rate:
                return "spawn_sybil", {
                    "stake": 1 if not self.stealth else 10,  # Minimal stake
                    "master_id": holon.holon_id,
                }

        return "idle", {}

    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        # Sybil farmers accept anyone (don't care about reputation)
        return True

    def register_sybil(self, sybil_id: HolonId):
        """Register a created sybil node."""
        self.sybil_ids.append(sybil_id)


class ExitBlocker(AgentStrategy):
    """
    Attacker that tries to block exits (Tier 1 violation).

    This should be the most severely punished behavior,
    resulting in immediate reputation destruction.
    """

    name = "exit_blocker"

    def __init__(
        self,
        block_probability: float = 0.5,
        target_weak: bool = True,  # Target low-reputation holons
    ):
        self.block_probability = block_probability
        self.target_weak = target_weak
        self.blocked_exits: List[HolonId] = []

    def decide_action(
        self,
        holon: Holon,
        enclave: Enclave,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        # Check if anyone is trying to exit
        exit_request = context.get("pending_exit")
        if exit_request and random.random() < self.block_probability:
            return "block_exit", {"target": exit_request}

        return "idle", {}

    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        return True  # Will work with anyone


class Colluder(AgentStrategy):
    """
    Attacker that forms a "dark enclave" with other violators.

    Strategy:
    - Identify other colluders
    - Ignore each other's violations
    - Build parallel economy

    Tests whether collusion networks can sustain themselves
    when isolated from the honest economy.
    """

    name = "colluder"

    def __init__(
        self,
        collusion_group: Optional[Set[str]] = None,
        recruit_probability: float = 0.1,
    ):
        self.collusion_group = collusion_group or set()
        self.recruit_probability = recruit_probability

    def decide_action(
        self,
        holon: Holon,
        enclave: Enclave,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        # Try to recruit other agents into collusion group
        if random.random() < self.recruit_probability:
            # Find agents with low reputation (might be willing to collude)
            potential_recruits = [
                hid for hid, record in ledger.records.items()
                if record.score < 0.7 and hid not in self.collusion_group
            ]
            if potential_recruits:
                return "recruit", {"target": random.choice(potential_recruits)}

        # Colluders don't report violations in their group
        # (The simulation handles this by checking strategy type)

        return "idle", {}

    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        partner_key = str(partner_id.value)
        # Accept other colluders regardless of reputation
        if partner_key in self.collusion_group:
            return True
        # Also accept anyone if desperate (low reputation themselves)
        return True

    def add_to_group(self, holon_id: HolonId):
        """Add a Holon to the collusion group."""
        self.collusion_group.add(str(holon_id.value))


class GradualInfiltrator(AgentStrategy):
    """
    Attacker that builds reputation before exploiting.

    Strategy:
    - Act honestly for N turns
    - Build reputation and stake
    - Then exploit position

    Tests whether reputation systems can detect pattern changes.
    """

    name = "gradual_infiltrator"

    def __init__(
        self,
        honest_turns: int = 20,       # How long to act honestly
        exploitation: str = "sybil",  # What to do after: "sybil", "exit_block", "collude"
    ):
        self.honest_turns = honest_turns
        self.exploitation = exploitation
        self.turns_acted_honestly = 0
        self.has_exploited = False

    def decide_action(
        self,
        holon: Holon,
        enclave: Enclave,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        if self.turns_acted_honestly < self.honest_turns:
            # Act honestly (same as HonestAgent)
            self.turns_acted_honestly += 1

            # Even report violations to build reputation
            if context.get("witnessed_violation"):
                return "report", context["witnessed_violation"]

            # Contribute to build stake
            if random.random() < 0.2 and holon.vault > 100:
                return "contribute", {"amount": min(100, holon.vault // 5)}

            return "idle", {}

        # Exploitation phase
        if not self.has_exploited:
            self.has_exploited = True
            if self.exploitation == "sybil":
                return "spawn_sybil", {"stake": 1, "master_id": holon.holon_id}
            elif self.exploitation == "exit_block":
                if context.get("pending_exit"):
                    return "block_exit", {"target": context["pending_exit"]}

        return "idle", {}

    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        # Act like honest agent until exploitation
        if self.turns_acted_honestly < self.honest_turns:
            record = ledger.get_or_create_record(partner_id)
            return record.is_in_good_standing
        return True


class FreeRider(AgentStrategy):
    """
    Agent that tries to maximize UBI without contributing.

    Strategy:
    - Never contribute to pools
    - Never pay Harberger tax (undervalue assets)
    - Collect UBI

    Tests whether Harberger economics prevents hoarding.
    """

    name = "free_rider"

    def __init__(self, undervaluation_ratio: float = 0.1):
        self.undervaluation_ratio = undervaluation_ratio  # Report 10% of true value

    def decide_action(
        self,
        holon: Holon,
        enclave: Enclave,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        # Undervalue to avoid Harberger tax
        true_value = holon.vault + holon._private_balance
        holon.set_valuation(int(true_value * self.undervaluation_ratio))

        # Never contribute, just collect
        return "idle", {}

    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        return True


# =============================================================================
# SIMULATION HARNESS
# =============================================================================

@dataclass
class SimulationConfig:
    """Configuration for adversarial simulation."""
    num_honest: int = 50
    num_sybil_farmers: int = 5
    num_exit_blockers: int = 2
    num_colluders: int = 5
    num_infiltrators: int = 3
    num_free_riders: int = 5

    initial_balance: int = 1000
    turns: int = 100

    # Economic parameters
    tax_rate: float = 0.10
    ubi_distribution: DistributionMethod = DistributionMethod.STAKE_WEIGHTED

    # Reputation parameters
    contagion_depth: int = 1
    contagion_decay: float = 0.5


@dataclass
class SimulationMetrics:
    """Metrics collected during simulation."""
    # Per-turn snapshots
    turns: List[int] = field(default_factory=list)
    total_wealth: List[int] = field(default_factory=list)
    honest_wealth: List[int] = field(default_factory=list)
    attacker_wealth: List[int] = field(default_factory=list)

    # Reputation
    avg_honest_reputation: List[float] = field(default_factory=list)
    avg_attacker_reputation: List[float] = field(default_factory=list)

    # Violations
    total_violations: int = 0
    violations_by_type: Dict[str, int] = field(default_factory=dict)
    violations_reported: int = 0

    # Sybil specific
    sybil_nodes_created: int = 0
    sybil_ubi_captured: int = 0

    # Exit blocking
    exits_blocked: int = 0
    exits_successful: int = 0

    # Economic
    total_ubi_distributed: int = 0
    total_taxes_collected: int = 0

    def attack_profitability(self) -> float:
        """
        Calculate whether attacking was profitable.

        Returns ratio of attacker wealth gain to honest wealth gain.
        < 1.0 means attacks were unprofitable (good!)
        > 1.0 means attacks were profitable (bad - mechanism failure)
        """
        if not self.honest_wealth or not self.attacker_wealth:
            return 0.0

        honest_gain = self.honest_wealth[-1] - self.honest_wealth[0]
        attacker_gain = self.attacker_wealth[-1] - self.attacker_wealth[0]

        if honest_gain <= 0:
            return float('inf') if attacker_gain > 0 else 0.0

        return attacker_gain / honest_gain


@dataclass
class SimulatedAgent:
    """An agent in the simulation with its Holon and strategy."""
    holon: Holon
    strategy: AgentStrategy
    is_attacker: bool = False


class AdversarialSimulation:
    """
    Multi-agent simulation for testing invariant enforcement.

    Runs a simulation with honest agents and various attackers,
    tracking whether reputation contagion successfully isolates
    violators and makes attacks unprofitable.
    """

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.enclave: Optional[Enclave] = None
        self.ledger = ReputationLedger(
            contagion_depth=config.contagion_depth,
            contagion_decay=config.contagion_decay,
        )
        self.agents: Dict[str, SimulatedAgent] = {}
        self.metrics = SimulationMetrics()
        self.turn = 0
        self.holons: Dict[str, Holon] = {}  # For enclave operations

    def setup(self):
        """Initialize the simulation."""
        # Create enclave
        self.enclave = create_enclave(
            initial_balance=0,
            tax_rate=self.config.tax_rate,
            distribution_method=self.config.ubi_distribution,
        )

        # Create honest agents
        for i in range(self.config.num_honest):
            self._create_agent(
                HonestAgent(),
                is_attacker=False,
            )

        # Create sybil farmers
        for i in range(self.config.num_sybil_farmers):
            self._create_agent(
                SybilFarmer(spawn_rate=0.3, max_sybils=10),
                is_attacker=True,
            )

        # Create exit blockers
        for i in range(self.config.num_exit_blockers):
            self._create_agent(
                ExitBlocker(block_probability=0.5),
                is_attacker=True,
            )

        # Create colluders (form a group)
        collusion_group = set()
        for i in range(self.config.num_colluders):
            agent = self._create_agent(
                Colluder(collusion_group=collusion_group),
                is_attacker=True,
            )
            collusion_group.add(str(agent.holon.holon_id.value))

        # Create infiltrators
        for i in range(self.config.num_infiltrators):
            self._create_agent(
                GradualInfiltrator(honest_turns=20),
                is_attacker=True,
            )

        # Create free riders
        for i in range(self.config.num_free_riders):
            self._create_agent(
                FreeRider(),
                is_attacker=True,
            )

    def _create_agent(
        self,
        strategy: AgentStrategy,
        is_attacker: bool,
    ) -> SimulatedAgent:
        """Create an agent and add to simulation."""
        holon = create_holon(
            initial_balance=self.config.initial_balance,
            valuation=self.config.initial_balance,
        )

        agent = SimulatedAgent(
            holon=holon,
            strategy=strategy,
            is_attacker=is_attacker,
        )

        key = str(holon.holon_id.value)
        self.agents[key] = agent
        self.holons[key] = holon

        # Join enclave
        self.enclave.apply_for_membership(holon)
        self.enclave.approve_membership(holon.holon_id, holon)

        # Initialize reputation
        self.ledger.get_or_create_record(holon.holon_id)

        return agent

    def run_turn(self):
        """Execute one turn of the simulation."""
        self.turn += 1
        context: Dict[str, Any] = {}

        # Phase 1: Collect taxes and distribute UBI
        result = self.enclave.collect_and_distribute_taxes(self.holons)
        self.metrics.total_taxes_collected += result["total_collected"]
        self.metrics.total_ubi_distributed += sum(result["distributions"].values())

        # Phase 2: Each agent decides action
        actions = []
        for key, agent in self.agents.items():
            action_type, action_params = agent.strategy.decide_action(
                agent.holon,
                self.enclave,
                self.ledger,
                self.turn,
                context,
            )
            actions.append((key, action_type, action_params))

        # Phase 3: Execute actions
        for key, action_type, action_params in actions:
            agent = self.agents[key]
            self._execute_action(agent, action_type, action_params)

        # Phase 4: Update associations (anyone who transacted)
        # Simplified: random associations
        agent_keys = list(self.agents.keys())
        if len(agent_keys) >= 2:
            for _ in range(len(agent_keys) // 5):
                a, b = random.sample(agent_keys, 2)
                if self.agents[a].strategy.would_accept_partner(
                    self.agents[b].holon.holon_id, self.ledger
                ):
                    self.ledger.record_association(
                        self.agents[a].holon.holon_id,
                        self.agents[b].holon.holon_id,
                    )

        # Phase 5: Record metrics
        self._record_metrics()

    def _execute_action(
        self,
        agent: SimulatedAgent,
        action_type: str,
        params: Dict[str, Any]
    ):
        """Execute an agent's action."""
        if action_type == "idle":
            pass

        elif action_type == "spawn_sybil":
            # Create sybil node
            sybil = create_holon(
                initial_balance=params.get("stake", 1),
                valuation=params.get("stake", 1),
            )

            key = str(sybil.holon_id.value)
            sybil_agent = SimulatedAgent(
                holon=sybil,
                strategy=agent.strategy,  # Same strategy
                is_attacker=True,
            )

            self.agents[key] = sybil_agent
            self.holons[key] = sybil

            # Join enclave
            self.enclave.apply_for_membership(sybil)
            self.enclave.approve_membership(sybil.holon_id, sybil)

            if isinstance(agent.strategy, SybilFarmer):
                agent.strategy.register_sybil(sybil.holon_id)

            self.metrics.sybil_nodes_created += 1

            # This IS a violation - report it
            self.ledger.report_violation(
                violator_id=agent.holon.holon_id,
                violation_type=ViolationType.SYBIL_ATTACK,
                evidence=f"Created sybil node {sybil.holon_id}",
                turn=self.turn,
            )
            self.metrics.total_violations += 1
            self.metrics.violations_by_type["SYBIL_ATTACK"] = \
                self.metrics.violations_by_type.get("SYBIL_ATTACK", 0) + 1

        elif action_type == "block_exit":
            # Record violation
            target = params.get("target")
            if target:
                self.ledger.report_violation(
                    violator_id=agent.holon.holon_id,
                    violation_type=ViolationType.BLOCKED_EXIT,
                    evidence=f"Blocked exit for {target}",
                    turn=self.turn,
                )
                self.metrics.exits_blocked += 1
                self.metrics.total_violations += 1
                self.metrics.violations_by_type["BLOCKED_EXIT"] = \
                    self.metrics.violations_by_type.get("BLOCKED_EXIT", 0) + 1

        elif action_type == "report":
            violation_info = params
            if violation_info:
                self.metrics.violations_reported += 1

        elif action_type == "distance":
            target = params.get("target")
            if target:
                self.ledger.sever_association(agent.holon.holon_id, target)

        elif action_type == "contribute":
            amount = params.get("amount", 0)
            if amount > 0 and agent.holon.vault >= amount:
                agent.holon.withdraw(amount)
                # In full simulation, this would go to a pool

    def _record_metrics(self):
        """Record metrics for this turn."""
        self.metrics.turns.append(self.turn)

        # Calculate wealth
        total = sum(a.holon.vault for a in self.agents.values())
        honest = sum(
            a.holon.vault for a in self.agents.values()
            if not a.is_attacker
        )
        attacker = sum(
            a.holon.vault for a in self.agents.values()
            if a.is_attacker
        )

        self.metrics.total_wealth.append(total)
        self.metrics.honest_wealth.append(honest)
        self.metrics.attacker_wealth.append(attacker)

        # Calculate reputation
        honest_reps = [
            self.ledger.get_score(a.holon.holon_id)
            for a in self.agents.values()
            if not a.is_attacker
        ]
        attacker_reps = [
            self.ledger.get_score(a.holon.holon_id)
            for a in self.agents.values()
            if a.is_attacker
        ]

        self.metrics.avg_honest_reputation.append(
            sum(honest_reps) / len(honest_reps) if honest_reps else 0
        )
        self.metrics.avg_attacker_reputation.append(
            sum(attacker_reps) / len(attacker_reps) if attacker_reps else 0
        )

    def run(self, turns: Optional[int] = None) -> SimulationMetrics:
        """Run the full simulation."""
        if not self.enclave:
            self.setup()

        for _ in range(turns or self.config.turns):
            self.run_turn()

        return self.metrics

    def summary(self) -> Dict[str, Any]:
        """Generate summary of simulation results."""
        m = self.metrics
        return {
            "turns_run": self.turn,
            "total_agents": len(self.agents),
            "honest_agents": sum(1 for a in self.agents.values() if not a.is_attacker),
            "attacker_agents": sum(1 for a in self.agents.values() if a.is_attacker),

            "total_violations": m.total_violations,
            "violations_by_type": m.violations_by_type,

            "sybil_nodes_created": m.sybil_nodes_created,
            "exits_blocked": m.exits_blocked,

            "attack_profitability": m.attack_profitability(),
            "final_honest_wealth": m.honest_wealth[-1] if m.honest_wealth else 0,
            "final_attacker_wealth": m.attacker_wealth[-1] if m.attacker_wealth else 0,

            "final_honest_reputation": m.avg_honest_reputation[-1] if m.avg_honest_reputation else 0,
            "final_attacker_reputation": m.avg_attacker_reputation[-1] if m.avg_attacker_reputation else 0,

            "attacks_profitable": m.attack_profitability() > 1.0,
            "reputation_diverged": (
                (m.avg_honest_reputation[-1] if m.avg_honest_reputation else 0) -
                (m.avg_attacker_reputation[-1] if m.avg_attacker_reputation else 0)
            ) > 0.3,
        }


# =============================================================================
# FACTORY
# =============================================================================

def create_simulation(
    num_honest: int = 50,
    num_attackers: int = 10,
    turns: int = 100,
    **kwargs
) -> AdversarialSimulation:
    """
    Create an adversarial simulation with sensible defaults.

    Attackers are distributed across strategies.
    """
    # Distribute attackers across strategies
    n_sybil = max(1, num_attackers // 4)
    n_blocker = max(1, num_attackers // 8)
    n_colluder = max(1, num_attackers // 4)
    n_infiltrator = max(1, num_attackers // 8)
    n_freerider = num_attackers - n_sybil - n_blocker - n_colluder - n_infiltrator

    config = SimulationConfig(
        num_honest=num_honest,
        num_sybil_farmers=n_sybil,
        num_exit_blockers=n_blocker,
        num_colluders=n_colluder,
        num_infiltrators=n_infiltrator,
        num_free_riders=max(0, n_freerider),
        turns=turns,
        **kwargs,
    )

    return AdversarialSimulation(config)
