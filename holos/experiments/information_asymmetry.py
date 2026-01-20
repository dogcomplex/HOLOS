"""
Information Asymmetry Testing for HOLOS

Tests how information advantages affect wealth inequality and market dominance,
and what mechanisms can erode those advantages.

Key insight: Harberger taxes solve ASSET hoarding but not KNOWLEDGE hoarding.
An agent who knows others' private state has massive trading advantage.

Test scenarios:
1. Legacy advantage - Start with historical data on all agents
2. Ongoing surveillance - Can see inside others' ZK bubbles
3. Fidelity variation - How accurate is the leaked information?
4. Coverage variation - What % of population can they surveil?

Questions to answer:
- How does info advantage translate to wealth inequality?
- What's the market dominance curve?
- What erodes the advantage (ZK, noise, churn)?
- How difficult is erosion?
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Tuple, Callable
from enum import Enum
from abc import ABC, abstractmethod
import random
import math
import uuid

from holos.kernel import (
    create_holon, create_enclave,
    HolonId, Holon,
    Enclave, MembershipStatus,
    FlowRouter, DistributionMethod,
)

from .adversarial import (
    AgentStrategy, ReputationLedger, ViolationType,
    SimulationMetrics,
)


# =============================================================================
# INFORMATION TYPES
# =============================================================================

class InformationType(Enum):
    """Types of private information that can be leaked/surveilled."""
    PRIVATE_BALANCE = "PRIVATE_BALANCE"       # True wealth (hidden in ZK)
    STRATEGY = "STRATEGY"                      # Trading/bidding strategy
    VALUATION = "VALUATION"                    # True asset valuation (vs Harberger declared)
    PENDING_DEALS = "PENDING_DEALS"            # Upcoming transactions
    EXIT_INTENT = "EXIT_INTENT"                # Planning to exit
    REPUTATION_PRIVATE = "REPUTATION_PRIVATE"  # Private reputation data
    COST_STRUCTURE = "COST_STRUCTURE"          # Production costs


@dataclass
class InformationPacket:
    """A piece of information about a target Holon."""
    target_id: HolonId
    info_type: InformationType
    true_value: Any
    observed_value: Any      # May differ based on fidelity
    fidelity: float          # 0.0 = pure noise, 1.0 = perfect
    timestamp: int           # When observed
    stale_after: int = 10    # Turns until info becomes stale

    def is_stale(self, current_turn: int) -> bool:
        return current_turn - self.timestamp > self.stale_after

    def accuracy(self) -> float:
        """How close observed is to true (for numeric values)."""
        if isinstance(self.true_value, (int, float)):
            if self.true_value == 0:
                return 1.0 if self.observed_value == 0 else 0.0
            return 1.0 - abs(self.true_value - self.observed_value) / abs(self.true_value)
        return 1.0 if self.true_value == self.observed_value else 0.0


# =============================================================================
# SURVEILLANCE CAPABILITIES
# =============================================================================

@dataclass
class SurveillanceCapability:
    """
    Defines an agent's ability to surveil others.

    Models different information advantage scenarios:
    - Legacy: High coverage, decaying fidelity (old data)
    - Active surveillance: Lower coverage, high fidelity
    - Insider: Specific targets, perfect fidelity
    """
    # What can this agent see?
    visible_info_types: Set[InformationType] = field(default_factory=lambda: {
        InformationType.PRIVATE_BALANCE,
        InformationType.VALUATION,
    })

    # Coverage: what fraction of population can be surveilled?
    coverage: float = 0.1  # 10% by default

    # Fidelity: how accurate is the information?
    base_fidelity: float = 0.8  # 80% accurate

    # Fidelity decay: how fast does old info become unreliable?
    fidelity_decay: float = 0.1  # 10% per turn

    # Specific targets (if set, only these can be surveilled)
    specific_targets: Optional[Set[str]] = None

    # Cost per surveillance action
    cost_per_peek: int = 10

    def can_surveil(self, target_id: HolonId, all_targets: List[HolonId]) -> bool:
        """Check if this target can be surveilled."""
        target_key = str(target_id.value)

        if self.specific_targets is not None:
            return target_key in self.specific_targets

        # Random coverage model
        # Use deterministic hash so same target always accessible
        hash_val = hash(target_key) % 1000
        return hash_val < (self.coverage * 1000)

    def get_fidelity(self, turns_since_observation: int) -> float:
        """Get fidelity accounting for decay."""
        decay = self.fidelity_decay * turns_since_observation
        return max(0.1, self.base_fidelity - decay)


@dataclass
class LegacyAdvantage(SurveillanceCapability):
    """
    Models a historical information advantage.

    Agent starts with data on everyone, but it's aging.
    Represents: incumbents, data brokers, former insiders.
    """
    coverage: float = 0.9        # Knows almost everyone
    base_fidelity: float = 0.7   # But data is somewhat old
    fidelity_decay: float = 0.15 # Decays faster (no refresh)

    # Historical data age at start
    initial_data_age: int = 20   # Turns old


@dataclass
class ActiveSurveillance(SurveillanceCapability):
    """
    Models ongoing active surveillance capability.

    Lower coverage but high fidelity - actively spying.
    Represents: sophisticated attackers, compromised systems.
    """
    coverage: float = 0.3        # Can only track 30%
    base_fidelity: float = 0.95  # But very accurate
    fidelity_decay: float = 0.05 # Stays fresh longer


@dataclass
class InsiderKnowledge(SurveillanceCapability):
    """
    Models insider access to specific targets.

    Perfect info on few targets.
    Represents: moles, compromised keys, social engineering.
    """
    coverage: float = 0.0        # Uses specific_targets instead
    base_fidelity: float = 1.0   # Perfect information
    fidelity_decay: float = 0.02 # Almost no decay


# =============================================================================
# MARKET MECHANICS
# =============================================================================

@dataclass
class Asset:
    """A tradeable asset in the market."""
    asset_id: str
    owner_id: HolonId
    true_value: int           # Actual value
    declared_value: int       # Harberger declared value
    category: str = "generic"


@dataclass
class TradeOffer:
    """An offer to buy an asset."""
    offer_id: str
    bidder_id: HolonId
    asset_id: str
    bid_amount: int
    turn: int


@dataclass
class Market:
    """
    Simple market where information advantage can be exploited.

    Key dynamics:
    - Harberger: Must sell at declared price
    - Information advantage: Know true values, can cherry-pick undervalued
    - Trading surplus: Difference between true value and price paid
    """
    assets: Dict[str, Asset] = field(default_factory=dict)
    trades: List[Dict[str, Any]] = field(default_factory=list)
    total_surplus_by_agent: Dict[str, int] = field(default_factory=dict)

    def create_asset(self, owner: Holon, true_value: int, declared_value: int) -> Asset:
        """Create a new asset owned by a Holon."""
        asset = Asset(
            asset_id=f"asset_{uuid.uuid4().hex[:8]}",
            owner_id=owner.holon_id,
            true_value=true_value,
            declared_value=declared_value,
        )
        self.assets[asset.asset_id] = asset
        return asset

    def harberger_buy(
        self,
        buyer_id: HolonId,
        asset_id: str,
        buyer_knows_true_value: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute Harberger forced sale.

        Buyer pays declared_value (not true_value).
        If buyer knows true_value > declared_value, they profit.
        """
        if asset_id not in self.assets:
            return None

        asset = self.assets[asset_id]
        price = asset.declared_value
        surplus = asset.true_value - price  # Buyer's information rent

        # Record trade
        trade = {
            "asset_id": asset_id,
            "seller_id": asset.owner_id,
            "buyer_id": buyer_id,
            "price": price,
            "true_value": asset.true_value,
            "surplus": surplus,
            "informed_trade": buyer_knows_true_value,
        }
        self.trades.append(trade)

        # Track surplus
        buyer_key = str(buyer_id.value)
        self.total_surplus_by_agent[buyer_key] = \
            self.total_surplus_by_agent.get(buyer_key, 0) + surplus

        # Transfer ownership
        asset.owner_id = buyer_id

        return trade

    def get_undervalued_assets(
        self,
        info_packets: List[InformationPacket],
        min_surplus_ratio: float = 0.2,
    ) -> List[Tuple[str, int]]:
        """
        Find assets where true_value > declared_value.

        Uses information packets to identify opportunities.
        Returns list of (asset_id, expected_surplus).
        """
        opportunities = []

        for asset_id, asset in self.assets.items():
            # Check if we have info on this asset's true value
            for packet in info_packets:
                if (packet.target_id == asset.owner_id and
                    packet.info_type == InformationType.VALUATION):
                    # Use observed value (may be imperfect)
                    estimated_true = packet.observed_value
                    if estimated_true > asset.declared_value * (1 + min_surplus_ratio):
                        surplus = estimated_true - asset.declared_value
                        opportunities.append((asset_id, surplus))

        return sorted(opportunities, key=lambda x: -x[1])  # Best opportunities first


# =============================================================================
# INFORMED TRADER AGENT
# =============================================================================

class InformedTrader(AgentStrategy):
    """
    Agent that exploits information advantage in markets.

    Strategy:
    1. Use surveillance to identify undervalued assets
    2. Execute Harberger forced purchases
    3. Accumulate trading surplus
    """

    name = "informed_trader"

    def __init__(
        self,
        surveillance: SurveillanceCapability,
        aggression: float = 0.5,  # How aggressively to trade
    ):
        self.surveillance = surveillance
        self.aggression = aggression
        self.info_cache: Dict[str, InformationPacket] = {}
        self.total_surplus: int = 0
        self.trades_made: int = 0

    def surveil(
        self,
        targets: List[Holon],
        turn: int,
    ) -> List[InformationPacket]:
        """
        Gather information on targets within surveillance capability.
        """
        packets = []

        for target in targets:
            if not self.surveillance.can_surveil(target.holon_id, [t.holon_id for t in targets]):
                continue

            for info_type in self.surveillance.visible_info_types:
                # Get true value
                if info_type == InformationType.PRIVATE_BALANCE:
                    true_value = target._private_balance
                elif info_type == InformationType.VALUATION:
                    true_value = target.vault + target._private_balance  # True worth
                elif info_type == InformationType.STRATEGY:
                    true_value = target._private_strategy
                else:
                    continue

                # Apply fidelity (add noise)
                fidelity = self.surveillance.get_fidelity(0)
                if isinstance(true_value, (int, float)):
                    noise = random.gauss(0, (1 - fidelity) * abs(true_value) * 0.5)
                    observed_value = true_value + noise
                else:
                    observed_value = true_value if random.random() < fidelity else "unknown"

                packet = InformationPacket(
                    target_id=target.holon_id,
                    info_type=info_type,
                    true_value=true_value,
                    observed_value=observed_value,
                    fidelity=fidelity,
                    timestamp=turn,
                )
                packets.append(packet)

                # Cache it
                cache_key = f"{target.holon_id.value}_{info_type.value}"
                self.info_cache[cache_key] = packet

        return packets

    def decide_action(
        self,
        holon: Holon,
        enclave: Enclave,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        # Surveil if market context available
        if "all_holons" in context:
            self.surveil(context["all_holons"], turn)

        # Look for trading opportunities
        if "market" in context and random.random() < self.aggression:
            market: Market = context["market"]
            packets = list(self.info_cache.values())
            opportunities = market.get_undervalued_assets(packets)

            if opportunities:
                best_asset, expected_surplus = opportunities[0]
                return "harberger_buy", {
                    "asset_id": best_asset,
                    "expected_surplus": expected_surplus,
                }

        return "idle", {}

    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        return True


class BlindTrader(AgentStrategy):
    """
    Agent without information advantage - trades randomly.

    Control group for comparison with InformedTrader.
    """

    name = "blind_trader"

    def __init__(self, trade_probability: float = 0.1):
        self.trade_probability = trade_probability
        self.total_surplus: int = 0
        self.trades_made: int = 0

    def decide_action(
        self,
        holon: Holon,
        enclave: Enclave,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        # Random trading
        if "market" in context and random.random() < self.trade_probability:
            market: Market = context["market"]
            if market.assets:
                random_asset = random.choice(list(market.assets.keys()))
                return "harberger_buy", {"asset_id": random_asset}

        return "idle", {}

    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        return True


# =============================================================================
# INEQUALITY METRICS
# =============================================================================

def gini_coefficient(values: List[float]) -> float:
    """
    Calculate Gini coefficient (0 = perfect equality, 1 = perfect inequality).
    """
    if not values or len(values) < 2:
        return 0.0

    sorted_values = sorted(values)
    n = len(sorted_values)
    total = sum(sorted_values)

    if total == 0:
        return 0.0

    cumulative = 0
    gini_sum = 0
    for i, value in enumerate(sorted_values):
        cumulative += value
        gini_sum += cumulative

    # Gini = 1 - 2 * (area under Lorenz curve)
    gini = 1 - (2 * gini_sum) / (n * total) + 1 / n
    return max(0.0, min(1.0, gini))


def herfindahl_index(values: List[float]) -> float:
    """
    Calculate Herfindahl-Hirschman Index (market concentration).

    0 = perfect competition, 1 = monopoly
    """
    if not values:
        return 0.0

    total = sum(values)
    if total == 0:
        return 0.0

    shares = [v / total for v in values]
    return sum(s ** 2 for s in shares)


def top_n_share(values: List[float], n: int = 1) -> float:
    """
    Calculate share of total held by top N agents.
    """
    if not values:
        return 0.0

    total = sum(values)
    if total == 0:
        return 0.0

    sorted_values = sorted(values, reverse=True)
    top_sum = sum(sorted_values[:n])
    return top_sum / total


@dataclass
class InequalityMetrics:
    """Comprehensive inequality measurements."""
    gini: float = 0.0
    herfindahl: float = 0.0
    top_1_share: float = 0.0
    top_10_share: float = 0.0
    median_wealth: float = 0.0
    mean_wealth: float = 0.0
    wealth_ratio_top_bottom: float = 0.0  # Top 10% / Bottom 10%

    @classmethod
    def from_wealth_distribution(cls, wealths: List[float]) -> 'InequalityMetrics':
        if not wealths:
            return cls()

        sorted_w = sorted(wealths)
        n = len(sorted_w)

        # Bottom and top 10%
        bottom_10_idx = max(1, n // 10)
        top_10_idx = n - bottom_10_idx

        bottom_10_avg = sum(sorted_w[:bottom_10_idx]) / bottom_10_idx if bottom_10_idx > 0 else 0
        top_10_avg = sum(sorted_w[top_10_idx:]) / (n - top_10_idx) if top_10_idx < n else 0

        ratio = top_10_avg / bottom_10_avg if bottom_10_avg > 0 else float('inf')

        return cls(
            gini=gini_coefficient(wealths),
            herfindahl=herfindahl_index(wealths),
            top_1_share=top_n_share(wealths, 1),
            top_10_share=top_n_share(wealths, max(1, n // 10)),
            median_wealth=sorted_w[n // 2],
            mean_wealth=sum(wealths) / n,
            wealth_ratio_top_bottom=ratio,
        )


# =============================================================================
# EROSION MECHANISMS
# =============================================================================

class ErosionMechanism(ABC):
    """Base class for mechanisms that erode information advantage."""

    @abstractmethod
    def apply(
        self,
        surveillance: SurveillanceCapability,
        turn: int,
    ) -> SurveillanceCapability:
        """Apply erosion and return modified capability."""
        pass


class IdentityRotation(ErosionMechanism):
    """
    Holons rotate identities, breaking surveillance targeting.

    Represents: key rotation, identity refresh, moving.
    """

    def __init__(
        self,
        rotation_rate: float = 0.1,  # 10% rotate per turn
    ):
        self.rotation_rate = rotation_rate
        self.rotated_ids: Set[str] = set()

    def apply(
        self,
        surveillance: SurveillanceCapability,
        turn: int,
    ) -> SurveillanceCapability:
        # Reduce effective coverage as targets rotate away
        # After N turns, coverage reduced by rotation_rate^N
        erosion = 1 - self.rotation_rate
        new_coverage = surveillance.coverage * erosion

        return SurveillanceCapability(
            visible_info_types=surveillance.visible_info_types,
            coverage=new_coverage,
            base_fidelity=surveillance.base_fidelity,
            fidelity_decay=surveillance.fidelity_decay,
            specific_targets=surveillance.specific_targets,
            cost_per_peek=surveillance.cost_per_peek,
        )


class NoiseInjection(ErosionMechanism):
    """
    Add noise to public signals, reducing fidelity of surveillance.

    Represents: differential privacy, decoy transactions, obfuscation.
    """

    def __init__(
        self,
        noise_level: float = 0.1,  # Reduce fidelity by 10%
    ):
        self.noise_level = noise_level

    def apply(
        self,
        surveillance: SurveillanceCapability,
        turn: int,
    ) -> SurveillanceCapability:
        new_fidelity = surveillance.base_fidelity * (1 - self.noise_level)

        return SurveillanceCapability(
            visible_info_types=surveillance.visible_info_types,
            coverage=surveillance.coverage,
            base_fidelity=new_fidelity,
            fidelity_decay=surveillance.fidelity_decay,
            specific_targets=surveillance.specific_targets,
            cost_per_peek=surveillance.cost_per_peek,
        )


class ZKShielding(ErosionMechanism):
    """
    ZK proofs hide private state, reducing visible info types.

    Represents: actual ZK implementation, private transactions.
    """

    def __init__(
        self,
        shielded_types: Set[InformationType] = None,
    ):
        self.shielded_types = shielded_types or {
            InformationType.PRIVATE_BALANCE,
            InformationType.STRATEGY,
        }

    def apply(
        self,
        surveillance: SurveillanceCapability,
        turn: int,
    ) -> SurveillanceCapability:
        # Remove shielded types from visible
        new_visible = surveillance.visible_info_types - self.shielded_types

        return SurveillanceCapability(
            visible_info_types=new_visible,
            coverage=surveillance.coverage,
            base_fidelity=surveillance.base_fidelity,
            fidelity_decay=surveillance.fidelity_decay,
            specific_targets=surveillance.specific_targets,
            cost_per_peek=surveillance.cost_per_peek,
        )


class PopulationChurn(ErosionMechanism):
    """
    New entrants dilute legacy knowledge advantage.

    Represents: market growth, new participants, ecosystem expansion.
    """

    def __init__(
        self,
        churn_rate: float = 0.05,  # 5% new entrants per turn
    ):
        self.churn_rate = churn_rate
        self.cumulative_new: float = 0.0

    def apply(
        self,
        surveillance: SurveillanceCapability,
        turn: int,
    ) -> SurveillanceCapability:
        # New entrants aren't in the legacy dataset
        self.cumulative_new += self.churn_rate
        # Coverage of original population diluted
        effective_coverage = surveillance.coverage / (1 + self.cumulative_new)

        return SurveillanceCapability(
            visible_info_types=surveillance.visible_info_types,
            coverage=effective_coverage,
            base_fidelity=surveillance.base_fidelity,
            fidelity_decay=surveillance.fidelity_decay,
            specific_targets=surveillance.specific_targets,
            cost_per_peek=surveillance.cost_per_peek,
        )


# =============================================================================
# INFORMATION ASYMMETRY SIMULATION
# =============================================================================

@dataclass
class InfoAsymmetryConfig:
    """Configuration for information asymmetry simulation."""
    # Population
    num_informed: int = 5
    num_blind: int = 45
    initial_wealth: int = 1000

    # Market
    assets_per_agent: int = 2
    valuation_variance: float = 0.3  # How much true value varies from declared

    # Surveillance scenarios
    surveillance_type: str = "legacy"  # "legacy", "active", "insider"
    coverage: float = 0.5
    fidelity: float = 0.8

    # Erosion
    erosion_mechanisms: List[str] = field(default_factory=list)  # ["rotation", "noise", "zk", "churn"]

    # Simulation
    turns: int = 100


@dataclass
class InfoAsymmetryMetrics:
    """Metrics for information asymmetry simulation."""
    turns: List[int] = field(default_factory=list)

    # Wealth tracking
    informed_wealth: List[float] = field(default_factory=list)
    blind_wealth: List[float] = field(default_factory=list)
    total_wealth: List[float] = field(default_factory=list)

    # Inequality over time
    gini_over_time: List[float] = field(default_factory=list)
    top_1_share_over_time: List[float] = field(default_factory=list)

    # Trading
    informed_surplus: int = 0
    blind_surplus: int = 0
    informed_trades: int = 0
    blind_trades: int = 0

    # Surveillance effectiveness
    effective_coverage_over_time: List[float] = field(default_factory=list)
    effective_fidelity_over_time: List[float] = field(default_factory=list)


class InfoAsymmetrySimulation:
    """
    Simulation testing information advantage effects.

    Measures:
    - How info advantage translates to wealth accumulation
    - Inequality dynamics over time
    - Effectiveness of erosion mechanisms
    """

    def __init__(self, config: InfoAsymmetryConfig):
        self.config = config
        self.market = Market()
        self.agents: Dict[str, Tuple[Holon, AgentStrategy, bool]] = {}  # key -> (holon, strategy, is_informed)
        self.metrics = InfoAsymmetryMetrics()
        self.turn = 0
        self.erosion_mechanisms: List[ErosionMechanism] = []

    def setup(self):
        """Initialize simulation."""
        # Create surveillance capability based on config
        if self.config.surveillance_type == "legacy":
            base_surveillance = LegacyAdvantage(
                coverage=self.config.coverage,
                base_fidelity=self.config.fidelity,
            )
        elif self.config.surveillance_type == "active":
            base_surveillance = ActiveSurveillance(
                coverage=self.config.coverage,
                base_fidelity=self.config.fidelity,
            )
        else:
            base_surveillance = InsiderKnowledge(
                coverage=self.config.coverage,
                base_fidelity=self.config.fidelity,
            )

        # Create informed traders
        for i in range(self.config.num_informed):
            holon = create_holon(
                initial_balance=self.config.initial_wealth,
                valuation=self.config.initial_wealth,
            )
            strategy = InformedTrader(
                surveillance=base_surveillance,
                aggression=0.5,
            )
            key = str(holon.holon_id.value)
            self.agents[key] = (holon, strategy, True)

            # Create assets
            for _ in range(self.config.assets_per_agent):
                true_value = self.config.initial_wealth // self.config.assets_per_agent
                variance = random.uniform(-self.config.valuation_variance, self.config.valuation_variance)
                declared_value = int(true_value * (1 + variance))
                self.market.create_asset(holon, true_value, declared_value)

        # Create blind traders
        for i in range(self.config.num_blind):
            holon = create_holon(
                initial_balance=self.config.initial_wealth,
                valuation=self.config.initial_wealth,
            )
            strategy = BlindTrader(trade_probability=0.1)
            key = str(holon.holon_id.value)
            self.agents[key] = (holon, strategy, False)

            # Create assets
            for _ in range(self.config.assets_per_agent):
                true_value = self.config.initial_wealth // self.config.assets_per_agent
                variance = random.uniform(-self.config.valuation_variance, self.config.valuation_variance)
                declared_value = int(true_value * (1 + variance))
                self.market.create_asset(holon, true_value, declared_value)

        # Setup erosion mechanisms
        for mech_name in self.config.erosion_mechanisms:
            if mech_name == "rotation":
                self.erosion_mechanisms.append(IdentityRotation(rotation_rate=0.1))
            elif mech_name == "noise":
                self.erosion_mechanisms.append(NoiseInjection(noise_level=0.1))
            elif mech_name == "zk":
                self.erosion_mechanisms.append(ZKShielding())
            elif mech_name == "churn":
                self.erosion_mechanisms.append(PopulationChurn(churn_rate=0.05))

    def run_turn(self):
        """Execute one turn."""
        self.turn += 1

        # Apply erosion mechanisms to all informed traders
        for key, (holon, strategy, is_informed) in self.agents.items():
            if is_informed and isinstance(strategy, InformedTrader):
                for mechanism in self.erosion_mechanisms:
                    strategy.surveillance = mechanism.apply(strategy.surveillance, self.turn)

        # Build context
        all_holons = [h for h, _, _ in self.agents.values()]
        context = {
            "all_holons": all_holons,
            "market": self.market,
        }

        # Each agent acts
        for key, (holon, strategy, is_informed) in self.agents.items():
            action, params = strategy.decide_action(
                holon, None, ReputationLedger(), self.turn, context
            )

            if action == "harberger_buy" and "asset_id" in params:
                asset_id = params["asset_id"]
                trade = self.market.harberger_buy(
                    buyer_id=holon.holon_id,
                    asset_id=asset_id,
                    buyer_knows_true_value=is_informed,
                )
                if trade:
                    if is_informed:
                        self.metrics.informed_surplus += trade["surplus"]
                        self.metrics.informed_trades += 1
                        if isinstance(strategy, InformedTrader):
                            strategy.total_surplus += trade["surplus"]
                            strategy.trades_made += 1
                    else:
                        self.metrics.blind_surplus += trade["surplus"]
                        self.metrics.blind_trades += 1
                        if isinstance(strategy, BlindTrader):
                            strategy.total_surplus += trade["surplus"]
                            strategy.trades_made += 1

        # Record metrics
        self._record_metrics()

    def _record_metrics(self):
        """Record metrics for this turn."""
        self.metrics.turns.append(self.turn)

        # Calculate wealth (vault + surplus from trades)
        informed_wealth = []
        blind_wealth = []

        for key, (holon, strategy, is_informed) in self.agents.items():
            wealth = holon.vault + self.market.total_surplus_by_agent.get(key, 0)
            if is_informed:
                informed_wealth.append(wealth)
            else:
                blind_wealth.append(wealth)

        self.metrics.informed_wealth.append(sum(informed_wealth))
        self.metrics.blind_wealth.append(sum(blind_wealth))
        self.metrics.total_wealth.append(sum(informed_wealth) + sum(blind_wealth))

        # Inequality
        all_wealth = informed_wealth + blind_wealth
        self.metrics.gini_over_time.append(gini_coefficient(all_wealth))
        self.metrics.top_1_share_over_time.append(top_n_share(all_wealth, 1))

        # Surveillance effectiveness (sample from informed traders)
        coverages = []
        fidelities = []
        for key, (holon, strategy, is_informed) in self.agents.items():
            if is_informed and isinstance(strategy, InformedTrader):
                coverages.append(strategy.surveillance.coverage)
                fidelities.append(strategy.surveillance.base_fidelity)

        if coverages:
            self.metrics.effective_coverage_over_time.append(sum(coverages) / len(coverages))
            self.metrics.effective_fidelity_over_time.append(sum(fidelities) / len(fidelities))

    def run(self, turns: Optional[int] = None) -> InfoAsymmetryMetrics:
        """Run full simulation."""
        if not self.agents:
            self.setup()

        for _ in range(turns or self.config.turns):
            self.run_turn()

        return self.metrics

    def summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        m = self.metrics

        # Final inequality metrics
        informed_wealth = []
        blind_wealth = []
        for key, (holon, strategy, is_informed) in self.agents.items():
            wealth = holon.vault + self.market.total_surplus_by_agent.get(key, 0)
            if is_informed:
                informed_wealth.append(wealth)
            else:
                blind_wealth.append(wealth)

        all_wealth = informed_wealth + blind_wealth
        inequality = InequalityMetrics.from_wealth_distribution(all_wealth)

        # Wealth advantage of informed
        avg_informed = sum(informed_wealth) / len(informed_wealth) if informed_wealth else 0
        avg_blind = sum(blind_wealth) / len(blind_wealth) if blind_wealth else 0
        wealth_advantage = avg_informed / avg_blind if avg_blind > 0 else float('inf')

        return {
            "turns_run": self.turn,
            "num_informed": self.config.num_informed,
            "num_blind": self.config.num_blind,

            # Wealth
            "avg_informed_wealth": avg_informed,
            "avg_blind_wealth": avg_blind,
            "wealth_advantage_ratio": wealth_advantage,

            # Inequality
            "final_gini": inequality.gini,
            "final_top_1_share": inequality.top_1_share,
            "final_top_10_share": inequality.top_10_share,
            "wealth_ratio_top_bottom": inequality.wealth_ratio_top_bottom,

            # Gini trajectory
            "initial_gini": m.gini_over_time[0] if m.gini_over_time else 0,
            "gini_change": m.gini_over_time[-1] - m.gini_over_time[0] if m.gini_over_time else 0,

            # Trading
            "informed_total_surplus": m.informed_surplus,
            "blind_total_surplus": m.blind_surplus,
            "informed_trades": m.informed_trades,
            "blind_trades": m.blind_trades,
            "surplus_per_informed_trade": m.informed_surplus / m.informed_trades if m.informed_trades > 0 else 0,
            "surplus_per_blind_trade": m.blind_surplus / m.blind_trades if m.blind_trades > 0 else 0,

            # Erosion effectiveness
            "final_coverage": m.effective_coverage_over_time[-1] if m.effective_coverage_over_time else 0,
            "final_fidelity": m.effective_fidelity_over_time[-1] if m.effective_fidelity_over_time else 0,
            "coverage_eroded": (
                m.effective_coverage_over_time[0] - m.effective_coverage_over_time[-1]
                if len(m.effective_coverage_over_time) > 1 else 0
            ),
        }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_info_asymmetry_sim(
    num_informed: int = 5,
    num_blind: int = 45,
    surveillance_type: str = "legacy",
    coverage: float = 0.5,
    fidelity: float = 0.8,
    erosion: List[str] = None,
    turns: int = 100,
) -> InfoAsymmetrySimulation:
    """Create an information asymmetry simulation with given parameters."""
    config = InfoAsymmetryConfig(
        num_informed=num_informed,
        num_blind=num_blind,
        surveillance_type=surveillance_type,
        coverage=coverage,
        fidelity=fidelity,
        erosion_mechanisms=erosion or [],
        turns=turns,
    )
    return InfoAsymmetrySimulation(config)
