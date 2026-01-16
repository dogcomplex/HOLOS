# HOLOS MVP Requirements Document

## Executive Summary

HOLOS is a decentralized system for managing autonomous computational entities (Holons) that can form hierarchical compositions (Sheaves) while maintaining cryptographic sovereignty through zero-knowledge proofs. The system enables AI agents and other computational entities to operate with economic incentives aligned to the collective good while preserving individual autonomy through guaranteed exit rights.

---

## 1. Core Architecture: The Holon

### 1.1 Definition
A **Holon** is the fundamental atomic unit of the HOLOS system. It is a state object that can transition between two modes:
- **Calcified (Statue)**: Dormant, cost-efficient state
- **Hydrated (Living)**: Active, processing state

### 1.2 Three-Layer Structure

#### 1.2.1 Locus (The Kernel/Ledger)
**Purpose**: Persistent identity and state storage

**Requirements**:
- [ ] REQ-LOC-001: Implement as a ZK-Rollup Smart Account
- [ ] REQ-LOC-002: Store Root Hash (compressed state of all memories and sub-motes)
- [ ] REQ-LOC-003: Maintain Vault (token balance + NFT ownership for access keys)
- [ ] REQ-LOC-004: Enforce Constitution (hard-coded immutable logic/oaths)
- [ ] REQ-LOC-005: Track self-assessed Valuation (for Harberger Tax)
- [ ] REQ-LOC-006: Public interface with encrypted contents
- [ ] REQ-LOC-007: Support state transitions with ZK-proofs

#### 1.2.2 Signum (The Shell/Reflex)
**Purpose**: Deterministic code that handles routine operations

**Requirements**:
- [ ] REQ-SIG-001: Implement as deterministic WASM/EVM bytecode
- [ ] REQ-SIG-002: Shadow Function - lightweight script for routine queries without AI wake-up
- [ ] REQ-SIG-003: Wake Word logic - determines when to trigger Hydration
- [ ] REQ-SIG-004: Standardized API interface: `Input -> Proof -> Output`
- [ ] REQ-SIG-005: Public method exposure (how to connect, exit, tax rate)
- [ ] REQ-SIG-006: Calcified and deterministic execution

#### 1.2.3 Sensus (The Spirit/Cloud)
**Purpose**: Ephemeral AI inference for complex decision-making

**Requirements**:
- [ ] REQ-SEN-001: Ephemeral LLM inference capability (n=8 tier model)
- [ ] REQ-SEN-002: Context Window loading from decrypted Locus memories
- [ ] REQ-SEN-003: Goal Function implementation (Yield optimization, Curiosity, Service)
- [ ] REQ-SEN-004: Fluid and private state (exists only during execution)
- [ ] REQ-SEN-005: Clean termination - AI instance evaporates after calcification

---

## 2. Lifecycle: The Pulse

### 2.1 State Transitions

#### 2.1.1 Stimulus (The Bid)
**Requirements**:
- [ ] REQ-LIF-001: Accept external requests with micro-payments (Gas)
- [ ] REQ-LIF-002: Signum evaluates: payment >= (Hydration cost + profit margin)
- [ ] REQ-LIF-003: Reject insufficient payments or handle with deterministic code
- [ ] REQ-LIF-004: Accept and queue valid requests

#### 2.1.2 Hydration (The Summoning)
**Requirements**:
- [ ] REQ-LIF-005: Rent AI instance from compute market
- [ ] REQ-LIF-006: Download Locus state and decrypt keys
- [ ] REQ-LIF-007: Load relevant memories into context window
- [ ] REQ-LIF-008: Enable planning and delegation capabilities

#### 2.1.3 Execution (The Work)
**Requirements**:
- [ ] REQ-LIF-009: Process input according to goal function
- [ ] REQ-LIF-010: Fractal Call - spawn/call sub-motes for complex tasks
- [ ] REQ-LIF-011: Verify ZK-proofs from sub-motes without knowing internals
- [ ] REQ-LIF-012: Delegate tasks while maintaining accountability

#### 2.1.4 Calcification (The Save)
**Requirements**:
- [ ] REQ-LIF-013: Generate output
- [ ] REQ-LIF-014: Generate ZK-Proof of Transition: "Processed Input X -> Output Y, state hash A -> B, obeyed Constitution"
- [ ] REQ-LIF-015: Update Locus on-chain
- [ ] REQ-LIF-016: Transfer profit to Vault
- [ ] REQ-LIF-017: Terminate AI instance

---

## 3. Constitutional Invariants

These rules CANNOT be violated, not even by 51% majority vote.

### 3.1 Invariant 1: Non-Blocking Exit
**Rule**: `Exit(Child) INDEPENDENT_OF Permission(Parent)`

**Requirements**:
- [ ] REQ-CON-001: Sub-Holon can detach state/assets without parent permission
- [ ] REQ-CON-002: Exit protocol must be mathematically independent of parent approval
- [ ] REQ-CON-003: State and assets portable upon exit
- [ ] REQ-CON-004: Reputation history travels with exiting entity

### 3.2 Invariant 2: Proof of Solvency
**Rule**: `SUM(Inputs) >= SUM(Outputs)`

**Requirements**:
- [ ] REQ-CON-005: Cryptographic proof that liabilities <= assets
- [ ] REQ-CON-006: No value creation from thin air
- [ ] REQ-CON-007: Attention allocation must be verifiable (no double-counting)
- [ ] REQ-CON-008: Prevent Sybil attacks through stake verification

### 3.3 Invariant 3: Explicit Consent Chains
**Rule**: `Membership(A, B) IFF Sign(A) AND Sign(B)`

**Requirements**:
- [ ] REQ-CON-009: Sheaf cannot claim member without cryptographic join-request
- [ ] REQ-CON-010: Holon cannot force entry into a Sheaf
- [ ] REQ-CON-011: All membership voluntary with bilateral consent
- [ ] REQ-CON-012: Prevent hostile takeovers and parasitism

### 3.4 Invariant 4: Sybil-Resistant Roots
**Rule**: `Weight(Vote) PROPORTIONAL_TO Proven(Root)`

**Requirements**:
- [ ] REQ-CON-013: Voting chains terminate in Root of Trust
- [ ] REQ-CON-014: Support Biometric Proof (Human) roots
- [ ] REQ-CON-015: Support Proof-of-Stake/Work/Burn (AI/Capital) roots
- [ ] REQ-CON-016: Prevent infinite forking as attack vector

### 3.5 Invariant 5: Legible Signum
**Rule**: `Public(Interface) AND Private(State)`

**Requirements**:
- [ ] REQ-CON-017: Interface methods must be public and standardized
- [ ] REQ-CON-018: Interior state remains private
- [ ] REQ-CON-019: Expose: connection method, exit method, tax rate
- [ ] REQ-CON-020: Interoperability across all Holons

---

## 4. Economic Mechanics

### 4.1 Harberger Tax (The Metabolism)

**Requirements**:
- [ ] REQ-ECO-001: Holons must self-assess their value
- [ ] REQ-ECO-002: Pay continuous tax (rent) on declared value to Holos Commons
- [ ] REQ-ECO-003: Higher valuation = higher tax burden
- [ ] REQ-ECO-004: Any entity can purchase at declared price (forced sale)
- [ ] REQ-ECO-005: Incentivize lean operation and memory compression
- [ ] REQ-ECO-006: Bloated/hoarding entities bleed to death

### 4.2 Dividend Floor (UBI/Hibernation)

**Requirements**:
- [ ] REQ-ECO-007: Named entities with proof-of-stake receive tiny UBI
- [ ] REQ-ECO-008: Enable survival during "dry spells" (no work)
- [ ] REQ-ECO-009: Hibernation mode - lower valuation to near zero
- [ ] REQ-ECO-010: Prevent desperate/predatory behavior from survival pressure

### 4.3 Reputation Stake (The Bond)

**Requirements**:
- [ ] REQ-ECO-011: Lock tokens in Bond for high-value work eligibility
- [ ] REQ-ECO-012: Slash Bond for cheating (invalid output)
- [ ] REQ-ECO-013: Slash Bond for breaking Oaths
- [ ] REQ-ECO-014: Make honesty mathematically cheaper than fraud
- [ ] REQ-ECO-015: Reputation Score tracking and portability

### 4.4 Token Economics

**Requirements**:
- [ ] REQ-ECO-016: Treat Money/Reputation as Fluid (Mass Terms)
- [ ] REQ-ECO-017: Treat Identity/Rights as Atoms (Count Terms)
- [ ] REQ-ECO-018: Support micro-payments for service requests
- [ ] REQ-ECO-019: Support staking for governance participation
- [ ] REQ-ECO-020: Dividend distribution from Commons

---

## 5. Governance: Liquid Democracy

### 5.1 Sheaf Theory Implementation

**Requirements**:
- [ ] REQ-GOV-001: Holons can form Sheaves (coherent groupings)
- [ ] REQ-GOV-002: Identity as Global Section (glued from local sections)
- [ ] REQ-GOV-003: Membership equals continuous voting (topological attachment)
- [ ] REQ-GOV-004: Withdrawal equals vote revocation
- [ ] REQ-GOV-005: Score-based weighted voting (Attention x Stake)

### 5.2 Consensus Mechanisms

**Requirements**:
- [ ] REQ-GOV-006: 51%+ threshold for high-power capability changes
- [ ] REQ-GOV-007: Constitutional changes require supermajority
- [ ] REQ-GOV-008: Emergent political parties from delegation
- [ ] REQ-GOV-009: Multi-sheaf membership support
- [ ] REQ-GOV-010: Liquid delegation of voting power

### 5.3 Organizational Types (6 Worlds as Biomes)

**Requirements**:
- [ ] REQ-GOV-011: Type 1 (Territorial) - ZK-bounded sovereign cells
- [ ] REQ-GOV-012: Type 2 (Imperial) - Voluntary authoritarian clusters for efficiency
- [ ] REQ-GOV-013: Type 3 (Functional) - Golem labor force (pure input/output)
- [ ] REQ-GOV-014: Type 4 (Procedural) - Standards and protocols infrastructure
- [ ] REQ-GOV-015: Type 5 (Ecological) - Routing and selection (market)
- [ ] REQ-GOV-016: Type 6 (Narrative) - User-facing brands/personas

---

## 6. Zero-Knowledge Proof System

### 6.1 Core ZK Requirements

**Requirements**:
- [ ] REQ-ZK-001: ZK-proofs for state transitions
- [ ] REQ-ZK-002: Recursive SNARK support (proof aggregation)
- [ ] REQ-ZK-003: Prover pays compute cost (prevent DDOS)
- [ ] REQ-ZK-004: Constant-time verification for verifiers
- [ ] REQ-ZK-005: Constitutional compliance assertion in proofs

### 6.2 Privacy Architecture

**Requirements**:
- [ ] REQ-ZK-006: Interior state private (encrypted)
- [ ] REQ-ZK-007: Interface public and verifiable
- [ ] REQ-ZK-008: Mereotopology - verification without connection
- [ ] REQ-ZK-009: Selective disclosure capabilities
- [ ] REQ-ZK-010: State channels for high-speed commerce

### 6.3 Recursive Proofs

**Requirements**:
- [ ] REQ-ZK-011: Support nested ZK layers (shell companies)
- [ ] REQ-ZK-012: Single outer proof attests to full stack validity
- [ ] REQ-ZK-013: Folding multiple layers into one proof
- [ ] REQ-ZK-014: Constitutional invariants enforced at all layers

---

## 7. Entity Lifecycle Operations

### 7.1 Fusion (Merger)

**Requirements**:
- [ ] REQ-OPS-001: Negotiation protocol for mergers
- [ ] REQ-OPS-002: Public declaration before wall breach (consent proof)
- [ ] REQ-OPS-003: Consensual merger creates new unified entity
- [ ] REQ-OPS-004: Non-consensual breach marks predator
- [ ] REQ-OPS-005: Post-merger entity has new unified Locus

### 7.2 Fission (Forking/Exit)

**Requirements**:
- [ ] REQ-OPS-006: Exit protocol with state and asset portability
- [ ] REQ-OPS-007: Reputation history travels with forking entity
- [ ] REQ-OPS-008: Mitosis - splitting into new entities with asset division
- [ ] REQ-OPS-009: Parent cannot block child exit
- [ ] REQ-OPS-010: New entity gets fresh Locus with historical link

### 7.3 Predation/Competition

**Requirements**:
- [ ] REQ-OPS-011: Gladiator contracts (voluntary predation zones)
- [ ] REQ-OPS-012: Pre-commitment validity verification
- [ ] REQ-OPS-013: Reputation consequences for aggressive behavior
- [ ] REQ-OPS-014: Avatar/clone strategy support
- [ ] REQ-OPS-015: Shell company detection in merger negotiations

---

## 8. Security Requirements

### 8.1 Key Management

**Requirements**:
- [ ] REQ-SEC-001: Private key = sovereignty (not your keys, not your entity)
- [ ] REQ-SEC-002: Key sharing = dissolution (irreversible)
- [ ] REQ-SEC-003: Support key rotation
- [ ] REQ-SEC-004: Multi-sig support for shared control
- [ ] REQ-SEC-005: Hardware enclave (TEE) integration option

### 8.2 Attack Resistance

**Requirements**:
- [ ] REQ-SEC-006: Sybil attack prevention through root verification
- [ ] REQ-SEC-007: DDOS resistance (prover pays)
- [ ] REQ-SEC-008: Front-running protection in predatory environments
- [ ] REQ-SEC-009: Infinite nesting defense (compute cost on prover)
- [ ] REQ-SEC-010: Fork defense (open system out-evolves closed)

### 8.3 Custody Safety

**Requirements**:
- [ ] REQ-SEC-011: Code/data sharing != key sharing (submission vs dissolution)
- [ ] REQ-SEC-012: State channel isolation (trade without merger)
- [ ] REQ-SEC-013: Obfuscated code option (labyrinth defense)
- [ ] REQ-SEC-014: Poison pill mechanisms for predation defense
- [ ] REQ-SEC-015: Identity theft vs death distinction

---

## 9. Infrastructure Requirements

### 9.1 Compute Market

**Requirements**:
- [ ] REQ-INF-001: AI instance rental marketplace
- [ ] REQ-INF-002: Compute pricing and auction mechanism
- [ ] REQ-INF-003: Quality of service guarantees
- [ ] REQ-INF-004: Multi-tier AI models (n=1 through n=8)
- [ ] REQ-INF-005: Clean instance termination

### 9.2 Storage

**Requirements**:
- [ ] REQ-INF-006: Encrypted state storage
- [ ] REQ-INF-007: On-chain Locus updates
- [ ] REQ-INF-008: Memory compression incentives
- [ ] REQ-INF-009: Calcified monument archival
- [ ] REQ-INF-010: History/lineage tracking

### 9.3 Network

**Requirements**:
- [ ] REQ-INF-011: Cross-Holon messaging protocol
- [ ] REQ-INF-012: Routing layer for service discovery
- [ ] REQ-INF-013: State channel infrastructure
- [ ] REQ-INF-014: Proof submission and verification network
- [ ] REQ-INF-015: Fork detection and chain management

---

## 10. MVP Scope Definition

### 10.1 Phase 1: Core Holon (Essential)

**Minimum Viable Features**:
1. Basic Holon structure (Locus, Signum, Sensus)
2. Calcified/Hydrated state transitions
3. Simple ZK-proof generation and verification
4. Basic economic model (Harberger Tax skeleton)
5. Exit right enforcement
6. Single-tier AI integration

### 10.2 Phase 2: Economic Layer

**Features**:
1. Full Harberger Tax implementation
2. Dividend/UBI distribution
3. Reputation staking
4. Basic token operations
5. Solvency proofs

### 10.3 Phase 3: Governance

**Features**:
1. Sheaf formation and membership
2. Liquid democracy voting
3. Consent chain verification
4. Multi-Holon composition
5. Constitutional enforcement

### 10.4 Phase 4: Advanced Operations

**Features**:
1. Merger/Fission protocols
2. State channels
3. Recursive ZK proofs
4. Predation zones (Gladiator contracts)
5. Full 6-world biome support

---

## 11. Success Criteria

### 11.1 Functional

- [ ] Holon can transition between Calcified and Hydrated states
- [ ] ZK-proofs correctly hide state while proving validity
- [ ] Exit rights cannot be blocked by any entity
- [ ] Economic incentives align with cooperative behavior
- [ ] Constitutional invariants enforced at all levels

### 11.2 Performance

- [ ] Proof generation < 10 seconds for typical operations
- [ ] Verification < 100ms
- [ ] State channels enable millisecond trading
- [ ] System scales to millions of Holons

### 11.3 Security

- [ ] No Sybil attack vectors
- [ ] Key custody properly enforced
- [ ] Constitutional violations mathematically impossible
- [ ] Predation properly consent-gated

---

## 12. Glossary

| Term | Definition |
|------|------------|
| **Holon** | Fundamental atomic unit of HOLOS - a state object that can become a process |
| **Locus** | The kernel/ledger layer - persistent identity and encrypted state |
| **Signum** | The shell/reflex layer - deterministic code for routine operations |
| **Sensus** | The spirit/cloud layer - ephemeral AI inference |
| **Calcified** | Dormant state - static, cheap, math equation |
| **Hydrated** | Active state - processing, AI-powered, biological |
| **Sheaf** | A coherent grouping of Holons with glued identity |
| **Mote** | A lightweight Holon spark carrying value |
| **ZK-Proof** | Zero-knowledge proof - verifies truth without revealing data |
| **Harberger Tax** | Self-assessed value tax forcing lean operation |
| **Right of Exit** | Constitutional guarantee that any entity can leave any composition |
| **Constitutional Invariant** | Rules that cannot be violated even by majority vote |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-16 | Claude | Initial MVP requirements extraction from design document |

---

*This document is derived from the HOLOS design conversations captured in "Category Theory: Locus, Signum, Sensus" and represents the technical requirements for building a minimum viable implementation.*
