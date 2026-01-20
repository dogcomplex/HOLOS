"""
HOLOS Protocol - Fractal Economic Sovereignty

Core protocol primitives for building collectives that scale
from 10 people to global while maintaining sovereignty.
"""

from .collective_protocol import (
    # ZK Primitives
    ZKProof,
    ZKProofSystem,

    # Identity
    SovereignIdentity,

    # Value Layer
    StakePosition,
    WealthBracket,
    ProgressiveFeeSchedule,
    UBIPool,

    # Trading Layer
    LiquidityPool,
    AtomicSwap,

    # Information Layer
    EncryptedInfoPacket,
    PredictionMarket,

    # Governance
    QuadraticVote,
    CollectiveParameters,

    # The Collective
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
    # ZK
    "ZKProof",
    "ZKProofSystem",

    # Identity
    "SovereignIdentity",

    # Value
    "StakePosition",
    "WealthBracket",
    "ProgressiveFeeSchedule",
    "UBIPool",

    # Trading
    "LiquidityPool",
    "AtomicSwap",

    # Information
    "EncryptedInfoPacket",
    "PredictionMarket",

    # Governance
    "QuadraticVote",
    "CollectiveParameters",

    # Collective
    "Collective",
    "calculate_collective_value",

    # Simulation
    "SimulatedAgent",
    "SmallCollectiveSimulation",
    "SmallCollectiveMetrics",
    "test_small_collective",
    "test_scaling",
]
