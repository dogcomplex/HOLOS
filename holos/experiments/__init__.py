"""
HOLOS Experiments - Adversarial Testing & Economic Simulations

This package contains experiments for testing HOLOS mechanisms under
adversarial conditions, validating that invariants self-enforce through
reputation contagion rather than central authority.
"""

from .adversarial import (
    # Agent strategies
    AgentStrategy,
    HonestAgent,
    SybilFarmer,
    ExitBlocker,
    Colluder,
    GradualInfiltrator,
    FreeRider,

    # Reputation system
    ReputationLedger,
    ViolationType,
    Violation,

    # Simulation
    AdversarialSimulation,
    SimulationConfig,
    SimulationMetrics,

    # Factory
    create_simulation,
)

__all__ = [
    # Strategies
    'AgentStrategy',
    'HonestAgent',
    'SybilFarmer',
    'ExitBlocker',
    'Colluder',
    'GradualInfiltrator',
    'FreeRider',

    # Reputation
    'ReputationLedger',
    'ViolationType',
    'Violation',

    # Simulation
    'AdversarialSimulation',
    'SimulationConfig',
    'SimulationMetrics',

    # Factory
    'create_simulation',
]
