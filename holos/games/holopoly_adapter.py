"""
HOLOPOLY Adapter - Bridge HOLOPOLY to HOLOS Kernel

This adapter wraps the existing HOLOPOLY implementation as a HOLOS Enclave,
allowing the 47+ existing experiments to run unchanged while enabling
new sovereign computing experiments.

Key mappings:
- Player → Holon (sovereign entity with hidden balance)
- Property → Mantle (transferable authority with Harberger pricing)
- Game → Enclave (group of Holons with shared governance/rules)

Constraint: run_holopoly_original(config) == run_holopoly_via_holos(config)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import sys
import os

# Add holopoly to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from holos.kernel.holon import Holon, HolonId, HolonStatus, Constitution, create_holon
from holos.kernel.identity import Mantle, Name, Right, Responsibility, RootType, create_name, create_mantle
from holos.kernel.enclave import Enclave, EnclaveType, create_enclave, MembershipStatus
from holos.kernel.contract import Contract, ContractType, create_membership_contract

# Import HOLOPOLY models (may not be available in all contexts)
try:
    from holopoly.kernel.models import Player, Property, PropertyId, GameConfig, GameState
    HOLOPOLY_AVAILABLE = True
except ImportError:
    HOLOPOLY_AVAILABLE = False
    Player = None
    Property = None


@dataclass
class PropertyMantle(Mantle):
    """
    A Mantle representing ownership of a HOLOPOLY property.

    Maps directly from holopoly.kernel.models.Property:
    - Rights: Collect rent from visitors
    - Responsibilities: Pay Harberger tax on valuation
    - Harberger-enabled: Always forced-sellable at valuation
    """
    # Property-specific fields
    property_id_tuple: tuple = (0, 0)  # (board, tile)
    face_value: int = 0
    color_group: Optional[str] = None
    houses: int = 0
    rent_rate: float = 0.10

    @property
    def property_id(self) -> 'PropertyId':
        """Reconstruct PropertyId from tuple."""
        if not HOLOPOLY_AVAILABLE:
            return None
        return PropertyId(board=self.property_id_tuple[0], tile=self.property_id_tuple[1])

    @classmethod
    def from_property(cls, prop: 'Property', issuing_enclave_id: str, rent_rate: float = 0.10) -> 'PropertyMantle':
        """Create a PropertyMantle from a HOLOPOLY Property."""
        return cls(
            mantle_id=f"mantle_b{prop.id.board}_t{prop.id.tile}",
            name=prop.name,
            issuing_sheaf_id=issuing_enclave_id,
            holder_holon_id=prop.owner_id,

            # Rights
            rights=[
                Right(
                    right_id=f"collect_rent_{prop.id.board}_{prop.id.tile}",
                    name="Collect Rent",
                    description=f"Collect {rent_rate*100}% of visitor valuation as rent",
                    resource_type="RENT",
                )
            ],

            # Responsibilities
            responsibilities=[
                Responsibility(
                    responsibility_id=f"pay_tax_{prop.id.board}_{prop.id.tile}",
                    name="Pay Harberger Tax",
                    description="Pay tax on property valuation each turn/circuit",
                    frequency="PER_TURN",
                )
            ],

            # Harberger economics
            bond_required=0,  # No bond for property ownership
            valuation=prop.valuation,
            transferable=True,
            harberger_enabled=True,

            # Property-specific
            property_id_tuple=prop.id.to_tuple(),
            face_value=prop.face_value,
            color_group=prop.color_group,
            houses=prop.houses,
            rent_rate=rent_rate,
        )

    def to_property(self) -> 'Property':
        """Convert back to HOLOPOLY Property."""
        if not HOLOPOLY_AVAILABLE:
            raise RuntimeError("HOLOPOLY not available")

        return Property(
            id=self.property_id,
            name=self.name,
            tile_type="property",
            color_group=self.color_group,
            face_value=self.face_value,
            owner_id=self.holder_holon_id,
            valuation=self.valuation,
            houses=self.houses,
        )


@dataclass
class HolopolyHolon:
    """
    A Holon representing a HOLOPOLY player.

    Wraps the existing Player model with Holon capabilities:
    - ZK-like hidden balance (balance is private)
    - Name with reputation tracking
    - Constitutional right to exit (quit the game)
    """
    holon: Holon
    name: Name

    # HOLOPOLY-specific state (pass-through to original Player)
    player_id: str = ""
    current_board: int = 0
    position: int = 0
    archetype: str = "default"
    turns_played: int = 0
    income_class: int = 0

    # Property ownership (as Mantle IDs)
    property_mantles: List[str] = field(default_factory=list)

    @classmethod
    def from_player(cls, player: 'Player', enclave_id: str) -> 'HolopolyHolon':
        """Create a HolopolyHolon from a HOLOPOLY Player."""
        # Create underlying Holon
        holon = create_holon(
            initial_balance=player.balance,
            valuation=0,  # Players don't have Harberger valuation
        )
        holon.parent_sheaf_id = enclave_id

        # Map player status to holon status
        if player.status.value == "BANKRUPT":
            holon.status = HolonStatus.BANKRUPT

        # Create Name for reputation tracking
        name = create_name(
            display_name=f"Player_{player.id}",
            owner_holon_id=str(holon.holon_id.value),
            root_type=RootType.AI,  # Assume AI player (can be configured)
        )
        holon.name_id = name.name_id

        return cls(
            holon=holon,
            name=name,
            player_id=player.id,
            current_board=player.current_board,
            position=player.position,
            archetype=player.archetype,
            turns_played=player.turns_played,
            income_class=player.income_class,
            property_mantles=[f"mantle_b{pid.board}_t{pid.tile}" for pid in player.properties],
        )

    def to_player(self) -> 'Player':
        """Convert back to HOLOPOLY Player for compatibility."""
        if not HOLOPOLY_AVAILABLE:
            raise RuntimeError("HOLOPOLY not available")

        from holopoly.kernel.models import PlayerStatus

        status = PlayerStatus.BANKRUPT if self.holon.status == HolonStatus.BANKRUPT else PlayerStatus.ACTIVE

        # Reconstruct property IDs from mantle IDs
        properties = []
        for mantle_id in self.property_mantles:
            # Parse "mantle_b0_t5" -> PropertyId(0, 5)
            parts = mantle_id.replace("mantle_b", "").split("_t")
            if len(parts) == 2:
                board, tile = int(parts[0]), int(parts[1])
                properties.append(PropertyId(board=board, tile=tile))

        return Player(
            id=self.player_id,
            balance=self.holon.vault,
            current_board=self.current_board,
            position=self.position,
            status=status,
            archetype=self.archetype,
            turns_played=self.turns_played,
            properties=properties,
            income_class=self.income_class,
        )

    @property
    def balance(self) -> int:
        """Public balance (from vault)."""
        return self.holon.vault

    @balance.setter
    def balance(self, value: int):
        self.holon.vault = value

    def is_active(self) -> bool:
        return self.holon.is_active()

    def is_bankrupt(self) -> bool:
        return self.holon.status == HolonStatus.BANKRUPT


class HolopolyEnclave(Enclave):
    """
    HOLOPOLY Game as an Enclave.

    The game itself is a sovereign entity (Enclave) that:
    - Manages membership (players joining/leaving)
    - Holds treasury (community pot)
    - Enforces rules (game mechanics as constitutional invariants)
    - Distributes dividends (GO salary, pot distributions)

    Players (Holons) can always exit - this maps to "quitting the game".
    """

    def __init__(
        self,
        config: Optional['GameConfig'] = None,
        **kwargs
    ):
        # Create the underlying Enclave
        enclave = create_enclave(
            enclave_type=EnclaveType.TEMPORARY,  # Games are time-bounded
            initial_treasury=0,
            tax_rate=config.tax_rate if config else 0.10,
        )

        # Copy enclave attributes
        super().__init__(
            holon=enclave.holon,
            enclave_type=enclave.enclave_type,
            treasury=enclave.treasury,
        )

        # Game-specific state
        self.config = config
        self.turn: int = 0
        self.property_mantles: Dict[str, PropertyMantle] = {}
        self.player_holons: Dict[str, HolopolyHolon] = {}
        self.community_pot: int = 0

    @classmethod
    def from_game_state(cls, state: 'GameState') -> 'HolopolyEnclave':
        """Create HolopolyEnclave from existing GameState."""
        enclave = cls(config=state.config)
        enclave.turn = state.turn
        enclave.community_pot = state.community_pot

        # Adapt players to Holons
        for player_id, player in state.players.items():
            holon_wrapper = HolopolyHolon.from_player(player, enclave.enclave_id)
            enclave.player_holons[player_id] = holon_wrapper

            # Register as member
            from holos.kernel.enclave import MembershipRecord, MembershipStatus
            enclave.members[str(holon_wrapper.holon.holon_id.value)] = MembershipRecord(
                holon_id=holon_wrapper.holon.holon_id,
                status=MembershipStatus.ACTIVE if player.is_active() else MembershipStatus.EXITED,
            )

        # Adapt properties to Mantles
        for prop_id, prop in state.properties.items():
            mantle = PropertyMantle.from_property(
                prop,
                issuing_enclave_id=enclave.enclave_id,
                rent_rate=state.config.rent_rate,
            )
            enclave.property_mantles[mantle.mantle_id] = mantle

        return enclave

    def to_game_state(self) -> 'GameState':
        """Convert back to HOLOPOLY GameState for compatibility."""
        if not HOLOPOLY_AVAILABLE or not self.config:
            raise RuntimeError("HOLOPOLY not available or no config")

        from holopoly.kernel.models import GameState, GameStatus

        # Convert players
        players = {}
        player_order = []
        for player_id, holon_wrapper in self.player_holons.items():
            players[player_id] = holon_wrapper.to_player()
            player_order.append(player_id)

        # Convert properties
        properties = {}
        for mantle_id, mantle in self.property_mantles.items():
            prop = mantle.to_property()
            properties[prop.id] = prop

        return GameState(
            config=self.config,
            turn=self.turn,
            players=players,
            properties=properties,
            community_pot=self.community_pot,
            current_player_id=player_order[0] if player_order else "",
            player_order=player_order,
            status=GameStatus.ACTIVE,
        )

    def player_exit(self, player_id: str) -> Dict[str, Any]:
        """
        Process a player exiting the game.

        Constitutional invariant: Exit CANNOT be blocked.
        The player forfeits their property Mantles but keeps their balance.
        """
        if player_id not in self.player_holons:
            return {"success": False, "reason": "Player not in game"}

        holon_wrapper = self.player_holons[player_id]

        # Forfeit property Mantles (they return to the game/bank)
        forfeited_mantles = []
        for mantle_id in holon_wrapper.property_mantles:
            if mantle_id in self.property_mantles:
                mantle = self.property_mantles[mantle_id]
                mantle.holder_holon_id = None  # Return to bank
                forfeited_mantles.append(mantle_id)

        holon_wrapper.property_mantles = []

        # Mark holon as exited
        holon_wrapper.holon.status = HolonStatus.EXITED

        return {
            "success": True,
            "player_id": player_id,
            "final_balance": holon_wrapper.balance,
            "mantles_forfeited": forfeited_mantles,
        }


# === Adapter Functions ===

def adapt_player_to_holon(player: 'Player', enclave_id: str) -> HolopolyHolon:
    """Convert a HOLOPOLY Player to a HolopolyHolon."""
    return HolopolyHolon.from_player(player, enclave_id)


def adapt_property_to_mantle(prop: 'Property', enclave_id: str, rent_rate: float = 0.10) -> PropertyMantle:
    """Convert a HOLOPOLY Property to a PropertyMantle."""
    return PropertyMantle.from_property(prop, enclave_id, rent_rate)


def adapt_game_to_enclave(state: 'GameState') -> HolopolyEnclave:
    """Convert a HOLOPOLY GameState to a HolopolyEnclave."""
    return HolopolyEnclave.from_game_state(state)


# === Verification ===

def verify_adapter_roundtrip(state: 'GameState') -> bool:
    """
    Verify that adapting and un-adapting preserves state.

    Critical for backward compatibility with 47 experiments.
    """
    if not HOLOPOLY_AVAILABLE:
        return False

    # Convert to enclave
    enclave = HolopolyEnclave.from_game_state(state)

    # Convert back
    recovered = enclave.to_game_state()

    # Verify key fields match
    if recovered.turn != state.turn:
        return False
    if recovered.community_pot != state.community_pot:
        return False
    if len(recovered.players) != len(state.players):
        return False
    if len(recovered.properties) != len(state.properties):
        return False

    # Verify player balances
    for pid, player in state.players.items():
        if pid not in recovered.players:
            return False
        if recovered.players[pid].balance != player.balance:
            return False

    # Verify property valuations
    for prop_id, prop in state.properties.items():
        if prop_id not in recovered.properties:
            return False
        if recovered.properties[prop_id].valuation != prop.valuation:
            return False

    return True
