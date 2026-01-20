"""
HOLOS Kernel - Sovereign Computing Simulation

Core abstractions for modeling ZK-proof bubbles (Holons) with:
- Names (persistent identity + reputation)
- Mantles (transferable authority)
- Contracts (cooperation primitive)
- Enclaves (compositional governance, fractal groups)
- FlowRouter (flow-through economics - no treasury accumulation)
- CrowdfundPool (voluntary funding for large projects)

Taxonomy by scale:
- Enclave: Base grouping (any size)
- Collective: 100+ members
- Kingdom: 1000+ members

Key economic principle: Taxes flow DOWN as UBI, not UP to a treasury.
"""

from .holon import Holon, HolonId, HolonStatus, Constitution, ExitSpec, create_holon
from .identity import Name, Mantle, RootType, create_name, create_mantle
from .contract import Contract, ContractType, ContractStatus, Obligation, ExitCondition
from .constitution import (
    ConstitutionalChecker, InvariantType, InvariantViolation,
    ConstitutionalReport, ViolationSeverity, create_checker
)
from .enclave import (
    Enclave, EnclaveType, EnclaveScale, MembershipRecord, MembershipStatus,
    FlowRouter, DistributionMethod, VotingMechanism, Proposal, Vote,
    create_enclave,
    Treasury,  # Legacy alias for FlowRouter
)
from .crowdfund import (
    CrowdfundPool, PoolStatus, PoolType, PoolRegistry, Contribution,
    create_pool
)

__all__ = [
    # Holon
    'Holon', 'HolonId', 'HolonStatus', 'Constitution', 'ExitSpec', 'create_holon',
    # Identity
    'Name', 'Mantle', 'RootType', 'create_name', 'create_mantle',
    # Contract
    'Contract', 'ContractType', 'ContractStatus', 'Obligation', 'ExitCondition',
    # Constitution
    'ConstitutionalChecker', 'InvariantType', 'InvariantViolation',
    'ConstitutionalReport', 'ViolationSeverity', 'create_checker',
    # Enclave
    'Enclave', 'EnclaveType', 'EnclaveScale', 'MembershipRecord', 'MembershipStatus',
    'FlowRouter', 'DistributionMethod', 'VotingMechanism', 'Proposal', 'Vote',
    'create_enclave',
    'Treasury',  # Legacy alias
    # Crowdfund
    'CrowdfundPool', 'PoolStatus', 'PoolType', 'PoolRegistry', 'Contribution',
    'create_pool',
]
