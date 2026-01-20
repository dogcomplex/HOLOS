"""
HOLOS Core - Essential Exports

This module re-exports all core types from kernel and protocol layers.
Import from here for a clean, unified interface.

Usage:
    from holos.core import Holon, Enclave, Contract, Name, Mantle
    from holos.core import FlowRouter, ConstitutionalChecker
    from holos.core import StatementType, MockProver, MockVerifier
"""

# =============================================================================
# KERNEL EXPORTS - Source of Truth
# =============================================================================

# Holon - Fundamental identity unit
from holos.kernel.holon import (
    Holon,
    HolonId,
    HolonStatus,
    Constitution,
    ExitSpec,
    ExitResult,
    WakeCondition,
    MethodSpec,
    create_holon,
)

# Identity - Name (portable reputation) and Mantle (transferable authority)
from holos.kernel.identity import (
    Name,
    Mantle,
    RootType,
    Right,
    Responsibility,
    NameRegistry,
    MantleRegistry,
    create_name,
    create_mantle,
)

# Constitution - The 5 immutable invariants
from holos.kernel.constitution import (
    InvariantType,
    ViolationSeverity,
    InvariantViolation,
    InvariantCheck,
    ConstitutionalReport,
    ConstitutionalChecker,
    DEFAULT_CONSTITUTION,
    create_checker,
)

# Enclave - Fractal group structure
from holos.kernel.enclave import (
    Enclave,
    EnclaveType,
    EnclaveScale,
    VotingMechanism,
    MembershipStatus,
    MembershipRecord,
    DistributionMethod,
    FlowRouter,
    Vote,
    Proposal,
    create_enclave,
)

# Contract - Cooperation primitive
from holos.kernel.contract import (
    Contract,
    ContractType,
    ContractStatus,
    EnforcementType,
    ObligationType,
    Obligation,
    ExitCondition,
    Signature,
    ALWAYS_EXIT,
    GRACEFUL_EXIT,
    create_exchange_contract,
    create_membership_contract,
)

# ZK Proofs - Mock ZK system
from holos.kernel.zk.mock_proof import (
    StatementType,
    ProofStatement,
    MockZKProof,
    VerificationResult,
    MockProver,
    MockVerifier,
    create_prover,
    create_verifier,
    estimate_proof_cost,
    is_proof_economically_viable,
)

# =============================================================================
# PROTOCOL EXPORTS - Economic Implementation
# =============================================================================

from holos.protocol.collective_protocol import (
    # Protocol-specific scale enum (uses auto() for values)
    EnclaveScale as ProtocolEnclaveScale,

    # Protocol ZK system (simplified)
    StatementType as ProtocolStatementType,
    ZKProof,
    ZKProofSystem,

    # Protocol identity
    RootType as ProtocolRootType,
    SovereignIdentity,

    # Protocol value layer
    StakePosition,
    WealthBracket,
    ProgressiveFeeSchedule,
    FlowRouter as ProtocolFlowRouter,
    UBIPool,

    # Protocol trading
    LiquidityPool,
    AtomicSwap,

    # Protocol information
    EncryptedInfoPacket,
    PredictionMarket,

    # Protocol governance
    QuadraticVote,
    CollectiveParameters,

    # Protocol constitutional
    ConstitutionalInvariant,
    ConstitutionalChecker as ProtocolConstitutionalChecker,

    # Protocol enclave (alias for Collective)
    Enclave as ProtocolEnclave,
    Collective,
    calculate_enclave_value,
    calculate_collective_value,
)

# Protocol simulation
from holos.protocol.small_collective_sim import (
    SimulatedAgent,
    SmallCollectiveSimulation,
    SmallCollectiveMetrics,
    test_small_collective,
    test_scaling,
)

# =============================================================================
# CONVENIENCE ALIASES
# =============================================================================

# For simple usage, kernel types are primary
# Protocol types are available with Protocol prefix

__all__ = [
    # Kernel - Holon
    "Holon", "HolonId", "HolonStatus", "Constitution", "ExitSpec",
    "ExitResult", "WakeCondition", "MethodSpec", "create_holon",

    # Kernel - Identity
    "Name", "Mantle", "RootType", "Right", "Responsibility",
    "NameRegistry", "MantleRegistry", "create_name", "create_mantle",

    # Kernel - Constitution
    "InvariantType", "ViolationSeverity", "InvariantViolation",
    "InvariantCheck", "ConstitutionalReport", "ConstitutionalChecker",
    "DEFAULT_CONSTITUTION", "create_checker",

    # Kernel - Enclave
    "Enclave", "EnclaveType", "EnclaveScale", "VotingMechanism",
    "MembershipStatus", "MembershipRecord", "DistributionMethod",
    "FlowRouter", "Vote", "Proposal", "create_enclave",

    # Kernel - Contract
    "Contract", "ContractType", "ContractStatus", "EnforcementType",
    "ObligationType", "Obligation", "ExitCondition", "Signature",
    "ALWAYS_EXIT", "GRACEFUL_EXIT",
    "create_exchange_contract", "create_membership_contract",

    # Kernel - ZK
    "StatementType", "ProofStatement", "MockZKProof", "VerificationResult",
    "MockProver", "MockVerifier", "create_prover", "create_verifier",
    "estimate_proof_cost", "is_proof_economically_viable",

    # Protocol - Enclave
    "ProtocolEnclave", "Collective", "ProtocolEnclaveScale",
    "calculate_enclave_value", "calculate_collective_value",

    # Protocol - ZK
    "ProtocolStatementType", "ZKProof", "ZKProofSystem",

    # Protocol - Identity
    "ProtocolRootType", "SovereignIdentity",

    # Protocol - Value
    "StakePosition", "WealthBracket", "ProgressiveFeeSchedule",
    "ProtocolFlowRouter", "UBIPool",

    # Protocol - Trading
    "LiquidityPool", "AtomicSwap",

    # Protocol - Information
    "EncryptedInfoPacket", "PredictionMarket",

    # Protocol - Governance
    "QuadraticVote", "CollectiveParameters",

    # Protocol - Constitutional
    "ConstitutionalInvariant", "ProtocolConstitutionalChecker",

    # Protocol - Simulation
    "SimulatedAgent", "SmallCollectiveSimulation", "SmallCollectiveMetrics",
    "test_small_collective", "test_scaling",
]
