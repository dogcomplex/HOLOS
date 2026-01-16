"""
Standard Monopoly Board Configuration (40 tiles)
Each tile has: id, name, type, color_group, face_value, rent_base
"""

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class TileConfig:
    id: int
    name: str
    tile_type: str  # go, property, railroad, utility, tax, chance, chest, jail, free_parking, go_to_jail
    color_group: Optional[str] = None
    face_value: int = 0
    rent_base: int = 0  # Base rent (before Harberger modification)
    house_cost: int = 0

# Standard Monopoly Board (US Edition)
BOARD_TILES: List[TileConfig] = [
    # Side 1: GO to Jail/Visiting
    TileConfig(0, "GO", "go"),
    TileConfig(1, "Mediterranean Avenue", "property", "brown", 60, 2, 50),
    TileConfig(2, "Community Chest", "chest"),
    TileConfig(3, "Baltic Avenue", "property", "brown", 60, 4, 50),
    TileConfig(4, "Income Tax", "tax", face_value=200),
    TileConfig(5, "Reading Railroad", "railroad", face_value=200),
    TileConfig(6, "Oriental Avenue", "property", "light_blue", 100, 6, 50),
    TileConfig(7, "Chance", "chance"),
    TileConfig(8, "Vermont Avenue", "property", "light_blue", 100, 6, 50),
    TileConfig(9, "Connecticut Avenue", "property", "light_blue", 120, 8, 50),

    # Side 2: Jail to Free Parking
    TileConfig(10, "Jail / Just Visiting", "jail"),
    TileConfig(11, "St. Charles Place", "property", "pink", 140, 10, 100),
    TileConfig(12, "Electric Company", "utility", face_value=150),
    TileConfig(13, "States Avenue", "property", "pink", 140, 10, 100),
    TileConfig(14, "Virginia Avenue", "property", "pink", 160, 12, 100),
    TileConfig(15, "Pennsylvania Railroad", "railroad", face_value=200),
    TileConfig(16, "St. James Place", "property", "orange", 180, 14, 100),
    TileConfig(17, "Community Chest", "chest"),
    TileConfig(18, "Tennessee Avenue", "property", "orange", 180, 14, 100),
    TileConfig(19, "New York Avenue", "property", "orange", 200, 16, 100),

    # Side 3: Free Parking to Go To Jail
    TileConfig(20, "Free Parking", "free_parking"),
    TileConfig(21, "Kentucky Avenue", "property", "red", 220, 18, 150),
    TileConfig(22, "Chance", "chance"),
    TileConfig(23, "Indiana Avenue", "property", "red", 220, 18, 150),
    TileConfig(24, "Illinois Avenue", "property", "red", 240, 20, 150),
    TileConfig(25, "B&O Railroad", "railroad", face_value=200),
    TileConfig(26, "Atlantic Avenue", "property", "yellow", 260, 22, 150),
    TileConfig(27, "Ventnor Avenue", "property", "yellow", 260, 22, 150),
    TileConfig(28, "Water Works", "utility", face_value=150),
    TileConfig(29, "Marvin Gardens", "property", "yellow", 280, 24, 150),

    # Side 4: Go To Jail to GO
    TileConfig(30, "Go To Jail", "go_to_jail"),
    TileConfig(31, "Pacific Avenue", "property", "green", 300, 26, 200),
    TileConfig(32, "North Carolina Avenue", "property", "green", 300, 26, 200),
    TileConfig(33, "Community Chest", "chest"),
    TileConfig(34, "Pennsylvania Avenue", "property", "green", 320, 28, 200),
    TileConfig(35, "Short Line Railroad", "railroad", face_value=200),
    TileConfig(36, "Chance", "chance"),
    TileConfig(37, "Park Place", "property", "blue", 350, 35, 200),
    TileConfig(38, "Luxury Tax", "tax", face_value=100),
    TileConfig(39, "Boardwalk", "property", "blue", 400, 50, 200),
]

# Color groups and their properties
COLOR_GROUPS = {
    "brown": [1, 3],
    "light_blue": [6, 8, 9],
    "pink": [11, 13, 14],
    "orange": [16, 18, 19],
    "red": [21, 23, 24],
    "yellow": [26, 27, 29],
    "green": [31, 32, 34],
    "blue": [37, 39],
}

# Railroads
RAILROADS = [5, 15, 25, 35]

# Utilities
UTILITIES = [12, 28]

# Special tiles
CHANCE_TILES = [7, 22, 36]
CHEST_TILES = [2, 17, 33]

def get_tile(tile_id: int) -> TileConfig:
    """Get tile configuration by ID."""
    return BOARD_TILES[tile_id]

def get_properties_in_group(color: str) -> List[int]:
    """Get all tile IDs in a color group."""
    return COLOR_GROUPS.get(color, [])

def is_property(tile_id: int) -> bool:
    """Check if tile is a purchasable property."""
    return BOARD_TILES[tile_id].tile_type == "property"

def is_railroad(tile_id: int) -> bool:
    """Check if tile is a railroad."""
    return tile_id in RAILROADS

def is_utility(tile_id: int) -> bool:
    """Check if tile is a utility."""
    return tile_id in UTILITIES

def is_purchasable(tile_id: int) -> bool:
    """Check if tile can be purchased."""
    tile_type = BOARD_TILES[tile_id].tile_type
    return tile_type in ("property", "railroad", "utility")

def get_house_cost(color: str) -> int:
    """Get house cost for a color group."""
    costs = {
        "brown": 50, "light_blue": 50,
        "pink": 100, "orange": 100,
        "red": 150, "yellow": 150,
        "green": 200, "blue": 200,
    }
    return costs.get(color, 100)
