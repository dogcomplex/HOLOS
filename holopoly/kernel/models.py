"""
Core data models for HOLO-POLY.
Using dataclasses for simplicity and Pydantic for validation where needed.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import json


class PlayerStatus(Enum):
    ACTIVE = "ACTIVE"
    BANKRUPT = "BANKRUPT"


class GameStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"


class TaxTiming(Enum):
    ON_GO = "on_go"
    PER_TURN = "per_turn"


class ActionType(Enum):
    ROLL = "ROLL"
    BUY_PROPERTY = "BUY_PROPERTY"
    SET_VALUATION = "SET_VALUATION"
    BUILD_HOUSE = "BUILD_HOUSE"
    HARBERGER_BUY = "HARBERGER_BUY"
    PASS = "PASS"
    PAY_RENT = "PAY_RENT"
    PAY_TAX = "PAY_TAX"
    COLLECT_DIVIDEND = "COLLECT_DIVIDEND"


@dataclass
class PropertyId:
    """Unique identifier for a property across multiple boards."""
    board: int
    tile: int

    def __hash__(self):
        return hash((self.board, self.tile))

    def __eq__(self, other):
        if not isinstance(other, PropertyId):
            return False
        return self.board == other.board and self.tile == other.tile

    def to_tuple(self) -> tuple:
        return (self.board, self.tile)


@dataclass
class Property:
    """A property on the board."""
    id: PropertyId
    name: str
    tile_type: str
    color_group: Optional[str]
    face_value: int
    owner_id: Optional[str] = None
    valuation: int = 0
    houses: int = 0
    is_mortgaged: bool = False

    def is_owned(self) -> bool:
        return self.owner_id is not None

    def is_monopoly_property(self) -> bool:
        return self.tile_type == "property"

    def to_dict(self) -> dict:
        return {
            "board": self.id.board,
            "tile": self.id.tile,
            "name": self.name,
            "type": self.tile_type,
            "color_group": self.color_group,
            "face_value": self.face_value,
            "owner_id": self.owner_id,
            "valuation": self.valuation,
            "houses": self.houses,
        }


@dataclass
class Player:
    """A player in the game."""
    id: str
    balance: int
    current_board: int = 0
    position: int = 0  # Tile position (0-39)
    status: PlayerStatus = PlayerStatus.ACTIVE
    archetype: str = "default"
    turns_played: int = 0
    properties: List[PropertyId] = field(default_factory=list)

    def is_active(self) -> bool:
        return self.status == PlayerStatus.ACTIVE

    def is_bankrupt(self) -> bool:
        return self.status == PlayerStatus.BANKRUPT

    def net_worth(self, properties: Dict[PropertyId, Property]) -> int:
        """Calculate total net worth (cash + property valuations)."""
        prop_value = sum(
            properties[pid].valuation
            for pid in self.properties
            if pid in properties
        )
        return self.balance + prop_value

    def total_valuation(self, properties: Dict[PropertyId, Property]) -> int:
        """Total valuation of owned properties (for tax calculation)."""
        return sum(
            properties[pid].valuation
            for pid in self.properties
            if pid in properties
        )

    def to_dict(self, hide_balance: bool = False) -> dict:
        return {
            "id": self.id,
            "balance": "HIDDEN" if hide_balance else self.balance,
            "status": self.status.value,
            "board": self.current_board,
            "position": self.position,
            "archetype": self.archetype,
        }


@dataclass
class Action:
    """An action taken by a player."""
    action_type: ActionType
    player_id: str
    params: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""

    @classmethod
    def from_dict(cls, data: dict, player_id: str) -> "Action":
        """Parse an action from LLM response."""
        action_str = data.get("action", "PASS").upper()
        try:
            action_type = ActionType(action_str)
        except ValueError:
            action_type = ActionType.PASS

        return cls(
            action_type=action_type,
            player_id=player_id,
            params=data.get("params", {}),
            reasoning=data.get("reasoning", ""),
        )

    def to_dict(self) -> dict:
        return {
            "action": self.action_type.value,
            "player_id": self.player_id,
            "params": self.params,
            "reasoning": self.reasoning,
        }


@dataclass
class DiceRoll:
    """Result of rolling two dice."""
    die1: int
    die2: int

    @property
    def total(self) -> int:
        return self.die1 + self.die2

    @property
    def is_doubles(self) -> bool:
        return self.die1 == self.die2

    def to_dict(self) -> dict:
        return {"die1": self.die1, "die2": self.die2, "total": self.total}


@dataclass
class Transaction:
    """A financial transaction in the game."""
    turn: int
    transaction_type: str
    from_id: str  # Player ID, "BANK", or "POT"
    to_id: str
    amount: int
    property_id: Optional[PropertyId] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GameConfig:
    """Game configuration loaded from YAML."""
    game_id: str
    max_turns: int
    num_boards: int
    num_players: int
    starting_balance: int
    archetypes: List[str]

    # Economics
    tax_timing: TaxTiming
    dividend_timing: TaxTiming
    tax_rate: float
    rent_rate: float
    pass_go_salary: int
    avg_circuit_length: int

    # Harberger
    harberger_enabled: bool
    force_buy_enabled: bool
    min_valuation: int

    # LLM
    llm_model: str
    llm_stub_mode: bool
    llm_temperature: float

    # Randomness
    random_seed: Optional[int]

    @classmethod
    def from_yaml(cls, config: dict) -> "GameConfig":
        """Parse configuration from YAML dict."""
        return cls(
            game_id=config.get("game", {}).get("id", "game_001"),
            max_turns=config.get("game", {}).get("max_turns", 200),
            num_boards=config.get("universe", {}).get("num_boards", 1),
            num_players=config.get("players", {}).get("count", 4),
            starting_balance=config.get("players", {}).get("starting_balance", 1500),
            archetypes=config.get("players", {}).get("archetypes", ["Slumlord", "Squatter", "Flipper", "Developer"]),

            tax_timing=TaxTiming(config.get("economics", {}).get("tax_timing", "on_go")),
            dividend_timing=TaxTiming(config.get("economics", {}).get("dividend_timing", "on_go")),
            tax_rate=config.get("economics", {}).get("tax_rate", 0.10),
            rent_rate=config.get("economics", {}).get("rent_rate", 0.10),
            pass_go_salary=config.get("economics", {}).get("pass_go_salary", 200),
            avg_circuit_length=config.get("economics", {}).get("avg_circuit_length", 10),

            harberger_enabled=config.get("harberger", {}).get("enabled", True),
            force_buy_enabled=config.get("harberger", {}).get("force_buy_enabled", True),
            min_valuation=config.get("harberger", {}).get("min_valuation", 1),

            llm_model=config.get("llm", {}).get("model", "gemini-2.0-flash-exp"),
            llm_stub_mode=config.get("llm", {}).get("stub_mode", True),
            llm_temperature=config.get("llm", {}).get("temperature", 0.7),

            random_seed=config.get("randomness", {}).get("seed"),
        )


@dataclass
class GameState:
    """Complete state of a game at a point in time."""
    config: GameConfig
    turn: int
    players: Dict[str, Player]
    properties: Dict[PropertyId, Property]
    community_pot: int
    current_player_id: str
    player_order: List[str]
    status: GameStatus = GameStatus.ACTIVE
    winner_id: Optional[str] = None

    def get_current_player(self) -> Player:
        return self.players[self.current_player_id]

    def get_active_players(self) -> List[Player]:
        return [p for p in self.players.values() if p.is_active()]

    def get_player_properties(self, player_id: str) -> List[Property]:
        return [
            self.properties[pid]
            for pid in self.players[player_id].properties
            if pid in self.properties
        ]

    def to_player_view(self, viewer_id: str) -> dict:
        """Generate the game state view for a specific player (with hidden info)."""
        viewer = self.players[viewer_id]

        # Own info (full visibility)
        own_properties = [
            self.properties[pid].to_dict()
            for pid in viewer.properties
            if pid in self.properties
        ]

        # Opponent info (balance hidden)
        opponents = []
        for pid, player in self.players.items():
            if pid != viewer_id and player.is_active():
                opp_props = [
                    self.properties[propid].to_dict()
                    for propid in player.properties
                    if propid in self.properties
                ]
                opponents.append({
                    "id": player.id,
                    "board": player.current_board,
                    "position": player.position,
                    "balance": "HIDDEN",
                    "status": player.status.value,
                    "portfolio": opp_props,
                })

        # Available actions
        available_actions = self._get_available_actions(viewer_id)

        return {
            "turn": self.turn,
            "timing_mode": {
                "tax": self.config.tax_timing.value,
                "dividend": self.config.dividend_timing.value,
            },
            "me": {
                "id": viewer.id,
                "board": viewer.current_board,
                "position": viewer.position,
                "balance": viewer.balance,
                "portfolio": own_properties,
            },
            "opponents": opponents,
            "community_pot": self.community_pot,
            "available_actions": available_actions,
        }

    def _get_available_actions(self, player_id: str) -> List[str]:
        """Determine what actions are available to a player."""
        actions = ["ROLL", "PASS"]

        player = self.players[player_id]

        # Can set valuations on owned properties
        if player.properties:
            actions.append("SET_VALUATION")

        # Can Harberger-buy any owned property
        if self.config.force_buy_enabled:
            for prop in self.properties.values():
                if prop.is_owned() and prop.owner_id != player_id:
                    if player.balance >= prop.valuation:
                        actions.append("HARBERGER_BUY")
                        break

        # Can build houses (simplified check)
        # TODO: Full monopoly checking
        if player.properties:
            actions.append("BUILD_HOUSE")

        return list(set(actions))
