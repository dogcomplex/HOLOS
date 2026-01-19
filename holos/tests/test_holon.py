"""
Tests for Holon lifecycle and basic operations.
"""

import pytest
from holos.kernel import (
    Holon, HolonId, HolonStatus, Constitution, ExitSpec,
    create_holon
)


class TestHolonCreation:
    """Test Holon creation and initialization."""

    def test_create_holon_default(self):
        """Create a Holon with default parameters."""
        holon = create_holon()

        assert holon.holon_id is not None
        assert holon.vault == 0
        assert holon.valuation == 0
        assert holon.status == HolonStatus.CALCIFIED
        assert holon.is_active()

    def test_create_holon_with_balance(self):
        """Create a Holon with initial balance."""
        holon = create_holon(initial_balance=1000)

        assert holon.vault == 1000
        assert holon._private_balance == 1000
        assert holon.is_solvent()

    def test_create_holon_with_valuation(self):
        """Create a Holon with Harberger valuation."""
        holon = create_holon(initial_balance=500, valuation=1000)

        assert holon.vault == 500
        assert holon.valuation == 1000
        assert holon.net_worth() == 1500  # vault + valuation

    def test_holon_id_uniqueness(self):
        """Each Holon gets a unique ID."""
        holon1 = create_holon()
        holon2 = create_holon()

        assert holon1.holon_id != holon2.holon_id

    def test_holon_state_hash_updates(self):
        """State hash changes when private state changes."""
        holon = create_holon(initial_balance=100)
        initial_hash = holon.state_hash

        holon._private_balance = 200
        holon._update_state_hash()

        assert holon.state_hash != initial_hash


class TestHolonLifecycle:
    """Test Holon hydration and calcification."""

    def test_hydrate_from_calcified(self):
        """Holon can be hydrated from calcified state."""
        holon = create_holon()
        assert holon.status == HolonStatus.CALCIFIED

        result = holon.hydrate()

        assert result is True
        assert holon.status == HolonStatus.HYDRATED

    def test_hydrate_bankrupt_fails(self):
        """Bankrupt Holon cannot be hydrated."""
        holon = create_holon()
        holon.status = HolonStatus.BANKRUPT

        result = holon.hydrate()

        assert result is False
        assert holon.status == HolonStatus.BANKRUPT

    def test_calcify_saves_state(self):
        """Calcification updates state hash."""
        holon = create_holon(initial_balance=100)
        holon.hydrate()

        holon._private_balance = 200
        holon.calcify()

        assert holon.status == HolonStatus.CALCIFIED
        # State hash should reflect the new balance
        assert holon.state_hash != ""


class TestHolonFinancials:
    """Test Holon financial operations."""

    def test_deposit(self):
        """Deposit adds to vault."""
        holon = create_holon(initial_balance=100)

        holon.deposit(50)

        assert holon.vault == 150

    def test_withdraw_success(self):
        """Withdraw removes from vault when sufficient funds."""
        holon = create_holon(initial_balance=100)

        result = holon.withdraw(30)

        assert result is True
        assert holon.vault == 70

    def test_withdraw_insufficient(self):
        """Withdraw fails when insufficient funds."""
        holon = create_holon(initial_balance=100)

        result = holon.withdraw(200)

        assert result is False
        assert holon.vault == 100  # Unchanged

    def test_set_valuation(self):
        """Set Harberger self-assessment."""
        holon = create_holon()

        holon.set_valuation(500)

        assert holon.valuation == 500

    def test_set_valuation_negative_clamps(self):
        """Valuation cannot be negative."""
        holon = create_holon()

        holon.set_valuation(-100)

        assert holon.valuation == 0


class TestHolonPublicView:
    """Test Holon public view generation."""

    def test_public_view_contains_public_fields(self):
        """Public view shows public information."""
        holon = create_holon(initial_balance=100, valuation=200)
        holon.name_id = "test_name"

        view = holon.to_public_view()

        assert "holon_id" in view
        assert view["vault"] == 100
        assert view["valuation"] == 200
        assert view["name_id"] == "test_name"
        assert view["status"] == "CALCIFIED"

    def test_public_view_hides_private_balance(self):
        """Private balance is not in public view."""
        holon = create_holon(initial_balance=100)
        holon._private_balance = 500  # Different from vault

        view = holon.to_public_view()

        assert "_private_balance" not in view
        assert view["vault"] == 100  # Only public vault shown


class TestHolonExit:
    """Test Holon exit functionality."""

    def test_can_exit_default(self):
        """By default, exit is always possible (constitutional invariant)."""
        holon = create_holon()

        assert holon.can_exit() is True

    def test_execute_exit_success(self):
        """Holon can exit its parent enclave."""
        holon = create_holon(initial_balance=100)
        holon.parent_sheaf_id = "enclave_123"
        holon.mantles = ["mantle_1", "mantle_2"]

        result = holon.execute_exit("enclave_123")

        assert result.success is True
        assert holon.status == HolonStatus.EXITED
        assert holon.parent_sheaf_id is None
        assert holon.mantles == []  # Mantles forfeited
        assert len(result.mantles_lost) == 2

    def test_execute_exit_wrong_enclave(self):
        """Exit fails if from wrong enclave."""
        holon = create_holon()
        holon.parent_sheaf_id = "enclave_123"

        result = holon.execute_exit("enclave_456")

        assert result.success is False
        assert holon.status != HolonStatus.EXITED

    def test_exit_cost_deducted(self):
        """Exit cost is deducted from vault."""
        holon = create_holon(initial_balance=1000)
        holon.parent_sheaf_id = "enclave_123"
        holon.exit_protocol = ExitSpec(
            always_allowed=True,
            exit_cost_rate=0.10,  # 10% exit fee
        )

        result = holon.execute_exit("enclave_123")

        assert result.success is True
        assert result.exit_cost == 100  # 10% of 1000
        assert holon.vault == 900


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
