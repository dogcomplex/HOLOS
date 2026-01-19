"""
Tests for Exit Economics.

The right to exit is a constitutional invariant - it cannot be blocked.
These tests verify that:
1. Exit always succeeds (regardless of parent Enclave)
2. Exit costs are bounded and predictable
3. Mantles are properly forfeited
4. Name (reputation) travels with the exiting Holon
"""

import pytest
from holos.kernel import (
    create_holon, create_enclave, create_name,
    HolonStatus, EnclaveType, MembershipStatus,
    ExitSpec
)
from holos.kernel.enclave import MembershipRecord


class TestExitAlwaysSucceeds:
    """Constitutional invariant: Exit cannot be blocked."""

    def test_holon_can_exit_enclave(self):
        """A Holon can always exit its parent Enclave."""
        enclave = create_enclave()
        holon = create_holon(initial_balance=100)

        # Join enclave
        holon.parent_sheaf_id = enclave.enclave_id
        enclave.members[str(holon.holon_id.value)] = MembershipRecord(
            holon_id=holon.holon_id,
            status=MembershipStatus.ACTIVE,
        )

        # Exit
        result = enclave.process_exit(holon)

        assert result["success"] is True
        assert holon.status == HolonStatus.EXITED
        assert holon.parent_sheaf_id is None

    def test_exit_succeeds_even_with_zero_balance(self):
        """Holon can exit even with zero balance."""
        enclave = create_enclave()
        holon = create_holon(initial_balance=0)

        holon.parent_sheaf_id = enclave.enclave_id
        enclave.members[str(holon.holon_id.value)] = MembershipRecord(
            holon_id=holon.holon_id,
            status=MembershipStatus.ACTIVE,
        )

        result = enclave.process_exit(holon)

        assert result["success"] is True

    def test_exit_removes_from_delegation_graph(self):
        """Exiting Holon is removed from liquid democracy delegation."""
        enclave = create_enclave()
        holon1 = create_holon()
        holon2 = create_holon()

        # Set up memberships
        holon1.parent_sheaf_id = enclave.enclave_id
        holon2.parent_sheaf_id = enclave.enclave_id

        h1_id = str(holon1.holon_id.value)
        h2_id = str(holon2.holon_id.value)

        enclave.members[h1_id] = MembershipRecord(
            holon_id=holon1.holon_id, status=MembershipStatus.ACTIVE
        )
        enclave.members[h2_id] = MembershipRecord(
            holon_id=holon2.holon_id, status=MembershipStatus.ACTIVE
        )

        # Holon2 delegates to Holon1
        enclave.delegation_graph[h2_id] = h1_id

        # Holon1 exits
        result = enclave.process_exit(holon1)

        assert result["success"] is True
        # Delegation should be removed
        assert h2_id not in enclave.delegation_graph


class TestExitCosts:
    """Test that exit costs are bounded and predictable."""

    def test_exit_cost_calculated_correctly(self):
        """Exit cost is percentage of vault."""
        holon = create_holon(initial_balance=1000)
        holon.exit_protocol = ExitSpec(
            always_allowed=True,
            exit_cost_rate=0.05,  # 5%
        )
        holon.parent_sheaf_id = "enclave_1"

        result = holon.execute_exit("enclave_1")

        assert result.exit_cost == 50  # 5% of 1000
        assert holon.vault == 950

    def test_zero_exit_cost_by_default(self):
        """Default exit cost is zero."""
        holon = create_holon(initial_balance=1000)
        holon.parent_sheaf_id = "enclave_1"

        result = holon.execute_exit("enclave_1")

        assert result.exit_cost == 0
        assert holon.vault == 1000

    def test_exit_cost_cannot_exceed_vault(self):
        """Exit cost rate applied to vault, cannot take more than available."""
        holon = create_holon(initial_balance=100)
        holon.exit_protocol = ExitSpec(
            always_allowed=True,
            exit_cost_rate=0.10,  # 10%
        )
        holon.parent_sheaf_id = "enclave_1"

        result = holon.execute_exit("enclave_1")

        assert result.exit_cost == 10
        assert holon.vault == 90


class TestMantleForfeiture:
    """Test Mantle handling on exit."""

    def test_mantles_forfeited_on_exit(self):
        """Mantles stay behind when Holon exits."""
        holon = create_holon()
        holon.mantles = ["mantle_1", "mantle_2", "mantle_3"]
        holon.parent_sheaf_id = "enclave_1"

        result = holon.execute_exit("enclave_1")

        assert result.success is True
        assert len(result.mantles_lost) == 3
        assert holon.mantles == []

    def test_mantles_returned_to_enclave(self):
        """Forfeited mantles return to enclave ownership."""
        from holos.kernel.identity import Mantle, create_mantle

        enclave = create_enclave()
        holon = create_holon()

        # Create a mantle
        mantle = create_mantle(
            name="Test Mantle",
            issuing_sheaf_id=enclave.enclave_id,
            holder_holon_id=str(holon.holon_id.value),
        )

        # Assign to holon
        holon.mantles = [mantle.mantle_id]
        holon.parent_sheaf_id = enclave.enclave_id

        enclave.members[str(holon.holon_id.value)] = MembershipRecord(
            holon_id=holon.holon_id,
            status=MembershipStatus.ACTIVE,
        )
        enclave.enclave_mantles.append(mantle.mantle_id)

        # Exit
        result = enclave.process_exit(holon)

        assert result["success"] is True
        assert mantle.mantle_id in result["mantles_lost"]


class TestNameTravelsWithHolon:
    """Test that Name (reputation) travels on exit."""

    def test_name_preserved_after_exit(self):
        """Holon's Name is preserved after exit."""
        holon = create_holon()
        name = create_name(
            display_name="Test Entity",
            owner_holon_id=str(holon.holon_id.value),
        )
        name.reputation_score = 100.0
        name.contracts_completed = 50

        holon.name_id = name.name_id
        holon.parent_sheaf_id = "enclave_1"

        # Exit
        result = holon.execute_exit("enclave_1")

        # Name should still be attached
        assert holon.name_id == name.name_id
        # Reputation unchanged
        assert name.reputation_score == 100.0
        assert name.contracts_completed == 50

    def test_exit_count_incremented(self):
        """Name's exit_count is incremented on exit."""
        name = create_name(display_name="Traveler", owner_holon_id="holon_1")
        initial_exits = name.exit_count

        name.record_exit()

        assert name.exit_count == initial_exits + 1


class TestEnclaveExitProcessing:
    """Test Enclave-level exit handling."""

    def test_member_status_updated_on_exit(self):
        """Membership record updated when Holon exits."""
        enclave = create_enclave()
        holon = create_holon()

        holon.parent_sheaf_id = enclave.enclave_id
        h_id = str(holon.holon_id.value)
        enclave.members[h_id] = MembershipRecord(
            holon_id=holon.holon_id,
            status=MembershipStatus.ACTIVE,
        )

        result = enclave.process_exit(holon)

        assert result["success"] is True
        assert enclave.members[h_id].status == MembershipStatus.EXITED

    def test_non_member_cannot_exit(self):
        """Non-member cannot exit an Enclave."""
        enclave = create_enclave()
        holon = create_holon()

        # Holon is not a member
        result = enclave.process_exit(holon)

        assert result["success"] is False
        assert "not a member" in result["reason"].lower()

    def test_member_count_decreases_on_exit(self):
        """Active member count decreases after exit."""
        enclave = create_enclave()
        holon = create_holon()

        holon.parent_sheaf_id = enclave.enclave_id
        enclave.members[str(holon.holon_id.value)] = MembershipRecord(
            holon_id=holon.holon_id,
            status=MembershipStatus.ACTIVE,
        )

        initial_count = enclave.member_count
        enclave.process_exit(holon)
        final_count = enclave.member_count

        assert final_count == initial_count - 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
