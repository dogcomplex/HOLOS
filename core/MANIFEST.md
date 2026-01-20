# HOLOS Core Manifest

## Source of Truth
This manifest documents the authoritative file structure for HOLOS, identifying core vs peripheral files.

**Generated from:** `find /home/user/HOLOS -type f \( -name "*.py" -o -name "*.md" \) | sort`

---

## Core Files (Essential for Understanding HOLOS)

### Kernel Layer - Source of Truth for Concepts
These define the fundamental abstractions. Protocol implementations MUST align with these.

| File | Lines | Purpose |
|------|-------|---------|
| `holos/kernel/holon.py` | 270 | **Holon** - Fundamental identity unit. ZK bubble with LOCUS/SIGNUM/SENSUS layers. |
| `holos/kernel/identity.py` | 365 | **Name/Mantle** - Portable reputation (Name) vs transferable authority (Mantle). |
| `holos/kernel/constitution.py` | 516 | **Constitutional Invariants** - The 5 immutable rules (InvariantType enum). |
| `holos/kernel/enclave.py` | 607 | **Enclave** - Fractal group structure. FlowRouter for UBI. Scale taxonomy. |
| `holos/kernel/contract.py` | 426 | **Contract** - Cooperation primitive with guaranteed exit. |
| `holos/kernel/zk/mock_proof.py` | 442 | **ZK System** - MockProver/MockVerifier. StatementType enum. Cost model. |

### Protocol Layer - Economic Implementation
Implements the economic mechanisms using kernel abstractions.

| File | Lines | Purpose |
|------|-------|---------|
| `holos/protocol/collective_protocol.py` | 1379 | **Full Protocol** - ZK proofs, progressive fees, FlowRouter UBI, AMM pools, quadratic voting. |
| `holos/protocol/small_collective_sim.py` | 396 | **Simulation** - Tests protocol at 10-100 member scale. |

### Requirements Documentation
| File | Lines | Purpose |
|------|-------|---------|
| `docs/HOLOS_V2_REQUIREMENTS.md` | 157 | **Core Requirements** - Mission, constitutional invariants, experiment design. |

---

## Naming Conventions (Authoritative)

### Scale Taxonomy (from kernel/enclave.py)
```
ENCLAVE   → < 100 members (base group)
COLLECTIVE → 100-999 members (mid-scale)
KINGDOM   → 1000+ members (large-scale)
```

### Root Types (from kernel/identity.py)
```
HUMAN    → Biometric/government verified
AI       → Verified AI agent
CAPITAL  → Proof-of-stake/work/burn
PROTOCOL → Smart contract / protocol
```

### Constitutional Invariants (from kernel/constitution.py)
```
NON_BLOCKING_EXIT  → Sub-Holon can detach without parent permission
PROOF_OF_SOLVENCY  → SUM(Inputs) >= SUM(Outputs)
EXPLICIT_CONSENT   → Membership requires bilateral consent
SYBIL_RESISTANCE   → Voting weight proportional to proven root
LEGIBLE_INTERFACE  → Public methods standardized; interior private
```

### ZK Statement Types (from kernel/zk/mock_proof.py)
```
SOLVENCY      → "My balance >= X"
RANGE         → "Value V is in range [A, B]"
MEMBERSHIP    → "I am a member of Enclave E"
IDENTITY      → "I control Name N"
CONSTITUTIONAL → "My action obeys Constitution C"
CONTRACT      → "I fulfilled Obligation O"
EXIT_RIGHT    → "I have the right to exit"
EXIT_CLEAN    → "I owe nothing to Enclave E"
```

---

## Non-Core Files (Supporting/Experimental)

### Experiments (Research/Validation)
| File | Lines | Purpose | Relevance |
|------|-------|---------|-----------|
| `holos/experiments/guild_victory.py` | 1566 | Information wars guild analysis | High - validates collective economics |
| `holos/experiments/collective_economics.py` | 933 | Wealth erosion mechanisms | High - informs protocol design |
| `holos/experiments/information_asymmetry.py` | 1008 | Information advantage analysis | Medium - validates ZK value |
| `holos/experiments/adversarial.py` | 1026 | Attack resistance testing | Medium - validates constitution |
| `holos/experiments/market_efficiency.py` | 931 | Market mechanism analysis | Medium - validates Harberger |

### Games (Simulation Environments)
| File | Lines | Purpose | Relevance |
|------|-------|---------|-----------|
| `holos/games/information_wars.py` | 1483 | Asymmetric information game | High - tests information economics |
| `holos/games/holopoly_adapter.py` | 418 | HOLOPOLY as HOLOS Enclave | Medium - bridge to existing game |

### Tests (Validation)
| File | Lines | Purpose |
|------|-------|---------|
| `holos/tests/test_information_wars.py` | 661 | Information wars test suite |
| `holos/tests/test_information_asymmetry.py` | 493 | Asymmetry test suite |
| `holos/tests/test_market_efficiency.py` | 473 | Market efficiency tests |
| `holos/tests/test_adversarial.py` | 456 | Adversarial attack tests |
| `holos/tests/test_guild_victory.py` | 393 | Guild victory tests |
| `holos/tests/test_flow_economics.py` | 316 | FlowRouter economics tests |
| `holos/tests/test_constitution.py` | 284 | Constitutional invariant tests |
| `holos/tests/test_exit.py` | 262 | Exit right tests |
| `holos/tests/test_holon.py` | 218 | Holon primitive tests |

### HOLOPOLY (Legacy Game Layer)
| File | Lines | Purpose | Relevance |
|------|-------|---------|-----------|
| `holopoly/kernel/game.py` | 605 | Monopoly-style game engine | Low - superseded by HOLOS |
| `holopoly/kernel/economics.py` | 565 | Harberger + UBI mechanics | Medium - foundational research |
| `holopoly/kernel/harberger.py` | 361 | Harberger tax implementation | Low - simpler version |
| `holopoly/agents/llm_client.py` | 450 | LLM agent integration | Low - game-specific |
| `holopoly/agents/agent.py` | 329 | Agent abstraction | Low - game-specific |
| `holopoly/ledger/db.py` | 415 | SQLite ledger | Low - game-specific |

### Documentation (Context)
| File | Lines | Purpose | Relevance |
|------|-------|---------|-----------|
| `docs/HOLOPOLY_MVP_REQUIREMENTS.md` | 911 | Original game requirements | Low - historical |
| `docs/HOLOPOLY_MVP_REQUIREMENTS_v2.md` | 706 | Updated game requirements | Low - historical |
| `docs/MVP_REQUIREMENTS.md` | 428 | General MVP requirements | Medium - context |
| `holopoly/EXPERIMENT_REPORT.md` | 593 | Experiment results | Medium - research findings |

---

## Consistency Notes

### Aligned ✓
- Protocol `Enclave` class matches kernel naming
- Protocol `EnclaveScale` taxonomy matches kernel
- Protocol `FlowRouter` implements kernel pattern (no treasury)
- Protocol constitutional checks reference kernel invariants

### Known Differences (Intentional)
- Protocol uses lowercase enum values ("solvency"), kernel uses uppercase ("SOLVENCY")
  - Protocol provides `proof_type` property for backward compat
- Protocol `ZKProof` is simplified vs kernel's `MockZKProof`
  - Protocol focuses on economic simulation, kernel on full ZK semantics
- Protocol has `SovereignIdentity`, kernel separates `Holon` + `Name`
  - Protocol merges for convenience at small scale

### To Reconcile (Future Work)
- Unify `ConstitutionalChecker` implementations
- Consider enum case consistency (uppercase recommended)
- Bridge `SovereignIdentity` ↔ `Holon` + `Name` more explicitly

---

## Quick Reference

### To understand HOLOS, read in order:
1. `docs/HOLOS_V2_REQUIREMENTS.md` - Mission and invariants
2. `holos/kernel/holon.py` - Fundamental identity
3. `holos/kernel/identity.py` - Name/Mantle split
4. `holos/kernel/constitution.py` - The 5 invariants
5. `holos/kernel/enclave.py` - Fractal groups + FlowRouter
6. `holos/protocol/collective_protocol.py` - Full implementation

### To run simulations:
```bash
python -c "from holos.protocol import test_small_collective; test_small_collective(100)"
python -c "from holos.protocol import test_scaling; test_scaling([10, 50, 100, 500])"
```

### To run experiments:
```bash
python -c "from holos.experiments.collective_economics import analyze_critical_mass; analyze_critical_mass()"
python -c "from holos.experiments.guild_victory import test_earning_parity; test_earning_parity()"
```
