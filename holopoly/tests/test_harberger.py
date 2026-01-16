"""Tests for Harberger mechanics."""

import pytest
from kernel.models import (
    GameConfig, GameState, Player, Property, PropertyId,
    TaxTiming, GameStatus
)
from kernel.harberger import HarbergerEngine


@pytest.fixture
def basic_config():
    """Create a basic game configuration."""
    return GameConfig(
        game_id="test_game",
        max_turns=100,
        num_boards=1,
        num_players=4,
        starting_balance=1500,
        archetypes=["Slumlord", "Squatter", "Flipper", "Developer"],
        tax_timing=TaxTiming.ON_GO,
        dividend_timing=TaxTiming.ON_GO,
        tax_rate=0.10,
        rent_rate=0.10,
        pass_go_salary=200,
        avg_circuit_length=10,
        harberger_enabled=True,
        force_buy_enabled=True,
        min_valuation=1,
        llm_model="stub",
        llm_stub_mode=True,
        llm_temperature=0.7,
        random_seed=42,
    )


@pytest.fixture
def basic_game_state(basic_config):
    """Create a basic game state with two players and one property."""
    players = {
        "player_0": Player(
            id="player_0",
            balance=1500,
            archetype="Slumlord",
        ),
        "player_1": Player(
            id="player_1",
            balance=1500,
            archetype="Flipper",
        ),
    }

    prop_id = PropertyId(board=0, tile=39)
    properties = {
        prop_id: Property(
            id=prop_id,
            name="Boardwalk",
            tile_type="property",
            color_group="blue",
            face_value=400,
            owner_id="player_0",
            valuation=500,
        )
    }
    players["player_0"].properties.append(prop_id)

    return GameState(
        config=basic_config,
        turn=1,
        players=players,
        properties=properties,
        community_pot=0,
        current_player_id="player_1",
        player_order=["player_0", "player_1"],
    )


class TestValuation:
    """Test valuation changes."""

    def test_set_valuation(self, basic_config, basic_game_state):
        """Owner should be able to set valuation."""
        engine = HarbergerEngine(basic_config)
        owner = basic_game_state.players["player_0"]
        prop_id = PropertyId(board=0, tile=39)

        result = engine.set_valuation(
            basic_game_state, owner, prop_id, 1000
        )

        assert result.success
        assert basic_game_state.properties[prop_id].valuation == 1000

    def test_min_valuation_enforced(self, basic_config, basic_game_state):
        """Valuation cannot be below minimum."""
        engine = HarbergerEngine(basic_config)
        owner = basic_game_state.players["player_0"]
        prop_id = PropertyId(board=0, tile=39)

        result = engine.set_valuation(
            basic_game_state, owner, prop_id, 0
        )

        assert result.success
        # Should be enforced to minimum
        assert basic_game_state.properties[prop_id].valuation == 1

    def test_non_owner_cannot_set_valuation(self, basic_config, basic_game_state):
        """Non-owner should not be able to set valuation."""
        engine = HarbergerEngine(basic_config)
        non_owner = basic_game_state.players["player_1"]
        prop_id = PropertyId(board=0, tile=39)

        result = engine.set_valuation(
            basic_game_state, non_owner, prop_id, 1000
        )

        assert not result.success
        assert "don't own" in result.message.lower()


class TestForcedSale:
    """Test Harberger forced sale mechanism."""

    def test_forced_sale_success(self, basic_config, basic_game_state):
        """Buyer should be able to force-buy at declared price."""
        engine = HarbergerEngine(basic_config)
        buyer = basic_game_state.players["player_1"]
        seller = basic_game_state.players["player_0"]
        prop_id = PropertyId(board=0, tile=39)

        # Valuation is $500, buyer has $1500
        result = engine.execute_forced_sale(
            basic_game_state, buyer, prop_id
        )

        assert result.success
        assert basic_game_state.properties[prop_id].owner_id == "player_1"
        assert buyer.balance == 1500 - 500  # Paid $500
        assert seller.balance == 1500 + 500  # Received $500
        assert prop_id in buyer.properties
        assert prop_id not in seller.properties

    def test_forced_sale_insufficient_funds(self, basic_config, basic_game_state):
        """Buyer should not be able to buy if insufficient funds."""
        engine = HarbergerEngine(basic_config)
        buyer = basic_game_state.players["player_1"]
        buyer.balance = 100  # Can't afford $500

        prop_id = PropertyId(board=0, tile=39)

        result = engine.execute_forced_sale(
            basic_game_state, buyer, prop_id
        )

        assert not result.success
        assert "cannot afford" in result.message.lower()

    def test_cannot_buy_own_property(self, basic_config, basic_game_state):
        """Owner should not be able to Harberger-buy their own property."""
        engine = HarbergerEngine(basic_config)
        owner = basic_game_state.players["player_0"]
        prop_id = PropertyId(board=0, tile=39)

        result = engine.execute_forced_sale(
            basic_game_state, owner, prop_id
        )

        assert not result.success
        assert "already own" in result.message.lower()

    def test_cannot_harberger_buy_unowned(self, basic_config, basic_game_state):
        """Cannot use Harberger buy on unowned property."""
        engine = HarbergerEngine(basic_config)
        buyer = basic_game_state.players["player_1"]

        # Add unowned property
        prop_id = PropertyId(board=0, tile=1)
        basic_game_state.properties[prop_id] = Property(
            id=prop_id,
            name="Mediterranean Avenue",
            tile_type="property",
            color_group="brown",
            face_value=60,
        )

        result = engine.execute_forced_sale(
            basic_game_state, buyer, prop_id
        )

        assert not result.success
        assert "not owned" in result.message.lower()


class TestBuyableProperties:
    """Test getting list of buyable properties."""

    def test_get_buyable_properties(self, basic_config, basic_game_state):
        """Should return properties buyer can afford to Harberger-buy."""
        engine = HarbergerEngine(basic_config)
        buyer = basic_game_state.players["player_1"]

        buyable = engine.get_buyable_properties(basic_game_state, buyer)

        assert len(buyable) == 1
        assert buyable[0]["name"] == "Boardwalk"
        assert buyable[0]["valuation"] == 500

    def test_no_buyable_if_broke(self, basic_config, basic_game_state):
        """Should return empty list if buyer can't afford anything."""
        engine = HarbergerEngine(basic_config)
        buyer = basic_game_state.players["player_1"]
        buyer.balance = 10

        buyable = engine.get_buyable_properties(basic_game_state, buyer)

        assert len(buyable) == 0


class TestValuationSuggestions:
    """Test valuation suggestion strategies."""

    def test_aggressive_valuation(self, basic_config, basic_game_state):
        """Aggressive strategy should suggest high valuation."""
        engine = HarbergerEngine(basic_config)
        prop_id = PropertyId(board=0, tile=39)
        property = basic_game_state.properties[prop_id]

        suggested = engine.suggest_valuation(
            property, basic_game_state, "aggressive"
        )

        # Face value $400, aggressive = 2x = $800
        assert suggested >= 800

    def test_conservative_valuation(self, basic_config, basic_game_state):
        """Conservative strategy should suggest low valuation."""
        engine = HarbergerEngine(basic_config)
        prop_id = PropertyId(board=0, tile=39)
        property = basic_game_state.properties[prop_id]

        suggested = engine.suggest_valuation(
            property, basic_game_state, "conservative"
        )

        # Should be low, but at least minimum
        assert suggested >= engine.min_valuation
        assert suggested < property.face_value
