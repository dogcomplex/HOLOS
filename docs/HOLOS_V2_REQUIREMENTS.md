# HOLOS v2: Sovereign Computing Simulation - Requirements & Design

## Mission Statement

**Find the ideal stable immutable constitution** for a marketplace where sovereign AIs can interoperate while maintaining network-wide security, stability, and market efficiency **without top-down authorities**.

This must **out-compete other network systems** - finding the most efficient and profitable market design, regardless of whether our initial hypothesis (Harberger + UBI) is correct.

---

## Current State: HOLOPOLY Achievements

47 experiments completed validating core economics:
- Tax rate dominates strategy selection (5-30% range tested)
- Rent/tax ratio determines optimal strategy
- Wealth inequality is self-reinforcing (33x → 40x gap)
- Property ownership is the great wealth divider
- Resurrection + UBI keeps players alive through downturns
- Inflation inverts optimal strategy (property beats cash)

**HOLOPOLY is ~70% generalizable** but deeply coupled to Monopoly mechanics.

---

## Core Concept: ZK Bubbles as Fundamental Identity

Every entity is a **ZK-proof bubble** protecting its interior while exposing a verifiable public interface:

```
┌─────────────────────────────────────────────┐
│              ZK BUBBLE (Holon)               │
│  ┌─────────────────────────────────────┐    │
│  │     PRIVATE INTERIOR                │    │
│  │     - Balance (hidden)              │    │
│  │     - Strategy (hidden)             │    │
│  │     - Sub-holons (hidden)           │    │
│  └─────────────────────────────────────┘    │
│                    │                         │
│            ZK Proofs (selective reveal)      │
│                    ▼                         │
│  ┌─────────────────────────────────────┐    │
│  │     PUBLIC INTERFACE                │    │
│  │     - Identity (Name)               │    │
│  │     - Solvency proof                │    │
│  │     - Constitutional compliance     │    │
│  │     - Exit protocol                 │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

**Fractal structure**: Individuals → Groups → Guilds → Network - all are ZK bubbles with identical interface.

---

## Key Principles

### 1. Right to Exit (Constitutional Invariant)
At any level of the fractal hierarchy, entities can exit without permission from parent/peers. This is an **ethical stance that must prove economically viable**.

### 2. Names vs Mantles
- **Name**: Persistent identity with reputation. Travels with you on exit. Accumulates history.
- **Mantle**: Transferable authority with rights + responsibilities. Stays behind on exit.

### 3. Dual Vision: AI and Human Operators
All roles designed for both AI and human operation (different timescales). Constitution must work for both.

### 4. Mock ZK, Real Economics
Mock ZK proofs for simulation; smart contracts for efficient trade pipelines; ZKP as fallback membrane.

---

## Constitutional Invariants (Must Test Economically)

These five rules **cannot be violated**, even by 51% majority:

| Invariant | Description | Test |
|-----------|-------------|------|
| **Non-Blocking Exit** | Sub-Holon can detach without parent permission | Exit always succeeds |
| **Proof of Solvency** | SUM(Inputs) >= SUM(Outputs), provable via ZK | No hidden insolvency |
| **Explicit Consent** | Membership requires bilateral cryptographic consent | No forced membership |
| **Sybil Resistance** | Voting weight proportional to proven root | Attacker can't dominate |
| **Legible Interface** | Public methods standardized; interior private | Interoperability |

---

## Key Experiments: Exit Economics & Cooperation

### Exit Viability (Critical - ethical stance must work economically)

| Experiment | Setup | Success Metric |
|------------|-------|----------------|
| **E1: Exit Survival** | Holon exits 4-level hierarchy | >80% remain solvent after 50 turns |
| **E2: Exit Cascade** | One exit in interconnected Sheaf | No cascade failures |
| **E3: Competitive Exit** | Two Sheafs, different governance | Migration toward better Sheaf |
| **E4: Exit Cost Sweep** | Vary exit cost 0-20% | Find viable range |

### Contract Cooperation

| Experiment | Setup | Success Metric |
|------------|-------|----------------|
| **C1: Contract vs Hierarchy** | Same task, both approaches | Contracts competitive on cost |
| **C2: Breach Economics** | Vary bond size | Higher bond → fewer breaches |
| **C3: Reputation Value** | Good vs bad Name | Good Names earn premium |
| **C4: Coalition Formation** | 10 Holons, can form Sheafs | Groups outperform solo |

### Market Efficiency (Must out-compete alternatives)

| Experiment | Setup | Success Metric |
|------------|-------|----------------|
| **M1: Price Discovery** | New Mantles introduced | Valuations converge to equilibrium |
| **M2: Harberger vs Auction** | Same assets, both markets | Compare efficiency |
| **M3: Sybil Attack** | 10x resources attacker | Constitution prevents takeover |
| **M4: Scale Test** | 10 → 100 → 1000 Holons | Sub-linear cost scaling |

---

## Implementation: File Structure

```
/home/user/HOLOS/
├── holopoly/                    # EXISTING - kept as game implementation
│   ├── kernel/                  # Monopoly-specific logic
│   ├── agents/
│   └── analysis/
│
└── holos/                       # NEW - sovereign computing layer
    ├── kernel/
    │   ├── holon.py
    │   ├── identity.py          # Name, Mantle
    │   ├── contract.py
    │   ├── sheaf.py
    │   ├── economics.py         # Extended from holopoly
    │   ├── constitution.py
    │   └── zk/
    │
    ├── games/
    │   └── holopoly_adapter.py  # HOLOPOLY as Sheaf
    │
    ├── experiments/
    │   ├── exit_economics/
    │   ├── contract_cooperation/
    │   └── market_efficiency/
    │
    └── tests/
```

---

## Core Abstractions

See implementation in `holos/kernel/`:
- `holon.py` - Holon, HolonId, HolonStatus
- `identity.py` - Name, Mantle
- `contract.py` - Contract, Obligation, Exit
- `sheaf.py` - Sheaf, Membership, Governance
- `constitution.py` - Constitutional invariant checker
- `zk/` - Mock ZK proof system
