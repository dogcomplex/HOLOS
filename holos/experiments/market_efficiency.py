"""
Market Efficiency & Cooperative Information Sharing

Tests the trade-off between information asymmetry and market efficiency.

Key economic concepts:
- Grossman-Stiglitz paradox: Perfect efficiency → no incentive to gather info
- Price discovery: Informed traders HELP set accurate prices
- Allocative efficiency: Assets go to highest-value users
- Deadweight loss: Transactions that should happen but don't

Questions:
1. Does erosion hurt market efficiency?
2. Can cooperative guilds match legacy information brokers?
3. What's the optimal information distribution for market function?
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Tuple, Callable
from enum import Enum
from abc import ABC, abstractmethod
import random
import math
import uuid
import os
import json

from holos.kernel import create_holon, HolonId, Holon

from .information_asymmetry import (
    InformationType, InformationPacket, SurveillanceCapability,
    LegacyAdvantage, ActiveSurveillance,
    Asset, Market, InformedTrader, BlindTrader,
    gini_coefficient, herfindahl_index, InequalityMetrics,
    IdentityRotation, NoiseInjection, ZKShielding, PopulationChurn,
    InfoAsymmetryConfig, InfoAsymmetrySimulation,
)

from .adversarial import ReputationLedger, AgentStrategy


# =============================================================================
# MARKET EFFICIENCY METRICS
# =============================================================================

@dataclass
class MarketEfficiencyMetrics:
    """
    Professional market efficiency measurements.

    Based on:
    - Fama's Efficient Market Hypothesis levels
    - Allocative efficiency (Pareto optimality)
    - Price discovery speed
    - Information incorporation rate
    """

    # Price accuracy: How close are declared prices to true values?
    avg_price_error: float = 0.0          # Mean |declared - true| / true
    price_error_std: float = 0.0          # Standard deviation

    # Allocative efficiency: Are assets with highest-value users?
    allocative_efficiency: float = 0.0     # % of optimal allocation achieved
    misallocated_assets: int = 0           # Assets not with highest-value user

    # Price discovery
    price_discovery_speed: float = 0.0     # Turns for prices to converge to true
    information_incorporation: float = 0.0 # How much new info moves prices

    # Transaction efficiency
    total_trades: int = 0
    beneficial_trades: int = 0             # Trades that increased total welfare
    harmful_trades: int = 0                # Trades that decreased welfare
    deadweight_loss: int = 0               # Value lost from missed trades

    # Surplus distribution
    total_surplus_generated: int = 0
    surplus_to_informed: int = 0
    surplus_to_uninformed: int = 0
    surplus_to_market: int = 0             # Fees, etc.

    # Bid-ask spread (if applicable)
    avg_spread: float = 0.0

    def efficiency_score(self) -> float:
        """
        Composite efficiency score (0-1).

        Weights:
        - Allocative efficiency: 40%
        - Price accuracy: 30%
        - Transaction efficiency: 30%
        """
        price_accuracy = max(0, 1 - self.avg_price_error)
        trade_efficiency = (
            self.beneficial_trades / max(1, self.total_trades)
        )

        return (
            0.4 * self.allocative_efficiency +
            0.3 * price_accuracy +
            0.3 * trade_efficiency
        )


def calculate_market_efficiency(
    market: Market,
    agents: Dict[str, Tuple[Holon, Any, bool]],  # key -> (holon, strategy, is_informed)
) -> MarketEfficiencyMetrics:
    """
    Calculate comprehensive market efficiency metrics.
    """
    metrics = MarketEfficiencyMetrics()

    # Price accuracy
    price_errors = []
    for asset in market.assets.values():
        if asset.true_value > 0:
            error = abs(asset.declared_value - asset.true_value) / asset.true_value
            price_errors.append(error)

    if price_errors:
        metrics.avg_price_error = sum(price_errors) / len(price_errors)
        mean = metrics.avg_price_error
        metrics.price_error_std = math.sqrt(
            sum((e - mean) ** 2 for e in price_errors) / len(price_errors)
        )

    # Allocative efficiency
    # An asset is optimally allocated if owner values it highest
    # (Simplified: assume all agents value assets equally, so current owner is fine)
    metrics.allocative_efficiency = 1.0 - metrics.avg_price_error

    # Transaction analysis
    metrics.total_trades = len(market.trades)
    for trade in market.trades:
        surplus = trade.get("surplus", 0)
        if surplus > 0:
            metrics.beneficial_trades += 1
            metrics.total_surplus_generated += surplus
            if trade.get("informed_trade"):
                metrics.surplus_to_informed += surplus
            else:
                metrics.surplus_to_uninformed += surplus
        elif surplus < 0:
            metrics.harmful_trades += 1

    return metrics


# =============================================================================
# COOPERATIVE GUILD / ENCLAVE
# =============================================================================

@dataclass
class InformationGuild:
    """
    Cooperative information-sharing organization.

    Members pool surveillance capabilities and share information.
    Competes with legacy information brokers through collective intelligence.

    Key dynamics:
    - Membership cost: stake/fee to join
    - Information sharing: members contribute and receive
    - Governance: how decisions are made
    - Trust: reputation within guild
    """

    guild_id: str
    name: str

    # Membership
    members: Set[str] = field(default_factory=set)  # Holon IDs
    membership_stake: int = 100                      # Required stake to join

    # Shared information pool
    shared_info: Dict[str, InformationPacket] = field(default_factory=dict)
    contribution_count: Dict[str, int] = field(default_factory=dict)  # By member

    # Collective surveillance capability
    collective_coverage: float = 0.0
    collective_fidelity: float = 0.0

    # Economics
    pool_balance: int = 0
    surplus_sharing: str = "proportional"  # "equal", "proportional", "contribution"

    def add_member(self, holon_id: HolonId, stake: int) -> bool:
        """Add a member to the guild."""
        if stake < self.membership_stake:
            return False

        key = str(holon_id.value)
        self.members.add(key)
        self.pool_balance += stake
        self.contribution_count[key] = 0
        self._update_collective_capability()
        return True

    def contribute_info(self, contributor_id: HolonId, packet: InformationPacket):
        """Contribute information to the shared pool."""
        key = str(contributor_id.value)
        if key not in self.members:
            return

        # Store with deduplication
        info_key = f"{packet.target_id.value}_{packet.info_type.value}"

        # Keep fresher information
        if info_key in self.shared_info:
            existing = self.shared_info[info_key]
            if packet.timestamp <= existing.timestamp:
                return  # Existing is fresher

        self.shared_info[info_key] = packet
        self.contribution_count[key] = self.contribution_count.get(key, 0) + 1

    def get_shared_info(self, requester_id: HolonId) -> List[InformationPacket]:
        """Get all shared information for a guild member."""
        key = str(requester_id.value)
        if key not in self.members:
            return []

        return list(self.shared_info.values())

    def distribute_surplus(self, total_surplus: int) -> Dict[str, int]:
        """Distribute trading surplus to members."""
        if not self.members:
            return {}

        distribution = {}

        if self.surplus_sharing == "equal":
            per_member = total_surplus // len(self.members)
            for member in self.members:
                distribution[member] = per_member

        elif self.surplus_sharing == "proportional":
            # Proportional to stake (simplified: equal for now)
            per_member = total_surplus // len(self.members)
            for member in self.members:
                distribution[member] = per_member

        elif self.surplus_sharing == "contribution":
            # Proportional to information contributions
            total_contributions = sum(self.contribution_count.values())
            if total_contributions == 0:
                per_member = total_surplus // len(self.members)
                for member in self.members:
                    distribution[member] = per_member
            else:
                for member in self.members:
                    contrib = self.contribution_count.get(member, 0)
                    distribution[member] = int(total_surplus * contrib / total_contributions)

        return distribution

    def _update_collective_capability(self):
        """Update collective surveillance capability based on membership."""
        # More members = more coverage (with diminishing returns)
        n = len(self.members)
        self.collective_coverage = min(0.95, 1 - (0.5 ** (n / 5)))  # Approaches 95%

        # Collective verification improves fidelity
        self.collective_fidelity = min(0.98, 0.5 + 0.1 * math.log(n + 1))


class GuildMember(AgentStrategy):
    """
    Agent that participates in an information-sharing guild.

    Strategy:
    1. Share discovered information with guild
    2. Use guild's collective intelligence for trading
    3. Contribute to guild's collective surveillance
    """

    name = "guild_member"

    def __init__(
        self,
        guild: InformationGuild,
        personal_surveillance: Optional[SurveillanceCapability] = None,
        contribution_rate: float = 0.8,  # How often to share discovered info
    ):
        self.guild = guild
        self.personal_surveillance = personal_surveillance or SurveillanceCapability(
            coverage=0.1,
            base_fidelity=0.7,
        )
        self.contribution_rate = contribution_rate
        self.personal_info: Dict[str, InformationPacket] = {}
        self.total_surplus: int = 0
        self.trades_made: int = 0

    def surveil_and_share(
        self,
        holon: Holon,
        targets: List[Holon],
        turn: int,
    ) -> List[InformationPacket]:
        """Surveil targets and optionally share with guild."""
        packets = []

        for target in targets:
            if not self.personal_surveillance.can_surveil(
                target.holon_id,
                [t.holon_id for t in targets]
            ):
                continue

            for info_type in self.personal_surveillance.visible_info_types:
                if info_type == InformationType.PRIVATE_BALANCE:
                    true_value = target._private_balance
                elif info_type == InformationType.VALUATION:
                    true_value = target.vault + target._private_balance
                else:
                    continue

                fidelity = self.personal_surveillance.get_fidelity(0)
                noise = random.gauss(0, (1 - fidelity) * abs(true_value) * 0.5)
                observed_value = true_value + noise

                packet = InformationPacket(
                    target_id=target.holon_id,
                    info_type=info_type,
                    true_value=true_value,
                    observed_value=observed_value,
                    fidelity=fidelity,
                    timestamp=turn,
                )
                packets.append(packet)

                # Share with guild
                if random.random() < self.contribution_rate:
                    self.guild.contribute_info(holon.holon_id, packet)

        return packets

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
            self.surveil_and_share(holon, context["all_holons"], turn)

        # Get guild's shared information
        all_info = self.guild.get_shared_info(holon.holon_id)

        # Look for trading opportunities
        if "market" in context and random.random() < 0.3:
            market: Market = context["market"]
            opportunities = market.get_undervalued_assets(all_info, min_surplus_ratio=0.15)

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
        # Prefer guild members
        return str(partner_id.value) in self.guild.members or random.random() < 0.5


# =============================================================================
# LLM-POWERED AGENTS
# =============================================================================

class LLMAgent(AgentStrategy):
    """
    Agent powered by actual LLM reasoning.

    Uses Claude/GPT to:
    1. Analyze market state
    2. Identify strategic opportunities
    3. Reason about other agents' likely behavior
    4. Make trading decisions
    """

    name = "llm_agent"

    def __init__(
        self,
        model: str = "claude-3-haiku-20240307",  # Fast, cheap for simulations
        surveillance: Optional[SurveillanceCapability] = None,
        system_prompt: Optional[str] = None,
    ):
        self.model = model
        self.surveillance = surveillance or SurveillanceCapability(
            coverage=0.3,
            base_fidelity=0.8,
        )
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.info_cache: Dict[str, InformationPacket] = {}
        self.total_surplus: int = 0
        self.trades_made: int = 0
        self.reasoning_log: List[str] = []

        # Check for API key
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.enabled = self.api_key is not None

    def _default_system_prompt(self) -> str:
        return """You are an economic agent in a Harberger tax market simulation.

Your goal is to maximize your wealth through strategic trading.

Key rules:
1. Assets have TRUE values and DECLARED values
2. Under Harberger rules, anyone can buy an asset at its declared price
3. If you know an asset's true value > declared value, buying it profits you
4. Information advantage is key - you can see some other agents' private state

When given market state, respond with a JSON action:
{"action": "buy", "asset_id": "xxx", "reasoning": "..."}
or
{"action": "hold", "reasoning": "..."}

Be strategic. Consider what others might know and do."""

    def _call_llm(self, prompt: str) -> Optional[str]:
        """Call the LLM API."""
        if not self.enabled:
            return None

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model=self.model,
                max_tokens=500,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text
        except Exception as e:
            self.reasoning_log.append(f"LLM error: {e}")
            return None

    def surveil(self, targets: List[Holon], turn: int) -> List[InformationPacket]:
        """Gather information on targets."""
        packets = []

        for target in targets:
            if not self.surveillance.can_surveil(
                target.holon_id,
                [t.holon_id for t in targets]
            ):
                continue

            for info_type in self.surveillance.visible_info_types:
                if info_type == InformationType.VALUATION:
                    true_value = target.vault + target._private_balance
                    fidelity = self.surveillance.get_fidelity(0)
                    noise = random.gauss(0, (1 - fidelity) * abs(true_value) * 0.3)

                    packet = InformationPacket(
                        target_id=target.holon_id,
                        info_type=info_type,
                        true_value=true_value,
                        observed_value=true_value + noise,
                        fidelity=fidelity,
                        timestamp=turn,
                    )
                    packets.append(packet)
                    self.info_cache[f"{target.holon_id.value}_{info_type.value}"] = packet

        return packets

    def _build_market_prompt(
        self,
        holon: Holon,
        market: Market,
        turn: int,
    ) -> str:
        """Build prompt describing market state for LLM."""
        prompt = f"""Turn {turn}. Your wealth: {holon.vault}

Available assets for purchase (Harberger - you can force buy at declared price):
"""

        for asset_id, asset in list(market.assets.items())[:10]:  # Limit for context
            # Check if we have info on this asset
            info_key = f"{asset.owner_id.value}_{InformationType.VALUATION.value}"
            estimated_true = None
            if info_key in self.info_cache:
                packet = self.info_cache[info_key]
                estimated_true = packet.observed_value

            prompt += f"\n- Asset {asset_id[:8]}: declared=${asset.declared_value}"
            if estimated_true:
                prompt += f", estimated true value=${estimated_true:.0f}"
                if estimated_true > asset.declared_value:
                    prompt += f" (UNDERVALUED by ${estimated_true - asset.declared_value:.0f})"

        prompt += "\n\nWhat action do you take? Respond with JSON."

        return prompt

    def decide_action(
        self,
        holon: Holon,
        enclave: Any,
        ledger: ReputationLedger,
        turn: int,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        # Surveil
        if "all_holons" in context:
            self.surveil(context["all_holons"], turn)

        # If LLM not enabled, fall back to rule-based
        if not self.enabled:
            return self._fallback_decision(holon, context, turn)

        # Build prompt and call LLM
        if "market" in context:
            market: Market = context["market"]
            prompt = self._build_market_prompt(holon, market, turn)

            response = self._call_llm(prompt)
            if response:
                self.reasoning_log.append(f"Turn {turn}: {response[:200]}")

                try:
                    # Parse JSON response
                    # Handle markdown code blocks
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0]
                    elif "```" in response:
                        response = response.split("```")[1].split("```")[0]

                    decision = json.loads(response.strip())

                    if decision.get("action") == "buy" and "asset_id" in decision:
                        # Find matching asset
                        for asset_id in market.assets:
                            if asset_id.startswith(decision["asset_id"][:8]):
                                return "harberger_buy", {"asset_id": asset_id}
                except (json.JSONDecodeError, KeyError) as e:
                    self.reasoning_log.append(f"Parse error: {e}")

        return "idle", {}

    def _fallback_decision(
        self,
        holon: Holon,
        context: Dict[str, Any],
        turn: int,
    ) -> Tuple[str, Dict[str, Any]]:
        """Fallback to rule-based when LLM not available."""
        if "market" not in context:
            return "idle", {}

        market: Market = context["market"]
        packets = list(self.info_cache.values())
        opportunities = market.get_undervalued_assets(packets, min_surplus_ratio=0.2)

        if opportunities and random.random() < 0.4:
            best_asset, expected_surplus = opportunities[0]
            return "harberger_buy", {"asset_id": best_asset}

        return "idle", {}

    def would_accept_partner(
        self,
        partner_id: HolonId,
        ledger: ReputationLedger,
    ) -> bool:
        return True


# =============================================================================
# ENHANCED SIMULATION WITH EFFICIENCY TRACKING
# =============================================================================

@dataclass
class EnhancedSimConfig:
    """Configuration for enhanced simulation with guilds and LLM agents."""

    # Agent composition
    num_legacy_informed: int = 3      # Legacy information brokers
    num_guild_members: int = 15       # Cooperative guild members
    num_llm_agents: int = 5           # LLM-powered agents
    num_blind: int = 27               # Uninformed traders

    # Guild settings
    num_guilds: int = 2
    guild_stake: int = 100

    # Legacy advantage
    legacy_coverage: float = 0.9
    legacy_fidelity: float = 0.8

    # Market
    initial_wealth: int = 1000
    assets_per_agent: int = 2
    valuation_variance: float = 0.3

    # Erosion
    erosion_mechanisms: List[str] = field(default_factory=list)

    # Simulation
    turns: int = 100

    # LLM
    use_real_llm: bool = True
    llm_model: str = "claude-3-haiku-20240307"


@dataclass
class EnhancedSimMetrics:
    """Comprehensive metrics including efficiency."""

    turns: List[int] = field(default_factory=list)

    # By agent type
    legacy_wealth: List[float] = field(default_factory=list)
    guild_wealth: List[float] = field(default_factory=list)
    llm_wealth: List[float] = field(default_factory=list)
    blind_wealth: List[float] = field(default_factory=list)

    # Efficiency over time
    efficiency_scores: List[float] = field(default_factory=list)
    price_errors: List[float] = field(default_factory=list)
    allocative_efficiency: List[float] = field(default_factory=list)

    # Guild metrics
    guild_total_contributions: int = 0
    guild_surplus_shared: int = 0

    # LLM metrics
    llm_decisions_made: int = 0
    llm_profitable_trades: int = 0

    # Summary
    final_efficiency: Optional[MarketEfficiencyMetrics] = None

    # Method tracking
    method: str = "rule_based"  # or "llm_powered"
    llm_model_used: Optional[str] = None
    llm_calls_made: int = 0


class EnhancedSimulation:
    """
    Enhanced simulation with:
    - Multiple agent types (legacy, guild, LLM, blind)
    - Market efficiency tracking
    - Guild dynamics
    - LLM reasoning
    """

    def __init__(self, config: EnhancedSimConfig):
        self.config = config
        self.market = Market()
        self.guilds: List[InformationGuild] = []
        self.agents: Dict[str, Tuple[Holon, AgentStrategy, str]] = {}  # key -> (holon, strategy, type)
        self.metrics = EnhancedSimMetrics()
        self.turn = 0
        self.erosion_mechanisms = []

    def setup(self):
        """Initialize simulation."""
        # Track method
        if self.config.use_real_llm and os.environ.get("ANTHROPIC_API_KEY"):
            self.metrics.method = "llm_powered"
            self.metrics.llm_model_used = self.config.llm_model
        else:
            self.metrics.method = "rule_based"

        # Create guilds
        for i in range(self.config.num_guilds):
            guild = InformationGuild(
                guild_id=f"guild_{i}",
                name=f"Information Cooperative {i+1}",
                membership_stake=self.config.guild_stake,
            )
            self.guilds.append(guild)

        # Create legacy informed traders
        legacy_surv = LegacyAdvantage(
            coverage=self.config.legacy_coverage,
            base_fidelity=self.config.legacy_fidelity,
        )
        for i in range(self.config.num_legacy_informed):
            holon = create_holon(
                initial_balance=self.config.initial_wealth,
                valuation=self.config.initial_wealth,
            )
            strategy = InformedTrader(surveillance=legacy_surv, aggression=0.5)
            self._register_agent(holon, strategy, "legacy")

        # Create guild members (distributed across guilds)
        for i in range(self.config.num_guild_members):
            holon = create_holon(
                initial_balance=self.config.initial_wealth,
                valuation=self.config.initial_wealth,
            )
            guild = self.guilds[i % len(self.guilds)]
            guild.add_member(holon.holon_id, self.config.guild_stake)
            strategy = GuildMember(guild=guild, contribution_rate=0.8)
            self._register_agent(holon, strategy, "guild")

        # Create LLM agents
        for i in range(self.config.num_llm_agents):
            holon = create_holon(
                initial_balance=self.config.initial_wealth,
                valuation=self.config.initial_wealth,
            )
            strategy = LLMAgent(
                model=self.config.llm_model,
                surveillance=SurveillanceCapability(coverage=0.4, base_fidelity=0.85),
            )
            self._register_agent(holon, strategy, "llm")

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
        for _ in range(self.config.assets_per_agent):
            true_value = self.config.initial_wealth // self.config.assets_per_agent
            variance = random.uniform(
                -self.config.valuation_variance,
                self.config.valuation_variance
            )
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
                    buyer_knows_true_value=(agent_type in ["legacy", "guild", "llm"]),
                )
                if trade:
                    surplus = trade["surplus"]
                    if isinstance(strategy, (InformedTrader, GuildMember, LLMAgent)):
                        strategy.total_surplus += surplus
                        strategy.trades_made += 1
                    if isinstance(strategy, LLMAgent):
                        self.metrics.llm_decisions_made += 1
                        if surplus > 0:
                            self.metrics.llm_profitable_trades += 1

        # Record metrics
        self._record_metrics()

    def _record_metrics(self):
        """Record metrics for this turn."""
        self.metrics.turns.append(self.turn)

        # Calculate wealth by type
        type_wealth = {"legacy": [], "guild": [], "llm": [], "blind": []}

        for key, (holon, strategy, agent_type) in self.agents.items():
            wealth = holon.vault + self.market.total_surplus_by_agent.get(key, 0)
            type_wealth[agent_type].append(wealth)

        self.metrics.legacy_wealth.append(sum(type_wealth["legacy"]))
        self.metrics.guild_wealth.append(sum(type_wealth["guild"]))
        self.metrics.llm_wealth.append(sum(type_wealth["llm"]))
        self.metrics.blind_wealth.append(sum(type_wealth["blind"]))

        # Calculate efficiency
        efficiency = calculate_market_efficiency(self.market, self.agents)
        self.metrics.efficiency_scores.append(efficiency.efficiency_score())
        self.metrics.price_errors.append(efficiency.avg_price_error)
        self.metrics.allocative_efficiency.append(efficiency.allocative_efficiency)
        self.metrics.final_efficiency = efficiency

    def run(self, turns: Optional[int] = None) -> EnhancedSimMetrics:
        """Run full simulation."""
        if not self.agents:
            self.setup()

        for _ in range(turns or self.config.turns):
            self.run_turn()

        return self.metrics

    def summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary."""
        m = self.metrics

        # Calculate per-agent averages
        n_legacy = self.config.num_legacy_informed or 1
        n_guild = self.config.num_guild_members or 1
        n_llm = self.config.num_llm_agents or 1
        n_blind = self.config.num_blind or 1

        avg_legacy = m.legacy_wealth[-1] / n_legacy if m.legacy_wealth else 0
        avg_guild = m.guild_wealth[-1] / n_guild if m.guild_wealth else 0
        avg_llm = m.llm_wealth[-1] / n_llm if m.llm_wealth else 0
        avg_blind = m.blind_wealth[-1] / n_blind if m.blind_wealth else 0

        return {
            # Method
            "method": m.method,
            "llm_model": m.llm_model_used,
            "llm_calls": m.llm_decisions_made,

            # Turns
            "turns_run": self.turn,

            # Agent counts
            "num_legacy": n_legacy,
            "num_guild": n_guild,
            "num_llm": n_llm,
            "num_blind": n_blind,

            # Average wealth by type
            "avg_legacy_wealth": avg_legacy,
            "avg_guild_wealth": avg_guild,
            "avg_llm_wealth": avg_llm,
            "avg_blind_wealth": avg_blind,

            # Relative advantages
            "legacy_vs_blind": avg_legacy / avg_blind if avg_blind > 0 else float('inf'),
            "guild_vs_blind": avg_guild / avg_blind if avg_blind > 0 else float('inf'),
            "llm_vs_blind": avg_llm / avg_blind if avg_blind > 0 else float('inf'),
            "guild_vs_legacy": avg_guild / avg_legacy if avg_legacy > 0 else float('inf'),

            # Efficiency
            "final_efficiency_score": m.efficiency_scores[-1] if m.efficiency_scores else 0,
            "avg_price_error": m.price_errors[-1] if m.price_errors else 0,
            "allocative_efficiency": m.allocative_efficiency[-1] if m.allocative_efficiency else 0,

            # Efficiency trajectory
            "initial_efficiency": m.efficiency_scores[0] if m.efficiency_scores else 0,
            "efficiency_change": (
                m.efficiency_scores[-1] - m.efficiency_scores[0]
            ) if len(m.efficiency_scores) > 1 else 0,

            # LLM performance
            "llm_profitable_trade_rate": (
                m.llm_profitable_trades / m.llm_decisions_made
                if m.llm_decisions_made > 0 else 0
            ),

            # Trading
            "total_trades": len(self.market.trades),
            "total_surplus_generated": m.final_efficiency.total_surplus_generated if m.final_efficiency else 0,
        }


# =============================================================================
# FACTORY
# =============================================================================

def create_enhanced_sim(
    num_legacy: int = 3,
    num_guild: int = 15,
    num_llm: int = 5,
    num_blind: int = 27,
    use_llm: bool = True,
    erosion: List[str] = None,
    turns: int = 100,
) -> EnhancedSimulation:
    """Create an enhanced simulation."""
    config = EnhancedSimConfig(
        num_legacy_informed=num_legacy,
        num_guild_members=num_guild,
        num_llm_agents=num_llm,
        num_blind=num_blind,
        use_real_llm=use_llm,
        erosion_mechanisms=erosion or [],
        turns=turns,
    )
    return EnhancedSimulation(config)
