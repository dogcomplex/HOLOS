"""
HOLOS Experiments - Adversarial Testing & Economic Simulations

This package contains experiments for testing HOLOS mechanisms under
adversarial conditions, validating that invariants self-enforce through
reputation contagion rather than central authority.

Modules:
- adversarial: Test constitutional invariant enforcement under attack
- information_asymmetry: Test wealth inequality from information advantages
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

from .information_asymmetry import (
    # Information types
    InformationType,
    InformationPacket,

    # Surveillance capabilities
    SurveillanceCapability,
    LegacyAdvantage,
    ActiveSurveillance,
    InsiderKnowledge,

    # Market
    Asset,
    Market,

    # Agents
    InformedTrader,
    BlindTrader,

    # Metrics
    gini_coefficient,
    herfindahl_index,
    top_n_share,
    InequalityMetrics,

    # Erosion mechanisms
    ErosionMechanism,
    IdentityRotation,
    NoiseInjection,
    ZKShielding,
    PopulationChurn,

    # Simulation
    InfoAsymmetryConfig,
    InfoAsymmetryMetrics,
    InfoAsymmetrySimulation,
    create_info_asymmetry_sim,
)

__all__ = [
    # === Adversarial ===
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
    'create_simulation',

    # === Information Asymmetry ===
    # Information
    'InformationType',
    'InformationPacket',

    # Surveillance
    'SurveillanceCapability',
    'LegacyAdvantage',
    'ActiveSurveillance',
    'InsiderKnowledge',

    # Market
    'Asset',
    'Market',

    # Agents
    'InformedTrader',
    'BlindTrader',

    # Metrics
    'gini_coefficient',
    'herfindahl_index',
    'top_n_share',
    'InequalityMetrics',

    # Erosion
    'ErosionMechanism',
    'IdentityRotation',
    'NoiseInjection',
    'ZKShielding',
    'PopulationChurn',

    # Simulation
    'InfoAsymmetryConfig',
    'InfoAsymmetryMetrics',
    'InfoAsymmetrySimulation',
    'create_info_asymmetry_sim',
]
