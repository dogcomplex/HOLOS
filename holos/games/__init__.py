"""
HOLOS Games - Game Implementations as Enclaves

Games are specialized Enclaves where Holons interact under specific rules.
HOLOPOLY is the first game adapter, treating Monopoly as a sovereign computing testbed.

Games:
- holopoly_adapter: Bridge HOLOPOLY to HOLOS kernel
- information_wars: Demonstrates information asymmetry dynamics
"""

from .holopoly_adapter import (
    HolopolyEnclave,
    PropertyMantle,
    HolopolyHolon,
    adapt_player_to_holon,
    adapt_property_to_mantle,
)

from .information_wars import (
    # Core game
    InformationWarsGame,
    InformationWarsConfig,
    InformationWarsMetrics,

    # Player types
    PlayerType,
    PlayerProfile,

    # Information types
    InformationType,
    InformationPacket,

    # Guild
    InformationGuild,

    # Cards
    ChanceCard,
    CHANCE_CARDS,
    CHEST_CARDS,

    # Test functions
    run_legacy_dominance_test,
    run_guild_vs_legacy_test,
    run_capital_plus_info_test,

    # Human rules
    print_human_rules,
    HUMAN_RULES,
)

__all__ = [
    # === HOLOPOLY Adapter ===
    'HolopolyEnclave',
    'PropertyMantle',
    'HolopolyHolon',
    'adapt_player_to_holon',
    'adapt_property_to_mantle',

    # === Information Wars ===
    # Core game
    'InformationWarsGame',
    'InformationWarsConfig',
    'InformationWarsMetrics',

    # Player types
    'PlayerType',
    'PlayerProfile',

    # Information types
    'InformationType',
    'InformationPacket',

    # Guild
    'InformationGuild',

    # Cards
    'ChanceCard',
    'CHANCE_CARDS',
    'CHEST_CARDS',

    # Test functions
    'run_legacy_dominance_test',
    'run_guild_vs_legacy_test',
    'run_capital_plus_info_test',

    # Human rules
    'print_human_rules',
    'HUMAN_RULES',
]
