"""
Tests for Flow-Through Economics.

Key principles being tested:
1. FlowRouter has NO balance (stateless routing)
2. Tax collection and UBI distribution are the SAME event
3. Stake-weighted distribution prevents Sybil attacks
4. CrowdfundPool enables voluntary project funding
"""

import pytest
from holos.kernel import (
    create_holon, create_enclave, create_pool,
    HolonId, FlowRouter, DistributionMethod, MembershipStatus,
    CrowdfundPool, PoolStatus, PoolType,
)
from holos.kernel.enclave import MembershipRecord


class TestFlowRouterStateless:
    """FlowRouter has no balance - just routes taxes to UBI."""

    def test_flow_router_has_no_balance(self):
        """FlowRouter does not accumulate a balance."""
        router = FlowRouter()

        # No balance attribute (or if exists, always 0)
        assert not hasattr(router, 'balance') or router.balance == 0

    def test_route_tax_returns_distribution(self):
        """route_tax immediately returns distribution dict."""
        router = FlowRouter(distribution_method=DistributionMethod.EQUAL)

        # Create mock members
        members = [
            MembershipRecord(holon_id=HolonId.generate(), status=MembershipStatus.ACTIVE, stake=100),
            MembershipRecord(holon_id=HolonId.generate(), status=MembershipStatus.ACTIVE, stake=100),
        ]

        distributions = router.route_tax(100, members)

        # Should return immediate distribution
        assert len(distributions) == 2
        assert sum(distributions.values()) == 100  # All routed, nothing held

    def test_total_routed_tracks_throughput(self):
        """total_routed tracks how much has flowed through."""
        router = FlowRouter()
        initial_routed = router.total_routed

        members = [
            MembershipRecord(holon_id=HolonId.generate(), status=MembershipStatus.ACTIVE, stake=100),
        ]

        router.route_tax(500, members)

        assert router.total_routed == initial_routed + 500


class TestStakeWeightedDistribution:
    """Stake-weighted UBI distribution prevents Sybil attacks."""

    def test_stake_weighted_favors_higher_stakes(self):
        """Higher stake = larger share of UBI."""
        router = FlowRouter(distribution_method=DistributionMethod.STAKE_WEIGHTED)

        h1 = HolonId.generate()
        h2 = HolonId.generate()

        members = [
            MembershipRecord(holon_id=h1, status=MembershipStatus.ACTIVE, stake=900),
            MembershipRecord(holon_id=h2, status=MembershipStatus.ACTIVE, stake=100),
        ]

        distributions = router.route_tax(1000, members)

        # h1 has 90% stake, should get ~90% of UBI
        assert distributions[h1] == 900
        assert distributions[h2] == 100

    def test_zero_stake_gets_nothing(self):
        """Zero stake members don't receive UBI (Sybil resistance)."""
        router = FlowRouter(distribution_method=DistributionMethod.STAKE_WEIGHTED)

        h1 = HolonId.generate()
        h2 = HolonId.generate()

        members = [
            MembershipRecord(holon_id=h1, status=MembershipStatus.ACTIVE, stake=100),
            MembershipRecord(holon_id=h2, status=MembershipStatus.ACTIVE, stake=0),  # Sybil node
        ]

        distributions = router.route_tax(100, members)

        assert distributions.get(h1, 0) == 100
        assert distributions.get(h2, 0) == 0  # Sybil gets nothing

    def test_sybil_attack_ineffective(self):
        """Creating many low-stake nodes doesn't increase total UBI received."""
        router = FlowRouter(distribution_method=DistributionMethod.STAKE_WEIGHTED)

        # Attacker has 100 total stake, honest user has 100
        attacker_nodes = [
            MembershipRecord(holon_id=HolonId.generate(), status=MembershipStatus.ACTIVE, stake=10)
            for _ in range(10)  # 10 nodes × 10 stake = 100 total
        ]
        honest_node = MembershipRecord(
            holon_id=HolonId.generate(), status=MembershipStatus.ACTIVE, stake=100
        )

        members = attacker_nodes + [honest_node]

        distributions = router.route_tax(1000, members)

        # Attacker's total share should equal honest user's
        attacker_total = sum(distributions.get(m.holon_id, 0) for m in attacker_nodes)
        honest_share = distributions.get(honest_node.holon_id, 0)

        assert attacker_total == honest_share  # Both 500


class TestEqualDistribution:
    """Equal distribution for high-trust small groups."""

    def test_equal_splits_evenly(self):
        """Equal distribution gives same amount to all."""
        router = FlowRouter(distribution_method=DistributionMethod.EQUAL)

        members = [
            MembershipRecord(holon_id=HolonId.generate(), status=MembershipStatus.ACTIVE, stake=1000),
            MembershipRecord(holon_id=HolonId.generate(), status=MembershipStatus.ACTIVE, stake=1),
        ]

        distributions = router.route_tax(100, members)

        # Both get equal shares regardless of stake
        shares = list(distributions.values())
        assert shares[0] == shares[1] == 50


class TestEnclaveFlowThrough:
    """Test flow-through at the Enclave level."""

    def test_collect_and_distribute_is_atomic(self):
        """Tax collection and UBI distribution happen in same call."""
        enclave = create_enclave(harberger_rate=0.10)

        # Create two holons
        h1 = create_holon(initial_balance=100, valuation=1000)
        h2 = create_holon(initial_balance=100, valuation=0)

        # Add as members with stakes
        enclave.approve_membership(h1.holon_id, h1)
        enclave.approve_membership(h2.holon_id, h2)

        holons = {
            str(h1.holon_id.value): h1,
            str(h2.holon_id.value): h2,
        }

        # Collect taxes (which immediately distributes UBI)
        result = enclave.collect_and_distribute_taxes(holons)

        # Tax was collected
        assert result["total_collected"] > 0

        # UBI was distributed in the same event
        assert len(result["distributions"]) > 0


class TestCrowdfundPool:
    """Test voluntary crowdfunding for large projects."""

    def test_create_pool(self):
        """Create a new crowdfund pool."""
        creator = HolonId.generate()

        pool = create_pool(
            name="Test Project",
            description="A test crowdfund",
            creator_id=creator,
            goal=1000,
            deadline=9999999999,
        )

        assert pool.name == "Test Project"
        assert pool.goal == 1000
        assert pool.status == PoolStatus.OPEN
        assert pool.total_raised == 0

    def test_contribute_to_pool(self):
        """Make voluntary contributions."""
        pool = create_pool(
            name="Test",
            description="Test",
            creator_id=HolonId.generate(),
            goal=1000,
            deadline=9999999999,
        )

        contributor = HolonId.generate()
        result = pool.contribute(contributor, 500)

        assert result is True
        assert pool.total_raised == 500
        assert pool.funding_percentage == 50.0

    def test_pool_reaches_goal(self):
        """Pool status changes when goal reached."""
        pool = create_pool(
            name="Test",
            description="Test",
            creator_id=HolonId.generate(),
            goal=100,
            deadline=9999999999,
        )

        pool.contribute(HolonId.generate(), 100)

        assert pool.is_funded is True
        assert pool.status == PoolStatus.FUNDED

    def test_all_or_nothing_refund(self):
        """ALL_OR_NOTHING pools refund if goal not reached."""
        pool = create_pool(
            name="Test",
            description="Test",
            creator_id=HolonId.generate(),
            goal=1000,
            deadline=1,  # Already past
            pool_type=PoolType.ALL_OR_NOTHING,
        )

        contributor = HolonId.generate()
        pool.contribute(contributor, 100)

        # Check deadline (simulating time passed)
        pool.check_deadline(current_time=2)

        assert pool.status == PoolStatus.FAILED

        # Request refund
        refund = pool.request_refund(contributor)
        assert refund == 100

    def test_multiple_contributors(self):
        """Pool tracks multiple contributors."""
        pool = create_pool(
            name="Test",
            description="Test",
            creator_id=HolonId.generate(),
            goal=1000,
            deadline=9999999999,
        )

        c1 = HolonId.generate()
        c2 = HolonId.generate()

        pool.contribute(c1, 300)
        pool.contribute(c2, 200)
        pool.contribute(c1, 100)  # c1 contributes again

        assert pool.total_raised == 600
        assert pool.contributor_count == 2
        assert pool.get_contribution(c1) == 400


class TestIntegration:
    """Integration tests for flow-through + crowdfunding."""

    def test_ubi_can_fund_crowdfund(self):
        """Holons can use UBI received to fund crowdfunds."""
        # This is the key flow:
        # Tax → UBI to individual → Individual voluntarily invests in pool

        enclave = create_enclave(harberger_rate=0.10)

        # Rich holon pays tax
        rich = create_holon(initial_balance=1000, valuation=10000)
        # Poor holon receives UBI
        poor = create_holon(initial_balance=100, valuation=0)

        enclave.approve_membership(rich.holon_id, rich)
        enclave.approve_membership(poor.holon_id, poor)

        holons = {
            str(rich.holon_id.value): rich,
            str(poor.holon_id.value): poor,
        }

        initial_poor_balance = poor.vault

        # Collect taxes (UBI distributed)
        enclave.collect_and_distribute_taxes(holons)

        # Poor holon received UBI
        assert poor.vault > initial_poor_balance

        # Now poor can voluntarily fund a crowdfund
        pool = create_pool(
            name="Community Project",
            description="Funded by UBI recipients",
            creator_id=poor.holon_id,
            goal=50,
            deadline=9999999999,
        )

        # Poor contributes some of their UBI
        ubi_received = poor.vault - initial_poor_balance
        pool.contribute(poor.holon_id, min(ubi_received, 50))

        assert pool.total_raised > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
