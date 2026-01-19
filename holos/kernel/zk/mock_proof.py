"""
Mock ZK Proof System

Simulates zero-knowledge proofs for testing economic dynamics without
real cryptography. Key asymmetry preserved:

- Proof CREATION is expensive (prover pays computation cost)
- Proof VERIFICATION is cheap (verifier pays minimal cost)

This allows us to test:
- Cost of privacy (how much does hiding information cost?)
- Value of selective disclosure (when is a proof worth creating?)
- Trust vs verification tradeoffs
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import hashlib
import time
import uuid


class StatementType(Enum):
    """Types of statements that can be proven via ZK."""

    # Financial proofs
    SOLVENCY = "SOLVENCY"          # "My balance >= X" without revealing exact balance
    RANGE = "RANGE"                 # "Value V is in range [A, B]"

    # Identity/membership proofs
    MEMBERSHIP = "MEMBERSHIP"       # "I am a member of Enclave E"
    IDENTITY = "IDENTITY"           # "I control Name N" without revealing Holon

    # Compliance proofs
    CONSTITUTIONAL = "CONSTITUTIONAL"  # "My action obeys Constitution C"
    CONTRACT = "CONTRACT"              # "I fulfilled Obligation O in Contract C"

    # Exit proofs
    EXIT_RIGHT = "EXIT_RIGHT"       # "I have the right to exit"
    EXIT_CLEAN = "EXIT_CLEAN"       # "I owe nothing to Enclave E"


@dataclass
class ProofStatement:
    """
    What a ZK proof asserts, without revealing the witness.

    Example:
        statement = ProofStatement(
            statement_type=StatementType.SOLVENCY,
            public_inputs={"threshold": 1000},
            claim="My balance is at least 1000"
        )
    """
    statement_type: StatementType
    public_inputs: Dict[str, Any] = field(default_factory=dict)
    claim: str = ""

    def to_hash(self) -> str:
        """Hash the statement for verification."""
        content = f"{self.statement_type.value}:{sorted(self.public_inputs.items())}:{self.claim}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class MockZKProof:
    """
    A simulated ZK proof.

    In production, this would be a real cryptographic proof.
    In simulation, we store the witness but pretend it's hidden.

    The economics are preserved:
    - Creation cost is proportional to proof complexity
    - Verification cost is minimal and constant
    """
    proof_id: str
    prover_id: str                 # Holon that created this proof
    statement: ProofStatement      # What is being proven (public)

    # Witness - the actual values (normally hidden in real ZK)
    # In mock, we keep these for simulation but treat them as private
    _witness: Dict[str, Any] = field(default_factory=dict)

    # Proof validity
    valid: bool = True             # Did the witness satisfy the statement?

    # Economics
    creation_cost: int = 0         # Prover paid this to create
    verification_cost: int = 1     # Verifier pays this (always cheap)

    # Metadata
    created_at: int = field(default_factory=lambda: int(time.time()))
    expires_at: Optional[int] = None  # Some proofs expire

    @property
    def is_expired(self) -> bool:
        """Check if proof has expired."""
        if self.expires_at is None:
            return False
        return int(time.time()) > self.expires_at

    def to_public_view(self) -> Dict[str, Any]:
        """What a verifier can see (no witness)."""
        return {
            "proof_id": self.proof_id,
            "prover_id": self.prover_id,
            "statement_type": self.statement.statement_type.value,
            "statement_hash": self.statement.to_hash(),
            "claim": self.statement.claim,
            "public_inputs": self.statement.public_inputs,
            "valid": self.valid,
            "creation_cost": self.creation_cost,
            "is_expired": self.is_expired,
        }


@dataclass
class VerificationResult:
    """Result of verifying a ZK proof."""
    proof_id: str
    valid: bool
    verification_cost: int
    message: str = ""
    verified_at: int = field(default_factory=lambda: int(time.time()))


class MockProver:
    """
    Creates ZK proofs (expensive operation).

    Simulates the asymmetric cost structure of real ZK systems:
    - Simple proofs (solvency, membership): ~10 cost units
    - Complex proofs (constitutional compliance): ~100 cost units
    - Aggregate proofs (batch of simple proofs): ~50 cost units
    """

    # Cost table by statement type
    BASE_COSTS: Dict[StatementType, int] = {
        StatementType.SOLVENCY: 10,
        StatementType.RANGE: 15,
        StatementType.MEMBERSHIP: 10,
        StatementType.IDENTITY: 20,
        StatementType.CONSTITUTIONAL: 100,
        StatementType.CONTRACT: 50,
        StatementType.EXIT_RIGHT: 10,
        StatementType.EXIT_CLEAN: 30,
    }

    def __init__(self, prover_id: str):
        self.prover_id = prover_id
        self.proofs_created: List[str] = []
        self.total_cost_paid: int = 0

    def create_solvency_proof(
        self,
        actual_balance: int,
        threshold: int,
        expiry_turns: Optional[int] = None
    ) -> MockZKProof:
        """
        Prove: "My balance >= threshold" without revealing actual balance.
        """
        valid = actual_balance >= threshold
        cost = self.BASE_COSTS[StatementType.SOLVENCY]

        statement = ProofStatement(
            statement_type=StatementType.SOLVENCY,
            public_inputs={"threshold": threshold},
            claim=f"Balance is at least {threshold}"
        )

        proof = MockZKProof(
            proof_id=f"prf_{uuid.uuid4().hex[:8]}",
            prover_id=self.prover_id,
            statement=statement,
            _witness={"actual_balance": actual_balance},
            valid=valid,
            creation_cost=cost,
            expires_at=int(time.time()) + expiry_turns if expiry_turns else None,
        )

        self.proofs_created.append(proof.proof_id)
        self.total_cost_paid += cost

        return proof

    def create_membership_proof(
        self,
        enclave_id: str,
        is_member: bool,
        member_since: Optional[int] = None
    ) -> MockZKProof:
        """
        Prove: "I am a member of Enclave E" without revealing my Holon ID.
        """
        cost = self.BASE_COSTS[StatementType.MEMBERSHIP]

        statement = ProofStatement(
            statement_type=StatementType.MEMBERSHIP,
            public_inputs={"enclave_id": enclave_id},
            claim=f"Is member of enclave {enclave_id[:8]}"
        )

        proof = MockZKProof(
            proof_id=f"prf_{uuid.uuid4().hex[:8]}",
            prover_id=self.prover_id,
            statement=statement,
            _witness={"is_member": is_member, "member_since": member_since},
            valid=is_member,
            creation_cost=cost,
        )

        self.proofs_created.append(proof.proof_id)
        self.total_cost_paid += cost

        return proof

    def create_constitutional_proof(
        self,
        constitution_hash: str,
        action_description: str,
        is_compliant: bool,
        invariants_checked: List[str]
    ) -> MockZKProof:
        """
        Prove: "My action complies with Constitution C" (expensive proof).
        """
        cost = self.BASE_COSTS[StatementType.CONSTITUTIONAL]

        statement = ProofStatement(
            statement_type=StatementType.CONSTITUTIONAL,
            public_inputs={
                "constitution_hash": constitution_hash,
                "action": action_description,
            },
            claim=f"Action '{action_description}' complies with constitution"
        )

        proof = MockZKProof(
            proof_id=f"prf_{uuid.uuid4().hex[:8]}",
            prover_id=self.prover_id,
            statement=statement,
            _witness={
                "is_compliant": is_compliant,
                "invariants_checked": invariants_checked,
            },
            valid=is_compliant,
            creation_cost=cost,
        )

        self.proofs_created.append(proof.proof_id)
        self.total_cost_paid += cost

        return proof

    def create_exit_right_proof(
        self,
        enclave_id: str,
        has_right: bool,
        exit_conditions_met: List[str]
    ) -> MockZKProof:
        """
        Prove: "I have the right to exit Enclave E".
        """
        cost = self.BASE_COSTS[StatementType.EXIT_RIGHT]

        statement = ProofStatement(
            statement_type=StatementType.EXIT_RIGHT,
            public_inputs={"enclave_id": enclave_id},
            claim=f"Has right to exit enclave {enclave_id[:8]}"
        )

        proof = MockZKProof(
            proof_id=f"prf_{uuid.uuid4().hex[:8]}",
            prover_id=self.prover_id,
            statement=statement,
            _witness={
                "has_right": has_right,
                "conditions_met": exit_conditions_met,
            },
            valid=has_right,
            creation_cost=cost,
        )

        self.proofs_created.append(proof.proof_id)
        self.total_cost_paid += cost

        return proof

    def create_exit_clean_proof(
        self,
        enclave_id: str,
        outstanding_obligations: List[Dict],
        owes_nothing: bool
    ) -> MockZKProof:
        """
        Prove: "I owe nothing to Enclave E" (medium complexity).
        """
        cost = self.BASE_COSTS[StatementType.EXIT_CLEAN]

        statement = ProofStatement(
            statement_type=StatementType.EXIT_CLEAN,
            public_inputs={"enclave_id": enclave_id},
            claim=f"Owes nothing to enclave {enclave_id[:8]}"
        )

        proof = MockZKProof(
            proof_id=f"prf_{uuid.uuid4().hex[:8]}",
            prover_id=self.prover_id,
            statement=statement,
            _witness={
                "obligations": outstanding_obligations,
                "owes_nothing": owes_nothing,
            },
            valid=owes_nothing,
            creation_cost=cost,
        )

        self.proofs_created.append(proof.proof_id)
        self.total_cost_paid += cost

        return proof

    def create_range_proof(
        self,
        actual_value: int,
        min_value: int,
        max_value: int
    ) -> MockZKProof:
        """
        Prove: "Value V is in range [min, max]" without revealing V.
        """
        valid = min_value <= actual_value <= max_value
        cost = self.BASE_COSTS[StatementType.RANGE]

        statement = ProofStatement(
            statement_type=StatementType.RANGE,
            public_inputs={"min": min_value, "max": max_value},
            claim=f"Value is in range [{min_value}, {max_value}]"
        )

        proof = MockZKProof(
            proof_id=f"prf_{uuid.uuid4().hex[:8]}",
            prover_id=self.prover_id,
            statement=statement,
            _witness={"actual_value": actual_value},
            valid=valid,
            creation_cost=cost,
        )

        self.proofs_created.append(proof.proof_id)
        self.total_cost_paid += cost

        return proof


class MockVerifier:
    """
    Verifies ZK proofs (cheap operation).

    Verification is always cheap (cost = 1) regardless of proof complexity.
    This asymmetry is fundamental to ZK economics.
    """

    VERIFICATION_COST: int = 1

    def __init__(self, verifier_id: str):
        self.verifier_id = verifier_id
        self.proofs_verified: List[str] = []
        self.total_cost_paid: int = 0

    def verify(self, proof: MockZKProof) -> VerificationResult:
        """
        Verify a proof.

        In mock system, we just check the 'valid' flag.
        In real system, this would be cryptographic verification.
        """
        self.proofs_verified.append(proof.proof_id)
        self.total_cost_paid += self.VERIFICATION_COST

        # Check expiration
        if proof.is_expired:
            return VerificationResult(
                proof_id=proof.proof_id,
                valid=False,
                verification_cost=self.VERIFICATION_COST,
                message="Proof has expired",
            )

        return VerificationResult(
            proof_id=proof.proof_id,
            valid=proof.valid,
            verification_cost=self.VERIFICATION_COST,
            message="Verified successfully" if proof.valid else "Proof invalid",
        )

    def batch_verify(self, proofs: List[MockZKProof]) -> List[VerificationResult]:
        """
        Verify multiple proofs.

        In real ZK, batch verification can be more efficient.
        In mock, it's just serial verification.
        """
        return [self.verify(proof) for proof in proofs]


# === Factory Functions ===

def create_prover(prover_id: str) -> MockProver:
    """Create a new MockProver for a Holon."""
    return MockProver(prover_id=prover_id)


def create_verifier(verifier_id: str) -> MockVerifier:
    """Create a new MockVerifier."""
    return MockVerifier(verifier_id=verifier_id)


# === Utility Functions ===

def estimate_proof_cost(statement_type: StatementType) -> int:
    """Estimate cost to create a proof of given type."""
    return MockProver.BASE_COSTS.get(statement_type, 50)


def is_proof_economically_viable(
    statement_type: StatementType,
    value_protected: int,
    probability_of_challenge: float = 0.1
) -> bool:
    """
    Determine if creating a proof is economically worthwhile.

    A proof is viable if:
        cost_of_proof < value_protected * probability_of_challenge
    """
    cost = estimate_proof_cost(statement_type)
    expected_value = value_protected * probability_of_challenge
    return cost < expected_value
