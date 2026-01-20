"""
Collective Economics: Can Voluntary Mechanisms Erode Wealth Gaps?

The challenge: Design mechanisms that:
1. Whales WANT to join (provides value)
2. Extract wealth from whales over time
3. Resist forking (leaving is worse than staying)
4. Work through pure incentives, not enforcement

Key insight: Network effects + information + liquidity can create
enough value that whales accept some wealth erosion to participate.

Mechanisms to test:
1. Liquidity Premium - Guild markets have better prices
2. Information Markets - Pay to access collective intelligence
3. Reputation Gatekeeping - High-rep traders only deal with members
4. Harberger Commons - Self-assessed values with forced sales
5. Progressive Fees - Transaction fees scale with wealth
6. Exit Costs - Staking with vesting periods
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set, Tuple
from enum import Enum
import random
import math

from holos.kernel import create_holon, HolonId, Holon


class MembershipTier(Enum):
    """Membership tiers with different benefits/costs."""
    OUTSIDER = "outsider"      # No access to guild markets
    BASIC = "basic"            # Basic access, low fees
    FULL = "full"              # Full access, moderate fees
    FOUNDER = "founder"        # Governance rights, higher fees


@dataclass
class CollectiveConfig:
    """Configuration for collective economics simulation."""

    # Population
    num_whales: int = 3           # High-capital players
    num_citizens: int = 50        # Regular players
    whale_capital_mult: float = 10.0  # Whale starting advantage

    # Guild mechanisms
    liquidity_premium: float = 0.15      # Better prices in guild (15% improvement)
    information_value: float = 0.10      # Info advantage from guild membership
    reputation_threshold: float = 0.7    # Min reputation to trade with members

    # Wealth extraction
    membership_fee_rate: float = 0.02    # 2% of wealth per period
    progressive_fee_enabled: bool = True # Scale fees with wealth
    progressive_fee_exp: float = 1.5     # Fee = base * (wealth/avg)^exp

    # Exit costs (fork resistance)
    staking_requirement: float = 0.10    # 10% of wealth staked
    vesting_periods: int = 10            # Periods before stake unlocks
    exit_penalty: float = 0.50           # Lose 50% of stake if leaving early

    # Redistribution
    ubi_enabled: bool = True             # Distribute collected fees as UBI
    quadratic_funding: bool = True       # Democratic matching for proposals

    # Harberger
    harberger_tax_rate: float = 0.05     # 5% of self-assessed value
    harberger_enabled: bool = True

    # Simulation
    turns: int = 200
    initial_wealth: int = 1000


@dataclass
class CollectiveMetrics:
    """Track collective economics outcomes."""

    turns: List[int] = field(default_factory=list)

    # Wealth by group
    whale_wealth: List[float] = field(default_factory=list)
    citizen_wealth: List[float] = field(default_factory=list)

    # Wealth ratio over time
    wealth_ratio: List[float] = field(default_factory=list)  # Whale/Citizen per capita

    # Membership
    whale_membership: List[int] = field(default_factory=list)  # How many whales in guild
    citizen_membership: List[int] = field(default_factory=list)

    # Revenue and redistribution
    fees_collected: List[float] = field(default_factory=list)
    ubi_distributed: List[float] = field(default_factory=list)

    # Fork tracking
    forks_attempted: List[int] = field(default_factory=list)
    forks_successful: List[int] = field(default_factory=list)

    # Earning rates
    whale_earning_rate: List[float] = field(default_factory=list)
    citizen_earning_rate: List[float] = field(default_factory=list)


@dataclass
class Agent:
    """An economic agent in the simulation."""
    id: str
    wealth: float
    is_whale: bool

    # Guild membership
    is_member: bool = False
    tier: MembershipTier = MembershipTier.OUTSIDER
    staked_amount: float = 0.0
    vesting_remaining: int = 0

    # Reputation
    reputation: float = 0.5
    trades_made: int = 0
    successful_trades: int = 0

    # Tracking
    prev_wealth: float = 0.0

    def earning_rate(self) -> float:
        """Calculate current earning rate."""
        return self.wealth - self.prev_wealth


class CollectiveSimulation:
    """
    Simulation of collective economics with voluntary wealth erosion.

    Key question: Can mechanisms be designed such that:
    1. Whales rationally choose to join (value > cost)
    2. Joining extracts wealth over time
    3. Forking is not attractive (network effects too valuable)
    """

    def __init__(self, config: CollectiveConfig):
        self.config = config
        self.agents: Dict[str, Agent] = {}
        self.metrics = CollectiveMetrics()
        self.turn = 0

        # Guild state
        self.guild_pool: float = 0.0  # Collected fees
        self.guild_liquidity: float = 0.0  # Total liquidity in guild markets
        self.guild_info_quality: float = 0.0  # Information value

    def setup(self):
        """Initialize simulation."""
        # Create whales
        whale_wealth = self.config.initial_wealth * self.config.whale_capital_mult
        for i in range(self.config.num_whales):
            agent = Agent(
                id=f"whale_{i}",
                wealth=whale_wealth,
                is_whale=True,
                prev_wealth=whale_wealth,
            )
            self.agents[agent.id] = agent

        # Create citizens
        for i in range(self.config.num_citizens):
            agent = Agent(
                id=f"citizen_{i}",
                wealth=self.config.initial_wealth,
                is_whale=False,
                prev_wealth=self.config.initial_wealth,
            )
            self.agents[agent.id] = agent

        # Citizens start as guild members
        for agent in self.agents.values():
            if not agent.is_whale:
                self._join_guild(agent)

    def _join_guild(self, agent: Agent):
        """Agent joins the guild."""
        stake = agent.wealth * self.config.staking_requirement
        agent.staked_amount = stake
        agent.wealth -= stake
        agent.is_member = True
        agent.tier = MembershipTier.FULL
        agent.vesting_remaining = self.config.vesting_periods

        # Add to guild liquidity
        self.guild_liquidity += agent.wealth * 0.5

    def _leave_guild(self, agent: Agent) -> float:
        """Agent leaves guild. Returns penalty paid."""
        penalty = 0.0

        if agent.vesting_remaining > 0:
            # Early exit - lose portion of stake
            penalty = agent.staked_amount * self.config.exit_penalty
            agent.wealth += agent.staked_amount - penalty
            self.guild_pool += penalty  # Penalty goes to pool
        else:
            # Vested - get full stake back
            agent.wealth += agent.staked_amount

        agent.staked_amount = 0
        agent.is_member = False
        agent.tier = MembershipTier.OUTSIDER

        # Remove from guild liquidity
        self.guild_liquidity = max(0, self.guild_liquidity - agent.wealth * 0.3)

        return penalty

    def _calculate_membership_fee(self, agent: Agent) -> float:
        """Calculate membership fee for this period."""
        base_fee = agent.wealth * self.config.membership_fee_rate

        if self.config.progressive_fee_enabled:
            # Progressive: fee scales with wealth relative to average
            avg_wealth = sum(a.wealth for a in self.agents.values()) / len(self.agents)
            if avg_wealth > 0:
                wealth_ratio = agent.wealth / avg_wealth
                multiplier = wealth_ratio ** self.config.progressive_fee_exp
                base_fee *= multiplier

        return base_fee

    def _calculate_guild_value(self, agent: Agent) -> float:
        """
        Calculate value of guild membership for this agent.

        Value comes from:
        1. Liquidity premium (better trade prices)
        2. Information advantage (better decisions)
        3. Network access (can trade with high-rep members)
        """
        if not agent.is_member:
            return 0.0

        # Liquidity value: proportional to guild liquidity
        liquidity_value = self.guild_liquidity * self.config.liquidity_premium * 0.001

        # Information value: proportional to member count
        member_count = sum(1 for a in self.agents.values() if a.is_member)
        info_value = math.log(1 + member_count) * self.config.information_value * agent.wealth * 0.01

        # Network value: access to high-rep traders
        high_rep_traders = sum(1 for a in self.agents.values()
                               if a.is_member and a.reputation > 0.7)
        network_value = high_rep_traders * agent.wealth * 0.005

        return liquidity_value + info_value + network_value

    def _simulate_trade(self, agent: Agent) -> float:
        """
        Simulate a trade for this agent.

        Returns profit/loss from trade.
        """
        # Base trade outcome (random with skill factor)
        base_outcome = random.gauss(0, agent.wealth * 0.05)

        # Guild bonus
        if agent.is_member:
            # Better information = better trades
            info_bonus = self.config.information_value * abs(base_outcome)
            if base_outcome > 0:
                base_outcome += info_bonus
            else:
                base_outcome += info_bonus * 0.5  # Reduces losses too

            # Liquidity premium = less slippage
            liquidity_bonus = self.config.liquidity_premium * abs(base_outcome) * 0.3
            base_outcome += liquidity_bonus

        # Outsider penalty: can't trade with high-rep guild members
        else:
            # Limited market access
            base_outcome *= 0.7  # 30% worse outcomes

        agent.trades_made += 1
        if base_outcome > 0:
            agent.successful_trades += 1

        # Update reputation
        win_rate = agent.successful_trades / max(1, agent.trades_made)
        agent.reputation = 0.9 * agent.reputation + 0.1 * win_rate

        return base_outcome

    def _whale_fork_decision(self, agent: Agent) -> bool:
        """
        Decide if whale should fork (leave guild).

        Fork is attractive if:
        - Cost of membership > value of membership
        - Exit penalty is acceptable
        - Can attract enough followers to new network
        """
        if not agent.is_member:
            return False

        # Calculate costs
        membership_fee = self._calculate_membership_fee(agent)

        # Calculate value
        guild_value = self._calculate_guild_value(agent)

        # Calculate exit cost
        if agent.vesting_remaining > 0:
            exit_cost = agent.staked_amount * self.config.exit_penalty
        else:
            exit_cost = 0

        # Net value of staying
        net_stay_value = guild_value - membership_fee

        # Value of forking: reduced by exit cost, but gain freedom from fees
        # Assume forked network has 30% of value (fewer members)
        fork_value = guild_value * 0.3 - exit_cost

        # Fork if: fork_value > net_stay_value AND rational threshold
        should_fork = fork_value > net_stay_value and fork_value > 0

        # Add some randomness for non-perfect rationality
        if random.random() < 0.1:
            should_fork = not should_fork

        return should_fork

    def _whale_join_decision(self, agent: Agent) -> bool:
        """
        Decide if whale should join guild.

        Join if value > cost (including staking).
        """
        if agent.is_member:
            return False

        # Calculate expected value
        guild_value = self._calculate_guild_value(agent)

        # Note: guild_value is 0 for non-members, need to estimate
        member_count = sum(1 for a in self.agents.values() if a.is_member)
        estimated_value = (
            self.guild_liquidity * self.config.liquidity_premium * 0.001 +
            math.log(1 + member_count) * self.config.information_value * agent.wealth * 0.01 +
            member_count * 0.3 * agent.wealth * 0.005
        )

        # Calculate costs
        staking_cost = agent.wealth * self.config.staking_requirement
        expected_fees = self._calculate_membership_fee(agent)

        # Opportunity cost of stake (could earn elsewhere)
        stake_opportunity = staking_cost * 0.05  # Assume 5% return elsewhere

        # Join if expected value > expected costs
        net_value = estimated_value - expected_fees - stake_opportunity

        return net_value > 0

    def run_turn(self):
        """Execute one turn of the simulation."""
        self.turn += 1

        # Store previous wealth for earning rate calculation
        for agent in self.agents.values():
            agent.prev_wealth = agent.wealth

        fees_collected = 0.0
        forks_attempted = 0
        forks_successful = 0

        # Process each agent
        for agent in self.agents.values():
            # Vesting countdown
            if agent.vesting_remaining > 0:
                agent.vesting_remaining -= 1

            # Membership decisions (whales)
            if agent.is_whale:
                if agent.is_member:
                    # Consider forking
                    if self._whale_fork_decision(agent):
                        forks_attempted += 1
                        penalty = self._leave_guild(agent)
                        if penalty > 0:
                            forks_successful += 1
                else:
                    # Consider joining
                    if self._whale_join_decision(agent):
                        self._join_guild(agent)

            # Collect membership fees
            if agent.is_member:
                fee = self._calculate_membership_fee(agent)
                agent.wealth -= fee
                fees_collected += fee
                self.guild_pool += fee

            # Simulate trading
            trade_result = self._simulate_trade(agent)
            agent.wealth += trade_result

            # Harberger tax (if enabled)
            if self.config.harberger_enabled and agent.is_member:
                # Tax on self-assessed value (simplified: use actual wealth)
                harberger_tax = agent.wealth * self.config.harberger_tax_rate
                agent.wealth -= harberger_tax
                self.guild_pool += harberger_tax
                fees_collected += harberger_tax

        # Distribute UBI
        ubi_distributed = 0.0
        if self.config.ubi_enabled and self.guild_pool > 0:
            # Distribute 80% of pool as UBI
            ubi_amount = self.guild_pool * 0.8
            self.guild_pool -= ubi_amount

            # Equal distribution to all members
            members = [a for a in self.agents.values() if a.is_member]
            if members:
                per_member = ubi_amount / len(members)
                for agent in members:
                    agent.wealth += per_member
                ubi_distributed = ubi_amount

        # Update guild liquidity based on member wealth
        self.guild_liquidity = sum(a.wealth * 0.3 for a in self.agents.values() if a.is_member)

        # Record metrics
        self._record_metrics(fees_collected, ubi_distributed, forks_attempted, forks_successful)

    def _record_metrics(self, fees: float, ubi: float, forks_att: int, forks_succ: int):
        """Record metrics for this turn."""
        self.metrics.turns.append(self.turn)

        # Wealth by group
        whale_wealth = sum(a.wealth + a.staked_amount for a in self.agents.values() if a.is_whale)
        citizen_wealth = sum(a.wealth + a.staked_amount for a in self.agents.values() if not a.is_whale)

        self.metrics.whale_wealth.append(whale_wealth)
        self.metrics.citizen_wealth.append(citizen_wealth)

        # Wealth ratio (per capita)
        whale_pc = whale_wealth / max(1, self.config.num_whales)
        citizen_pc = citizen_wealth / max(1, self.config.num_citizens)
        ratio = whale_pc / citizen_pc if citizen_pc > 0 else float('inf')
        self.metrics.wealth_ratio.append(ratio)

        # Membership
        whale_members = sum(1 for a in self.agents.values() if a.is_whale and a.is_member)
        citizen_members = sum(1 for a in self.agents.values() if not a.is_whale and a.is_member)
        self.metrics.whale_membership.append(whale_members)
        self.metrics.citizen_membership.append(citizen_members)

        # Finances
        self.metrics.fees_collected.append(fees)
        self.metrics.ubi_distributed.append(ubi)

        # Forks
        self.metrics.forks_attempted.append(forks_att)
        self.metrics.forks_successful.append(forks_succ)

        # Earning rates
        whale_earning = sum(a.earning_rate() for a in self.agents.values() if a.is_whale)
        citizen_earning = sum(a.earning_rate() for a in self.agents.values() if not a.is_whale)
        self.metrics.whale_earning_rate.append(whale_earning / max(1, self.config.num_whales))
        self.metrics.citizen_earning_rate.append(citizen_earning / max(1, self.config.num_citizens))

    def run(self) -> CollectiveMetrics:
        """Run full simulation."""
        self.setup()
        for _ in range(self.config.turns):
            self.run_turn()
        return self.metrics

    def summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        m = self.metrics

        initial_ratio = m.wealth_ratio[0] if m.wealth_ratio else self.config.whale_capital_mult
        final_ratio = m.wealth_ratio[-1] if m.wealth_ratio else initial_ratio

        # Calculate convergence
        converging = final_ratio < initial_ratio
        erosion_rate = (initial_ratio - final_ratio) / initial_ratio if initial_ratio > 0 else 0

        # Whale retention
        final_whale_membership = m.whale_membership[-1] if m.whale_membership else 0
        whale_retention = final_whale_membership / max(1, self.config.num_whales)

        # Total forks
        total_forks = sum(m.forks_successful)

        return {
            "initial_ratio": initial_ratio,
            "final_ratio": final_ratio,
            "converging": converging,
            "erosion_rate": erosion_rate,
            "whale_retention": whale_retention,
            "total_forks": total_forks,
            "total_fees_collected": sum(m.fees_collected),
            "total_ubi_distributed": sum(m.ubi_distributed),
            "final_whale_wealth": m.whale_wealth[-1] if m.whale_wealth else 0,
            "final_citizen_wealth": m.citizen_wealth[-1] if m.citizen_wealth else 0,
        }


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_baseline(turns: int = 200) -> Dict[str, Any]:
    """Test baseline: No mechanisms, just trading."""
    print("\n" + "="*70)
    print("  BASELINE: No Collective Mechanisms")
    print("="*70)

    config = CollectiveConfig(
        num_whales=3,
        num_citizens=50,
        whale_capital_mult=10.0,
        membership_fee_rate=0.0,  # No fees
        progressive_fee_enabled=False,
        harberger_enabled=False,
        ubi_enabled=False,
        turns=turns,
    )

    sim = CollectiveSimulation(config)
    sim.run()
    s = sim.summary()

    print(f"  Initial ratio: {s['initial_ratio']:.1f}x")
    print(f"  Final ratio:   {s['final_ratio']:.1f}x")
    print(f"  Converging:    {s['converging']}")

    return s


def test_progressive_fees(turns: int = 200) -> Dict[str, Any]:
    """Test progressive fees with UBI redistribution."""
    print("\n" + "="*70)
    print("  PROGRESSIVE FEES + UBI")
    print("="*70)

    config = CollectiveConfig(
        num_whales=3,
        num_citizens=50,
        whale_capital_mult=10.0,
        membership_fee_rate=0.03,  # 3% base
        progressive_fee_enabled=True,
        progressive_fee_exp=1.5,
        harberger_enabled=False,
        ubi_enabled=True,
        turns=turns,
    )

    sim = CollectiveSimulation(config)
    sim.run()
    s = sim.summary()

    print(f"  Initial ratio: {s['initial_ratio']:.1f}x")
    print(f"  Final ratio:   {s['final_ratio']:.1f}x")
    print(f"  Erosion rate:  {s['erosion_rate']:.1%}")
    print(f"  Whale retention: {s['whale_retention']:.0%}")
    print(f"  Total forks:   {s['total_forks']}")

    return s


def test_harberger_commons(turns: int = 200) -> Dict[str, Any]:
    """Test Harberger taxation."""
    print("\n" + "="*70)
    print("  HARBERGER COMMONS")
    print("="*70)

    config = CollectiveConfig(
        num_whales=3,
        num_citizens=50,
        whale_capital_mult=10.0,
        membership_fee_rate=0.01,
        progressive_fee_enabled=True,
        harberger_enabled=True,
        harberger_tax_rate=0.07,  # 7% Harberger tax
        ubi_enabled=True,
        turns=turns,
    )

    sim = CollectiveSimulation(config)
    sim.run()
    s = sim.summary()

    print(f"  Initial ratio: {s['initial_ratio']:.1f}x")
    print(f"  Final ratio:   {s['final_ratio']:.1f}x")
    print(f"  Erosion rate:  {s['erosion_rate']:.1%}")
    print(f"  Whale retention: {s['whale_retention']:.0%}")

    return s


def test_high_exit_costs(turns: int = 200) -> Dict[str, Any]:
    """Test high exit costs to prevent forking."""
    print("\n" + "="*70)
    print("  HIGH EXIT COSTS (Fork Resistance)")
    print("="*70)

    config = CollectiveConfig(
        num_whales=3,
        num_citizens=50,
        whale_capital_mult=10.0,
        membership_fee_rate=0.05,  # High fees
        progressive_fee_enabled=True,
        progressive_fee_exp=2.0,  # Very progressive
        staking_requirement=0.20,  # 20% stake
        vesting_periods=20,  # Long vesting
        exit_penalty=0.70,  # 70% penalty
        harberger_enabled=True,
        ubi_enabled=True,
        turns=turns,
    )

    sim = CollectiveSimulation(config)
    sim.run()
    s = sim.summary()

    print(f"  Initial ratio: {s['initial_ratio']:.1f}x")
    print(f"  Final ratio:   {s['final_ratio']:.1f}x")
    print(f"  Erosion rate:  {s['erosion_rate']:.1%}")
    print(f"  Whale retention: {s['whale_retention']:.0%}")
    print(f"  Total forks:   {s['total_forks']}")

    return s


def find_optimal_collective(turns: int = 150) -> Dict[str, Any]:
    """
    Search for optimal collective parameters that:
    1. Erode wealth gap
    2. Keep whales participating
    3. Resist forking
    """
    print("\n" + "="*70)
    print("  OPTIMAL COLLECTIVE SEARCH")
    print("="*70)

    best_result = None
    all_results = []

    configs = [
        {"name": "Low fees", "fee": 0.02, "prog_exp": 1.2, "harb": 0.03, "exit": 0.3},
        {"name": "Moderate fees", "fee": 0.03, "prog_exp": 1.5, "harb": 0.05, "exit": 0.5},
        {"name": "High fees", "fee": 0.05, "prog_exp": 1.8, "harb": 0.07, "exit": 0.6},
        {"name": "Very progressive", "fee": 0.03, "prog_exp": 2.5, "harb": 0.05, "exit": 0.5},
        {"name": "High Harberger", "fee": 0.02, "prog_exp": 1.5, "harb": 0.10, "exit": 0.5},
        {"name": "Network lock-in", "fee": 0.04, "prog_exp": 1.5, "harb": 0.05, "exit": 0.8},
    ]

    for cfg in configs:
        config = CollectiveConfig(
            num_whales=3,
            num_citizens=50,
            whale_capital_mult=10.0,
            membership_fee_rate=cfg["fee"],
            progressive_fee_enabled=True,
            progressive_fee_exp=cfg["prog_exp"],
            harberger_enabled=True,
            harberger_tax_rate=cfg["harb"],
            exit_penalty=cfg["exit"],
            ubi_enabled=True,
            turns=turns,
        )

        sim = CollectiveSimulation(config)
        sim.run()
        s = sim.summary()
        s["name"] = cfg["name"]
        all_results.append(s)

        # Score: maximize erosion while maintaining whale retention
        # Erosion only counts if whales stay!
        score = s["erosion_rate"] * s["whale_retention"]
        s["score"] = score

        if best_result is None or score > best_result.get("score", 0):
            best_result = s

        status = "★" if score > 0.3 else ("◐" if score > 0.1 else "○")
        print(f"  {status} {cfg['name']:20s} | Erosion: {s['erosion_rate']:5.1%} | Retention: {s['whale_retention']:5.0%} | Score: {score:.2f}")

    print("\n" + "-"*70)
    print("  BEST CONFIGURATION:")
    if best_result:
        print(f"    {best_result['name']}")
        print(f"    Erosion rate: {best_result['erosion_rate']:.1%}")
        print(f"    Whale retention: {best_result['whale_retention']:.0%}")
        print(f"    Final ratio: {best_result['final_ratio']:.1f}x (from {best_result['initial_ratio']:.1f}x)")

    return {
        "all_results": all_results,
        "best": best_result,
    }


def test_real_world_collective(turns: int = 200) -> Dict[str, Any]:
    """
    Test with real-world-like parameters.
    Can a global collective erode billionaire advantages?
    """
    print("\n" + "="*70)
    print("  REAL-WORLD COLLECTIVE SIMULATION")
    print("="*70)
    print("""
  Parameters:
  - 3 billionaires (100x capital advantage)
  - 100 coordinated citizens
  - Progressive fees + Harberger tax + UBI
  - High network value (liquidity + information)
    """)

    config = CollectiveConfig(
        num_whales=3,
        num_citizens=100,
        whale_capital_mult=100.0,  # 100x advantage
        liquidity_premium=0.25,     # 25% better prices in guild
        information_value=0.15,     # 15% info advantage
        membership_fee_rate=0.03,
        progressive_fee_enabled=True,
        progressive_fee_exp=2.0,    # Strongly progressive
        harberger_enabled=True,
        harberger_tax_rate=0.07,
        staking_requirement=0.15,
        vesting_periods=15,
        exit_penalty=0.60,
        ubi_enabled=True,
        turns=turns,
    )

    sim = CollectiveSimulation(config)
    sim.run()
    s = sim.summary()

    print(f"  Initial ratio: {s['initial_ratio']:.1f}x")
    print(f"  Final ratio:   {s['final_ratio']:.1f}x")
    print(f"  Erosion rate:  {s['erosion_rate']:.1%}")
    print(f"  Whale retention: {s['whale_retention']:.0%}")
    print(f"  Total forks:   {s['total_forks']}")

    # Track trajectory
    m = sim.metrics
    print(f"\n  Wealth Ratio Trajectory:")
    for i in range(0, len(m.wealth_ratio), 40):
        r = m.wealth_ratio[i]
        bar = "█" * min(50, int(r / 2))
        print(f"    Turn {i:4d}: {bar} {r:.1f}x")

    if s["converging"] and s["whale_retention"] > 0.5:
        print("\n  ★ SUCCESS: Wealth gap eroding while whales stay!")
    elif s["converging"]:
        print("\n  ◐ PARTIAL: Gap eroding but whales leaving")
    else:
        print("\n  ○ FAILURE: Gap not eroding")

    return s
