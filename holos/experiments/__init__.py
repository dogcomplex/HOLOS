"""
HOLOS Experiments - Adversarial Testing & Economic Simulations

This package contains experiments for testing HOLOS mechanisms under
adversarial conditions, validating that invariants self-enforce through
reputation contagion rather than central authority.

Modules:
- adversarial: Test constitutional invariant enforcement under attack
- information_asymmetry: Test wealth inequality from information advantages
- market_efficiency: Test market efficiency vs information distribution
- guild_victory: Test paths for cooperative guilds to overcome legacy advantages
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

from .market_efficiency import (
    # Efficiency metrics
    MarketEfficiencyMetrics,
    calculate_market_efficiency,

    # Cooperative guilds
    InformationGuild,
    GuildMember,

    # LLM agents
    LLMAgent,

    # Enhanced simulation
    EnhancedSimConfig,
    EnhancedSimMetrics,
    EnhancedSimulation,
    create_enhanced_sim,
)

from .guild_victory import (
    # Reputation market
    TradingReputation,
    ReputationMarket,

    # Prediction market
    Prediction,
    PredictionMarket,

    # Counter-surveillance
    CounterSurveillanceGuild,
    CounterSurveillanceAgent,

    # Simulation
    GuildVictoryConfig,
    GuildVictoryMetrics,
    GuildVictorySimulation,

    # Test functions
    test_pure_time_erosion,
    test_counter_surveillance,
    test_all_mechanisms,
    find_victory_conditions,
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

    # === Market Efficiency ===
    # Metrics
    'MarketEfficiencyMetrics',
    'calculate_market_efficiency',

    # Guilds
    'InformationGuild',
    'GuildMember',

    # LLM
    'LLMAgent',

    # Simulation
    'EnhancedSimConfig',
    'EnhancedSimMetrics',
    'EnhancedSimulation',
    'create_enhanced_sim',

    # === Guild Victory ===
    # Reputation market
    'TradingReputation',
    'ReputationMarket',

    # Prediction market
    'Prediction',
    'PredictionMarket',

    # Counter-surveillance
    'CounterSurveillanceGuild',
    'CounterSurveillanceAgent',

    # Simulation
    'GuildVictoryConfig',
    'GuildVictoryMetrics',
    'GuildVictorySimulation',

    # Test functions
    'test_pure_time_erosion',
    'test_counter_surveillance',
    'test_all_mechanisms',
    'find_victory_conditions',
]
