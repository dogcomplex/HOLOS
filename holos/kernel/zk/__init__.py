"""
HOLOS ZK Proof System

Mock ZK proofs for economic testing without real cryptography.
Key design: Creation is expensive, verification is cheap.
"""

from .mock_proof import (
    MockZKProof,
    ProofStatement,
    StatementType,
    MockProver,
    MockVerifier,
    create_prover,
    create_verifier,
)

__all__ = [
    'MockZKProof',
    'ProofStatement',
    'StatementType',
    'MockProver',
    'MockVerifier',
    'create_prover',
    'create_verifier',
]
