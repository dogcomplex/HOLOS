"""
Small Enclave Simulation - Testing the Protocol at 10-100 Scale

This simulates a small enclave to validate:
1. Membership incentives work at small scale
2. Progressive fees extract from wealthy members
3. UBI distributes to all members fairly (flow-through)
4. Liquidity pools provide trading value
5. The enclave can attract new members over time

Aligned with holos/kernel/ naming conventions:
- Enclave: Base group (<100 members)
- Collective: 100+ members
- Kingdom: 1000+ members
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
import random

from .collective_protocol import (
    # Using Enclave as primary, Collective as alias for backward compat
    Enclave, Collective, CollectiveParameters, SovereignIdentity,
    LiquidityPool, calculate_enclave_value, calculate_collective_value,
    WealthBracket, EnclaveScale,
)


@dataclass
class SimulatedAgent:
    """An agent in the simulation."""
    identity: SovereignIdentity
    wealth: float
    is_whale: bool = False

    # State
    is_member: bool = False
    last_ubi: float = 0.0
    last_fee: float = 0.0
    trade_profits: float = 0.0

    @property
    def commitment(self) -> bytes:
        return self.identity.public_commitment


@dataclass
class SmallCollectiveMetrics:
    """Track simulation metrics."""
    turns: List[int] = field(default_factory=list)

    # Membership
    total_members: List[int] = field(default_factory=list)
    whale_members: List[int] = field(default_factory=list)

    # Wealth distribution
    whale_wealth: List[float] = field(default_factory=list)
    citizen_wealth: List[float] = field(default_factory=list)
    wealth_ratio: List[float] = field(default_factory=list)

    # Protocol metrics
    fees_collected: List[float] = field(default_factory=list)
    ubi_distributed: List[float] = field(default_factory=list)
    total_liquidity: List[float] = field(default_factory=list)

    # Value metrics
    collective_value: List[float] = field(default_factory=list)


class SmallCollectiveSimulation:
    """
    Simulate a small enclave (10-100 members).

    Tests whether the protocol creates sufficient value to:
    1. Attract initial members
    2. Keep members participating
    3. Eventually attract whales
    4. Erode wealth gap through progressive fees

    Scale taxonomy:
    - <100 members: Enclave
    - 100-999 members: Collective
    - 1000+ members: Kingdom
    """

    def __init__(
        self,
        num_citizens: int = 50,
        num_whales: int = 3,
        whale_wealth_mult: float = 10.0,
        initial_citizen_wealth: float = 1000.0,
    ):
        self.num_citizens = num_citizens
        self.num_whales = num_whales
        self.whale_wealth_mult = whale_wealth_mult
        self.initial_citizen_wealth = initial_citizen_wealth

        self.enclave: Enclave = None  # Primary reference
        self.agents: Dict[bytes, SimulatedAgent] = {}
        self.metrics = SmallCollectiveMetrics()
        self.turn = 0

    # Backward compatibility alias
    @property
    def collective(self) -> Enclave:
        return self.enclave

    @collective.setter
    def collective(self, value: Enclave):
        self.enclave = value

    def setup(self):
        """Initialize the simulation."""
        # Create enclave with small-scale parameters
        params = CollectiveParameters(
            base_fee_rate=0.03,  # 3% base fee
            progressive_exponent=1.5,
            min_stake=50.0,  # Low barrier for small enclave
            vesting_periods=5,
            early_exit_penalty=0.4,
            ubi_distribution_rate=0.8,
            swap_fee=0.003,
            min_liquidity=500.0,
        )

        self.enclave = Enclave(
            enclave_id="small_enclave_001",
            params=params,
        )

        # Create citizens
        for i in range(self.num_citizens):
            identity = SovereignIdentity()
            agent = SimulatedAgent(
                identity=identity,
                wealth=self.initial_citizen_wealth,
                is_whale=False,
            )
            self.agents[agent.commitment] = agent

        # Create whales
        whale_wealth = self.initial_citizen_wealth * self.whale_wealth_mult
        for i in range(self.num_whales):
            identity = SovereignIdentity()
            agent = SimulatedAgent(
                identity=identity,
                wealth=whale_wealth,
                is_whale=True,
            )
            self.agents[agent.commitment] = agent

        # Citizens join immediately (they have most to gain)
        for commitment, agent in self.agents.items():
            if not agent.is_whale:
                stake = min(agent.wealth * 0.1, 100)  # Stake 10% up to 100
                if self.collective.join(agent.identity, stake):
                    agent.is_member = True
                    agent.wealth -= stake

        # Create initial liquidity pool
        # Some citizens pool resources
        initial_liq_a = 0
        initial_liq_b = 0
        contributors = []

        for commitment, agent in self.agents.items():
            if agent.is_member and random.random() < 0.3:  # 30% contribute
                contrib = agent.wealth * 0.1  # 10% of wealth
                initial_liq_a += contrib
                initial_liq_b += contrib
                agent.wealth -= contrib * 2
                contributors.append(commitment)

        if initial_liq_a > 0:
            self.collective.create_pool("TOKEN_A/TOKEN_B", initial_liq_a, initial_liq_b, contributors[0])

    def run_turn(self):
        """Execute one turn of the simulation."""
        self.turn += 1

        # 1. Whales decide whether to join
        self._whale_membership_decisions()

        # 2. Collect fees from members
        self._collect_fees()

        # 3. Distribute UBI
        self._distribute_ubi()

        # 4. Members trade
        self._simulate_trading()

        # 5. Record metrics
        self._record_metrics()

    def _whale_membership_decisions(self):
        """Whales decide whether to join based on value calculation."""
        value_info = calculate_enclave_value(self.enclave)

        for commitment, agent in self.agents.items():
            if not agent.is_whale:
                continue

            if agent.is_member:
                # Consider leaving
                # Leave if value < cost significantly
                if value_info["net_value"] < -0.1:
                    refund = self.collective.leave(agent.identity)
                    agent.wealth += refund
                    agent.is_member = False
            else:
                # Consider joining
                # Join if value > cost
                if value_info["should_join"]:
                    stake = min(agent.wealth * 0.1, 500)
                    if self.collective.join(agent.identity, stake):
                        agent.is_member = True
                        agent.wealth -= stake

    def _collect_fees(self):
        """Collect progressive fees from members."""
        member_wealth = {
            commitment: agent.wealth
            for commitment, agent in self.agents.items()
            if agent.is_member
        }

        total_fees = self.collective.collect_fees(member_wealth)

        # Deduct fees from members
        for commitment, agent in self.agents.items():
            if not agent.is_member:
                continue

            fee, _ = self.collective.fee_schedule.calculate_fee(agent.wealth)
            agent.wealth -= fee
            agent.last_fee = fee

    def _distribute_ubi(self):
        """Distribute UBI to members."""
        distributions = self.collective.distribute_ubi()

        for commitment, amount in distributions.items():
            if commitment in self.agents:
                self.agents[commitment].wealth += amount
                self.agents[commitment].last_ubi = amount

    def _simulate_trading(self):
        """Simulate trading activity."""
        if "TOKEN_A/TOKEN_B" not in self.collective.liquidity_pools:
            return

        pool = self.collective.liquidity_pools["TOKEN_A/TOKEN_B"]

        for commitment, agent in self.agents.items():
            if not agent.is_member:
                continue

            # Random trading activity
            if random.random() < 0.2:  # 20% chance to trade
                trade_size = agent.wealth * random.uniform(0.01, 0.05)
                input_is_a = random.choice([True, False])

                # Calculate expected output
                output = pool.get_output_amount(trade_size, input_is_a)

                # Execute trade
                actual_output = self.collective.swap(
                    "TOKEN_A/TOKEN_B",
                    trade_size,
                    input_is_a,
                    commitment,
                )

                # For simulation, assume trade was profitable with some variance
                profit = random.gauss(0, trade_size * 0.02)
                agent.wealth += profit
                agent.trade_profits += profit

    def _record_metrics(self):
        """Record metrics for this turn."""
        self.metrics.turns.append(self.turn)

        # Membership
        total_members = self.collective.member_count
        whale_members = sum(1 for c, a in self.agents.items() if a.is_whale and a.is_member)
        self.metrics.total_members.append(total_members)
        self.metrics.whale_members.append(whale_members)

        # Wealth
        whale_wealth = sum(a.wealth for a in self.agents.values() if a.is_whale)
        citizen_wealth = sum(a.wealth for a in self.agents.values() if not a.is_whale)
        self.metrics.whale_wealth.append(whale_wealth)
        self.metrics.citizen_wealth.append(citizen_wealth)

        whale_pc = whale_wealth / max(1, self.num_whales)
        citizen_pc = citizen_wealth / max(1, self.num_citizens)
        ratio = whale_pc / citizen_pc if citizen_pc > 0 else float('inf')
        self.metrics.wealth_ratio.append(ratio)

        # Protocol metrics
        self.metrics.fees_collected.append(self.collective.total_fees_collected)
        self.metrics.ubi_distributed.append(self.collective.total_ubi_distributed)

        total_liq = sum(
            p.token_a_reserve + p.token_b_reserve
            for p in self.collective.liquidity_pools.values()
        )
        self.metrics.total_liquidity.append(total_liq)

        # Value
        value_info = calculate_enclave_value(self.enclave)
        self.metrics.collective_value.append(value_info["total_value"])

    def run(self, turns: int = 100) -> SmallCollectiveMetrics:
        """Run the simulation."""
        self.setup()

        for _ in range(turns):
            self.run_turn()

        return self.metrics

    def summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        m = self.metrics

        return {
            "initial_wealth_ratio": m.wealth_ratio[0] if m.wealth_ratio else self.whale_wealth_mult,
            "final_wealth_ratio": m.wealth_ratio[-1] if m.wealth_ratio else 0,
            "erosion_rate": 1 - (m.wealth_ratio[-1] / m.wealth_ratio[0]) if m.wealth_ratio and m.wealth_ratio[0] > 0 else 0,
            "final_members": m.total_members[-1] if m.total_members else 0,
            "whale_retention": m.whale_members[-1] / max(1, self.num_whales) if m.whale_members else 0,
            "total_fees": m.fees_collected[-1] if m.fees_collected else 0,
            "total_ubi": m.ubi_distributed[-1] if m.ubi_distributed else 0,
            "final_liquidity": m.total_liquidity[-1] if m.total_liquidity else 0,
            "final_value": m.collective_value[-1] if m.collective_value else 0,
        }


def test_small_collective(turns: int = 100) -> Dict[str, Any]:
    """Test a small enclave (backward compat name: collective)."""
    print("\n" + "="*70)
    print("  SMALL ENCLAVE TEST (50 citizens, 3 whales)")
    print("="*70)

    sim = SmallCollectiveSimulation(
        num_citizens=50,
        num_whales=3,
        whale_wealth_mult=10.0,
    )
    sim.run(turns)
    s = sim.summary()

    print(f"\n  Initial wealth ratio: {s['initial_wealth_ratio']:.1f}x")
    print(f"  Final wealth ratio:   {s['final_wealth_ratio']:.1f}x")
    print(f"  Erosion rate:         {s['erosion_rate']:.1%}")
    print(f"  Whale retention:      {s['whale_retention']:.0%}")
    print(f"  Final members:        {s['final_members']}")
    print(f"  Collective value:     {s['final_value']:.2f}")

    return s


def test_scaling(sizes: List[int] = [10, 50, 100, 500]) -> Dict[str, Any]:
    """Test enclave at different scales (Enclave → Collective → Kingdom)."""
    print("\n" + "="*70)
    print("  FRACTAL SCALING TEST (Enclave → Collective → Kingdom)")
    print("="*70)

    results = []

    for size in sizes:
        num_whales = max(1, size // 20)  # 5% whales

        sim = SmallCollectiveSimulation(
            num_citizens=size - num_whales,
            num_whales=num_whales,
            whale_wealth_mult=10.0,
        )
        sim.run(100)
        s = sim.summary()
        s["size"] = size

        results.append(s)

        print(f"\n  Size {size}:")
        print(f"    Wealth ratio: {s['initial_wealth_ratio']:.1f}x → {s['final_wealth_ratio']:.1f}x")
        print(f"    Erosion: {s['erosion_rate']:.1%} | Whales: {s['whale_retention']:.0%}")

    return {"results": results}


if __name__ == "__main__":
    test_small_collective()
    test_scaling()
