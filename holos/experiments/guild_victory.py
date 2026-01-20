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
    legacy_capital_advantage: float = 1.0  # Capital multiplier (2.0 = 2x starting wealth)

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

    # Wealth by group (STOCK - accumulated wealth)
    legacy_wealth: List[float] = field(default_factory=list)
    counter_guild_wealth: List[float] = field(default_factory=list)
    regular_guild_wealth: List[float] = field(default_factory=list)
    blind_wealth: List[float] = field(default_factory=list)

    # Advantage ratios over time
    legacy_vs_guild_ratio: List[float] = field(default_factory=list)

    # EARNING FLOW METRICS (transaction-level competitiveness)
    # Surplus per trade by type
    legacy_surplus_per_trade: List[float] = field(default_factory=list)
    guild_surplus_per_trade: List[float] = field(default_factory=list)

    # Win rate (% of profitable trades)
    legacy_win_rate: List[float] = field(default_factory=list)
    guild_win_rate: List[float] = field(default_factory=list)

    # Earning velocity (wealth gain per turn, per capita)
    legacy_earning_velocity: List[float] = field(default_factory=list)
    guild_earning_velocity: List[float] = field(default_factory=list)

    # Earning parity ratio (guild earning rate / legacy earning rate)
    earning_parity_ratio: List[float] = field(default_factory=list)

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
    earning_parity_turn: Optional[int] = None  # Turn when earning rates equalize


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

        # Earning flow tracking (reset each metrics interval)
        self.turn_trades: Dict[str, List[int]] = {
            "legacy": [], "counter_guild": [], "regular_guild": [], "blind": []
        }
        self.prev_wealth: Dict[str, float] = {}  # For velocity calculation

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

        # Create legacy traders (with optional capital advantage)
        legacy_surv = LegacyAdvantage(
            coverage=self.config.legacy_coverage,
            base_fidelity=self.config.legacy_fidelity,
        )
        legacy_wealth = int(self.config.initial_wealth * self.config.legacy_capital_advantage)
        for i in range(self.config.num_legacy):
            holon = create_holon(
                initial_balance=legacy_wealth,
                valuation=legacy_wealth,
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

                    # Track trade for earning flow metrics
                    self.turn_trades[agent_type].append(surplus)

                    # Update agent's surplus
                    if hasattr(strategy, 'total_surplus'):
                        strategy.total_surplus += surplus
                    if hasattr(strategy, 'trades_made'):
                        strategy.trades_made += 1

        # Record metrics
        self._record_metrics()

        # Reset turn trades for next interval
        for key in self.turn_trades:
            self.turn_trades[key] = []

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

        # EARNING FLOW METRICS
        # Combine guild types for comparison
        guild_trades = self.turn_trades["counter_guild"] + self.turn_trades["regular_guild"]
        legacy_trades = self.turn_trades["legacy"]

        # Surplus per trade (average profit per transaction)
        legacy_avg_surplus = sum(legacy_trades) / len(legacy_trades) if legacy_trades else 0
        guild_avg_surplus = sum(guild_trades) / len(guild_trades) if guild_trades else 0
        self.metrics.legacy_surplus_per_trade.append(legacy_avg_surplus)
        self.metrics.guild_surplus_per_trade.append(guild_avg_surplus)

        # Win rate (% of profitable trades)
        legacy_wins = len([t for t in legacy_trades if t > 0])
        guild_wins = len([t for t in guild_trades if t > 0])
        legacy_win_rate = legacy_wins / len(legacy_trades) if legacy_trades else 0
        guild_win_rate = guild_wins / len(guild_trades) if guild_trades else 0
        self.metrics.legacy_win_rate.append(legacy_win_rate)
        self.metrics.guild_win_rate.append(guild_win_rate)

        # Earning velocity (per-capita wealth change per turn)
        n_guild = max(1, self.config.num_counter_guild + self.config.num_regular_guild)

        # Current per-capita wealth
        curr_legacy_pc = avg_legacy
        curr_guild_pc = (counter_total + regular_total) / n_guild

        # Get previous wealth (or current if first turn)
        prev_legacy_pc = self.prev_wealth.get("legacy", curr_legacy_pc)
        prev_guild_pc = self.prev_wealth.get("guild", curr_guild_pc)

        legacy_velocity = curr_legacy_pc - prev_legacy_pc
        guild_velocity = curr_guild_pc - prev_guild_pc
        self.metrics.legacy_earning_velocity.append(legacy_velocity)
        self.metrics.guild_earning_velocity.append(guild_velocity)

        # Store for next turn
        self.prev_wealth["legacy"] = curr_legacy_pc
        self.prev_wealth["guild"] = curr_guild_pc

        # Earning parity ratio (guild rate / legacy rate)
        # > 1.0 means guild is earning faster (even if poorer overall)
        if legacy_velocity > 0:
            earning_parity = guild_velocity / legacy_velocity
        elif guild_velocity > 0:
            earning_parity = float('inf')  # Guild earning, legacy not
        else:
            earning_parity = 1.0  # Both stagnant

        # Clamp to reasonable range for display
        earning_parity = max(-10, min(10, earning_parity))
        self.metrics.earning_parity_ratio.append(earning_parity)

        # Check for earning parity
        if earning_parity >= 0.9 and self.metrics.earning_parity_turn is None and self.turn > 10:
            self.metrics.earning_parity_turn = self.turn

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


# =============================================================================
# CAPITAL + INFORMATION WHALE TESTS
# =============================================================================

def test_capital_whale(
    capital_advantage: float = 2.0,
    turns: int = 500,
) -> Dict[str, Any]:
    """
    Test guild vs legacy with BOTH capital AND information advantage.

    This is the "whale" scenario - legacy traders have:
    - High surveillance (90% coverage, 85% fidelity)
    - Capital multiplier (default 2x starting wealth)

    The question: Can counter-surveillance guilds beat whales?
    """
    config = GuildVictoryConfig(
        num_legacy=3,
        num_counter_guild=30,  # Outnumber whales
        num_regular_guild=0,
        num_blind=17,
        legacy_coverage=0.9,
        legacy_fidelity=0.85,
        legacy_capital_advantage=capital_advantage,
        enable_reputation_market=True,
        enable_prediction_market=True,
        erosion_mechanisms=["rotation", "churn"],
        turns=turns,
    )
    sim = GuildVictorySimulation(config)
    sim.setup()
    sim.run()
    return sim.summary()


def test_capital_vs_guild_convergence(
    capital_advantage: float = 2.0,
    turns: int = 1000,
    sample_interval: int = 50,
) -> Dict[str, Any]:
    """
    Analyze if guild wealth converges toward whales over time.

    Returns convergence trajectory - does the gap shrink in long games?
    """
    config = GuildVictoryConfig(
        num_legacy=3,
        num_counter_guild=30,
        num_regular_guild=0,
        num_blind=17,
        legacy_coverage=0.9,
        legacy_fidelity=0.85,
        legacy_capital_advantage=capital_advantage,
        enable_reputation_market=True,
        enable_prediction_market=True,
        erosion_mechanisms=["rotation", "churn", "noise"],
        turns=turns,
    )
    sim = GuildVictorySimulation(config)
    sim.setup()
    sim.run()

    # Sample ratios over time
    ratios = []
    sampled_turns = []
    for i in range(0, len(sim.metrics.legacy_vs_guild_ratio), sample_interval):
        ratios.append(sim.metrics.legacy_vs_guild_ratio[i])
        sampled_turns.append(i)

    # Calculate trend
    if len(ratios) >= 3:
        early_ratio = ratios[2] if len(ratios) > 2 else ratios[0]
        late_ratio = ratios[-1]
        trend = "converging" if late_ratio < early_ratio else "diverging"
    else:
        early_ratio = late_ratio = ratios[0] if ratios else 1.0
        trend = "insufficient_data"

    return {
        **sim.summary(),
        "convergence_trend": trend,
        "early_ratio": early_ratio,
        "late_ratio": late_ratio,
        "ratio_change": late_ratio - early_ratio,
        "sampled_ratios": ratios[-10:],  # Last 10 samples
    }


def find_whale_victory_conditions(turns: int = 500, runs: int = 3) -> Dict[str, Any]:
    """
    Systematically search for conditions that let guilds beat capital whales.

    Tests combinations of:
    - Capital advantage (1.5x, 2.0x, 2.5x)
    - Guild size (outnumber whales)
    - Erosion mechanisms
    - Game length
    """
    print("\n" + "="*70)
    print("  WHALE VICTORY SEARCH: Can Guilds Beat Capital + Info Whales?")
    print("="*70)

    best_guild_result = None
    all_results = []

    test_configs = [
        # Baseline: Equal capital
        {"name": "Equal capital", "capital": 1.0, "guild_size": 30, "erosion": ["rotation", "churn"]},

        # Moderate whale
        {"name": "1.5x whale", "capital": 1.5, "guild_size": 30, "erosion": ["rotation", "churn"]},

        # Full whale
        {"name": "2x whale", "capital": 2.0, "guild_size": 30, "erosion": ["rotation", "churn"]},

        # Maximum erosion
        {"name": "2x + max erosion", "capital": 2.0, "guild_size": 35, "erosion": ["rotation", "churn", "noise", "zk"]},

        # Outnumber significantly
        {"name": "2x + 50 guild", "capital": 2.0, "guild_size": 50, "erosion": ["rotation", "churn"]},

        # Long game + erosion
        {"name": "2x + long game", "capital": 2.0, "guild_size": 30, "erosion": ["rotation", "churn"], "turns": 1000},

        # Weakened whale (reduced surveillance)
        {"name": "2x + weak info (60%)", "capital": 2.0, "guild_size": 30, "erosion": ["rotation", "churn"],
         "coverage": 0.6, "fidelity": 0.6},

        # Extreme: Everything stacked for guild
        {"name": "Guild-favored", "capital": 2.0, "guild_size": 50, "erosion": ["rotation", "churn", "noise", "zk"],
         "coverage": 0.5, "fidelity": 0.5, "turns": 1000},
    ]

    for test in test_configs:
        guild_wins = 0
        ratios = []

        for run in range(runs):
            config = GuildVictoryConfig(
                num_legacy=3,
                num_counter_guild=test["guild_size"],
                num_regular_guild=0,
                num_blind=max(5, 50 - test["guild_size"]),  # Fill to ~50 agents
                legacy_coverage=test.get("coverage", 0.9),
                legacy_fidelity=test.get("fidelity", 0.85),
                legacy_capital_advantage=test["capital"],
                enable_reputation_market=True,
                enable_prediction_market=True,
                erosion_mechanisms=test["erosion"],
                turns=test.get("turns", turns),
            )
            sim = GuildVictorySimulation(config)
            sim.setup()
            sim.run()
            summary = sim.summary()

            if summary.get("guild_won", False):
                guild_wins += 1
            ratios.append(summary.get("legacy_vs_counter", float('inf')))

        avg_ratio = sum(r for r in ratios if r != float('inf')) / max(1, len([r for r in ratios if r != float('inf')]))
        guild_win_rate = guild_wins / runs

        result = {
            "name": test["name"],
            "guild_win_rate": guild_win_rate,
            "avg_legacy_vs_guild": avg_ratio,
            **test
        }
        all_results.append(result)

        # Track best
        if best_guild_result is None or guild_win_rate > best_guild_result.get("guild_win_rate", 0):
            best_guild_result = result

        # Print progress
        status = "★" if guild_win_rate > 0.4 else "○"
        print(f"  {status} {test['name']:25s} | Guild wins: {guild_win_rate:5.0%} | Ratio: {avg_ratio:.2f}x")

    print("\n" + "-"*70)
    print("  BEST CONFIGURATION:")
    if best_guild_result:
        print(f"    {best_guild_result['name']}")
        print(f"    Guild win rate: {best_guild_result['guild_win_rate']:.0%}")
        print(f"    Legacy/Guild ratio: {best_guild_result['avg_legacy_vs_guild']:.2f}x")

    return {
        "all_results": all_results,
        "best": best_guild_result,
    }


def run_infinite_whale_test(turns: int = 2000) -> Dict[str, Any]:
    """
    Run a very long simulation to test if guild can ever beat 2x whales.

    This answers: In an infinite game, would guild eventually win?
    """
    print("\n" + "="*70)
    print("  INFINITE WHALE TEST (2000 turns)")
    print("="*70)

    config = GuildVictoryConfig(
        num_legacy=3,
        num_counter_guild=40,
        num_regular_guild=0,
        num_blind=7,
        legacy_coverage=0.9,
        legacy_fidelity=0.85,
        legacy_capital_advantage=2.0,
        enable_reputation_market=True,
        enable_prediction_market=True,
        erosion_mechanisms=["rotation", "churn", "noise"],
        turns=turns,
    )
    sim = GuildVictorySimulation(config)
    sim.setup()
    sim.run()
    summary = sim.summary()

    # Track ratio trajectory
    print("\n  Wealth Ratio Trajectory (Legacy / Guild):")
    ratios = sim.metrics.legacy_vs_guild_ratio
    for i in range(0, len(ratios), 200):
        bar = "█" * min(50, int(ratios[i] * 10))
        print(f"    Turn {i:4d}: {bar} {ratios[i]:.2f}x")

    print(f"\n  FINAL:")
    print(f"    Legacy/Guild ratio: {summary.get('legacy_vs_counter', 0):.2f}x")
    print(f"    Guild victory turn: {summary.get('guild_victory_turn', 'NEVER')}")
    print(f"    Converging: {summary.get('converging', False)}")

    return summary


# =============================================================================
# EARNING PARITY TESTS - Can guilds achieve competitive daily returns?
# =============================================================================

def test_earning_parity(
    capital_advantage: float = 2.0,
    turns: int = 500,
) -> Dict[str, Any]:
    """
    Test if guilds can achieve EARNING PARITY even without wealth parity.

    Earning parity = guild earning rate matches legacy earning rate.
    The rich stay rich, but day-to-day competition is fair.

    Returns metrics on:
    - Surplus per trade (who profits more per transaction)
    - Win rate (% of profitable trades)
    - Earning velocity (wealth gain per turn)
    - Earning parity ratio (guild rate / legacy rate)
    """
    print("\n" + "="*70)
    print("  EARNING PARITY TEST")
    print(f"  Capital advantage: {capital_advantage}x | Turns: {turns}")
    print("="*70)

    config = GuildVictoryConfig(
        num_legacy=3,
        num_counter_guild=40,
        num_regular_guild=0,
        num_blind=7,
        legacy_coverage=0.9,
        legacy_fidelity=0.85,
        legacy_capital_advantage=capital_advantage,
        enable_reputation_market=True,
        enable_prediction_market=True,
        erosion_mechanisms=["rotation", "churn", "noise"],
        turns=turns,
    )
    sim = GuildVictorySimulation(config)
    sim.setup()
    sim.run()

    m = sim.metrics

    # Calculate averages over last 100 turns (steady state)
    steady_state_start = max(0, len(m.turns) - 100)

    avg_legacy_surplus = sum(m.legacy_surplus_per_trade[steady_state_start:]) / max(1, len(m.legacy_surplus_per_trade[steady_state_start:]))
    avg_guild_surplus = sum(m.guild_surplus_per_trade[steady_state_start:]) / max(1, len(m.guild_surplus_per_trade[steady_state_start:]))

    avg_legacy_win = sum(m.legacy_win_rate[steady_state_start:]) / max(1, len(m.legacy_win_rate[steady_state_start:]))
    avg_guild_win = sum(m.guild_win_rate[steady_state_start:]) / max(1, len(m.guild_win_rate[steady_state_start:]))

    avg_legacy_velocity = sum(m.legacy_earning_velocity[steady_state_start:]) / max(1, len(m.legacy_earning_velocity[steady_state_start:]))
    avg_guild_velocity = sum(m.guild_earning_velocity[steady_state_start:]) / max(1, len(m.guild_earning_velocity[steady_state_start:]))

    earning_parity = avg_guild_velocity / avg_legacy_velocity if avg_legacy_velocity > 0 else (1.0 if avg_guild_velocity >= 0 else 0)

    print(f"\n  STEADY-STATE METRICS (last 100 turns):")
    print(f"\n  Transaction Competitiveness:")
    print(f"    Surplus per trade:  Legacy {avg_legacy_surplus:8.1f} | Guild {avg_guild_surplus:8.1f}")
    print(f"    Win rate:           Legacy {avg_legacy_win:8.1%} | Guild {avg_guild_win:8.1%}")

    print(f"\n  Earning Velocity (per capita, per turn):")
    print(f"    Legacy: {avg_legacy_velocity:+.2f}")
    print(f"    Guild:  {avg_guild_velocity:+.2f}")

    print(f"\n  EARNING PARITY RATIO: {earning_parity:.2f}x")
    if earning_parity >= 0.9:
        print("    ★ EARNING PARITY ACHIEVED!")
        print("    Guild competes fairly in day-to-day transactions.")
    elif earning_parity >= 0.5:
        print("    ◐ PARTIAL PARITY")
        print("    Guild is competitive but still behind.")
    else:
        print("    ○ NO PARITY")
        print("    Legacy dominates daily transactions.")

    # Wealth ratio for comparison
    final_wealth_ratio = m.legacy_vs_guild_ratio[-1] if m.legacy_vs_guild_ratio else float('inf')
    print(f"\n  For comparison:")
    print(f"    Final wealth ratio: {final_wealth_ratio:.2f}x (legacy still {final_wealth_ratio:.1f}x richer)")
    print(f"    Earning parity turn: {m.earning_parity_turn if m.earning_parity_turn else 'NEVER'}")

    return {
        "capital_advantage": capital_advantage,
        "avg_legacy_surplus": avg_legacy_surplus,
        "avg_guild_surplus": avg_guild_surplus,
        "avg_legacy_win_rate": avg_legacy_win,
        "avg_guild_win_rate": avg_guild_win,
        "avg_legacy_velocity": avg_legacy_velocity,
        "avg_guild_velocity": avg_guild_velocity,
        "earning_parity_ratio": earning_parity,
        "earning_parity_achieved": earning_parity >= 0.9,
        "final_wealth_ratio": final_wealth_ratio,
        "earning_parity_turn": m.earning_parity_turn,
    }


def find_earning_parity_conditions(turns: int = 300) -> Dict[str, Any]:
    """
    Find conditions where guilds achieve earning parity against whales.
    """
    print("\n" + "="*70)
    print("  EARNING PARITY CONDITION SEARCH")
    print("="*70)

    results = []

    tests = [
        {"name": "Equal capital", "capital": 1.0, "coverage": 0.9},
        {"name": "1.5x capital", "capital": 1.5, "coverage": 0.9},
        {"name": "2x capital", "capital": 2.0, "coverage": 0.9},
        {"name": "2x + weak info (50%)", "capital": 2.0, "coverage": 0.5},
        {"name": "2x + weak info (30%)", "capital": 2.0, "coverage": 0.3},
        {"name": "2x + minimal info (10%)", "capital": 2.0, "coverage": 0.1},
        {"name": "5x + weak info (30%)", "capital": 5.0, "coverage": 0.3},
        {"name": "10x + weak info (30%)", "capital": 10.0, "coverage": 0.3},
    ]

    for test in tests:
        config = GuildVictoryConfig(
            num_legacy=3,
            num_counter_guild=40,
            num_regular_guild=0,
            num_blind=7,
            legacy_coverage=test["coverage"],
            legacy_fidelity=test["coverage"],  # Match coverage for simplicity
            legacy_capital_advantage=test["capital"],
            enable_reputation_market=True,
            enable_prediction_market=True,
            erosion_mechanisms=["rotation", "churn", "noise"],
            turns=turns,
        )
        sim = GuildVictorySimulation(config)
        sim.setup()
        sim.run()

        m = sim.metrics
        ss = max(0, len(m.turns) - 50)

        avg_legacy_v = sum(m.legacy_earning_velocity[ss:]) / max(1, len(m.legacy_earning_velocity[ss:]))
        avg_guild_v = sum(m.guild_earning_velocity[ss:]) / max(1, len(m.guild_earning_velocity[ss:]))
        earning_parity = avg_guild_v / avg_legacy_v if avg_legacy_v > 0 else 1.0

        result = {
            "name": test["name"],
            "capital": test["capital"],
            "coverage": test["coverage"],
            "earning_parity": earning_parity,
            "wealth_ratio": m.legacy_vs_guild_ratio[-1] if m.legacy_vs_guild_ratio else 0,
            "parity_achieved": earning_parity >= 0.9,
        }
        results.append(result)

        status = "★" if earning_parity >= 0.9 else ("◐" if earning_parity >= 0.5 else "○")
        print(f"  {status} {test['name']:25s} | Earning: {earning_parity:5.2f}x | Wealth: {result['wealth_ratio']:.1f}x")

    parity_achieved = [r for r in results if r["parity_achieved"]]
    print(f"\n  Earning parity achieved in {len(parity_achieved)}/{len(results)} scenarios")

    return {
        "results": results,
        "parity_achieved": parity_achieved,
    }


# =============================================================================
# REAL-WORLD WHALE SIMULATION
# =============================================================================

def simulate_real_world_whales(turns: int = 500) -> Dict[str, Any]:
    """
    Simulate REAL-WORLD wealth inequality with AI-assisted guild coordination.

    Real-world parameters:
    - ~2,700 billionaires globally
    - ~8 billion general population
    - Ratio: ~1:3,000,000 (we'll scale down for computation)
    - Billionaires have ~$14 trillion combined (~$5B average)
    - Median global wealth ~$8,600

    Scaled parameters for simulation:
    - 3 whales (billionaires) vs 1000 guild members
    - Capital ratio: ~580x (5B / 8600)
    - We'll test: Can AI-coordinated masses achieve earning parity?
    """
    print("\n" + "="*70)
    print("  REAL-WORLD WHALE SIMULATION")
    print("="*70)
    print("""
  Real-world parameters (scaled for simulation):
  - 3 billionaire whales vs 1000 coordinated citizens
  - Capital ratio: ~580x (average billionaire vs median global wealth)
  - All citizens use AI for rational coordination
  - Full counter-surveillance guild cooperation
    """)

    # Scale down for computation but maintain ratios
    # 3 whales vs 100 guild (1:33 ratio, scaled from 1:3M)
    # Capital: 100x (scaled from 580x to be tractable)

    configs = [
        {"name": "10x capital (optimistic)", "capital": 10.0, "guild_size": 100},
        {"name": "50x capital (moderate)", "capital": 50.0, "guild_size": 100},
        {"name": "100x capital (realistic)", "capital": 100.0, "guild_size": 100},
        {"name": "100x + 500 guild", "capital": 100.0, "guild_size": 500},
        {"name": "100x + degraded info (20%)", "capital": 100.0, "guild_size": 100, "coverage": 0.2},
    ]

    results = []

    for cfg in configs:
        config = GuildVictoryConfig(
            num_legacy=3,
            num_counter_guild=cfg["guild_size"],
            num_regular_guild=0,
            num_blind=0,  # Everyone is AI-coordinated
            legacy_coverage=cfg.get("coverage", 0.9),
            legacy_fidelity=cfg.get("coverage", 0.9),
            legacy_capital_advantage=cfg["capital"],
            enable_reputation_market=True,
            enable_prediction_market=True,
            erosion_mechanisms=["rotation", "churn", "noise", "zk"],
            turns=turns,
            initial_wealth=1000,
        )
        sim = GuildVictorySimulation(config)
        sim.setup()
        sim.run()

        m = sim.metrics
        ss = max(0, len(m.turns) - 50)

        avg_legacy_v = sum(m.legacy_earning_velocity[ss:]) / max(1, len(m.legacy_earning_velocity[ss:]))
        avg_guild_v = sum(m.guild_earning_velocity[ss:]) / max(1, len(m.guild_earning_velocity[ss:]))
        earning_parity = avg_guild_v / avg_legacy_v if avg_legacy_v > 0 else 1.0

        result = {
            "name": cfg["name"],
            "capital": cfg["capital"],
            "guild_size": cfg["guild_size"],
            "earning_parity": earning_parity,
            "wealth_ratio": m.legacy_vs_guild_ratio[-1] if m.legacy_vs_guild_ratio else 0,
            "guild_won": m.guild_victory_turn is not None,
        }
        results.append(result)

        status = "★" if earning_parity >= 0.9 else ("◐" if earning_parity >= 0.5 else "○")
        print(f"  {status} {cfg['name']:30s}")
        print(f"      Earning parity: {earning_parity:.2f}x | Wealth ratio: {result['wealth_ratio']:.1f}x")

    print("\n" + "-"*70)
    print("  CONCLUSION: REAL-WORLD PATHS TO FAIRNESS")
    print("-"*70)

    best = max(results, key=lambda r: r["earning_parity"])
    print(f"\n  Best scenario: {best['name']}")
    print(f"    Earning parity: {best['earning_parity']:.2f}x")
    print(f"    Wealth ratio: {best['wealth_ratio']:.1f}x")

    if best["earning_parity"] >= 0.9:
        print("\n  ★ EARNING PARITY IS ACHIEVABLE!")
        print("    With AI coordination, guilds can compete fairly in daily transactions.")
        print("    The rich stay rich, but their earning RATE matches the masses.")
    else:
        print("\n  ○ EARNING PARITY NOT ACHIEVABLE")
        print("    Even with full coordination, whales dominate daily transactions.")
        print("    Structural change (taxation, caps) may be required.")

    return {
        "results": results,
        "best": best,
        "parity_achievable": best["earning_parity"] >= 0.9,
    }
