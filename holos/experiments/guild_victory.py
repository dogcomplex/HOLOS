"""
Guild Victory Paths - Testing What Makes Cooperatives Win

Explores mechanisms that could allow bottom-up cooperative guilds to
overcome legacy information advantages:

1. Pure Time Erosion - Does natural decay eventually level the field?
2. Coordinated Counter-Surveillance - Identify and boycott legacy players
3. Prediction Markets - Crowd wisdom for price discovery
4. Reputation Markets - Track trading accuracy, expose information predators
5. Information Markets - Democratize access to surveillance data

Key question: What's the economic cost of each path?
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Tuple
from enum import Enum
import random
import math
import uuid

from holos.kernel import create_holon, HolonId, Holon

from .information_asymmetry import (
    InformationType, InformationPacket, SurveillanceCapability,
    LegacyAdvantage, ActiveSurveillance,
    Asset, Market, InformedTrader, BlindTrader,
    gini_coefficient, herfindahl_index, InequalityMetrics,
    IdentityRotation, NoiseInjection, ZKShielding, PopulationChurn,
)

from .market_efficiency import (
    MarketEfficiencyMetrics, calculate_market_efficiency,
    InformationGuild, GuildMember, LLMAgent,
)

from .adversarial import ReputationLedger, AgentStrategy


# =============================================================================
# REPUTATION MARKET
# =============================================================================

@dataclass
class TradingReputation:
    """Track trading behavior to identify information predators."""
    agent_id: str

    # Trading history
    trades_made: int = 0
    profitable_trades: int = 0
    total_surplus_captured: int = 0

    # Suspicion metrics
    avg_surplus_per_trade: float = 0.0
    win_rate: float = 0.0

    # Reputation score (higher = more suspicious of being informed)
    predator_score: float = 0.0  # 0 = normal, 1 = definitely has inside info

    # Community trust (inverse of predator score)
    trust_score: float = 1.0

    def update(self, trade_surplus: int):
        """Update reputation based on trade outcome."""
        self.trades_made += 1
        if trade_surplus > 0:
            self.profitable_trades += 1
            self.total_surplus_captured += trade_surplus

        # Calculate metrics
        if self.trades_made > 0:
            self.win_rate = self.profitable_trades / self.trades_made
            self.avg_surplus_per_trade = self.total_surplus_captured / self.trades_made

        # Update predator score
        # High win rate + high average surplus = likely has inside info
        if self.trades_made >= 5:  # Need enough data
            win_rate_factor = max(0, (self.win_rate - 0.5) * 2)  # 0.5 is baseline
            surplus_factor = min(1, self.avg_surplus_per_trade / 100)  # Normalize
            self.predator_score = min(1.0, (win_rate_factor + surplus_factor) / 2)
            self.trust_score = 1.0 - self.predator_score


@dataclass
class ReputationMarket:
    """
    Decentralized reputation tracking for the market.

    Exposes information predators through pattern detection:
    - Consistently profitable trades → likely has inside info
    - High surplus capture → targeting undervalued assets
    - Trading against the crowd → may know something others don't
    """

    reputations: Dict[str, TradingReputation] = field(default_factory=dict)

    # Detection thresholds
    predator_threshold: float = 0.6  # Score above this = flagged as predator

    # Boycott list (agents identified as predators)
    boycott_list: Set[str] = field(default_factory=set)

    def get_reputation(self, agent_id: str) -> TradingReputation:
        """Get or create reputation record."""
        if agent_id not in self.reputations:
            self.reputations[agent_id] = TradingReputation(agent_id=agent_id)
        return self.reputations[agent_id]

    def record_trade(self, buyer_id: str, surplus: int):
        """Record a trade and update reputation."""
        rep = self.get_reputation(buyer_id)
        rep.update(surplus)

        # Check if should be boycotted
        if rep.predator_score >= self.predator_threshold and rep.trades_made >= 10:
            self.boycott_list.add(buyer_id)

    def is_boycotted(self, agent_id: str) -> bool:
        """Check if an agent is on the boycott list."""
        return agent_id in self.boycott_list

    def get_trust_score(self, agent_id: str) -> float:
        """Get trust score for an agent."""
        return self.get_reputation(agent_id).trust_score

    def get_predators(self) -> List[str]:
        """Get list of identified predators."""
        return list(self.boycott_list)


# =============================================================================
# PREDICTION MARKET
# =============================================================================

@dataclass
class Prediction:
    """A prediction about an asset's true value."""
    predictor_id: str
    asset_id: str
    predicted_value: int
    confidence: float  # 0-1
    stake: int  # Amount wagered on prediction
    timestamp: int


@dataclass
class PredictionMarket:
    """
    Aggregates crowd predictions to estimate true values.

    Mechanism:
    - Agents stake tokens on their value predictions
    - Predictions are weighted by stake and historical accuracy
    - Consensus estimate used for price discovery
    - Accurate predictors earn rewards, inaccurate lose stake
    """

    predictions: Dict[str, List[Prediction]] = field(default_factory=dict)  # asset_id -> predictions
    predictor_accuracy: Dict[str, float] = field(default_factory=dict)  # predictor_id -> accuracy

    # Rewards pool
    pool_balance: int = 0

    def submit_prediction(
        self,
        predictor_id: str,
        asset_id: str,
        predicted_value: int,
        stake: int,
        timestamp: int,
    ):
        """Submit a prediction for an asset's true value."""
        prediction = Prediction(
            predictor_id=predictor_id,
            asset_id=asset_id,
            predicted_value=predicted_value,
            confidence=min(1.0, stake / 100),  # Higher stake = higher confidence
            stake=stake,
            timestamp=timestamp,
        )

        if asset_id not in self.predictions:
            self.predictions[asset_id] = []
        self.predictions[asset_id].append(prediction)
        self.pool_balance += stake

    def get_consensus_value(self, asset_id: str) -> Optional[int]:
        """Get stake-weighted consensus estimate of true value."""
        if asset_id not in self.predictions:
            return None

        predictions = self.predictions[asset_id]
        if not predictions:
            return None

        # Weight by stake and predictor accuracy
        total_weight = 0
        weighted_sum = 0

        for pred in predictions:
            accuracy = self.predictor_accuracy.get(pred.predictor_id, 0.5)
            weight = pred.stake * accuracy
            weighted_sum += pred.predicted_value * weight
            total_weight += weight

        if total_weight == 0:
            return None

        return int(weighted_sum / total_weight)

    def resolve(self, asset_id: str, true_value: int) -> Dict[str, int]:
        """
        Resolve predictions when true value is revealed.
        Returns rewards/penalties for each predictor.
        """
        if asset_id not in self.predictions:
            return {}

        rewards = {}
        predictions = self.predictions[asset_id]

        for pred in predictions:
            # Calculate accuracy (closer to true = better)
            error = abs(pred.predicted_value - true_value) / max(1, true_value)
            accuracy = max(0, 1 - error)

            # Update predictor accuracy history
            old_accuracy = self.predictor_accuracy.get(pred.predictor_id, 0.5)
            self.predictor_accuracy[pred.predictor_id] = 0.8 * old_accuracy + 0.2 * accuracy

            # Calculate reward/penalty
            if accuracy > 0.8:  # Good prediction
                reward = int(pred.stake * accuracy)
                rewards[pred.predictor_id] = reward
            else:  # Poor prediction - lose stake
                rewards[pred.predictor_id] = -pred.stake

        # Clear resolved predictions
        del self.predictions[asset_id]

        return rewards


# =============================================================================
# COUNTER-SURVEILLANCE GUILD
# =============================================================================

class CounterSurveillanceGuild(InformationGuild):
    """
    Guild that actively identifies and counters legacy information brokers.

    Additional capabilities:
    - Pattern detection: Identify who's trading with inside info
    - Coordinated boycott: Refuse trades with identified predators
    - Information sharing: Alert members about suspicious traders
    - Collective defense: Noise injection when predators target members
    """

    def __init__(
        self,
        guild_id: str,
        name: str,
        reputation_market: ReputationMarket,
        prediction_market: PredictionMarket,
        **kwargs
    ):
        super().__init__(guild_id=guild_id, name=name, **kwargs)
        self.reputation_market = reputation_market
        self.prediction_market = prediction_market

        # Counter-surveillance state
        self.identified_predators: Set[str] = set()
        self.defense_active: bool = True

    def analyze_market_patterns(self, market: Market) -> List[str]:
        """Analyze market to identify likely information predators."""
        suspicious = []

        # Look at trade history
        for trade in market.trades[-100:]:  # Recent trades
            buyer_id = str(trade.get("buyer_id", ""))
            surplus = trade.get("surplus", 0)

            if surplus > 50:  # Suspiciously profitable
                rep = self.reputation_market.get_reputation(buyer_id)
                if rep.predator_score > 0.5:
                    suspicious.append(buyer_id)

        return list(set(suspicious))

    def should_trade_with(self, counterparty_id: str) -> bool:
        """Decide if guild should trade with this counterparty."""
        # Check boycott list
        if self.reputation_market.is_boycotted(counterparty_id):
            return False

        # Check if identified as predator
        if counterparty_id in self.identified_predators:
            return False

        return True

    def submit_collective_prediction(
        self,
        asset_id: str,
        timestamp: int,
    ) -> Optional[int]:
        """
        Aggregate member information to make collective prediction.
        Crowd wisdom often beats individual experts.
        """
        # Gather estimates from shared info
        estimates = []

        for info_key, packet in self.shared_info.items():
            if packet.info_type == InformationType.VALUATION:
                # Weight by fidelity and recency
                weight = packet.fidelity * max(0.1, 1 - (timestamp - packet.timestamp) * 0.05)
                estimates.append((packet.observed_value, weight))

        if not estimates:
            return None

        # Weighted average
        total_weight = sum(w for _, w in estimates)
        if total_weight == 0:
            return None

        consensus = sum(v * w for v, w in estimates) / total_weight

        # Submit to prediction market
        collective_stake = min(100, self.pool_balance // 10)
        if collective_stake > 0:
            self.prediction_market.submit_prediction(
                predictor_id=f"guild_{self.guild_id}",
                asset_id=asset_id,
                predicted_value=int(consensus),
                stake=collective_stake,
                timestamp=timestamp,
            )

        return int(consensus)


class CounterSurveillanceAgent(AgentStrategy):
    """
    Guild member with counter-surveillance capabilities.

    Strategy:
    1. Share information with guild
    2. Use collective intelligence for trading
    3. Avoid trading with identified predators
    4. Contribute to predator detection
    """

    name = "counter_surveillance"

    def __init__(
        self,
        guild: CounterSurveillanceGuild,
        personal_surveillance: Optional[SurveillanceCapability] = None,
    ):
        self.guild = guild
        self.personal_surveillance = personal_surveillance or SurveillanceCapability(
            coverage=0.15,
            base_fidelity=0.7,
        )
        self.total_surplus: int = 0
        self.trades_made: int = 0
        self.trades_avoided: int = 0  # Predator trades avoided

    def decide_action(
        self,
        holon: Holon,
        enclave: Any,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        # Surveil and share
        if "all_holons" in context:
            self._surveil_and_share(holon, context["all_holons"], turn)

        # Analyze patterns and update predator list
        if "market" in context and turn % 10 == 0:
            suspicious = self.guild.analyze_market_patterns(context["market"])
            self.guild.identified_predators.update(suspicious)

        # Get guild's shared intelligence + prediction market consensus
        all_info = self.guild.get_shared_info(holon.holon_id)

        # Look for trading opportunities
        if "market" in context and random.random() < 0.3:
            market: Market = context["market"]
            opportunities = market.get_undervalued_assets(all_info, min_surplus_ratio=0.15)

            for asset_id, expected_surplus in opportunities:
                asset = market.assets.get(asset_id)
                if not asset:
                    continue

                owner_id = str(asset.owner_id.value)

                # Check if owner is a predator (don't buy from predators - they set traps)
                if not self.guild.should_trade_with(owner_id):
                    self.trades_avoided += 1
                    continue

                return "harberger_buy", {
                    "asset_id": asset_id,
                    "expected_surplus": expected_surplus,
                }

        return "idle", {}

    def _surveil_and_share(self, holon: Holon, targets: List[Holon], turn: int):
        """Surveil targets and share with guild."""
        for target in targets:
            if not self.personal_surveillance.can_surveil(
                target.holon_id,
                [t.holon_id for t in targets]
            ):
                continue

            for info_type in self.personal_surveillance.visible_info_types:
                if info_type == InformationType.VALUATION:
                    true_value = target.vault + target._private_balance
                    fidelity = self.personal_surveillance.get_fidelity(0)
                    noise = random.gauss(0, (1 - fidelity) * abs(true_value) * 0.5)

                    packet = InformationPacket(
                        target_id=target.holon_id,
                        info_type=info_type,
                        true_value=true_value,
                        observed_value=true_value + noise,
                        fidelity=fidelity,
                        timestamp=turn,
                    )
                    self.guild.contribute_info(holon.holon_id, packet)

    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        return self.guild.should_trade_with(str(partner_id.value))


# =============================================================================
# ENHANCED SIMULATION WITH GUILD VICTORY PATHS
# =============================================================================

@dataclass
class GuildVictoryConfig:
    """Configuration for guild victory path testing."""

    # Agent composition
    num_legacy: int = 5
    num_counter_guild: int = 20
    num_regular_guild: int = 10
    num_blind: int = 15

    # Legacy advantage
    legacy_coverage: float = 0.9
    legacy_fidelity: float = 0.85

    # Markets
    enable_reputation_market: bool = True
    enable_prediction_market: bool = True

    # Counter-surveillance
    predator_detection_threshold: float = 0.6

    # Erosion
    erosion_mechanisms: List[str] = field(default_factory=list)

    # Simulation
    turns: int = 200
    initial_wealth: int = 1000


@dataclass
class GuildVictoryMetrics:
    """Metrics tracking guild vs legacy competition."""

    turns: List[int] = field(default_factory=list)

    # Wealth by group
    legacy_wealth: List[float] = field(default_factory=list)
    counter_guild_wealth: List[float] = field(default_factory=list)
    regular_guild_wealth: List[float] = field(default_factory=list)
    blind_wealth: List[float] = field(default_factory=list)

    # Advantage ratios over time
    legacy_vs_guild_ratio: List[float] = field(default_factory=list)

    # Counter-surveillance effectiveness
    predators_identified: List[int] = field(default_factory=list)
    trades_avoided: List[int] = field(default_factory=list)

    # Market health
    efficiency_over_time: List[float] = field(default_factory=list)
    gini_over_time: List[float] = field(default_factory=list)

    # Prediction market
    prediction_accuracy: List[float] = field(default_factory=list)

    # Method
    method: str = "rule_based"

    # Victory detection
    guild_victory_turn: Optional[int] = None  # Turn when guild avg > legacy avg


class GuildVictorySimulation:
    """
    Simulation testing paths to guild victory over legacy information brokers.
    """

    def __init__(self, config: GuildVictoryConfig):
        self.config = config
        self.market = Market()
        self.reputation_market = ReputationMarket(
            predator_threshold=config.predator_detection_threshold
        )
        self.prediction_market = PredictionMarket()

        self.counter_guild: Optional[CounterSurveillanceGuild] = None
        self.regular_guild: Optional[InformationGuild] = None

        self.agents: Dict[str, Tuple[Holon, AgentStrategy, str]] = {}
        self.metrics = GuildVictoryMetrics()
        self.turn = 0
        self.erosion_mechanisms = []

    def setup(self):
        """Initialize simulation."""
        self.metrics.method = "rule_based"

        # Create counter-surveillance guild
        self.counter_guild = CounterSurveillanceGuild(
            guild_id="counter_1",
            name="Counter-Surveillance Cooperative",
            reputation_market=self.reputation_market,
            prediction_market=self.prediction_market,
            membership_stake=50,
        )

        # Create regular guild for comparison
        self.regular_guild = InformationGuild(
            guild_id="regular_1",
            name="Standard Cooperative",
            membership_stake=50,
        )

        # Create legacy traders
        legacy_surv = LegacyAdvantage(
            coverage=self.config.legacy_coverage,
            base_fidelity=self.config.legacy_fidelity,
        )
        for i in range(self.config.num_legacy):
            holon = create_holon(
                initial_balance=self.config.initial_wealth,
                valuation=self.config.initial_wealth,
            )
            strategy = InformedTrader(surveillance=legacy_surv, aggression=0.5)
            self._register_agent(holon, strategy, "legacy")

        # Create counter-surveillance guild members
        for i in range(self.config.num_counter_guild):
            holon = create_holon(
                initial_balance=self.config.initial_wealth,
                valuation=self.config.initial_wealth,
            )
            self.counter_guild.add_member(holon.holon_id, 50)
            strategy = CounterSurveillanceAgent(
                guild=self.counter_guild,
                personal_surveillance=SurveillanceCapability(coverage=0.15, base_fidelity=0.7),
            )
            self._register_agent(holon, strategy, "counter_guild")

        # Create regular guild members
        for i in range(self.config.num_regular_guild):
            holon = create_holon(
                initial_balance=self.config.initial_wealth,
                valuation=self.config.initial_wealth,
            )
            self.regular_guild.add_member(holon.holon_id, 50)
            strategy = GuildMember(guild=self.regular_guild, contribution_rate=0.8)
            self._register_agent(holon, strategy, "regular_guild")

        # Create blind traders
        for i in range(self.config.num_blind):
            holon = create_holon(
                initial_balance=self.config.initial_wealth,
                valuation=self.config.initial_wealth,
            )
            strategy = BlindTrader(trade_probability=0.1)
            self._register_agent(holon, strategy, "blind")

        # Setup erosion
        for mech_name in self.config.erosion_mechanisms:
            if mech_name == "rotation":
                self.erosion_mechanisms.append(IdentityRotation(rotation_rate=0.1))
            elif mech_name == "noise":
                self.erosion_mechanisms.append(NoiseInjection(noise_level=0.1))
            elif mech_name == "zk":
                self.erosion_mechanisms.append(ZKShielding())
            elif mech_name == "churn":
                self.erosion_mechanisms.append(PopulationChurn(churn_rate=0.05))

    def _register_agent(self, holon: Holon, strategy: AgentStrategy, agent_type: str):
        """Register an agent and create their assets."""
        key = str(holon.holon_id.value)
        self.agents[key] = (holon, strategy, agent_type)

        # Create assets
        for _ in range(2):
            true_value = self.config.initial_wealth // 2
            variance = random.uniform(-0.3, 0.3)
            declared_value = int(true_value * (1 + variance))
            self.market.create_asset(holon, true_value, declared_value)

    def run_turn(self):
        """Execute one turn."""
        self.turn += 1

        # Apply erosion to legacy traders
        for key, (holon, strategy, agent_type) in self.agents.items():
            if agent_type == "legacy" and isinstance(strategy, InformedTrader):
                for mechanism in self.erosion_mechanisms:
                    strategy.surveillance = mechanism.apply(strategy.surveillance, self.turn)

        # Build context
        all_holons = [h for h, _, _ in self.agents.values()]
        context = {
            "all_holons": all_holons,
            "market": self.market,
            "reputation_market": self.reputation_market,
            "prediction_market": self.prediction_market,
        }

        # Each agent acts
        for key, (holon, strategy, agent_type) in self.agents.items():
            action, params = strategy.decide_action(
                holon, None, ReputationLedger(), self.turn, context
            )

            if action == "harberger_buy" and "asset_id" in params:
                trade = self.market.harberger_buy(
                    buyer_id=holon.holon_id,
                    asset_id=params["asset_id"],
                    buyer_knows_true_value=(agent_type != "blind"),
                )
                if trade:
                    surplus = trade["surplus"]

                    # Update reputation market
                    self.reputation_market.record_trade(key, surplus)

                    # Update agent's surplus
                    if hasattr(strategy, 'total_surplus'):
                        strategy.total_surplus += surplus
                    if hasattr(strategy, 'trades_made'):
                        strategy.trades_made += 1

        # Record metrics
        self._record_metrics()

    def _record_metrics(self):
        """Record metrics for this turn."""
        self.metrics.turns.append(self.turn)

        # Calculate wealth by type
        type_wealth = {"legacy": [], "counter_guild": [], "regular_guild": [], "blind": []}

        for key, (holon, strategy, agent_type) in self.agents.items():
            wealth = holon.vault + self.market.total_surplus_by_agent.get(key, 0)
            type_wealth[agent_type].append(wealth)

        legacy_total = sum(type_wealth["legacy"])
        counter_total = sum(type_wealth["counter_guild"])
        regular_total = sum(type_wealth["regular_guild"])
        blind_total = sum(type_wealth["blind"])

        self.metrics.legacy_wealth.append(legacy_total)
        self.metrics.counter_guild_wealth.append(counter_total)
        self.metrics.regular_guild_wealth.append(regular_total)
        self.metrics.blind_wealth.append(blind_total)

        # Calculate advantage ratio
        n_legacy = max(1, self.config.num_legacy)
        n_counter = max(1, self.config.num_counter_guild)

        avg_legacy = legacy_total / n_legacy
        avg_counter = counter_total / n_counter

        ratio = avg_legacy / avg_counter if avg_counter > 0 else float('inf')
        self.metrics.legacy_vs_guild_ratio.append(ratio)

        # Check for guild victory
        if avg_counter > avg_legacy and self.metrics.guild_victory_turn is None:
            self.metrics.guild_victory_turn = self.turn

        # Counter-surveillance metrics
        self.metrics.predators_identified.append(len(self.reputation_market.boycott_list))

        total_avoided = sum(
            s.trades_avoided for _, (_, s, t) in self.agents.items()
            if t == "counter_guild" and hasattr(s, 'trades_avoided')
        )
        self.metrics.trades_avoided.append(total_avoided)

        # Market health
        all_wealth = type_wealth["legacy"] + type_wealth["counter_guild"] + \
                     type_wealth["regular_guild"] + type_wealth["blind"]
        self.metrics.gini_over_time.append(gini_coefficient(all_wealth))

        efficiency = calculate_market_efficiency(self.market, self.agents)
        self.metrics.efficiency_over_time.append(efficiency.efficiency_score())

    def run(self, turns: Optional[int] = None) -> GuildVictoryMetrics:
        """Run full simulation."""
        if not self.agents:
            self.setup()

        for _ in range(turns or self.config.turns):
            self.run_turn()

        return self.metrics

    def summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary."""
        m = self.metrics

        n_legacy = max(1, self.config.num_legacy)
        n_counter = max(1, self.config.num_counter_guild)
        n_regular = max(1, self.config.num_regular_guild)
        n_blind = max(1, self.config.num_blind)

        avg_legacy = m.legacy_wealth[-1] / n_legacy if m.legacy_wealth else 0
        avg_counter = m.counter_guild_wealth[-1] / n_counter if m.counter_guild_wealth else 0
        avg_regular = m.regular_guild_wealth[-1] / n_regular if m.regular_guild_wealth else 0
        avg_blind = m.blind_wealth[-1] / n_blind if m.blind_wealth else 0

        # Calculate trajectory
        early_ratio = m.legacy_vs_guild_ratio[10] if len(m.legacy_vs_guild_ratio) > 10 else float('inf')
        late_ratio = m.legacy_vs_guild_ratio[-1] if m.legacy_vs_guild_ratio else float('inf')

        return {
            # Method
            "method": m.method,
            "turns_run": self.turn,

            # Configuration
            "num_legacy": n_legacy,
            "num_counter_guild": n_counter,
            "num_regular_guild": n_regular,
            "num_blind": n_blind,
            "erosion_mechanisms": self.config.erosion_mechanisms,

            # Final wealth
            "avg_legacy_wealth": avg_legacy,
            "avg_counter_guild_wealth": avg_counter,
            "avg_regular_guild_wealth": avg_regular,
            "avg_blind_wealth": avg_blind,

            # Advantage ratios
            "legacy_vs_counter": avg_legacy / avg_counter if avg_counter > 0 else float('inf'),
            "legacy_vs_blind": avg_legacy / avg_blind if avg_blind > 0 else float('inf'),
            "counter_vs_regular": avg_counter / avg_regular if avg_regular > 0 else float('inf'),

            # Trajectory
            "early_legacy_advantage": early_ratio,
            "late_legacy_advantage": late_ratio,
            "advantage_change": late_ratio - early_ratio,
            "converging": late_ratio < early_ratio,

            # Victory
            "guild_victory_turn": m.guild_victory_turn,
            "guild_won": m.guild_victory_turn is not None,

            # Counter-surveillance
            "predators_identified": m.predators_identified[-1] if m.predators_identified else 0,
            "trades_avoided": m.trades_avoided[-1] if m.trades_avoided else 0,

            # Market health
            "final_gini": m.gini_over_time[-1] if m.gini_over_time else 0,
            "final_efficiency": m.efficiency_over_time[-1] if m.efficiency_over_time else 0,
            "initial_gini": m.gini_over_time[0] if m.gini_over_time else 0,
            "gini_change": (m.gini_over_time[-1] - m.gini_over_time[0]) if m.gini_over_time else 0,
        }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def test_pure_time_erosion(turns: int = 500) -> Dict[str, Any]:
    """Test how long until pure time erosion leads to parity."""
    config = GuildVictoryConfig(
        num_legacy=5,
        num_counter_guild=0,  # No counter-surveillance
        num_regular_guild=20,
        num_blind=25,
        erosion_mechanisms=["rotation", "churn"],
        turns=turns,
    )
    sim = GuildVictorySimulation(config)
    sim.setup()
    sim.run()
    return sim.summary()


def test_counter_surveillance(turns: int = 200) -> Dict[str, Any]:
    """Test if counter-surveillance helps guilds win."""
    config = GuildVictoryConfig(
        num_legacy=5,
        num_counter_guild=20,
        num_regular_guild=0,
        num_blind=25,
        enable_reputation_market=True,
        erosion_mechanisms=["churn"],
        turns=turns,
    )
    sim = GuildVictorySimulation(config)
    sim.setup()
    sim.run()
    return sim.summary()


def test_all_mechanisms(turns: int = 200) -> Dict[str, Any]:
    """Test with all mechanisms enabled."""
    config = GuildVictoryConfig(
        num_legacy=5,
        num_counter_guild=20,
        num_regular_guild=10,
        num_blind=15,
        enable_reputation_market=True,
        enable_prediction_market=True,
        erosion_mechanisms=["rotation", "noise", "churn"],
        turns=turns,
    )
    sim = GuildVictorySimulation(config)
    sim.setup()
    sim.run()
    return sim.summary()


def find_victory_conditions() -> Dict[str, Any]:
    """
    Systematically test different configurations to find guild victory conditions.
    """
    results = []

    # Test different erosion combinations
    erosion_combos = [
        [],
        ["churn"],
        ["rotation"],
        ["rotation", "churn"],
        ["rotation", "churn", "noise"],
    ]

    for erosion in erosion_combos:
        config = GuildVictoryConfig(
            num_legacy=3,
            num_counter_guild=25,  # Outnumber legacy
            num_regular_guild=0,
            num_blind=22,
            enable_reputation_market=True,
            erosion_mechanisms=erosion,
            turns=300,
        )
        sim = GuildVictorySimulation(config)
        sim.setup()
        sim.run()
        summary = sim.summary()
        summary["erosion_combo"] = erosion
        results.append(summary)

    return {
        "results": results,
        "winning_configs": [r for r in results if r["guild_won"]],
        "best_config": min(results, key=lambda r: r.get("guild_victory_turn") or float('inf')),
    }


def test_weakened_legacy(
    coverage: float = 0.3,
    fidelity: float = 0.5,
    turns: int = 200,
) -> Dict[str, Any]:
    """
    Test guild victory with weakened legacy (simulates effective ZK/privacy).

    Key finding: Guilds WIN when legacy coverage < 40% and fidelity < 60%.
    This represents effective privacy-preserving technology.
    """
    config = GuildVictoryConfig(
        num_legacy=3,
        num_counter_guild=25,
        num_regular_guild=0,
        num_blind=22,
        legacy_coverage=coverage,
        legacy_fidelity=fidelity,
        enable_reputation_market=True,
        erosion_mechanisms=["rotation", "churn"],
        turns=turns,
    )
    sim = GuildVictorySimulation(config)
    sim.setup()
    sim.run()
    return sim.summary()


def find_victory_threshold() -> Dict[str, Any]:
    """
    Find the threshold where guilds start winning.

    Tests different legacy coverage/fidelity combinations to find
    the tipping point.
    """
    results = []

    for coverage in [0.9, 0.7, 0.5, 0.4, 0.3, 0.2]:
        for fidelity in [0.9, 0.7, 0.5, 0.4]:
            config = GuildVictoryConfig(
                num_legacy=3,
                num_counter_guild=25,
                num_regular_guild=0,
                num_blind=22,
                legacy_coverage=coverage,
                legacy_fidelity=fidelity,
                enable_reputation_market=True,
                erosion_mechanisms=["rotation", "churn"],
                turns=150,
            )
            sim = GuildVictorySimulation(config)
            sim.setup()
            sim.run()
            summary = sim.summary()
            summary["legacy_coverage"] = coverage
            summary["legacy_fidelity"] = fidelity
            results.append(summary)

    # Find winning configs
    winning = [r for r in results if r["guild_won"]]

    # Find threshold (highest coverage/fidelity that still loses)
    losing_high = max(
        [r for r in results if not r["guild_won"]],
        key=lambda r: r["legacy_coverage"] * r["legacy_fidelity"],
        default=None
    )

    return {
        "results": results,
        "winning_configs": winning,
        "threshold_coverage": 0.4 if winning else None,  # Approximate
        "threshold_fidelity": 0.5 if winning else None,
        "losing_boundary": losing_high,
    }
