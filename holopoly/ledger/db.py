"""
Database operations for HOLO-POLY.
Uses SQLite for persistence.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from ..kernel.models import (
    GameState, GameConfig, GameStatus, Player, PlayerStatus,
    Property, PropertyId, Transaction
)

logger = logging.getLogger(__name__)

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class Database:
    """SQLite database for HOLO-POLY game state and history."""

    def __init__(self, db_path: str = "holopoly.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._initialize()

    def _initialize(self):
        """Initialize database with schema."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

        # Load and execute schema
        if SCHEMA_PATH.exists():
            schema = SCHEMA_PATH.read_text()
            self.connection.executescript(schema)
            self.connection.commit()
            logger.info(f"Database initialized at {self.db_path}")
        else:
            logger.warning(f"Schema file not found: {SCHEMA_PATH}")

    @contextmanager
    def cursor(self):
        """Context manager for database cursor."""
        cur = self.connection.cursor()
        try:
            yield cur
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    # ==================== Game Operations ====================

    def create_game(self, game_id: str, config: dict) -> bool:
        """Create a new game record."""
        with self.cursor() as cur:
            cur.execute(
                "INSERT INTO games (id, config, status) VALUES (?, ?, ?)",
                (game_id, json.dumps(config), "ACTIVE")
            )

            # Create economy record
            cur.execute(
                "INSERT INTO economy (game_id, community_pot) VALUES (?, ?)",
                (game_id, 0)
            )

        logger.info(f"Created game: {game_id}")
        return True

    def update_game_status(
        self,
        game_id: str,
        status: str,
        winner_id: Optional[str] = None,
        total_turns: int = 0
    ):
        """Update game status."""
        with self.cursor() as cur:
            cur.execute(
                """UPDATE games
                   SET status = ?, winner_id = ?, total_turns = ?,
                       completed_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (status, winner_id, total_turns, game_id)
            )

    def get_game(self, game_id: str) -> Optional[dict]:
        """Get game record."""
        with self.cursor() as cur:
            cur.execute("SELECT * FROM games WHERE id = ?", (game_id,))
            row = cur.fetchone()
            if row:
                return dict(row)
        return None

    # ==================== Player Operations ====================

    def create_player(
        self,
        game_id: str,
        player_id: str,
        balance: int,
        archetype: str
    ):
        """Create a player record."""
        with self.cursor() as cur:
            cur.execute(
                """INSERT INTO players
                   (game_id, player_id, balance, current_board, position, status, archetype)
                   VALUES (?, ?, ?, 0, 0, 'ACTIVE', ?)""",
                (game_id, player_id, balance, archetype)
            )

    def update_player(self, game_id: str, player: Player):
        """Update player state."""
        with self.cursor() as cur:
            cur.execute(
                """UPDATE players
                   SET balance = ?, current_board = ?, position = ?,
                       status = ?, turns_played = ?
                   WHERE game_id = ? AND player_id = ?""",
                (player.balance, player.current_board, player.position,
                 player.status.value, player.turns_played,
                 game_id, player.id)
            )

    def get_players(self, game_id: str) -> List[dict]:
        """Get all players for a game."""
        with self.cursor() as cur:
            cur.execute(
                "SELECT * FROM players WHERE game_id = ?",
                (game_id,)
            )
            return [dict(row) for row in cur.fetchall()]

    # ==================== Property Operations ====================

    def create_property(
        self,
        game_id: str,
        board_id: int,
        tile_id: int,
        name: str,
        tile_type: str,
        color_group: Optional[str],
        face_value: int
    ):
        """Create a property record."""
        with self.cursor() as cur:
            cur.execute(
                """INSERT INTO properties
                   (game_id, board_id, tile_id, name, tile_type,
                    color_group, face_value, owner_id, valuation, houses)
                   VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 0, 0)""",
                (game_id, board_id, tile_id, name, tile_type,
                 color_group, face_value)
            )

    def update_property(self, game_id: str, property: Property):
        """Update property state."""
        with self.cursor() as cur:
            cur.execute(
                """UPDATE properties
                   SET owner_id = ?, valuation = ?, houses = ?, is_mortgaged = ?
                   WHERE game_id = ? AND board_id = ? AND tile_id = ?""",
                (property.owner_id, property.valuation, property.houses,
                 int(property.is_mortgaged),
                 game_id, property.id.board, property.id.tile)
            )

    def get_properties(self, game_id: str) -> List[dict]:
        """Get all properties for a game."""
        with self.cursor() as cur:
            cur.execute(
                "SELECT * FROM properties WHERE game_id = ?",
                (game_id,)
            )
            return [dict(row) for row in cur.fetchall()]

    # ==================== Economy Operations ====================

    def update_economy(self, game_id: str, community_pot: int):
        """Update economy state."""
        with self.cursor() as cur:
            cur.execute(
                "UPDATE economy SET community_pot = ? WHERE game_id = ?",
                (community_pot, game_id)
            )

    def get_economy(self, game_id: str) -> Optional[dict]:
        """Get economy state."""
        with self.cursor() as cur:
            cur.execute(
                "SELECT * FROM economy WHERE game_id = ?",
                (game_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None

    # ==================== Transaction Operations ====================

    def log_transaction(self, game_id: str, tx: Transaction):
        """Log a transaction."""
        with self.cursor() as cur:
            prop_board = tx.property_id.board if tx.property_id else None
            prop_tile = tx.property_id.tile if tx.property_id else None

            cur.execute(
                """INSERT INTO transactions
                   (game_id, turn, phase, from_id, to_id, amount,
                    property_board, property_tile, details)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (game_id, tx.turn, tx.transaction_type, tx.from_id, tx.to_id,
                 tx.amount, prop_board, prop_tile, json.dumps(tx.details))
            )

    def get_transactions(
        self,
        game_id: str,
        turn: Optional[int] = None,
        transaction_type: Optional[str] = None
    ) -> List[dict]:
        """Get transactions with optional filters."""
        query = "SELECT * FROM transactions WHERE game_id = ?"
        params = [game_id]

        if turn is not None:
            query += " AND turn = ?"
            params.append(turn)

        if transaction_type:
            query += " AND phase = ?"
            params.append(transaction_type)

        query += " ORDER BY id"

        with self.cursor() as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    # ==================== Turn History ====================

    def log_turn(
        self,
        game_id: str,
        turn_number: int,
        player_id: str,
        dice_roll: Optional[tuple],
        start_pos: int,
        end_pos: int,
        start_board: int,
        end_board: int,
        passed_go: bool,
        action: Optional[dict],
        llm_response: Optional[str] = None
    ):
        """Log a turn."""
        with self.cursor() as cur:
            cur.execute(
                """INSERT OR REPLACE INTO turns
                   (game_id, turn_number, player_id, dice_roll,
                    start_position, end_position, start_board, end_board,
                    passed_go, action_taken, llm_response)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (game_id, turn_number, player_id,
                 json.dumps(dice_roll) if dice_roll else None,
                 start_pos, end_pos, start_board, end_board,
                 int(passed_go), json.dumps(action) if action else None,
                 llm_response)
            )

    # ==================== Full State Save/Load ====================

    def save_game_state(self, game_id: str, state: GameState):
        """Save complete game state to database."""
        # Update game record
        self.update_game_status(
            game_id,
            state.status.value,
            state.winner_id,
            state.turn
        )

        # Update all players
        for player in state.players.values():
            self.update_player(game_id, player)

        # Update all properties
        for property in state.properties.values():
            self.update_property(game_id, property)

        # Update economy
        self.update_economy(game_id, state.community_pot)

        logger.debug(f"Saved game state: turn {state.turn}")

    def load_game_state(self, game_id: str, config: GameConfig) -> Optional[GameState]:
        """Load game state from database."""
        game = self.get_game(game_id)
        if not game:
            return None

        # Load players
        players = {}
        player_order = []
        for row in self.get_players(game_id):
            player = Player(
                id=row["player_id"],
                balance=row["balance"],
                current_board=row["current_board"],
                position=row["position"],
                status=PlayerStatus(row["status"]),
                archetype=row["archetype"],
                turns_played=row["turns_played"],
            )
            players[player.id] = player
            player_order.append(player.id)

        # Load properties
        properties = {}
        for row in self.get_properties(game_id):
            prop_id = PropertyId(board=row["board_id"], tile=row["tile_id"])
            prop = Property(
                id=prop_id,
                name=row["name"],
                tile_type=row["tile_type"],
                color_group=row["color_group"],
                face_value=row["face_value"],
                owner_id=row["owner_id"],
                valuation=row["valuation"],
                houses=row["houses"],
                is_mortgaged=bool(row["is_mortgaged"]),
            )
            properties[prop_id] = prop

            # Update player property lists
            if prop.owner_id and prop.owner_id in players:
                players[prop.owner_id].properties.append(prop_id)

        # Load economy
        economy = self.get_economy(game_id)
        community_pot = economy["community_pot"] if economy else 0

        # Determine current player (first active)
        current_player_id = player_order[0]
        for pid in player_order:
            if players[pid].is_active():
                current_player_id = pid
                break

        return GameState(
            config=config,
            turn=game["total_turns"],
            players=players,
            properties=properties,
            community_pot=community_pot,
            current_player_id=current_player_id,
            player_order=player_order,
            status=GameStatus(game["status"]),
            winner_id=game["winner_id"],
        )

    # ==================== Analytics Queries ====================

    def get_game_stats(self, game_id: str) -> dict:
        """Get aggregate statistics for a game."""
        with self.cursor() as cur:
            # Total transactions by type
            cur.execute(
                """SELECT phase, COUNT(*) as count, SUM(amount) as total
                   FROM transactions WHERE game_id = ?
                   GROUP BY phase""",
                (game_id,)
            )
            tx_stats = {row["phase"]: {"count": row["count"], "total": row["total"]}
                       for row in cur.fetchall()}

            # Property ownership changes
            cur.execute(
                """SELECT COUNT(*) FROM transactions
                   WHERE game_id = ? AND phase IN ('PURCHASE', 'HARBERGER_BUY')""",
                (game_id,)
            )
            ownership_changes = cur.fetchone()[0]

            # Bankruptcies
            cur.execute(
                """SELECT COUNT(*) FROM players
                   WHERE game_id = ? AND status = 'BANKRUPT'""",
                (game_id,)
            )
            bankruptcies = cur.fetchone()[0]

        return {
            "transaction_stats": tx_stats,
            "ownership_changes": ownership_changes,
            "bankruptcies": bankruptcies,
        }
