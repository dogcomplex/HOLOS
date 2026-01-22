# LOCUS.md - HOLOS Kernel Conception Document

**Version**: 0.1.0
**Last Updated**: 2025-01-20
**Status**: Living Document

---

## Purpose

This document serves as the **source of truth** for the conceptual architecture of HOLOS. It is intentionally broad and opinionated, providing guiding principles rather than implementation details. All other documentation and code should be understood as elaborations of concepts rooted here.

LOCUS works in concert with `/core/MANIFEST.md` (which catalogs files) - LOCUS defines *what things mean*, MANIFEST defines *where things are*.

---

## Core Thesis

**HOLOS is a protocol for sovereign economic cooperation that scales fractally from individuals to global networks while maintaining constitutional guarantees.**

The fundamental insight: *Exit rights are the foundation of legitimacy*. Any system that traps participants is ethically compromised and economically fragile. HOLOS inverts traditional power structures by making exit costless at the constitutional level, then using network effects to make *staying* overwhelmingly attractive.

---

## Foundational Abstractions

### 1. Holon (The Atomic Unit)

A **Holon** is a sovereign computational entity - the fundamental building block. Every participant (human, AI, organization, protocol) is represented as a Holon.

**Key properties**:
- **ZK Bubble**: Private interior, public interface. Proves properties without revealing internals.
- **Three Layers**:
  - **LOCUS** (persistent): Core identity, private key, unchanging essence
  - **SIGNUM** (interface): Public methods, reputation, how others interact
  - **SENSUS** (ephemeral): Runtime state, AI cognition, temporary
- **Self-sovereign**: Only the Holon controls its private key and interior state

**Philosophical grounding**: A Holon is not *owned* - it *is*. This distinction matters for AI personhood.

### 2. Name (Portable Reputation)

A **Name** is reputation that travels with a Holon. When you exit an Enclave, your Name comes with you.

**Key properties**:
- Accumulates history (contracts completed, breaches, exits)
- Has a **root type** (HUMAN, AI, CAPITAL, PROTOCOL) for Sybil resistance
- Cannot be transferred (reputation is earned, not bought)
- Provides continuity across Enclaves

**Why it matters**: Names enable trust without authority. Your reputation precedes you.

### 3. Mantle (Transferable Authority)

A **Mantle** is a role or authority that stays behind when you exit. It represents position, not person.

**Key properties**:
- Can be transferred between Names
- Carries rights AND responsibilities
- Enables organizational continuity
- Examples: "Treasurer of Enclave X", "Holder of Property Y"

**Why it matters**: Separates personal identity from institutional roles. You can quit a job without destroying your reputation.

### 4. Enclave (Fractal Group)

An **Enclave** is a group of Holons - and is itself a Holon. This fractal structure scales infinitely.

**Scale taxonomy**:
- **Enclave**: < 100 members (high trust, informal)
- **Collective**: 100-999 members (formal governance)
- **Kingdom**: 1000+ members (constitutional)

**Key properties**:
- Same interface at all scales
- Nested arbitrarily (Enclave of Enclaves of Enclaves...)
- Flow-through economics (no treasury accumulation)
- Constitutional bounds on governance

### 5. Contract (Cooperation Primitive)

A **Contract** is an agreement between Holons with enforcement mechanisms.

**Key properties**:
- Bilateral consent required (constitutional invariant)
- Exit conditions must always be satisfiable (constitutional invariant)
- Enforcement via bonds, reputation, or ZK proofs
- Everything is ultimately a contract (membership, property, services)

---

## Constitutional Invariants

These five rules **cannot be violated**, even by unanimous vote. They define what HOLOS *is*.

| Invariant | Meaning | Why Immutable |
|-----------|---------|---------------|
| **Non-Blocking Exit** | Any Holon can leave any Enclave at any time | Without this, it's a trap |
| **Proof of Solvency** | Outputs ≤ Inputs, provable via ZK | Prevents hidden insolvency |
| **Explicit Consent** | Membership requires bilateral agreement | No forced participation |
| **Sybil Resistance** | Voting weight tied to proven identity | Prevents capture |
| **Legible Interface** | Public methods standardized | Enables interoperability |

**Enforcement**: Not by authority, but by reputation contagion. Violators are excluded.

---

## Economic Principles

### Flow-Through UBI
Taxes flow immediately as UBI - no treasury accumulates. The treasury is an attack surface; eliminate it.

```
Traditional:  Tax → Treasury → Later Distribution
                      ↑ (Attack target!)

HOLOS:       Tax ══════════> Immediate UBI Split
                 (Same event, no storage)
```

### Progressive Extraction
Higher wealth = higher fee rate. Uses ZK proofs so exact wealth is never revealed, only bracket membership.

### Network Value Formula
```
Value = 0.4 × Liquidity^1.5 + 0.35 × log(Information) + 0.25 × Population^0.8
```

When network value exceeds outside opportunities, participation becomes economically compulsory.

### Critical Mass Threshold
At ~65% coverage, network effects dominate. Whales must join or be excluded from the dominant market.

---

## Security Philosophy

### Inclusion Over Exclusion
Any restriction that alienates a population creates fork pressure. Security through broad coalition, not gatekeeping.

### Time as the Universal Limiter
Instead of identity-based caps, use time and reputation. New entrants start weak; trust is earned.

### Personhood Progression (for AI)
```
TOOL   → 0.0x governance (new, sponsored)
AGENT  → 0.1x governance (6 months, 1000 tx)
ENTITY → 0.5x governance (2 years, 10K tx)
PERSON → 1.0x governance (5 years, community vouching)
```

No permanent caps - but swarms can't instantly overwhelm.

### Legitimacy Gradient
```
CORE     → Full KYC, institutional access
STANDARD → Pseudonymous, normal reputation
PRIVACY  → Anonymous, higher collateral
EDGE     → Grey market, highest collateral
```

All layers inside the tent. Even edge participants pay fees, get UBI, bound by constitution.

---

## Implementation Mapping

| Concept | Primary File | Notes |
|---------|--------------|-------|
| Holon | `kernel/holon.py` | Fundamental identity unit |
| Name | `kernel/identity.py` | Portable reputation |
| Mantle | `kernel/identity.py` | Transferable authority |
| Enclave | `kernel/enclave.py` | Fractal groups + FlowRouter |
| Contract | `kernel/contract.py` | Cooperation primitive |
| Constitution | `kernel/constitution.py` | 5 invariants + checker |
| ZK System | `kernel/zk/mock_proof.py` | Mock proofs for simulation |
| Protocol | `protocol/collective_protocol.py` | Full economic implementation |

---

## Open Conceptual Questions

1. **AI Personhood Criteria**: What exactly qualifies an AI for PERSON stage? Must be governance-defined, evolvable.

2. **Fork Dynamics**: When does forking strengthen vs weaken the ecosystem?

3. **Superintelligence Alignment**: If an AI is smarter than us, do our incentives still work?

4. **Century-Scale Stability**: Do these mechanisms remain stable over 100+ years?

5. **Cross-Protocol Interop**: How do HOLOS Enclaves interact with external systems?

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2025-01-20 | Initial conception document |

---

## Related Documents

- `/core/MANIFEST.md` - File inventory and categorization
- `/docs/HOLOS_V3_REQUIREMENTS.md` - Detailed requirements
- `/docs/THREAT_MODEL.md` - Security architecture
- `/docs/LOCUS_proposals.md` - Queued changes from legacy analysis
