"""
Economics Engine for HOLO-POLY.
Handles tax collection, rent calculation, and UBI dividend distribution.
Supports 4 timing modes: (on_go/per_turn) × (on_go/per_turn)
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
import logging

from .models import (
    GameState, Player, Property, PropertyId,
    Transaction, TaxTiming, GameConfig
)

logger = logging.getLogger(__name__)


@dataclass
class EconomicsResult:
    """Result of an economic operation."""
    success: bool
    transactions: List[Transaction]
    message: str = ""
    bankruptcy: bool = False


class EconomicsEngine:
    """
    Handles all economic calculations and transactions.

    Timing Modes:
    - Tax ON_GO: Collect tax when player passes GO
    - Tax PER_TURN: Collect tax at start of each turn (rate adjusted)
    - Dividend ON_GO: Distribute pot share when player passes GO
    - Dividend PER_TURN: Distribute pot share at start of each turn
    """

    def __init__(self, config: GameConfig):
        self.config = config
        self.base_tax_rate = config.tax_rate
        self.rent_rate = config.rent_rate
        self.pass_go_salary = config.pass_go_salary
        self.circuit_length = config.avg_circuit_length

    @property
    def effective_tax_rate(self) -> float:
        """Tax rate adjusted for timing mode."""
        if self.config.tax_timing == TaxTiming.PER_TURN:
            # Spread the tax over circuit length
            return self.base_tax_rate / self.circuit_length
        return self.base_tax_rate

    def process_turn_start(
        self,
        game_state: GameState,
        player: Player
    ) -> EconomicsResult:
        """
        Process economics at the start of a turn.
        Called for every turn, but only acts if timing is PER_TURN.
        """
        transactions = []

        # Per-turn tax collection
        if self.config.tax_timing == TaxTiming.PER_TURN:
            tax_result = self._collect_tax(game_state, player)
            transactions.extend(tax_result.transactions)
            if tax_result.bankruptcy:
                return EconomicsResult(
                    success=False,
                    transactions=transactions,
                    message=f"Player {player.id} went bankrupt from taxes",
                    bankruptcy=True
                )

        # Per-turn dividend distribution
        if self.config.dividend_timing == TaxTiming.PER_TURN:
            div_result = self._distribute_dividend(game_state, player)
            transactions.extend(div_result.transactions)

        return EconomicsResult(success=True, transactions=transactions)

    def process_pass_go(
        self,
        game_state: GameState,
        player: Player
    ) -> EconomicsResult:
        """
        Process economics when a player passes GO.
        Always gives salary, conditionally does tax/dividend based on timing.
        """
        transactions = []

        # Always collect GO salary
        salary_tx = self._pay_salary(game_state, player)
        transactions.append(salary_tx)

        # On-GO tax collection
        if self.config.tax_timing == TaxTiming.ON_GO:
            tax_result = self._collect_tax(game_state, player)
            transactions.extend(tax_result.transactions)
            if tax_result.bankruptcy:
                return EconomicsResult(
                    success=False,
                    transactions=transactions,
                    message=f"Player {player.id} went bankrupt from taxes",
                    bankruptcy=True
                )

        # On-GO dividend distribution
        if self.config.dividend_timing == TaxTiming.ON_GO:
            div_result = self._distribute_dividend(game_state, player)
            transactions.extend(div_result.transactions)

        return EconomicsResult(success=True, transactions=transactions)

    def _pay_salary(self, game_state: GameState, player: Player) -> Transaction:
        """Pay the GO salary to a player."""
        player.balance += self.pass_go_salary
        logger.info(f"Player {player.id} collected ${self.pass_go_salary} salary")

        return Transaction(
            turn=game_state.turn,
            transaction_type="SALARY",
            from_id="BANK",
            to_id=player.id,
            amount=self.pass_go_salary,
        )

    def _collect_tax(
        self,
        game_state: GameState,
        player: Player
    ) -> EconomicsResult:
        """Collect Harberger tax from a player."""
        total_valuation = player.total_valuation(game_state.properties)
        tax_amount = int(total_valuation * self.effective_tax_rate)

        if tax_amount == 0:
            return EconomicsResult(success=True, transactions=[])

        # Check if player can afford tax
        if player.balance < tax_amount:
            # Bankruptcy
            logger.warning(
                f"Player {player.id} cannot afford tax ${tax_amount} "
                f"(balance: ${player.balance})"
            )
            return EconomicsResult(
                success=False,
                transactions=[],
                message=f"Cannot afford tax: ${tax_amount}",
                bankruptcy=True
            )

        # Deduct tax
        player.balance -= tax_amount
        game_state.community_pot += tax_amount

        logger.info(
            f"Player {player.id} paid ${tax_amount} tax "
            f"(valuation: ${total_valuation})"
        )

        tx = Transaction(
            turn=game_state.turn,
            transaction_type="TAX",
            from_id=player.id,
            to_id="POT",
            amount=tax_amount,
            details={"valuation": total_valuation, "rate": self.effective_tax_rate}
        )

        return EconomicsResult(success=True, transactions=[tx])

    def _distribute_dividend(
        self,
        game_state: GameState,
        player: Player
    ) -> EconomicsResult:
        """Distribute UBI dividend to a player."""
        active_players = game_state.get_active_players()
        num_players = len(active_players)

        if num_players == 0 or game_state.community_pot == 0:
            return EconomicsResult(success=True, transactions=[])

        # Calculate share
        if self.config.dividend_timing == TaxTiming.PER_TURN:
            # Distribute 1/circuit_length of the pot per turn
            pot_fraction = 1.0 / self.circuit_length
            share = int(game_state.community_pot * pot_fraction / num_players)
        else:
            # ON_GO: Distribute equal share of current pot
            share = game_state.community_pot // num_players

        if share == 0:
            return EconomicsResult(success=True, transactions=[])

        # Pay dividend
        player.balance += share
        game_state.community_pot -= share

        logger.info(f"Player {player.id} received ${share} dividend")

        tx = Transaction(
            turn=game_state.turn,
            transaction_type="DIVIDEND",
            from_id="POT",
            to_id=player.id,
            amount=share,
            details={"pot_before": game_state.community_pot + share}
        )

        return EconomicsResult(success=True, transactions=[tx])

    def calculate_rent(
        self,
        property: Property,
        game_state: GameState,
        dice_roll: Optional[int] = None
    ) -> int:
        """
        Calculate rent for landing on a property.

        HOLO-POLY Rule: Rent = valuation × rent_rate (typically 10%)

        For utilities: 4× or 10× dice roll (standard Monopoly)
        For railroads: $25 × 2^(num_owned - 1) (standard Monopoly)
        """
        if not property.is_owned():
            return 0

        if property.tile_type == "utility":
            # Check how many utilities owner has
            owner = game_state.players.get(property.owner_id)
            if not owner:
                return 0
            num_utilities = sum(
                1 for pid in owner.properties
                if pid in game_state.properties
                and game_state.properties[pid].tile_type == "utility"
            )
            multiplier = 10 if num_utilities == 2 else 4
            return (dice_roll or 7) * multiplier  # Default to 7 if no dice

        if property.tile_type == "railroad":
            # Check how many railroads owner has
            owner = game_state.players.get(property.owner_id)
            if not owner:
                return 0
            num_railroads = sum(
                1 for pid in owner.properties
                if pid in game_state.properties
                and game_state.properties[pid].tile_type == "railroad"
            )
            return 25 * (2 ** (num_railroads - 1))

        # Standard property: Harberger rent = valuation × rate
        base_rent = int(property.valuation * self.rent_rate)

        # House multiplier (simplified from standard Monopoly)
        if property.houses > 0:
            house_multipliers = [1, 5, 15, 45, 80, 125]  # 0-4 houses, hotel
            multiplier = house_multipliers[min(property.houses, 5)]
            # Blend Harberger rent with house bonus
            base_rent = max(base_rent, property.face_value * multiplier // 10)

        return base_rent

    def process_rent_payment(
        self,
        game_state: GameState,
        payer: Player,
        property: Property,
        dice_roll: Optional[int] = None
    ) -> EconomicsResult:
        """Process rent payment from one player to another."""
        if not property.is_owned() or property.owner_id == payer.id:
            return EconomicsResult(success=True, transactions=[])

        rent = self.calculate_rent(property, game_state, dice_roll)
        if rent == 0:
            return EconomicsResult(success=True, transactions=[])

        owner = game_state.players.get(property.owner_id)
        if not owner or not owner.is_active():
            return EconomicsResult(success=True, transactions=[])

        # Check if payer can afford
        if payer.balance < rent:
            # Pay what they can, then bankruptcy
            rent = payer.balance
            bankruptcy = True
        else:
            bankruptcy = False

        # Transfer rent
        payer.balance -= rent
        owner.balance += rent

        logger.info(
            f"Player {payer.id} paid ${rent} rent to {owner.id} "
            f"for {property.name}"
        )

        tx = Transaction(
            turn=game_state.turn,
            transaction_type="RENT",
            from_id=payer.id,
            to_id=owner.id,
            amount=rent,
            property_id=property.id,
            details={"property_name": property.name, "valuation": property.valuation}
        )

        return EconomicsResult(
            success=not bankruptcy,
            transactions=[tx],
            bankruptcy=bankruptcy
        )

    def process_property_purchase(
        self,
        game_state: GameState,
        buyer: Player,
        property: Property
    ) -> EconomicsResult:
        """Process purchase of an unowned property from the bank."""
        if property.is_owned():
            return EconomicsResult(
                success=False,
                transactions=[],
                message="Property already owned"
            )

        price = property.face_value
        if buyer.balance < price:
            return EconomicsResult(
                success=False,
                transactions=[],
                message=f"Cannot afford ${price}"
            )

        # Execute purchase
        buyer.balance -= price
        property.owner_id = buyer.id
        property.valuation = price  # Initial valuation = purchase price
        buyer.properties.append(property.id)

        logger.info(f"Player {buyer.id} bought {property.name} for ${price}")

        tx = Transaction(
            turn=game_state.turn,
            transaction_type="PURCHASE",
            from_id=buyer.id,
            to_id="BANK",
            amount=price,
            property_id=property.id,
            details={"property_name": property.name}
        )

        return EconomicsResult(success=True, transactions=[tx])
