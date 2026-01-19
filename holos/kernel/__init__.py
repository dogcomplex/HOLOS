"""
HOLOS Kernel - Sovereign Computing Simulation

Core abstractions for modeling ZK-proof bubbles (Holons) with:
- Names (persistent identity + reputation)
- Mantles (transferable authority)
- Contracts (cooperation primitive)
- Sheafs (compositional governance)
"""

from .holon import Holon, HolonId, HolonStatus
from .identity import Name, Mantle, RootType
from .contract import Contract, ContractType, ContractStatus, Obligation, ExitCondition
from .constitution import (
    ConstitutionalChecker, InvariantType, InvariantViolation,
    ConstitutionalReport, ViolationSeverity, create_checker
)

__all__ = [
    'Holon', 'HolonId', 'HolonStatus',
    'Name', 'Mantle', 'RootType',
    'Contract', 'ContractType', 'ContractStatus', 'Obligation', 'ExitCondition',
    'ConstitutionalChecker', 'InvariantType', 'InvariantViolation',
    'ConstitutionalReport', 'ViolationSeverity', 'create_checker',
]
