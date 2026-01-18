"""
Game Orchestrator for HOLO-POLY.
Manages the game loop, turn execution, and player coordination.
"""

import random
import logging
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass

from .models import (
    GameState, GameConfig, GameStatus, Player, PlayerStatus,
    Property, PropertyId, Action, ActionType, DiceRoll, Transaction
)
from .board_data import BOARD_TILES, COLOR_GROUPS, is_purchasable, get_tile
from .economics import EconomicsEngine, EconomicsResult
from .harberger import HarbergerEngine

logger = logging.getLogger(__name__)


@dataclass
class TurnResult:
    """Result of executing a turn."""
    success: bool
    player_id: str
    dice_roll: Optional[DiceRoll]
    actions_taken: List[Action]
    transactions: List[Transaction]
    passed_go: bool = False
    new_board: Optional[int] = None
    bankruptcy: bool = False
    message: str = ""


class Game:
    """
    Main game orchestrator.

    Handles:
    - Game initialization
    - Turn execution
    - Player actions
    - Win conditions
    """

    def __init__(
        self,
        config: GameConfig,
        agent_callback: Optional[Callable] = None
    ):
        self.config = config
        self.economics = EconomicsEngine(config)
        self.harberger = HarbergerEngine(config)
        self.agent_callback = agent_callback  # Function to get agent decisions

        # Set random seed if specified
        if config.random_seed is not None:
            random.seed(config.random_seed)

        # Initialize game state
        self.state = self._initialize_game()
        self.transaction_log: List[Transaction] = []

    def _initialize_game(self) -> GameState:
        """Set up initial game state."""
        # Create players
        players = {}
        player_order = []
        for i in range(self.config.num_players):
            player_id = f"player_{i}"
            archetype = self.config.archetypes[i % len(self.config.archetypes)]

            # Apply wealth inequality if configured
            starting_balance = self.config.starting_balance
            if self.config.wealth_inequality and i < len(self.config.wealth_inequality):
                multiplier = self.config.wealth_inequality[i]
                starting_balance = int(starting_balance * multiplier)

            players[player_id] = Player(
                id=player_id,
                balance=starting_balance,
                archetype=archetype,
                income_class=i,  # Used for income inequality
            )
            player_order.append(player_id)

        # Create properties for all boards
        properties = {}
        for board_id in range(self.config.num_boards):
            for tile in BOARD_TILES:
                if is_purchasable(tile.id):
                    prop_id = PropertyId(board=board_id, tile=tile.id)
                    properties[prop_id] = Property(
                        id=prop_id,
                        name=tile.name,
                        tile_type=tile.tile_type,
                        color_group=tile.color_group,
                        face_value=tile.face_value,
                    )

        return GameState(
            config=self.config,
            turn=0,
            players=players,
            properties=properties,
            community_pot=0,
            current_player_id=player_order[0],
            player_order=player_order,
        )

    def roll_dice(self) -> DiceRoll:
        """Roll two six-sided dice."""
        return DiceRoll(
            die1=random.randint(1, 6),
            die2=random.randint(1, 6)
        )

    def execute_turn(self) -> TurnResult:
        """Execute a single turn for the current player."""
        player = self.state.get_current_player()
        transactions = []
        actions_taken = []

        if not player.is_active():
            # If resurrection enabled, still process UBI for bankrupt players
            if self.config.resurrection_enabled:
                econ_result = self.economics.process_turn_start(self.state, player)
                transactions.extend(econ_result.transactions)
                # Check if resurrected
                if player.is_active():
                    logger.info(f"Player {player.id} has been RESURRECTED!")
                else:
                    return self._advance_to_next_player(TurnResult(
                        success=True,
                        player_id=player.id,
                        dice_roll=None,
                        actions_taken=[],
                        transactions=transactions,
                        message="Player is bankrupt, waiting for resurrection"
                    ))
            else:
                return self._advance_to_next_player(TurnResult(
                    success=True,
                    player_id=player.id,
                    dice_roll=None,
                    actions_taken=[],
                    transactions=[],
                    message="Player is bankrupt, skipping"
                ))

        logger.info(f"=== Turn {self.state.turn}: {player.id} ({player.archetype}) ===")
        logger.info(f"Balance: ${player.balance}, Position: {player.position}")

        # PHASE 0: Turn start economics (if per_turn timing)
        econ_result = self.economics.process_turn_start(self.state, player)
        transactions.extend(econ_result.transactions)
        if econ_result.bankruptcy:
            self._handle_bankruptcy(player)
            return self._advance_to_next_player(TurnResult(
                success=False,
                player_id=player.id,
                dice_roll=None,
                actions_taken=[],
                transactions=transactions,
                bankruptcy=True,
                message="Bankrupt from taxes"
            ))

        # PHASE 1: Roll dice and move
        dice = self.roll_dice()
        logger.info(f"Rolled {dice.die1} + {dice.die2} = {dice.total}")

        old_position = player.position
        new_position = (player.position + dice.total) % 40
        passed_go = new_position < old_position  # Wrapped around

        player.position = new_position
        new_board = None

        # Handle passing GO
        if passed_go:
            go_result = self.economics.process_pass_go(self.state, player)
            transactions.extend(go_result.transactions)

            if go_result.bankruptcy:
                self._handle_bankruptcy(player)
                return self._advance_to_next_player(TurnResult(
                    success=False,
                    player_id=player.id,
                    dice_roll=dice,
                    actions_taken=[],
                    transactions=transactions,
                    passed_go=True,
                    bankruptcy=True,
                    message="Bankrupt from taxes on GO"
                ))

            # Multi-board: Cycle to next board
            if self.config.num_boards > 1:
                player.current_board = (player.current_board + 1) % self.config.num_boards
                new_board = player.current_board
                logger.info(f"Player moved to board {new_board}")

        # PHASE 2: Process tile landing
        tile = get_tile(player.position)
        logger.info(f"Landed on: {tile.name} (type: {tile.tile_type})")

        tile_result = self._process_tile_landing(player, tile, dice)
        transactions.extend(tile_result.transactions)
        actions_taken.extend(tile_result.actions_taken)

        if tile_result.bankruptcy:
            self._handle_bankruptcy(player)
            return self._advance_to_next_player(TurnResult(
                success=False,
                player_id=player.id,
                dice_roll=dice,
                actions_taken=actions_taken,
                transactions=transactions,
                passed_go=passed_go,
                new_board=new_board,
                bankruptcy=True,
                message="Bankrupt from rent"
            ))

        # PHASE 3: Get agent decision for market actions
        if self.agent_callback and player.is_active():
            agent_actions = self._get_agent_actions(player)
            for action in agent_actions:
                action_result = self._execute_action(player, action)
                transactions.extend(action_result.transactions)
                actions_taken.append(action)

                if action_result.bankruptcy:
                    self._handle_bankruptcy(player)
                    break

        # PHASE 4: Advance turn
        player.turns_played += 1
        result = TurnResult(
            success=True,
            player_id=player.id,
            dice_roll=dice,
            actions_taken=actions_taken,
            transactions=transactions,
            passed_go=passed_go,
            new_board=new_board,
        )

        # Log transactions
        self.transaction_log.extend(transactions)

        return self._advance_to_next_player(result)

    def _process_tile_landing(
        self,
        player: Player,
        tile,
        dice: DiceRoll
    ) -> TurnResult:
        """Process the effect of landing on a tile."""
        transactions = []
        actions_taken = []
        bankruptcy = False

        prop_id = PropertyId(board=player.current_board, tile=tile.id)

        if tile.tile_type == "property" or tile.tile_type == "railroad" or tile.tile_type == "utility":
            property = self.state.properties.get(prop_id)

            if property and not property.is_owned():
                # Unowned: Offer to buy
                action = self._decide_buy_property(player, property)
                if action and action.action_type == ActionType.BUY_PROPERTY:
                    result = self.economics.process_property_purchase(
                        self.state, player, property
                    )
                    transactions.extend(result.transactions)
                    actions_taken.append(action)

            elif property and property.is_owned() and property.owner_id != player.id:
                # Owned by other: Pay rent
                result = self.economics.process_rent_payment(
                    self.state, player, property, dice.total
                )
                transactions.extend(result.transactions)
                bankruptcy = result.bankruptcy

        elif tile.tile_type == "tax":
            # Pay tax to bank (goes to pot)
            tax_amount = tile.face_value
            if player.balance >= tax_amount:
                player.balance -= tax_amount
                self.state.community_pot += tax_amount
                transactions.append(Transaction(
                    turn=self.state.turn,
                    transaction_type="TILE_TAX",
                    from_id=player.id,
                    to_id="POT",
                    amount=tax_amount,
                ))
            else:
                bankruptcy = True

        elif tile.tile_type == "go_to_jail":
            player.position = 10  # Jail position
            logger.info(f"Player {player.id} sent to jail")

        elif tile.tile_type == "chance" or tile.tile_type == "chest":
            # Skip if chance cards are disabled
            if self.config.chance_cards_enabled:
                # Simplified: Random cash event
                event_amount = random.choice([-50, -25, 0, 25, 50, 100, 200])
                if event_amount != 0:
                    if event_amount > 0:
                        player.balance += event_amount
                        from_id, to_id = "BANK", player.id
                    else:
                        if player.balance >= abs(event_amount):
                            player.balance += event_amount  # Negative
                            self.state.community_pot += abs(event_amount)
                        else:
                            bankruptcy = True
                        from_id, to_id = player.id, "POT"

                    if not bankruptcy:
                        transactions.append(Transaction(
                            turn=self.state.turn,
                            transaction_type="CHANCE_CHEST",
                            from_id=from_id,
                            to_id=to_id,
                            amount=abs(event_amount),
                            details={"card_type": tile.tile_type}
                        ))
                        logger.info(f"Card event: {'+' if event_amount > 0 else ''}{event_amount}")

        return TurnResult(
            success=not bankruptcy,
            player_id=player.id,
            dice_roll=None,
            actions_taken=actions_taken,
            transactions=transactions,
            bankruptcy=bankruptcy,
        )

    def _decide_buy_property(
        self,
        player: Player,
        property: Property
    ) -> Optional[Action]:
        """Decide whether to buy an unowned property."""
        if player.balance < property.face_value:
            return None

        # Use agent callback if available
        if self.agent_callback:
            game_view = self.state.to_player_view(player.id)
            decision = self.agent_callback(player, game_view, "BUY_DECISION", {
                "property": property.to_dict()
            })
            if decision and decision.get("action") == "BUY_PROPERTY":
                return Action(
                    action_type=ActionType.BUY_PROPERTY,
                    player_id=player.id,
                    params={"property_id": property.id.to_tuple()}
                )
            return None

        # Default: Buy if can afford and have buffer
        if player.balance >= property.face_value * 2:
            return Action(
                action_type=ActionType.BUY_PROPERTY,
                player_id=player.id,
                params={"property_id": property.id.to_tuple()}
            )
        return None

    def _get_agent_actions(self, player: Player) -> List[Action]:
        """Get market actions from the agent."""
        if not self.agent_callback:
            return []

        game_view = self.state.to_player_view(player.id)
        decisions = self.agent_callback(player, game_view, "MARKET_ACTIONS", {})

        actions = []
        if decisions:
            for decision in decisions if isinstance(decisions, list) else [decisions]:
                action = Action.from_dict(decision, player.id)
                if action.action_type != ActionType.PASS:
                    actions.append(action)

        return actions

    def _execute_action(self, player: Player, action: Action) -> EconomicsResult:
        """Execute a player action."""
        if action.action_type == ActionType.SET_VALUATION:
            prop_tuple = action.params.get("property_id")
            if prop_tuple:
                prop_id = PropertyId(board=prop_tuple[0], tile=prop_tuple[1])
                new_val = action.params.get("valuation", 0)
                return self.harberger.set_valuation(
                    self.state, player, prop_id, new_val
                )

        elif action.action_type == ActionType.HARBERGER_BUY:
            prop_tuple = action.params.get("property_id")
            if prop_tuple:
                prop_id = PropertyId(board=prop_tuple[0], tile=prop_tuple[1])
                return self.harberger.execute_forced_sale(
                    self.state, player, prop_id
                )

        elif action.action_type == ActionType.BUILD_HOUSE:
            # Simplified house building
            prop_tuple = action.params.get("property_id")
            if prop_tuple:
                prop_id = PropertyId(board=prop_tuple[0], tile=prop_tuple[1])
                return self._build_house(player, prop_id)

        return EconomicsResult(success=True, transactions=[])

    def _build_house(self, player: Player, prop_id: PropertyId) -> EconomicsResult:
        """Build a house on a property."""
        if prop_id not in self.state.properties:
            return EconomicsResult(success=False, transactions=[], message="Property not found")

        property = self.state.properties[prop_id]

        if property.owner_id != player.id:
            return EconomicsResult(success=False, transactions=[], message="Not your property")

        if property.houses >= 5:
            return EconomicsResult(success=False, transactions=[], message="Max houses reached")

        # Get house cost (simplified)
        house_cost = 100  # Could vary by color
        if player.balance < house_cost:
            return EconomicsResult(success=False, transactions=[], message="Cannot afford house")

        # Build house
        player.balance -= house_cost
        property.houses += 1

        # Must increase valuation
        min_new_val = property.valuation + house_cost
        property.valuation = min_new_val

        logger.info(f"Player {player.id} built house on {property.name}")

        return EconomicsResult(
            success=True,
            transactions=[Transaction(
                turn=self.state.turn,
                transaction_type="BUILD_HOUSE",
                from_id=player.id,
                to_id="BANK",
                amount=house_cost,
                property_id=prop_id,
            )]
        )

    def _handle_bankruptcy(self, player: Player):
        """Handle player bankruptcy."""
        logger.warning(f"Player {player.id} is BANKRUPT!")
        player.status = PlayerStatus.BANKRUPT

        # Return all properties to bank
        for prop_id in player.properties:
            if prop_id in self.state.properties:
                prop = self.state.properties[prop_id]
                prop.owner_id = None
                prop.valuation = 0
                prop.houses = 0

        player.properties.clear()
        player.balance = 0

    def _advance_to_next_player(self, result: TurnResult) -> TurnResult:
        """Advance to the next active player."""
        self.state.turn += 1

        active_players = self.state.get_active_players()

        # Check win conditions
        if len(active_players) <= 1:
            self.state.status = GameStatus.COMPLETED
            if active_players:
                self.state.winner_id = active_players[0].id
            logger.info(f"Game over! Winner: {self.state.winner_id}")
            return result

        if self.config.max_turns > 0 and self.state.turn >= self.config.max_turns:
            self.state.status = GameStatus.COMPLETED
            # Winner is player with highest net worth
            winner = max(
                active_players,
                key=lambda p: p.net_worth(self.state.properties)
            )
            self.state.winner_id = winner.id
            logger.info(f"Max turns reached. Winner: {winner.id}")
            return result

        # Find next active player
        current_idx = self.state.player_order.index(self.state.current_player_id)
        for _ in range(len(self.state.player_order)):
            current_idx = (current_idx + 1) % len(self.state.player_order)
            next_player_id = self.state.player_order[current_idx]
            if self.state.players[next_player_id].is_active():
                self.state.current_player_id = next_player_id
                break

        return result

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return self.state.status != GameStatus.ACTIVE

    def get_winner(self) -> Optional[str]:
        """Get the winner's ID, if game is over."""
        return self.state.winner_id

    def get_standings(self) -> List[dict]:
        """Get current standings sorted by net worth."""
        standings = []
        for player in self.state.players.values():
            standings.append({
                "id": player.id,
                "archetype": player.archetype,
                "balance": player.balance,
                "net_worth": player.net_worth(self.state.properties),
                "properties": len(player.properties),
                "status": player.status.value,
            })

        return sorted(standings, key=lambda x: x["net_worth"], reverse=True)

    def run_game(self, max_turns: Optional[int] = None, max_turns_this_run: Optional[int] = None) -> dict:
        """Run the game to completion or for a limited number of turns.

        Args:
            max_turns: Maximum total turns for the game
            max_turns_this_run: Maximum turns to run in this execution (for chunked runs)
        """
        max_turns = max_turns or self.config.max_turns or 1000
        start_turn = self.state.turn
        turns_run = 0

        while not self.is_game_over() and self.state.turn < max_turns:
            # Check if we've hit the per-run limit
            if max_turns_this_run and turns_run >= max_turns_this_run:
                logger.info(f"Chunk complete: ran {turns_run} turns (total: {self.state.turn})")
                break

            self.execute_turn()
            turns_run += 1

            # Progress indicator every 10 turns
            if turns_run % 10 == 0:
                logger.info(f"[PROGRESS] Turn {self.state.turn}/{max_turns} (this run: {turns_run})")

        return {
            "turns": self.state.turn,
            "turns_this_run": turns_run,
            "winner": self.get_winner(),
            "standings": self.get_standings(),
            "transactions": len(self.transaction_log),
            "complete": self.is_game_over() or self.state.turn >= max_turns,
        }

    def load_state(self, saved_state: dict):
        """Load game state from saved data (for resume functionality)."""
        if not saved_state:
            return

        # Restore turn counter
        self.state.turn = saved_state.get('turn', 0)

        # Restore player states
        for player_data in saved_state.get('players', []):
            player_id = player_data['id']
            if player_id in self.state.players:
                player = self.state.players[player_id]
                player.balance = player_data.get('balance', player.balance)
                player.position = player_data.get('position', player.position)
                player.board_id = player_data.get('board_id', player.board_id)
                player.properties = set(player_data.get('properties', []))
                if player_data.get('status') == 'BANKRUPT':
                    from kernel.models import PlayerStatus
                    player.status = PlayerStatus.BANKRUPT

        # Restore property states
        for prop_data in saved_state.get('properties', []):
            prop_id = prop_data['id']
            if prop_id in self.state.properties:
                prop = self.state.properties[prop_id]
                prop.owner_id = prop_data.get('owner_id')
                prop.valuation = prop_data.get('valuation', prop.valuation)
                prop.houses = prop_data.get('houses', 0)

        # Restore community pot
        self.state.community_pot = saved_state.get('community_pot', 0)

        logger.info(f"Loaded game state from turn {self.state.turn}")
