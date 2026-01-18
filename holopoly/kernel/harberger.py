"""
Harberger Tax Mechanics for HOLO-POLY.
Implements forced sales and valuation management.
"""

from typing import Optional
import logging

from .models import (
    GameState, Player, Property, PropertyId,
    Transaction, GameConfig
)
from .economics import EconomicsResult

logger = logging.getLogger(__name__)


class HarbergerEngine:
    """
    Implements Harberger tax mechanics:
    1. Self-assessment: Owners declare property valuations
    2. Forced sale: Anyone can buy at declared price
    3. Min valuation: Properties cannot be valued at $0
    """

    def __init__(self, config: GameConfig):
        self.config = config
        self.min_valuation = config.min_valuation
        self.force_buy_enabled = config.force_buy_enabled

    def set_valuation(
        self,
        game_state: GameState,
        player: Player,
        property_id: PropertyId,
        new_valuation: int
    ) -> EconomicsResult:
        """
        Set a new valuation for a property.

        Rules:
        - Only owner can set valuation
        - Valuation must be >= min_valuation
        - Higher valuation = higher rent, higher tax
        - Lower valuation = lower tax, risk of forced sale
        """
        if property_id not in game_state.properties:
            return EconomicsResult(
                success=False,
                transactions=[],
                message="Property not found"
            )

        property = game_state.properties[property_id]

        if property.owner_id != player.id:
            return EconomicsResult(
                success=False,
                transactions=[],
                message="You don't own this property"
            )

        # Enforce minimum valuation
        new_valuation = max(new_valuation, self.min_valuation)

        old_valuation = property.valuation
        property.valuation = new_valuation

        logger.info(
            f"Player {player.id} set {property.name} valuation: "
            f"${old_valuation} -> ${new_valuation}"
        )

        tx = Transaction(
            turn=game_state.turn,
            transaction_type="VALUATION_CHANGE",
            from_id=player.id,
            to_id=player.id,
            amount=new_valuation - old_valuation,
            property_id=property_id,
            details={
                "property_name": property.name,
                "old_valuation": old_valuation,
                "new_valuation": new_valuation
            }
        )

        return EconomicsResult(success=True, transactions=[tx])

    def execute_forced_sale(
        self,
        game_state: GameState,
        buyer: Player,
        property_id: PropertyId
    ) -> EconomicsResult:
        """
        Execute a Harberger forced sale (buy any property at declared price).

        Rules:
        - Buyer pays the declared valuation to the owner
        - Owner CANNOT refuse
        - Ownership transfers immediately
        - Houses transfer with property
        - New owner inherits the valuation (can change it)
        """
        if not self.force_buy_enabled:
            return EconomicsResult(
                success=False,
                transactions=[],
                message="Harberger force-buy is disabled"
            )

        if property_id not in game_state.properties:
            return EconomicsResult(
                success=False,
                transactions=[],
                message="Property not found"
            )

        property = game_state.properties[property_id]

        # Can't buy unowned property via Harberger
        if not property.is_owned():
            return EconomicsResult(
                success=False,
                transactions=[],
                message="Property is not owned (use normal purchase)"
            )

        # Can't buy from yourself
        if property.owner_id == buyer.id:
            return EconomicsResult(
                success=False,
                transactions=[],
                message="You already own this property"
            )

        # Check buyer can afford
        price = property.valuation
        if buyer.balance < price:
            return EconomicsResult(
                success=False,
                transactions=[],
                message=f"Cannot afford ${price} (balance: ${buyer.balance})"
            )

        # Get seller
        seller = game_state.players.get(property.owner_id)
        if not seller:
            return EconomicsResult(
                success=False,
                transactions=[],
                message="Seller not found"
            )

        # Execute the forced sale
        buyer.balance -= price
        seller.balance += price

        # Transfer ownership
        seller.properties.remove(property_id)
        buyer.properties.append(property_id)
        property.owner_id = buyer.id

        logger.info(
            f"HARBERGER BUY: {buyer.id} bought {property.name} from {seller.id} "
            f"for ${price}"
        )

        tx = Transaction(
            turn=game_state.turn,
            transaction_type="HARBERGER_BUY",
            from_id=buyer.id,
            to_id=seller.id,
            amount=price,
            property_id=property_id,
            details={
                "property_name": property.name,
                "houses": property.houses,
                "valuation": price
            }
        )

        return EconomicsResult(success=True, transactions=[tx])

    def get_buyable_properties(
        self,
        game_state: GameState,
        buyer: Player
    ) -> list:
        """Get all properties the buyer could Harberger-buy."""
        if not self.force_buy_enabled:
            return []

        buyable = []
        for prop_id, prop in game_state.properties.items():
            if prop.is_owned() and prop.owner_id != buyer.id:
                if buyer.balance >= prop.valuation:
                    buyable.append({
                        "property_id": prop_id.to_tuple(),
                        "name": prop.name,
                        "owner": prop.owner_id,
                        "valuation": prop.valuation,
                        "houses": prop.houses,
                    })

        return buyable

    def validate_valuation(
        self,
        property: Property,
        new_valuation: int
    ) -> tuple:
        """
        Validate a proposed valuation.
        Returns (is_valid, adjusted_valuation, message).
        """
        if new_valuation < self.min_valuation:
            return (
                False,
                self.min_valuation,
                f"Valuation must be at least ${self.min_valuation}"
            )

        # Optional: Could add max valuation rules here
        # e.g., max 10x face value to prevent griefing

        return (True, new_valuation, "OK")

    def execute_bulk_colorset_buy(
        self,
        game_state: GameState,
        buyer: Player,
        color_group: str
    ) -> EconomicsResult:
        """
        Buy all properties in a color group at their summed valuations.
        Price is locked at time of decision (seller can't change mid-transaction).

        Rules:
        - Must buy ALL properties in the color group at once
        - Total price = sum of all individual valuations
        - Buyer must afford the total
        - All properties transfer atomically
        """
        if not self.config.bulk_colorset_buy:
            return EconomicsResult(
                success=False,
                transactions=[],
                message="Bulk color set purchase is disabled"
            )

        # Find all properties in this color group
        color_properties = []
        for prop_id, prop in game_state.properties.items():
            if prop.color_group == color_group:
                color_properties.append((prop_id, prop))

        if not color_properties:
            return EconomicsResult(
                success=False,
                transactions=[],
                message=f"No properties in color group: {color_group}"
            )

        # Calculate total price and check ownership
        total_price = 0
        sellers = {}  # seller_id -> amount they receive
        for prop_id, prop in color_properties:
            if not prop.is_owned():
                return EconomicsResult(
                    success=False,
                    transactions=[],
                    message=f"Property {prop.name} is unowned, cannot bulk buy"
                )
            if prop.owner_id == buyer.id:
                return EconomicsResult(
                    success=False,
                    transactions=[],
                    message=f"You already own {prop.name}"
                )
            total_price += prop.valuation
            sellers[prop.owner_id] = sellers.get(prop.owner_id, 0) + prop.valuation

        # Check if buyer can afford
        if buyer.balance < total_price:
            return EconomicsResult(
                success=False,
                transactions=[],
                message=f"Cannot afford ${total_price} (balance: ${buyer.balance})"
            )

        # Execute the bulk purchase
        transactions = []
        buyer.balance -= total_price

        for seller_id, amount in sellers.items():
            seller = game_state.players.get(seller_id)
            if seller:
                seller.balance += amount

        # Transfer all properties
        for prop_id, prop in color_properties:
            old_owner = game_state.players.get(prop.owner_id)
            if old_owner and prop_id in old_owner.properties:
                old_owner.properties.remove(prop_id)
            buyer.properties.append(prop_id)
            prop.owner_id = buyer.id

        logger.info(
            f"BULK COLOR BUY: {buyer.id} bought all {color_group} properties "
            f"for ${total_price}"
        )

        tx = Transaction(
            turn=game_state.turn,
            transaction_type="BULK_COLORSET_BUY",
            from_id=buyer.id,
            to_id="MULTIPLE",
            amount=total_price,
            details={
                "color_group": color_group,
                "properties": [p[1].name for p in color_properties],
                "sellers": sellers
            }
        )

        return EconomicsResult(success=True, transactions=[tx])

    def suggest_valuation(
        self,
        property: Property,
        game_state: GameState,
        strategy: str = "balanced"
    ) -> int:
        """
        Suggest a valuation based on strategy.

        Strategies:
        - "aggressive": High valuation (max rent, high tax)
        - "defensive": Very high valuation (prevent buyouts)
        - "conservative": Low valuation (min tax, risk buyout)
        - "balanced": Face value + improvements
        """
        base = property.face_value

        if strategy == "aggressive":
            # 2x face value + house value
            return base * 2 + (property.houses * 100)

        elif strategy == "defensive":
            # 5x face value (make it expensive to buy)
            return base * 5

        elif strategy == "conservative":
            # Just above minimum
            return max(self.min_valuation, base // 2)

        else:  # balanced
            # Face value + house improvements
            return base + (property.houses * property.face_value // 2)
