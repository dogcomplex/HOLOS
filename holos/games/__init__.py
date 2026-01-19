"""
HOLOS Games - Game Implementations as Enclaves

Games are specialized Enclaves where Holons interact under specific rules.
HOLOPOLY is the first game adapter, treating Monopoly as a sovereign computing testbed.
"""

from .holopoly_adapter import (
    HolopolyEnclave,
    PropertyMantle,
    HolopolyHolon,
    adapt_player_to_holon,
    adapt_property_to_mantle,
)

__all__ = [
    'HolopolyEnclave',
    'PropertyMantle',
    'HolopolyHolon',
    'adapt_player_to_holon',
    'adapt_property_to_mantle',
]
