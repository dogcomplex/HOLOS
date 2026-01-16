"""Tests for the economics engine."""

import pytest
from kernel.models import (
    GameConfig, GameState, Player, Property, PropertyId,
    TaxTiming, GameStatus
)
from kernel.economics import EconomicsEngine


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
    """Create a basic game state."""
    players = {
        "player_0": Player(
            id="player_0",
            balance=1500,
            archetype="Slumlord",
        ),
        "player_1": Player(
            id="player_1",
            balance=1500,
            archetype="Squatter",
        ),
    }

    prop_id = PropertyId(board=0, tile=1)
    properties = {
        prop_id: Property(
            id=prop_id,
            name="Mediterranean Avenue",
            tile_type="property",
            color_group="brown",
            face_value=60,
            owner_id="player_0",
            valuation=100,
        )
    }
    players["player_0"].properties.append(prop_id)

    return GameState(
        config=basic_config,
        turn=1,
        players=players,
        properties=properties,
        community_pot=0,
        current_player_id="player_0",
        player_order=["player_0", "player_1"],
    )


class TestTaxCalculation:
    """Test tax calculation."""

    def test_effective_tax_rate_on_go(self, basic_config):
        """Tax rate should be full rate for on_go timing."""
        engine = EconomicsEngine(basic_config)
        assert engine.effective_tax_rate == 0.10

    def test_effective_tax_rate_per_turn(self, basic_config):
        """Tax rate should be reduced for per_turn timing."""
        basic_config.tax_timing = TaxTiming.PER_TURN
        engine = EconomicsEngine(basic_config)
        # Should be 0.10 / 10 = 0.01
        assert engine.effective_tax_rate == 0.01

    def test_tax_collection_on_go(self, basic_config, basic_game_state):
        """Tax should be collected when passing GO."""
        engine = EconomicsEngine(basic_config)
        player = basic_game_state.players["player_0"]

        # Player has $100 valuation, 10% tax = $10
        result = engine.process_pass_go(basic_game_state, player)

        assert result.success
        # Salary ($200) - Tax ($10) = net +$190
        assert player.balance == 1500 + 200 - 10
        assert basic_game_state.community_pot == 10

    def test_tax_bankruptcy(self, basic_config, basic_game_state):
        """Player should go bankrupt if can't afford tax."""
        engine = EconomicsEngine(basic_config)
        player = basic_game_state.players["player_0"]
        player.balance = 5  # Can't afford $10 tax

        # Set high valuation to trigger bankruptcy
        prop_id = PropertyId(board=0, tile=1)
        basic_game_state.properties[prop_id].valuation = 1000  # $100 tax

        result = engine.process_pass_go(basic_game_state, player)

        # Should still collect salary, then fail on tax
        assert result.bankruptcy


class TestRentCalculation:
    """Test rent calculation."""

    def test_basic_rent(self, basic_config, basic_game_state):
        """Rent should be 10% of valuation."""
        engine = EconomicsEngine(basic_config)
        prop_id = PropertyId(board=0, tile=1)
        property = basic_game_state.properties[prop_id]

        rent = engine.calculate_rent(property, basic_game_state)

        # Valuation is $100, rent = 10% = $10
        assert rent == 10

    def test_rent_payment(self, basic_config, basic_game_state):
        """Rent should transfer from payer to owner."""
        engine = EconomicsEngine(basic_config)
        payer = basic_game_state.players["player_1"]
        prop_id = PropertyId(board=0, tile=1)
        property = basic_game_state.properties[prop_id]

        result = engine.process_rent_payment(
            basic_game_state, payer, property
        )

        assert result.success
        assert payer.balance == 1500 - 10  # Paid $10 rent
        assert basic_game_state.players["player_0"].balance == 1500 + 10  # Received rent


class TestDividend:
    """Test dividend distribution."""

    def test_dividend_distribution(self, basic_config, basic_game_state):
        """Dividend should be distributed from pot."""
        engine = EconomicsEngine(basic_config)
        basic_game_state.community_pot = 100
        player = basic_game_state.players["player_0"]

        result = engine.process_pass_go(basic_game_state, player)

        # Pot splits between 2 players = $50 each
        # But player_0 also paid tax...
        assert result.success
        # Check that pot was reduced
        assert basic_game_state.community_pot < 100


class TestPropertyPurchase:
    """Test property purchase."""

    def test_buy_unowned_property(self, basic_config, basic_game_state):
        """Should be able to buy unowned property."""
        engine = EconomicsEngine(basic_config)

        # Add an unowned property
        prop_id = PropertyId(board=0, tile=3)
        basic_game_state.properties[prop_id] = Property(
            id=prop_id,
            name="Baltic Avenue",
            tile_type="property",
            color_group="brown",
            face_value=60,
        )

        buyer = basic_game_state.players["player_1"]
        property = basic_game_state.properties[prop_id]

        result = engine.process_property_purchase(
            basic_game_state, buyer, property
        )

        assert result.success
        assert property.owner_id == "player_1"
        assert property.valuation == 60  # Initial valuation = price
        assert buyer.balance == 1500 - 60

    def test_cannot_buy_owned_property(self, basic_config, basic_game_state):
        """Should not be able to buy already owned property (use Harberger)."""
        engine = EconomicsEngine(basic_config)
        buyer = basic_game_state.players["player_1"]
        prop_id = PropertyId(board=0, tile=1)
        property = basic_game_state.properties[prop_id]

        result = engine.process_property_purchase(
            basic_game_state, buyer, property
        )

        assert not result.success
        assert "already owned" in result.message.lower()
