"""
HOLOS Kernel - Sovereign Computing Simulation

Core abstractions for modeling ZK-proof bubbles (Holons) with:
- Names (persistent identity + reputation)
- Mantles (transferable authority)
- Contracts (cooperation primitive)
- Enclaves (compositional governance, fractal groups)

Taxonomy by scale:
- Enclave: Base grouping (any size)
- Collective: 100+ members
- Kingdom: 1000+ members
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
    Treasury, DividendPolicy, VotingMechanism, Proposal, Vote,
    create_enclave
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
    'Treasury', 'DividendPolicy', 'VotingMechanism', 'Proposal', 'Vote',
    'create_enclave',
]
