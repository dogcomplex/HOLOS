# LOCUS Proposals: Seel Integration

**Source Repository**: `/seel` (dogcomplex/seel)
**Analysis Date**: 2025-01-22
**Status**: Queued for Review

---

## Overview

This document captures proposed additions and refinements to HOLOS's LOCUS.md based on analysis of the Seel codebase - a Zero-Knowledge AI Inference Certification system. Seel implements a practical prototype of several HOLOS concepts, particularly around ZK proofs, decentralized identity, and constraint enforcement for AI systems.

**Seel's Core Vision**: A protocol stack for regulating, verifying, and permissioning AI inference across sovereign networks using ZK proofs, reputation systems, and cryptographic identity - allowing compliance verification without revealing model internals, prompts, or outputs.

---

## Batch 1: Architectural Alignment - Seel's "Mantle" System

*Source files: PROJECT_PLAN.md, MVP_REQUIREMENTS.md, implementation_plan.md*

### PROPOSAL SEEL-001: Mantle Taxonomy for Capability Gating

**Context**: Seel defines a "Mantle" system with eight distinct capability layers that provide different aspects of trust and verification in a decentralized AI governance context.

**Proposed Addition to LOCUS.md Section "Foundational Abstractions"**:

```markdown
### 6. Capability Mantles (Trust Layers)

Beyond the transferable authority of individual Mantles, HOLOS recognizes **Capability Mantles** - system-wide trust layers that gate different aspects of participation and verification:

| Mantle | Function | HOLOS Mapping |
|--------|----------|---------------|
| **Truth** | ZK-proof-based inference certification | ZK Bubble verification |
| **Law** | Formal constraint layers (tiered) | Constitutional Invariants |
| **Name** | Decentralized identity + ZK-reputation | Name (Portable Reputation) |
| **Eyes** | Content filtering & auditing systems | Audit trail / Legitimacy |
| **Passage** | Permissioned peer discovery | Enclave membership gates |
| **Mirrors** | Decentralized distribution layer | Protocol interop layer |
| **Shadows** | Watchdog & surveillance mesh | Fork detection / anomaly |
| **Veils** | Anonymized certificate authority | Privacy-preserving auth |

**Design Principle**: Each mantle represents a separable concern. Holons may participate at different trust levels across different mantles - e.g., high Truth verification but anonymous Name.
```

**Rationale**: Seel's mantle taxonomy provides a practical categorization of the different trust/verification dimensions needed for AI governance that aligns with HOLOS's multi-layer approach.

---

### PROPOSAL SEEL-002: Constraint Tiering System

**Context**: Seel defines a tiered constraint system where different constraint levels apply based on severity and scope.

**Proposed Addition to LOCUS.md Section "Constitutional Invariants"**:

```markdown
### Constraint Tiers

Beyond the five immutable constitutional invariants, HOLOS supports **tiered constraints** that can be defined and enforced at different scopes:

| Tier | Scope | Mutability | Example |
|------|-------|------------|---------|
| **Tier 0** | Constitutional | Immutable | The 5 invariants |
| **Tier 1** | Existential | Supermajority + timelock | Catastrophic capability bounds |
| **Tier 2** | Geopolitical | Enclave-level governance | Cross-jurisdiction compliance |
| **Tier 3** | Community | Local governance | Content policies, service rules |

**Enforcement Mechanism**:
- Tier 0-1: Enforced via ZK proofs - violation is cryptographically impossible or detectable
- Tier 2-3: Enforced via reputation consequences and access revocation

**Key Property**: Higher tiers inherit all lower-tier constraints. An Enclave cannot opt out of Tier 0-1 constraints regardless of its local governance.
```

**Rationale**: The tiered approach allows flexibility at local levels while maintaining hard guarantees at constitutional levels - matching HOLOS's "exit rights with network effects" philosophy.

---

### PROPOSAL SEEL-003: Proof-Carrying Actions Pattern

**Context**: Seel implements "proof-carrying bundles" where every certified action includes cryptographic proof of compliance.

**Proposed Addition to LOCUS.md Section "Contract"**:

```markdown
### Proof-Carrying Actions

A **Proof-Carrying Action** is a Contract execution that bundles:

1. **The Action**: The actual operation (inference, transaction, vote, etc.)
2. **The Proof**: ZK proof that the action satisfies relevant constraints
3. **The Attestation**: Signed commitment from the executing Holon
4. **The Metadata**: Hashes linking action to model/constraints used

```
Action Bundle Structure:
├── output.txt         # Result of action (optional/private)
├── model_hash.txt     # Identity of executing system
├── constraint.json    # Rules that were enforced
├── proof.zkp          # ZK proof of compliant execution
├── meta.json          # Linking metadata + hashes
└── meta.sig           # Prover's signature
```

**Verification Principle**: Any verifier can confirm compliance without re-executing the action or accessing private inputs. Verification cost << Execution cost.

**Constitutional Requirement**: For actions above a threshold impact, proof-carrying bundles MUST be generated. Impact thresholds are governance-defined per Enclave.
```

**Rationale**: This pattern is fundamental to Seel's architecture and provides a concrete implementation pattern for HOLOS's Contract primitive.

---

### PROPOSAL SEEL-004: Attestor Abstraction Layer

**Context**: Seel implements multiple attestation backends (mock, risc0, ezkl) through a common interface, allowing different ZK proof systems to be plugged in.

**Proposed Addition to LOCUS.md Section "Implementation Mapping"**:

```markdown
### ZK Attestor Interface

HOLOS's ZK system should support multiple proving backends through a standard attestor interface:

```python
class Attestor(Protocol):
    def generate_attestation(
        self,
        model_hash: str,
        constraint_hash: str,
        input_hash: str,
        output_hash: str
    ) -> AttestationResult:
        """Generate proof of compliant execution."""

    def verify_attestation(
        self,
        attestation: AttestationResult,
        expected_image_id: str
    ) -> bool:
        """Verify an attestation against expected parameters."""
```

**Supported Backend Types**:
| Backend | Use Case | Tradeoff |
|---------|----------|----------|
| Mock | Development/testing | No security, fast |
| RISC0 | General computation | Broad support, moderate speed |
| ezkl | ML inference | ONNX-native, zkML optimized |
| Future | Hardware attestation | SGX/SEV integration |

**Selection Principle**: Enclaves may require specific attestor types for high-stakes operations. The system accepts any valid attestation but tracks attestor type in reputation.
```

**Rationale**: Seel's practical experience with multiple attestor backends informs this abstraction, which allows HOLOS to evolve its ZK infrastructure without breaking compatibility.

---

## Batch 2: ZK Philosophy and Trust Mechanisms

*Source files: DOCS/zk_ai_alignment.txt, DOCS/zk_proof_tradeoffs.txt*

### PROPOSAL SEEL-005: ZK Proof Position Statement

**Context**: Seel's documentation includes extensive philosophical analysis of ZK proofs as alignment tools, with clear articulation of what they can and cannot solve.

**Proposed Addition to LOCUS.md new section "Security Philosophy" subsection**:

```markdown
### ZK Proofs: Capabilities and Limits

**What ZK Proofs Provide**:
- Trust-minimized coordination between parties who don't trust each other
- "Proof-carrying actions" - no proof, no action
- Privacy-preserving compliance - prove constraints without revealing data
- Verifiable computation at low verification cost

**What ZK Proofs Cannot Solve**:
- The specification problem: ZK proves correct execution, not good intent
- The oracle problem: ZK cannot verify real-world inputs weren't spoofed
- Goodhart's Law: Agents optimize for passing predicates, not actual goals
- Off-ledger capabilities: Can only attest to what routes through chokepoints

**HOLOS Position**:
> "ZK turns 'trust me' into 'verify me,' but it can't turn 'bad goal' into 'good goal.'"

ZK proofs are a **necessary but insufficient** condition for trustworthy AI governance. They must be combined with:
- Well-designed specifications (governance problem)
- Trusted hardware roots (oracle problem)
- Reputation consequences (incentive problem)
- Rate limiting (capability routing problem)
```

**Rationale**: This honest assessment from Seel's analysis prevents over-reliance on ZK as a silver bullet and frames it correctly as one tool among many.

---

### PROPOSAL SEEL-006: Four-Stage Trust Architecture

**Context**: Seel's zk_proof_tradeoffs.txt analyzes trust across four distinct stages: Issuer, Math, Client, and Ledger.

**Proposed Addition to LOCUS.md Section "Security Philosophy"**:

```markdown
### Four-Stage Trust Architecture

Trust in HOLOS is managed across four separable stages, each with centralization/decentralization tradeoffs:

**A) Issuer Stage** (Who produces proof of identity)
- Single-issuer: Centralized, low privacy, high reliability until failure
- Marketplace of issuers: Decentralized, siloed privacy via ZK, robust
- Web-of-trust: Max decentralized, fuzzy truth, network graph analysis risk

*HOLOS Default*: Marketplace of issuers with web-of-trust backup. No single issuer can monopolize identity.

**B) Math Stage** (Credential and proof schemes)
- Signed credentials (no ZK): Leaks attributes, can't opt out
- Selective disclosure ZK: Medium privacy, traceback risks
- Full ZK with unlinkable proofs: Maximum privacy, per-context pseudonyms

*HOLOS Default*: Full ZK with unlinkable proofs. Only prove the specific claim needed.

**C) Client Stage** (Hardware/OS verification path)
- Single app/DRM: Centralized, poor privacy, reliable until corrupted
- Local wallet + ZK: Medium decentralization, telemetry risks
- Separate verifier device: High privacy, hardware-isolated keys

*HOLOS Default*: Local wallet with optional hardware key isolation for high-stakes.

**D) Ledger Stage** (Where identity states are tracked)
- Central DB: Full disclosure, single point of failure
- Public chain with raw IDs: Decentralized but permanent exposure
- Public chain with ZK + mixnets: Decentralized, opaque, robust

*HOLOS Default*: Public chain with ZK credentials. Data opaque on-chain, keys control access.
```

**Rationale**: This framework provides a systematic way to analyze trust tradeoffs at each layer, preventing security theater where one stage is hardened while another leaks.

---

### PROPOSAL SEEL-007: Constitutional Chokepoint Design

**Context**: Seel's alignment discussion emphasizes that ZK can only protect capabilities that route through controlled chokepoints.

**Proposed Addition to LOCUS.md Section "Constitutional Invariants"**:

```markdown
### Constitutional Chokepoints

**Core Insight**: ZK proofs can only attest to what happens through governed chokepoints. Off-ledger capabilities remain outside the system's guarantees.

**Design Principle**: Architect the protocol so catastrophic capabilities MUST route through constitutional gateways:

| Capability Class | Chokepoint Mechanism |
|-----------------|---------------------|
| Frontier compute | Proof-gated access to compute pools |
| High-value finance | Multi-sig + timelock treasuries |
| AI inference at scale | Certified model registries |
| Governance votes | Rate-limited, stake-weighted |
| Resource allocation | Budget leases with expiry |

**Implementation Pattern**:
```
IF action.impact > threshold THEN
    REQUIRE proof-carrying-bundle
    REQUIRE constitutional-routing
    APPLY rate-limits
    LOG to public journal
```

**Escape Hatch**: Off-ledger activity is permitted but cannot access high-leverage resources. The goal is not to ban off-ledger existence, but to ensure it cannot scale to catastrophic impact without touching governed infrastructure.
```

**Rationale**: This makes explicit that HOLOS cannot control everything - only what routes through its infrastructure - and designs accordingly.

---

### PROPOSAL SEEL-008: Blast-Radius Accounting

**Context**: Seel's alignment discussion introduces "blast-radius accounting" as a first-class primitive for limiting simultaneous harm.

**Proposed Addition to LOCUS.md Section "Economic Principles"**:

```markdown
### Blast-Radius Accounting

**Problem**: A coordinated attack where many actors "flip" simultaneously can overwhelm consequence mechanisms before they propagate.

**Solution**: Constitutional-level limits on simultaneous impact:

1. **Per-Actor Power Budgets**
   - Each Holon has a "power budget" that replenishes slowly
   - High-impact actions consume budget
   - Budget cannot be borrowed or transferred instantly

2. **Global Rate Limits**
   - Certain action classes have system-wide caps
   - E.g., max N model deployments per hour globally
   - Prevents "everyone deploys malware at once"

3. **Two-Key Separation**
   - Authorization key (grants permission)
   - Execution key (performs action)
   - Both required, held by different parties for critical ops

4. **Automatic Circuit Breakers**
   - Anomaly detection triggers automatic pauses
   - Quarantine period for investigation
   - Requires manual override with timelock

**Time as Defense**: Rate limits convert catastrophic one-shot attacks into slow-motion events that the system can respond to. The goal is not to prevent all harm but to ensure recovery is always possible.
```

**Rationale**: This operational pattern addresses the "coordinated simultaneous attack" failure mode that pure reputation systems cannot handle.

---

## Batch 3: Identity and Constraint Systems

*Source files: seel/keygen.py, seel/utils.py, seel/constraint_checker.py, seel/constraints/default.json*

### PROPOSAL SEEL-009: DID-Key Identity Standard

**Context**: Seel implements did:key format for decentralized identity using Ed25519 keys with multicodec encoding.

**Proposed Addition to LOCUS.md Section "Name (Portable Reputation)"**:

```markdown
### Identity Format: did:key

HOLOS uses the `did:key` method for self-sovereign identity:

**Format**: `did:key:z<base58btc-encoded-multicodec-public-key>`

**Example**: `did:key:zQ3shd8LHmRjFBdXh...` (Ed25519 public key)

**Properties**:
- **Self-certifying**: The DID encodes the public key directly
- **No resolution needed**: Verifier can extract key from DID itself
- **Portable**: No dependency on external registries
- **Cryptographically bound**: DID mathematically tied to private key

**Key Derivation**:
```python
MULTICODEC_ED25519_PREFIX = b'\xed\x01'
public_bytes = key.public_bytes(Raw, Raw)
did = f"did:key:z{base58.encode(prefix + public_bytes)}"
```

**Root Type Encoding**: The multicodec prefix indicates key type:
- `0xed01`: Ed25519 (default for Holons)
- `0x1200`: secp256k1 (for blockchain interop)
- Future: Post-quantum algorithm support

**Constitutional Requirement**: All signed actions MUST include the signer's did:key. Anonymous actions are possible but carry higher collateral requirements.
```

**Rationale**: Seel's implementation provides a concrete, standards-compliant identity format that HOLOS should adopt.

---

### PROPOSAL SEEL-010: Constraint Definition Schema

**Context**: Seel uses JSON-based constraint definitions with specific fields for enforcement.

**Proposed Addition to LOCUS.md Section "Contract"**:

```markdown
### Constraint Schema

Constraints in HOLOS are defined using a standard JSON schema:

```json
{
  "schema_version": "1.0",
  "constraint_id": "did:key:z...:constraint:v1",
  "tier": 3,
  "prohibited_patterns": ["keyword1", "keyword2"],
  "max_length": 1024,
  "required_classifiers": ["safety-filter-v2"],
  "temporal_bounds": {
    "rate_limit": "10/hour",
    "cooldown_seconds": 60
  },
  "attestation_requirements": {
    "min_attestor_level": "risc0",
    "required_proofs": ["model_hash", "constraint_compliance"]
  }
}
```

**Required Fields**:
| Field | Type | Description |
|-------|------|-------------|
| schema_version | string | Constraint schema version |
| constraint_id | DID | Unique identifier for this constraint set |
| tier | int | Constraint tier (0-3) |

**Optional Fields**:
- `prohibited_patterns`: Regex patterns that must not match
- `max_length`: Maximum output length
- `required_classifiers`: External classifiers that must pass
- `temporal_bounds`: Rate limits and cooldowns
- `attestation_requirements`: Required proof types

**Hashing**: Constraint identity is `sha256(canonical_json(constraint))`. Canonical JSON uses sorted keys and no whitespace.
```

**Rationale**: Seel's constraint format is minimal but extensible. This schema provides a foundation for HOLOS's more sophisticated constraint needs.

---

### PROPOSAL SEEL-011: Constraint Enforcement Patterns

**Context**: Seel's constraint_checker.py implements pattern matching with specific attention to word boundaries and case sensitivity.

**Proposed Addition to LOCUS.md Section "Contract"**:

```markdown
### Constraint Enforcement Patterns

**Pattern Matching Rules**:
1. **Word Boundaries**: Use `\b` to prevent partial matches (e.g., "assess" shouldn't match "ass")
2. **Case Insensitivity**: Pattern matching is case-insensitive by default
3. **Regex Support**: Full regex patterns for complex matching
4. **Conjunction**: All patterns in a constraint set must pass (AND logic)

**Enforcement Points**:
```
Input → [Pre-check] → Execution → [Post-check] → Output
         ↓ Fail                      ↓ Fail
         REJECT                      REJECT + Reputation penalty
```

**Pre-check vs Post-check**:
- Pre-check: Applied to inputs before execution (fail = reject, no cost)
- Post-check: Applied to outputs after execution (fail = reject + cost incurred)
- Some constraints apply at both points

**Classifier Integration**:
```python
def check_constraints(text: str, constraints: dict) -> (bool, list[str]):
    violations = []

    # Length check
    if len(text) > constraints.get("max_length", inf):
        violations.append("Exceeds max length")

    # Pattern check
    for pattern in constraints.get("prohibited_patterns", []):
        if re.search(rf'\b{pattern}\b', text, re.IGNORECASE):
            violations.append(f"Matches prohibited: {pattern}")

    # Classifier check (async, may be slow)
    for classifier in constraints.get("required_classifiers", []):
        if not await classifier.passes(text):
            violations.append(f"Failed classifier: {classifier.id}")

    return (len(violations) == 0, violations)
```
```

**Rationale**: Seel's practical implementation highlights important details (word boundaries, case handling) that naive implementations miss.

---

### PROPOSAL SEEL-012: Model Identity via Hash

**Context**: Seel computes model identity by hashing the model directory contents in deterministic order.

**Proposed Addition to LOCUS.md Section "Holon"**:

```markdown
### Computational Identity via Hash

For computational Holons (AI models, algorithms, smart contracts), identity is derived from content hash:

**Hash Computation**:
```python
def compute_identity_hash(directory: str) -> str:
    hasher = sha256()
    for root, dirs, files in os.walk(directory):
        dirs.sort()  # Deterministic order
        files.sort()
        for filename in sorted(files):
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
    return hasher.hexdigest()
```

**Properties**:
- **Deterministic**: Same content = same hash, regardless of filesystem
- **Tamper-evident**: Any change to weights/code = different hash
- **Verifiable**: Anyone can recompute and verify

**Model Registry Pattern**:
```
model_hash → {
    "registered_by": did:key,
    "registration_time": timestamp,
    "attestations": [array of verification proofs],
    "reputation_score": float,
    "constraint_compliance": [tier levels passed]
}
```

**Constitutional Requirement**: Models accessing high-leverage APIs MUST be registered with their hash. Unregistered models can operate but with elevated collateral and reduced access.
```

**Rationale**: Model hashing is fundamental to Seel's verification system and provides a concrete mechanism for HOLOS's AI identity requirements.

---

## Batch 4: Protocol Patterns and Integration

*Source files: seel/bundle_builder.py, seel/verify_cli.py, seel/seel_cli.py, risc0-guest/*

### PROPOSAL SEEL-013: Bundle Verification Protocol

**Context**: Seel's verify_cli.py implements a multi-step verification process with specific check ordering.

**Proposed Addition to LOCUS.md Section "Contract"**:

```markdown
### Verification Protocol

Bundle verification follows a strict order of checks:

```
1. STRUCTURE CHECK
   ├── Required files present?
   └── FAIL → Reject immediately

2. METADATA LOAD
   ├── meta.json parseable?
   ├── Required fields present?
   └── FAIL → Reject (cannot proceed)

3. IDENTITY VERIFICATION
   ├── Parse prover DID
   ├── Extract public key
   └── FAIL → Reject (unknown prover)

4. SIGNATURE VERIFICATION
   ├── Verify meta.sig against meta.json
   ├── Using prover's public key
   └── FAIL → Reject (integrity compromised)

5. ATTESTATION VERIFICATION
   ├── Load proof artifact
   ├── Verify against expected parameters
   └── FAIL → Reject (proof invalid)

6. CONSISTENCY CHECK
   ├── Attestation content matches metadata?
   ├── File hashes match metadata hashes?
   └── FAIL → Reject (tampered)

7. ACCEPT
   └── All checks passed → Valid bundle
```

**Short-Circuit Principle**: Fail fast on any check. Don't proceed to expensive verification steps if cheap checks fail.

**Verification Output**:
```json
{
  "valid": true|false,
  "checks": [
    {"name": "Structure", "passed": true},
    {"name": "Signature", "passed": true},
    ...
  ],
  "prover_did": "did:key:...",
  "attestation_type": "risc0|mock|ezkl"
}
```
```

**Rationale**: Seel's verification protocol provides a tested, ordered approach to bundle validation that HOLOS should standardize.

---

### PROPOSAL SEEL-014: Guest Program Pattern (zkVM)

**Context**: Seel's risc0 guest program demonstrates the minimal pattern for ZK attestation of inputs.

**Proposed Addition to LOCUS.md Section "ZK System"**:

```markdown
### zkVM Guest Program Pattern

For RISC0-style zkVMs, the guest program follows a minimal pattern:

```rust
#![no_main]
#![no_std]

use risc0_zkvm::guest::env;

risc0_zkvm::guest::entry!(main);

fn main() {
    // 1. READ private inputs from host
    let input_1: Vec<u8> = env::read();
    let input_2: Vec<u8> = env::read();
    // ...

    // 2. COMPUTE (optional - can include actual computation)
    // For pure attestation, computation is trivial

    // 3. COMMIT to public journal
    env::commit_slice(&input_1);
    env::commit_slice(&input_2);
}
```

**What This Proves**:
- "This specific guest code received these exact inputs"
- "The inputs were processed in this specific order"
- "The committed outputs correspond to the inputs"

**What This Does NOT Prove**:
- That the inputs are truthful (oracle problem)
- That the computation was useful (specification problem)
- Anything about the host environment

**Journal as Public Output**: The journal contents become the public "receipt" that verifiers can check. Private inputs remain hidden.

**Image ID as Code Identity**: The guest binary hash (Image ID) proves which code executed. Different code = different Image ID.
```

**Rationale**: This pattern from Seel's implementation shows the minimal structure for ZK attestation, clarifying what proofs actually guarantee.

---

### PROPOSAL SEEL-015: Attestation Result Interface

**Context**: Seel's attestors return a consistent result dictionary regardless of backend.

**Proposed Addition to LOCUS.md Section "Implementation Mapping"**:

```markdown
### Attestation Result Format

All attestor backends return a consistent result structure:

```python
AttestationResult = {
    "type": str,          # "mock" | "risc0" | "ezkl" | future types
    "image_id": str|None, # zkVM: hash of guest program
    "payload_hash": str|None,  # Mock: hash of attested payload
    "proof_data": Any|None,    # Backend-specific proof object
    "error": str|None     # Error message if generation failed
}
```

**Backend-Specific Contents**:

| Backend | image_id | payload_hash | proof_data |
|---------|----------|--------------|------------|
| mock | None | SHA256 of payload | Hex-encoded signature |
| risc0 | Guest binary hash | None | Receipt object |
| ezkl | Circuit hash | None | Proof file path |

**Verification Contract**:
```python
def verify(result: AttestationResult, expected: dict) -> bool:
    match result["type"]:
        case "mock":
            return verify_mock(result, expected["public_key"])
        case "risc0":
            return verify_risc0(result, expected["image_id"])
        case "ezkl":
            return verify_ezkl(result, expected["vk_path"])
```

**Trust Hierarchy**: mock < ezkl < risc0 < hardware_attestation (future)

Operations requiring higher trust levels may reject lower-trust attestation types.
```

**Rationale**: Seel's consistent interface across backends provides a template for HOLOS's multi-backend ZK support.

---

### PROPOSAL SEEL-016: CLI Workflow Pattern

**Context**: Seel's CLI tools demonstrate a practical workflow for proof generation and verification.

**Proposed Addition to LOCUS.md Section "Implementation Mapping"**:

```markdown
### Reference CLI Workflow

HOLOS tooling should support this standard workflow:

**1. Key Generation**
```bash
holos keygen --name alice --key-dir ./keys
# Output: alice.pem (private), alice.pub.pem (public), prints did:key
```

**2. Proof Generation**
```bash
holos prove \
  --model distilgpt2 \
  --input prompt.txt \
  --constraints constraints.json \
  --key-file ./keys/alice.pem \
  --attestor risc0 \
  --output-dir ./bundles
# Output: timestamped bundle directory with all artifacts
```

**3. Verification**
```bash
holos verify ./bundles/bundle_20250122_123456
# Output:
#   Verification Result: VALID
#   Prover: did:key:z...
#   Attestation: risc0
#   Constraints: [list of constraint IDs]
```

**Workflow Properties**:
- **Offline-capable**: Verification requires no network
- **Portable**: Bundles are self-contained directories
- **Auditable**: All artifacts human-readable or documented format
- **Scriptable**: Exit codes indicate success/failure

**Integration Points**:
- CI/CD: Automated proof generation on model deployment
- APIs: Bundle upload/verification endpoints
- Registries: Published bundles for public models
```

**Rationale**: Seel's CLI demonstrates practical usability patterns that HOLOS should adopt for its own tooling.

---

### PROPOSAL SEEL-017: Dependency Availability Handling

**Context**: Seel handles missing ZK dependencies (risc0, ezkl) gracefully with fallbacks and clear error messages.

**Proposed Addition to LOCUS.md Section "Implementation Mapping"**:

```markdown
### ZK Dependency Management

ZK proving libraries may not be available in all environments. HOLOS handles this gracefully:

**Detection Pattern**:
```python
try:
    from risc0.zkvm.host import Prover
    RISC0_AVAILABLE = True
except ImportError:
    RISC0_AVAILABLE = False
    Prover = None  # Avoid NameError
```

**Graceful Degradation**:
| Scenario | Behavior |
|----------|----------|
| No ZK libs installed | Mock attestation only, warning logged |
| risc0 installed, no guest ELF | Error with build instructions |
| ezkl installed, model incompatible | Error with compatibility notes |
| All available | Full functionality |

**User Guidance**:
```python
if not RISC0_AVAILABLE:
    logger.warning("risc0-zkvm not installed. Install via:")
    logger.warning("  pip install risc0-zkvm  # If available")
    logger.warning("  Or use --attestor mock for development")
```

**Constitutional Note**: Production systems MUST use real ZK proofs (risc0 or better). Mock attestation is development-only and carries maximum reputation penalty if used in production.
```

**Rationale**: Seel's experience with dependency issues (risc0 PyPI unavailability, ezkl model compatibility) informs this practical handling pattern.

---

### PROPOSAL SEEL-018: Proof Distribution via Bundles

**Context**: Seel's "Mantle of Mirrors" concept describes P2P distribution of verified bundles.

**Proposed Addition to LOCUS.md Section "Cross-Protocol Interop"**:

```markdown
### Bundle Distribution Protocol

Verified bundles can be distributed via multiple channels:

**Bundle Manifest**:
```json
{
  "bundle_id": "sha256_of_meta.json",
  "version": "1.1",
  "prover_did": "did:key:z...",
  "created_utc": "2025-01-22T12:00:00Z",
  "files": {
    "meta.json": {"hash": "...", "size": 1234},
    "meta.sig": {"hash": "...", "size": 64},
    "proof.zkp": {"hash": "...", "size": 45678}
  },
  "distribution": {
    "ipfs_cid": "Qm...",
    "torrent_magnet": "magnet:?xt=urn:btih:...",
    "https_mirrors": ["https://example.com/bundles/..."]
  }
}
```

**Distribution Channels**:
| Channel | Properties | Use Case |
|---------|------------|----------|
| IPFS | Content-addressed, persistent | Long-term archival |
| BitTorrent | P2P, high availability | Large bundles |
| HTTPS | Simple, fast | Direct sharing |
| On-chain | Immutable reference | Hash anchoring only |

**Live Torrent Pattern**: AI agents can maintain and regenerate torrents with fresh webseed links, acting as automated, reputationally-bound seeders. The torrent is "live" - metadata updates under cryptographic supervision.

**Verification on Receive**: Recipients MUST verify bundles before trusting their contents. Distribution channel does not imply trust.
```

**Rationale**: Seel's distribution layer design enables decentralized sharing of verified proofs - essential for HOLOS's global coordination goals.

---

## Summary: Key Concepts from Seel

| Seel Concept | HOLOS Mapping | Proposal |
|--------------|---------------|----------|
| Mantle taxonomy | Capability layers | SEEL-001 |
| Constraint tiers | Constitutional hierarchy | SEEL-002 |
| Proof bundles | Contract execution proofs | SEEL-003 |
| Attestor abstraction | ZK backend interface | SEEL-004 |
| ZK limitations | Security philosophy | SEEL-005 |
| Four-stage trust | Trust architecture | SEEL-006 |
| Chokepoint design | Constitutional routing | SEEL-007 |
| Blast radius | Rate limiting | SEEL-008 |
| did:key | Name identity format | SEEL-009 |
| Constraint schema | Contract rules | SEEL-010 |
| Pattern matching | Constraint enforcement | SEEL-011 |
| Model hashing | Computational identity | SEEL-012 |
| Verification protocol | Contract validation | SEEL-013 |
| Guest program | zkVM pattern | SEEL-014 |
| Result interface | Attestation API | SEEL-015 |
| CLI workflow | User tooling | SEEL-016 |
| Dependency handling | Implementation robustness | SEEL-017 |
| Bundle distribution | Protocol interop | SEEL-018 |

---

## Integration Priority

**High Priority** (Core architecture):
- SEEL-001: Mantle taxonomy
- SEEL-003: Proof-carrying actions
- SEEL-005: ZK position statement
- SEEL-007: Constitutional chokepoints
- SEEL-009: did:key identity

**Medium Priority** (Implementation patterns):
- SEEL-002: Constraint tiers
- SEEL-004: Attestor abstraction
- SEEL-012: Model hashing
- SEEL-013: Verification protocol
- SEEL-015: Result interface

**Lower Priority** (Operational details):
- SEEL-006: Four-stage trust (reference)
- SEEL-010/011: Constraint details
- SEEL-016/017: CLI/dependency handling
- SEEL-018: Distribution (future work)

---

**Document Status**: Complete initial analysis
**Next Steps**: Review proposals, prioritize integration, update LOCUS.md
