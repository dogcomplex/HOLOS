"""
HOLOS Protocol - Fractal Economic Sovereignty

Core protocol primitives for building enclaves that scale
from 10 people to global while maintaining sovereignty.

Aligned with holos/kernel/ naming conventions:
- Enclave: Base group (<100 members)
- Collective: Mid-scale (100-999 members)
- Kingdom: Large-scale (1000+ members)

Constitutional Invariants:
1. Non-Blocking Exit - Sub-Holon can detach without parent permission
2. Proof of Solvency - SUM(Inputs) >= SUM(Outputs)
3. Explicit Consent - Membership requires bilateral consent
4. Sybil Resistance - Voting weight proportional to proven root
5. Legible Interface - Public methods standardized
"""

from .collective_protocol import (
    # Scale Taxonomy (aligned with kernel)
    EnclaveScale,

    # ZK Primitives (aligned with kernel/zk/)
    StatementType,
    ZKProof,
    ZKProofSystem,

    # Identity (aligned with kernel/identity.py)
    RootType,
    SovereignIdentity,

    # Value Layer
    StakePosition,
    WealthBracket,
    ProgressiveFeeSchedule,
    FlowRouter,  # New: flow-through UBI
    UBIPool,     # Backward compat alias

    # Trading Layer
    LiquidityPool,
    AtomicSwap,

    # Information Layer
    EncryptedInfoPacket,
    PredictionMarket,

    # Governance
    QuadraticVote,
    CollectiveParameters,

    # Constitutional (aligned with kernel/constitution.py)
    ConstitutionalInvariant,
    ConstitutionalChecker,

    # The Enclave (primary, aligned with kernel)
    Enclave,
    calculate_enclave_value,

    # Backward compatibility aliases
    Collective,
    calculate_collective_value,
)

from .small_collective_sim import (
    SimulatedAgent,
    SmallCollectiveSimulation,
    SmallCollectiveMetrics,
    test_small_collective,
    test_scaling,
)

__all__ = [
    # Scale Taxonomy
    "EnclaveScale",

    # ZK
    "StatementType",
    "ZKProof",
    "ZKProofSystem",

    # Identity
    "RootType",
    "SovereignIdentity",

    # Value
    "StakePosition",
    "WealthBracket",
    "ProgressiveFeeSchedule",
    "FlowRouter",
    "UBIPool",  # Backward compat

    # Trading
    "LiquidityPool",
    "AtomicSwap",

    # Information
    "EncryptedInfoPacket",
    "PredictionMarket",

    # Governance
    "QuadraticVote",
    "CollectiveParameters",

    # Constitutional
    "ConstitutionalInvariant",
    "ConstitutionalChecker",

    # Enclave (primary)
    "Enclave",
    "calculate_enclave_value",

    # Backward compat aliases
    "Collective",
    "calculate_collective_value",

    # Simulation
    "SimulatedAgent",
    "SmallCollectiveSimulation",
    "SmallCollectiveMetrics",
    "test_small_collective",
    "test_scaling",
]
