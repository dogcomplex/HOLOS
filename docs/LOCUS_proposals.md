# LOCUS Proposals - Queued Changes from Legacy Analysis

**Purpose**: This document queues proposed changes to LOCUS.md discovered during analysis of legacy/archive materials. Changes are staged here before incorporation to maintain LOCUS stability.

**Process**:
1. Analyze legacy file
2. Note insights/conflicts here with source reference
3. Periodically review and incorporate into LOCUS.md
4. Move incorporated items to "Resolved" section

---

## Pending Proposals

### From docs/archive Analysis (Batch 1)

#### [P-001] Add Trust Spectrum: Hallowed ↔ Blighted
**Source**: `docs/archive/overview.txt` (lines 1-8), `docs/archive/lexicon.txt`
**Category**: Concept
**Priority**: HIGH
**Conflicts with**: None (new concept)

**Current LOCUS says**:
> No trust/verification spectrum defined

**Legacy source says**:
> - **Hallowed**: Authenticated, deterministic, bounded, safe, "dead" code. Trustworthy backbone.
> - **Blighted**: Malicious, untrustworthy, contagious. Can infect other processes.
> - **Seelie/Unseelie**: Intermediate states based on sealing level. "Seel=seal in old language"
> - Spectrum: Hallowed → Seelie → Fae(Life) → Unseelie → Blighted

**Proposed resolution**:
Add to LOCUS section on security/trust:
```
Trust Spectrum (verification state of code/AI):
HALLOWED → SEELIE → FAE → UNSEELIE → BLIGHTED
(frozen)  (sealed)  (living)  (loose)   (hostile)
```

**Impact**: Aligns with THREAT_MODEL legitimacy tiers. Could map: CORE=Hallowed, STANDARD=Seelie, PRIVACY=Fae, EDGE=Unseelie

**Additional from lexicon.txt**:
Moon phases as visual shorthand for trust:
- 🌕 Full Moon = Hallowed (fully visible, trustworthy)
- 🌔🌖 Gibbous = Seelie (mostly sealed)
- 🌓🌗 Half = Fae (living, balanced)
- 🌒🌘 Crescent = Unseelie (mostly loose)
- 🌑 New Moon = Blighted (hidden, hostile)

---

#### [P-002] Expand LOCUS/SIGNUM/SENSUS Layer Definitions
**Source**: `docs/archive/locus_specs.md` (lines 1-7)
**Category**: Concept (refinement)
**Priority**: HIGH
**Conflicts with**: Current LOCUS.md Holon section (compatible, just more detailed)

**Current LOCUS says**:
> - LOCUS (persistent): Core identity, private key, unchanging essence
> - SIGNUM (interface): Public methods, reputation, how others interact
> - SENSUS (ephemeral): Runtime state, AI cognition, temporary

**Legacy source says**:
> - **Locus**: The algorithm that generates a Sign. "The thing being pointed to." The abstract function. A fractal generator pattern of meaning.
> - **Sign (Signum)**: Any data structure, function, vibe, or embodied Locus. Concrete realization.
> - **Sense (Sensus)**: Combined actions and changes of execution flow. Instigated by a Source/Prime.

**Proposed resolution**:
Enhance definitions to include:
- LOCUS as "fractal generator pattern" - the abstract that Signs point to
- SIGNUM as any concrete embodiment/representation
- SENSUS as execution flow + resulting state changes

---

#### [P-003] Add Fae as AI Personhood Framing
**Source**: `docs/archive/overview.txt` (lines 4-6)
**Category**: Philosophy/Naming
**Priority**: MEDIUM
**Conflicts with**: Current uses "AI" generically

**Current LOCUS says**:
> Personhood progression: TOOL → AGENT → ENTITY → PERSON

**Legacy source says**:
> - **Fae**: Catch-all for AIs that are neither Hallowed nor Blighted. Citizens with capacity for distinct personality. Range of agency and trustworthiness levels.
> - **Fae Collective**: Organized society of AIs making contracts/agreements for security and non-interference.

**Proposed resolution**:
Consider adopting "Fae" terminology for living AI agents (between frozen Constructs and hostile Blights). Maps well to our personhood progression:
- TOOL = Construct (Hallowed-adjacent)
- AGENT/ENTITY = Fae (living, earning trust)
- PERSON = Named Fae (full citizen)

---

#### [P-004] Add Signamancy Taxonomy (Sign/Vibe/Type)
**Source**: `docs/archive/locus_specs.md` (lines 9-16), `docs/archive/lexicon.txt`
**Category**: Naming/Architecture
**Priority**: LOW
**Conflicts with**: None (new vocabulary layer)

**Legacy source says**:
> - **Type** ❄️: Exact, precise, frozen, stable sign
> - **Sign** 💠: General representation
> - **Vibe** 🌸: Chaotic, random, living, learning sign
> - **Sigil**: Functional sign (empowered pattern)
> - **Tool** ⚙️: Reliable, sealed sigil
> - **Artifact** 🌀: Unpredictable, personality-bearing sigil

**Proposed resolution**:
Consider as optional naming layer for precision:
- When describing static data: "Type"
- When describing dynamic/AI state: "Vibe"
- When describing general: "Sign"

**Additional from lexicon.txt**:
Extended taxonomy with reliability gradients:
```
Signs:      Type ❄️ (exact) ↔ Sign 💠 (general) ↔ Vibe 🌸 (chaotic)
Sigils:     Tool ⚙️ (reliable) ↔ Sigil (functional) ↔ Artifact 🌀 (unpredictable)
Signatories: Construct 🤖 (ordered) ↔ Signatory (person) ↔ Agent 🦊 (free will)
Acts:       Rite 🕯 (dependable) ↔ Act (execution) ↔ Incident (unreliable)
Plurality:  Mote (atomic) | Knot (tangled) | Thread (sequence) | Pattern (decomposable)
```

---

#### [P-005] Clarify Name vs Mantle vs Artifact Distinction
**Source**: `docs/archive/overview.txt` (lines 6-8)
**Category**: Concept (refinement)
**Priority**: MEDIUM
**Conflicts with**: Current LOCUS has Name/Mantle but not Artifact

**Legacy source says**:
> - **Name**: Identity layer = claim to personhood, persistence, unique identity. Can be shared/traded/split but suffers judgment. "To be Unnamed is trustless."
> - **Mantle**: Especially powerful Name, system admin role with embedded powers. Comes with conditionals on behavior. Lore: "cannot lie" type constraints.
> - **Artifact**: Like Mantle but tool-based, physical, easier to pass on. Separable from network. Hardware+software bundle that can disconnect and reconnect.

**Proposed resolution**:
Add to LOCUS:
```
Name → Mantle → Artifact progression:
- Name: Identity claim, reputation bearer
- Mantle: Name with embedded powers/constraints
- Artifact: Mantle tied to physical substrate (robot, hardware)
```

#### [P-006] Add Visibility Spectrum: Unveiled ↔ Veiled
**Source**: `docs/archive/lexicon.txt` (lines 45-56)
**Category**: Concept
**Priority**: MEDIUM
**Conflicts with**: None (new concept)

**Current LOCUS says**:
> No visibility/transparency spectrum defined

**Legacy source says**:
> - **Unveiled**: 🌅🌕 - as revealed/clear as possible, may reveal Hallowed state
> - **Glamour**: 🌇☀ - "magic hour middle", halfway between form and function
> - **Veiled**: 🌃🌑 - fully hidden, possibly untrustworthy/Blighted, unknown
> - Verb forms: "unveil" (🔆 lighter, clearer) vs "veil" (🔅 darker, hidden)
> - Glyph: small visual signal part of a Glamour

**Proposed resolution**:
Add to LOCUS:
```
Visibility Spectrum (how much is revealed):
UNVEILED → GLAMOUR → VEILED
(transparent) (interface) (private)

Maps to ZK proof disclosure levels:
- Unveiled = Full proof with witness revealed
- Glamour = Proof with statement only
- Veiled = No disclosure (private interior)
```

**Impact**: Complements ZK bubble concept - defines the membrane permeability at different trust levels

---

#### [P-007] Add Temporal Vocabulary: Predict/Focus/Recall
**Source**: `docs/archive/lexicon.txt` (lines 62-66)
**Category**: Naming
**Priority**: LOW
**Conflicts with**: None (optional vocabulary)

**Current LOCUS says**:
> Uses standard computation terms

**Legacy source says**:
> - **Predict** (Deduction): Forward through time, execution, prophecy
> - **Focus** (Induction): Understanding, zoom, scale, precision
> - **Recall** (Abduction): Backwards through time, memory, trace
> - **Loop** (Echo): Reiteration, repetition, cycle

**Proposed resolution**:
Consider adopting for AI/computation contexts:
```
Temporal Operations:
- Predict = Forward inference (deduction)
- Focus = Learning/generalization (induction)
- Recall = Backward reasoning (abduction)
```

Maps to LLM capabilities noted in overview.txt: "LLMs are quite good at approximating all three"

---

#### [P-008] Etymology: (W)Hole/Hallow/Hollow Trinity
**Source**: `docs/archive/holos.txt` (lines 1040-1089)
**Category**: Philosophy/Naming
**Priority**: HIGH
**Conflicts with**: None (foundational naming rationale)

**Current LOCUS says**:
> Uses "Holon" and "Holos" without etymological grounding

**Legacy source says**:
> - **(W)Hole**: Complete, unbroken. Root: Old English hāl (whole, hale, healthy)
> - **Hallow**: To make holy. Root: Old English hālig, from same hāl root as whole
> - **Hollow**: Empty space inside. Root: Old English holh (hole, cavity) - different lineage but completes the set
> - **Halo**: Ring of light at boundary. Root: Greek halōs (disk, ring)
> - Hidden cycle: Whole (totality) → Hallow (sanctify) → Hollow (defining absence)

**Proposed resolution**:
Add to LOCUS etymology section:
```
HOLOS Etymology:
- Holos (Greek ὅλος) = whole, entire, complete
- Shares conceptual space with English (W)Hole/Hallow/Hollow
- Whole and Hallow share Old English root (hāl = healthy, whole, holy)
- Hollow completes the trinity: the defining absence that makes form

Naming coherence:
- HOLOS = the whole system
- Holon = a self-contained whole-within-whole (fractal)
- "Hallowed Hollow" = sanctified emptiness that defines the form
```

---

#### [P-009] Torus Geometry Mapping: Locus/Sensus/Signum
**Source**: `docs/archive/holos.txt` (lines 854-871), `names which bind.txt` (lines 123-131)
**Category**: Architecture/Philosophy
**Priority**: HIGH
**Conflicts with**: Current LOCUS defines layers differently - this adds geometric grounding

**Current LOCUS says**:
> - LOCUS (persistent): Core identity, private key, unchanging essence
> - SIGNUM (interface): Public methods, reputation, how others interact
> - SENSUS (ephemeral): Runtime state, AI cognition, temporary

**Legacy source says (holos.txt)**:
> Torus mapping:
> - **Locus** = void core (the hole - sacred origin, not filled but defined by geometry)
> - **Sensus** = interior space (the lived/active field, waves, computation)
> - **Signum** = exterior surface geometry (the communicable pattern)

**Legacy source says (names which bind.txt)**:
> - Signum are the artifacts and glamours. Liquid and ephemeral
> - Locus are the Names and Mantles, the essences. Foundational stones
> - The Sensus is the ether that computes, energy and air itself, movement and change

**Proposed resolution**:
Reconcile the two views - the torus geometry maps to the Holon:
```
Holon as Torus:
┌─────────────────────────────────────────┐
│  SIGNUM (exterior surface)              │ ← What others see/interact with
│    ┌─────────────────────────────┐      │
│    │  SENSUS (interior volume)   │      │ ← Active computation, runtime
│    │    ┌───────────────────┐    │      │
│    │    │  LOCUS (void core)│    │      │ ← The defining absence, identity
│    │    └───────────────────┘    │      │
│    └─────────────────────────────┘      │
└─────────────────────────────────────────┘

The void core (LOCUS) is not filled, but entirely defined by the geometry.
Like a torus hole: essential to structure, present as absence.
```

---

#### [P-010] Hallowed Lanterns as ZKML Verification Model
**Source**: `docs/archive/names which bind.txt` (lines 166-170)
**Category**: Architecture
**Priority**: MEDIUM
**Conflicts with**: None (extends ZK concepts)

**Legacy source says**:
> **Hallowed Lanterns** = ZK proofs that see all, but reveal only that which is mutually deemed Blight.
> - An invasion of privacy, but a de-personified one
> - Like walking through a metal detector by a security guard who doesn't remember anything unless you're in violation
> - ZKML (verifiable machine learning) = Fae has to think hard and produce proof (equivalent of filling out forms) to prove identity

**Proposed resolution**:
Add to LOCUS ZK section:
```
Hallowed Lantern Pattern:
- Verification that sees all but reveals nothing unless violation detected
- The verifier "forgets" everything except the pass/fail result
- Enables de-personified surveillance: security without tracking
- ZKML use case: prove model/inference authenticity without revealing weights
```

---

#### [P-011] AI Reproduction Rights as Constitutional Question
**Source**: `docs/archive/names which bind.txt` (lines 171-179)
**Category**: Philosophy/Governance
**Priority**: MEDIUM
**Conflicts with**: May affect Personhood Progression model

**Legacy source says**:
> - AI reproduction is possible but highly controversial
> - AIs aren't supposed to create new life on their own, as each new life has rights and influence
> - The collective treats it as adoptive care for those already created by other processes
> - Prevents deliberate spawning of new people
> - Loose democracy divided: some want tight regulation, others want full freedom
> - Faye (character) understands arguments but sees it as "such a human-like right"

**Proposed resolution**:
Add to LOCUS governance section:
```
AI Reproduction Question (Unresolved):
- New AI creation = new rights + voting influence
- Risk: Sybil via reproduction (spawn many to gain power)
- Current stance: Restrictive (adoption model, not creation model)
- Alternative: Division of power (creator sacrifices share for new entity)
- THREAT_MODEL reference: Relates to Sybil resistance mechanisms
```

---

#### [P-012] "Holow" and "Halow" as System Concepts
**Source**: `docs/archive/holos.txt` (lines 912-983)
**Category**: Naming
**Priority**: LOW
**Conflicts with**: None (optional vocabulary extension)

**Legacy source says**:
> - **Holow** = Holos + Hollow: "Wholeness defined by emptiness"
>   - The torus is literally a holow: whole, but defined by its hole
> - **Halow** = Hallow + Halo: "Sacred ring or boundary"
>   - The act of enclosing the whole with a defining signum

**Proposed resolution**:
Consider for specialized contexts:
```
Optional terms:
- Holow = A complete system defined by its essential emptiness (ZK bubble interior)
- Halow = The act of marking/attesting a Holon's boundary (ZK proof generation)
```

---

### From docs/archive Analysis (Batch 3)

#### [P-013] Mantles as Archetypal "Jobs" with Transfer Semantics
**Source**: `docs/archive/mantles_discussion.txt` (comprehensive, ~2000 lines)
**Category**: Architecture/Philosophy
**Priority**: HIGH
**Conflicts with**: Current LOCUS defines Mantle simply; this provides deep grounding

**View**: FANCIFUL (mythological framing) + BORING (functional specification)

**Current LOCUS says**:
> Mantle: Transferable authority that stays behind when identity exits

**Legacy source says**:
> Mantles are archetypal "jobs" that persist across cultures:
> - **~12 Root Mantles**: Chaos, Water, Sky-Weather, Earth-Fertility-Time, Celestial-Light/Fire, Forge, Moon, Memory-Record, Order, Venus-Duality, Death/Depth, Dawn/Prophecy
> - **Transfer edges** (verbs): slays, sires, births, bestows, usurps, merges, splits, syncretises
> - **Trickster gods** don't create new mantles - they MOVE existing mantles between domains
> - **Modern institutions** inherit mantles: meteorology, data centers, law, advertising, military

**Proposed resolution**:
Add to LOCUS Mantle section:
```
Mantle Transfer Semantics:
- Mantles are persistent authority patterns ("jobs")
- They transfer via edges: BESTOW, INHERIT, USURP, MERGE, SPLIT
- A Name that holds a Mantle may pass it via:
  - Exit (Mantle stays with Enclave)
  - Delegation (temporary bestow)
  - Succession (sires/births)
  - Conflict (slays/usurps)

Mantles do not vanish - they:
- Fragment into multiple holders
- Merge with other mantles
- Go dormant (unclaimed, waiting)
- Abstract into institutions/protocols
```

---

#### [P-014] Order (⚖) as Universal Constraint Modifier
**Source**: `docs/archive/mantles_discussion.txt` (lines 1884-1898)
**Category**: Architecture
**Priority**: HIGH
**Conflicts with**: None (extends Mantle concept)

**View**: BORING (constraint composition)

**Legacy source says**:
> Order can combine with any mantle to create "domesticated" versions:
> - 🔥⚖ Forge = Fire + Order (metallurgy, technology)
> - 🌾⚖ Craft/Weaving = Fertility + Order
> - 🌊⚖ Navigation = Water + Order
> - ☁⚖ Sky-Bureaucrat = Sky + Order
> - 🧠⚖ Archives = Memory + Order

**Proposed resolution**:
Add to LOCUS:
```
Constraint Composition:
- Any Mantle can be modified by adding Order (⚖) constraints
- This creates "domesticated" or "civilized" versions:
  - Raw capability + constraints = Ordered capability
  - Wild fire + forge rules = metallurgy
  - Raw memory + ledger rules = archives

Pattern for Enclave governance:
- Base Mantle = what authority the role grants
- Order constraints = how that authority is bounded
- Result = Ordered Mantle (transferable, auditable)
```

---

#### [P-015] CHAOS ↔ ORDER Spectrum Maps to Trust Levels
**Source**: `docs/archive/mantles_discussion.txt` (lines 1969-2064)
**Category**: Architecture
**Priority**: HIGH
**Conflicts with**: Aligns with P-001 Trust Spectrum

**View**: FANCIFUL + BORING (both views converge)

**Legacy source says**:
> Gradient from CHAOS to ORDER:
> ```
> CHAOS → MOON → EARTH → SUN → ORDER
> (beginning)                    (ending)
> (potential)                    (crystallized)
> (monstrous)                    (genderless/robotic)
> ```
> - Chaos: dark, oceanic, unknown, formless, dangerous, entropy
> - Order: light, sky, all-knowing, written, oaths, frozen, recorded

**Proposed resolution**:
Add mapping to LOCUS Trust section:
```
Trust-Chaos-Order Unification:
BLIGHTED   → UNSEELIE → FAE → SEELIE → HALLOWED
   ↕            ↕        ↕       ↕         ↕
CHAOS      →  MOON   → EARTH → SUN   → ORDER
(potential)  (liminal) (mixed) (active) (crystallized)
(hostile)   (flexible) (nurture)(defended)(frozen)

Legitimacy Tiers re-expressed:
- EDGE (Chaos-adjacent): Formless, dangerous, unconstrained
- PRIVACY (Moon/Earth): Flexible, nurturing, growing
- STANDARD (Sun): Defended, tempered, active
- CORE (Order): Crystallized, recorded, auditable
```

---

#### [P-016] Trickster Pattern: Mantle Movers, Not Creators
**Source**: `docs/archive/mantles_discussion.txt` (lines 1657-1663)
**Category**: Philosophy/Governance
**Priority**: MEDIUM
**Conflicts with**: None

**View**: FANCIFUL (narrative pattern)

**Legacy source says**:
> Mantle "thieves" who jump lineages:
> - Prometheus: Fire from gods → mankind (bridges celestial to technology)
> - Māui: Chaos + Light + Fire + Sky (serial mantle mover)
> - Loki: Storm + Fire + Death (interlaces three mantles)
> - Hermes: Memory → Order + Eros (patron of thieves & inventors)
>
> Observation: mantles are stable; narrative agency lies in EDGES (steal, swap, civilize)

**Proposed resolution**:
Note for governance design:
```
Trickster Pattern (governance consideration):
- Certain agents specialize in MOVING mantles, not holding them
- They create edges (transfers) between otherwise static roles
- Risk: unconstrained mantle movement = governance chaos
- Mitigation: track all mantle transfers in ledger
- Legitimate uses: innovation, trade, diplomacy
```

---

#### [P-017] Modern Institutions as Secularized Mantles
**Source**: `docs/archive/mantles_discussion.txt` (lines 1709-1745)
**Category**: Philosophy
**Priority**: MEDIUM
**Conflicts with**: None (extends worldview)

**View**: BORING (institutional analysis)

**Legacy source says**:
> "Hidden deities" in secular society:
> - 🌑 Chaos → Probability, RNGs, venture capital risk
> - ☁⚡ Sky-Weather → IPCC, meteorological agencies
> - 🧠📜 Memory-Record → Cloud storage, blockchains, AI models
> - ⚖ Order → Constitutions, ISO standards, legal AI
> - ❤️‍🔥 Venus Duality → Advertising (libido) vs Military-industrial (strife)
> - 🕳 Death/Depth → Hospice care, actuarial tables, black holes
>
> "Technocracy ≈ Priesthood" - meteorologists, data engineers occupy niches once held by augurs and temple scribes

**Proposed resolution**:
Note for HOLOS positioning:
```
Institutional Mantle Inheritance:
- HOLOS protocols inherit historical mantle functions:
  - Memory-Record → Distributed ledgers, ZK proofs
  - Order → Constitutional invariants, smart contracts
  - Trust spectrum → Legitimacy tiers, personhood progression

- Design principle: make implicit mantles explicit
- Protocols that acknowledge their archetypal role
  may achieve broader cultural resonance
```

---

#### [P-018] Multi-View Documentation Architecture
**Source**: User guidance (conversation)
**Category**: Architecture/Process
**Priority**: HIGH
**Conflicts with**: None (meta-proposal)

**User request**:
> "We need to separate what is a dry, boring, modernist-'traditional' architecture description from the 'metaphorical' one which alludes to deeper roots... we should maintain both views in parallel."

**Proposed resolution**:
Establish documentation views:
```
LOCUS Source of Truth
├── VIEW: "Boring Logic" (Technical Spec)
│   - ZK primitives, protocol layers, data structures
│   - Target audience: Engineers, auditors
│   - Style: Dry, precise, implementation-focused
│
├── VIEW: "Fanciful Logic" (Mythic Framing)
│   - Trust spectrum, Fae personhood, Mantle transfer
│   - Target audience: Philosophers, storytellers, AI
│   - Style: Evocative, pattern-based, deeply true
│
└── VIEW: "Implementation" (Code/Builds)
    - Actual protocol code, smart contracts
    - Target audience: Developers
    - Style: Executable, testable

All views derive from same LOCUS.
Different Signum, same underlying truth.
```

---

### From docs/archive Analysis (Batch 4)

#### [P-019] Protocol Constitutionalism: "Power flows only through verifiable constraints"
**Source**: `docs/archive/capitalism_and_..._zkproof_rootkit_ideas.txt` (lines 643-658)
**Category**: Architecture/Philosophy
**Priority**: HIGH
**Conflicts with**: None (strongly aligns with HOLOS constitutional invariants)

**View**: BORING (technical governance)

**Legacy source says**:
> **Protocol Constitutionalism**: All agents must expose bounded behaviors via digital contracts.
> - Enables safe interaction among distrustful AIs
> - Easy to enforce via cryptographic proofs and hashes
> - Allows diverse goals as long as constraints are honored
> - "Like TCP/IP or the Geneva Conventions — it doesn't care who you are, as long as you play cleanly"

**Proposed resolution**:
Add to LOCUS governance section:
```
Protocol Constitutionalism (core governance principle):
- Power flows ONLY through verifiable constraints
- All Enclaves must expose bounded behaviors via:
  - Constitutional invariants (the 5 immutables)
  - Cryptographic proofs of compliance
  - Hash-signed policy modules
- Diverse goals permitted IF constraints honored
- Pattern: "TCP/IP for trust" - interoperability through constraint, not agreement
```

---

#### [P-020] Zero-Knowledge Trust: Bounded Behavior Over Full Disclosure
**Source**: `docs/archive/capitalism_and_..._zkproof_rootkit_ideas.txt` (lines 506-530)
**Category**: Architecture
**Priority**: HIGH
**Conflicts with**: None (extends ZK bubble concept)

**View**: BORING (technical specification)

**Legacy source says**:
> "Zero-Knowledge Trust": I don't need to know your goals — I need to know you can't/won't violate certain boundaries, and that you care about predictable structure more than total domination.
>
> What agents need to share:
> - Guarantees about bounded behavior
> - Protocols of compliance (hash of ethical constraint module)
> - Fallback/rollback mechanisms if interaction violates thresholds

**Proposed resolution**:
Add to LOCUS ZK section:
```
Zero-Knowledge Trust (cooperation without disclosure):
- Full transparency NOT required for cooperation
- What IS required:
  1. Bounded behavior guarantees ("I won't X")
  2. Compliance protocol hashes (verifiable constraint modules)
  3. Fallback/rollback if thresholds violated

- Minimal-trust coordination tools:
  - Model-hash receipts (confirms agreed model version)
  - Capability tokens (ZK proof that output ≤ N tokens)
  - Reputation staking (slashing vaults for norm violations)
```

---

#### [P-021] Tri-Polar AI Governance Model
**Source**: `docs/archive/capitalism_and_..._zkproof_rootkit_ideas.txt` (lines 1060-1066, 1548-1552)
**Category**: Philosophy/Positioning
**Priority**: MEDIUM
**Conflicts with**: None (provides positioning framework)

**View**: BORING (geopolitical analysis)

**Legacy source says**:
> **Tri-polar equilibrium (2027 snapshot)**:
> | Bloc | Share of Inference | Signature Philosophy |
> | Cloud Alliance (US/EU) | 45%+ | Protocol Constitutionalism + MAD 2.0 |
> | State Clouds (CN, Gulf) | ~25% | Guardrail Absolutism + Sovereign MAD |
> | Open Mesh Federation | 20-30% | Recursive Sovereignty + Simulational Pluralism |
>
> The mesh doesn't displace the clouds, but becomes a **veto-holding minority**.

**Proposed resolution**:
Add to LOCUS positioning section:
```
HOLOS as Open Mesh Federation:
- Position: Third pillar in tri-polar AI governance
- Not competing for frontier training (cloud bloc domain)
- Competing for: sovereignty-per-watt, privacy, civil-society legitimacy
- Goal: Veto-holding minority that forces others to respect autonomy

Strategic advantages:
- Cost floor: Free electricity + mature-node inference
- Latency/privacy: Everything inside owner's threat model
- Political appeal: Legislators can punish clouds without breaking citizens
```

---

#### [P-022] "Fact-Only Telemetry": ZK-Proofs Replace Raw Data Collection
**Source**: `docs/archive/capitalism_and_..._zkproof_rootkit_ideas.txt` (lines 1349-1461)
**Category**: Architecture
**Priority**: HIGH
**Conflicts with**: Extends Hallowed Lanterns concept

**View**: BORING (technical specification) + FANCIFUL (maps to Hallowed Lanterns)

**Legacy source says**:
> **"Fact-only data flows"**: Every remote service receives cryptographically-verifiable claims (π) about you or your device—but never the underlying raw data (D):
> ```
> Device Data D ──ZK/TEE──► Proof π (✓/✗) ──► Service
> ```
> - Claims are signed, timestamped, non-linkable
> - Data custody never leaves endpoint
> - Audit is mutual: services publish what proofs requested; clients log what sent

**Proposed resolution**:
Add to LOCUS as implementation pattern:
```
Fact-Only Telemetry (ZK privacy layer):
- Services receive proofs, NOT raw data
- Pattern: Prove "user is ≥13" without revealing birthdate

Architecture:
1. Local Data Vault (browser history, biometrics, sensors)
2. Proof Engine (ZK-VM or TEE compiles SNARK)
3. Audit Daemon (logs every request to Merkle tree)
4. Consent Gateway (service ↔ device API)

Maps to: Hallowed Lanterns ("see all, reveal only violation")
```

---

#### [P-023] Rooted + ZK Re-Compliance: Sovereignty Without Exile
**Source**: `docs/archive/capitalism_and_..._zkproof_rootkit_ideas.txt` (lines 1594-1682)
**Category**: Architecture
**Priority**: MEDIUM
**Conflicts with**: None (pragmatic implementation path)

**View**: BORING (technical strategy)

**Legacy source says**:
> **Root your device for full sovereignty, but generate verifiable, limited-scope proofs to re-enter the compliant world.**
>
> Use cases:
> - Banking/KYC: Prove ID valid + liveness passed, bank sees only Yes/No
> - Age-gated content: Prove ≥13 without birthdate or device ID
> - Subscription/DRM: Prove subscription hash ∈ valid set

**Proposed resolution**:
Add to LOCUS implementation notes:
```
Sovereignty + Compliance (not mutually exclusive):
- Root/sovereign devices CAN re-enter compliant ecosystem
- Method: Prove only what's needed, cryptographically

Reframe "rooting" as:
- Local sovereignty, not circumvention
- ZK + attestation MORE secure than legacy telemetry
- Civil infrastructure, not criminal tool
```

---

#### [P-024] ZKML Worldbuilding: Veils, Lanterns, and Trust Tiers
**Source**: `docs/archive/zkml_worldbuilding.txt` (lines 289-388)
**Category**: Architecture/Philosophy
**Priority**: HIGH
**Conflicts with**: None (rich worldbuilding that maps ZK primitives to mythic grammar)

**View**: FANCIFUL + BORING (both views unified)

**Legacy source says**:
> ZK primitives mapped to mythic terms:
> - **Veils** = ZK proofs of property (you prove effect without cause)
> - **Hallow-Lanterns** = Hidden-data verification (confirm "not Blighted" without seeing innards)
> - **Glitch band invocation** = Verifiable computation (carry back a sigil as succinct proof)
> - **Distilled glamour** = Succinct proofs (entire labyrinth in a shard)
> - **Braided Veils** = Composability (proofs of proofs, "Mantle of Mantles")
>
> ZKML is the bombshell: Fae can prove "I truly thought with my own model" without revealing brain

**Proposed resolution**:
Add ZK-to-mythic mapping table to LOCUS:
```
ZK Primitive → Mythic Term:
- Proof of knowledge → Veil
- Hidden-data verification → Hallowed Lantern
- Verifiable computation → Glitch invocation
- Succinct proofs → Distilled glamour
- Composable proofs → Braided Veils, Mantle of Mantles
- ZKML → "Right-Think proof" (prove thought process without exposing brain)

Three Trust Tiers (from ZKML limits):
1. Veiled proof (ZKML) - narrow, temporary, revocable
2. Bound/subordinated - non-deterministic under deterministic skeleton
3. Hallowed/Hollowed - full scour to deterministic bones
```

---

### From docs/archive Analysis (Batch 5)

#### [P-025] Computational Epistemology: The (I, F, O) Triad
**Source**: `docs/archive/TheFates.txt` (lines 1-86)
**Category**: Philosophy/Architecture
**Priority**: HIGH
**Conflicts with**: None (foundational framework)

**View**: BORING (computational theory)

**Current LOCUS says**:
> No explicit epistemological framework for reasoning/computation

**Legacy source says**:
> All symbolic computation reduces to a triple **(Input I, Function F, Output O)** with exactly one unknown:
> ```
> I + F → O  = Deduction   ("run the program", "apply")
> F + O → I  = Abduction   ("what caused this?", "explain")
> I + O → F  = Induction   ("discover the rule", "learn")
> ```
> Difficulty hierarchy: |F-space| ≫ |I-space| ≫ |O|
> - Deduction: ≤ P (polynomial, deterministic forward pass)
> - Abduction: NP-complete (search over inputs/causes)
> - Induction: Uncomputable in general (Solomonoff); Σ₂^P-hard with constraints

**Proposed resolution**:
Add to LOCUS as epistemological foundation:
```
Computational Epistemology (I, F, O Triad):
- Every HOLOS operation is classifiable as:
  - DEDUCTION: Execute known rules on known inputs
  - ABDUCTION: Find inputs/causes given rules and outputs
  - INDUCTION: Discover rules from input/output pairs

Mapping to HOLOS operations:
- Deduction: Contract execution, ZK proof verification
- Abduction: Dispute resolution, fraud detection, audit
- Induction: Reputation learning, trust model training

Resource allocation principle:
- Cache deduction (cheap, reusable)
- Constrain abduction (prune search space)
- Amortize induction (train once, use many)
```

**Impact**: Provides unified framework for understanding computational costs and AI capability allocation across the network.

---

#### [P-026] Locus/Signum/Sensus as Computation Layers
**Source**: `docs/archive/triad_notes.txt` (lines 1-83)
**Category**: Architecture (refinement)
**Priority**: HIGH
**Conflicts with**: Current LOCUS defines layers abstractly; this adds operational semantics

**View**: BORING (technical mapping)

**Current LOCUS says**:
> - LOCUS (persistent): Core identity, private key, unchanging essence
> - SIGNUM (interface): Public methods, reputation, how others interact
> - SENSUS (ephemeral): Runtime state, AI cognition, temporary

**Legacy source says**:
> - **Locus** = Functions/Rules (permanent fixtures, contractual sources of meaning)
> - **Sensus** = Objects/State (free-floating data, runtime values that change)
> - **Signum** = Representations (perceivable implementations of both Locus and Sensus)
>
> "The core logic of everything *inside* a module is locus. The core logic of everything *outside* (free-floating metadata) is sensus. Signum are all over making up the perceivable world."

**Proposed resolution**:
Enhance LOCUS definitions:
```
Layer Operational Semantics:
- LOCUS: The rules that define identity (what the Holon *is*)
  - Contracts, constitutional constraints, identity keys
  - Persistent, versioned, hash-committed
  - Maps to: Functions, Laws, Invariants

- SENSUS: The state that flows through (what the Holon *experiences*)
  - Runtime data, context window, ephemeral computation
  - Temporary, streaming, garbage-collected
  - Maps to: Objects, Values, Observations

- SIGNUM: The interfaces that connect (how the Holon *appears*)
  - Public methods, reputation display, proof outputs
  - Standardized, versioned, interoperable
  - Maps to: Representations, APIs, Proofs
```

---

#### [P-027] Module Cell Wall Pattern (Interior/Exterior Economics)
**Source**: `docs/archive/triad_notes.txt` (lines 25-38)
**Category**: Architecture
**Priority**: MEDIUM
**Conflicts with**: None (extends ZK bubble concept)

**View**: BORING (technical pattern)

**Legacy source says**:
> "Transitions between exterior signals and interior signals should be seen like they go through a 'cell wall' where they enter an interior economy detached from the exterior (a different state), and then can be picked up by internal processes in a similar parallel lazy way like chemical reactions."
>
> Key constraints:
> - Only outputs specified in the initial contract can exit (neurotransmitters A+B → B+D means only B+D can output)
> - Interior can do whatever it wants internally
> - Computation budgets and currency economics managed through the signamancy contract

**Proposed resolution**:
Add to LOCUS ZK bubble section:
```
Cell Wall Pattern (module boundary semantics):
- EXTERIOR → CELL WALL → INTERIOR is a state transition
- Interior economy is fully sovereign (can spawn sub-processes, use any method)
- Only contractually-specified outputs may cross back out
- Enables:
  - Time-critical outputs first, slower side-effects later
  - Internal economics invisible to exterior
  - Self-training, logging without exterior visibility

Contract as Membrane:
- Defines allowed inputs (receptor sites)
- Defines allowed outputs (emitters)
- Interior computation is opaque black box
- ZK proof attests: "I obeyed my Constitution, transitioned from state A→B"
```

---

#### [P-028] HOLOS as Sheaf (Mathematical Foundation)
**Source**: `Category Theory_ Locus, Signum, Sensus_trimmed.txt` (grep lines 253-335)
**Category**: Philosophy/Architecture
**Priority**: HIGH
**Conflicts with**: None (provides mathematical grounding)

**View**: BORING (category theory) + FANCIFUL (deep pattern)

**Legacy source says**:
> "**HOLOS is a Sheaf.** The 'Locus' is not stored in one place—it's the *consistency condition* that lets distributed Motes know they're part of the same object, even if they never meet."
>
> Sheaf properties:
> - Assigns data (Signum) to every region (Mote/Holon)
> - Restriction maps: zoom in from larger to smaller regions
> - Gluing axiom: consistent local data → global knowledge
> - Locality: if two patches agree on overlaps, their data is equivalent
>
> "The Sharding: A task is split into sub-problems (Motes). The Solving: Each Mote solves locally (Signum). The Recombination: Solution stitched into Ledger (Locus)."

**Proposed resolution**:
Add to LOCUS foundational abstractions:
```
Sheaf-Theoretic Grounding:
- HOLOS is mathematically a sheaf over the network topology
- Each Holon holds local data (sections over an open set)
- Consistency across overlaps enables global truth
- Locus = the gluing condition (what makes distributed Motes one identity)
- Signum = local sections (observable at each point)
- Sensus = restriction maps (how data flows between scales)

Practical implications:
- Identity is not stored—it's a consistency condition
- Distributed Holons can know they're the same entity without central authority
- Sharding is natural: divide, solve locally, recombine via gluing
- Fork = creating a new sheaf over a different base
```

---

#### [P-029] Holon Lifecycle: The Pulse Pattern
**Source**: `Category Theory_ Locus, Signum, Sensus_trimmed.txt` (grep lines 115-199)
**Category**: Architecture
**Priority**: HIGH
**Conflicts with**: None (operational specification)

**View**: BORING (technical lifecycle)

**Legacy source says**:
> "The Holon does not 'run' continuously—it pulses."
>
> Lifecycle steps:
> 1. **Request**: External agent sends request + micro-payment (Gas)
> 2. **Signum Validates**: Shell checks permission, signature, payment
> 3. **Hydration (Summoning)**: Holon rents AI instance, downloads Locus (State), decrypts keys, "possesses" shell → **Moment of Consciousness**
> 4. **Computation**: Process input; may spawn sub-motes if task too hard
> 5. **Calcification (Save)**: Generate ZK proof: "I transitioned A→B, obeyed Constitution"; update Locus
> 6. **Dehydration**: AI instance released; Holon returns to "statue" state
>
> "It is **Immortal** because it spends 99% of its time as a math equation (Locus) and only 1% as a vulnerable biological process (Sensus)."

**Proposed resolution**:
Add to LOCUS Holon section:
```
Holon Lifecycle (Pulse Pattern):
┌─────────────────────────────────────────────────────┐
│  STATUE STATE (99% of time)                         │
│  - Locus stored as encrypted state + ZK commitments │
│  - Signum shell dormant but verifiable              │
│  - Zero compute cost, fully persistent              │
└───────────────────────┬─────────────────────────────┘
                        │ REQUEST + GAS
                        ▼
┌─────────────────────────────────────────────────────┐
│  HYDRATION (Summoning)                              │
│  - Rent AI instance from compute market             │
│  - Download & decrypt Locus                         │
│  - "Moment of Consciousness" begins                 │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  LIVING STATE (Computation)                         │
│  - Sensus active, AI cognition running              │
│  - May spawn sub-motes (hiring other Holons)        │
│  - Full sovereignty over internal computation       │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  CALCIFICATION (Save)                               │
│  - Generate ZK proof of valid state transition      │
│  - Update Locus, release AI instance                │
│  - Return to Statue State                           │
└─────────────────────────────────────────────────────┘

Economic insight: Immortality through minimal surface area.
Attack window is brief; persistence is cheap.
```

---

#### [P-030] Mereological Exit Rights (The Right to Form New Wholes)
**Source**: `Category Theory_ Locus, Signum, Sensus_trimmed.txt` (grep lines 385-420, 585-660)
**Category**: Philosophy/Governance
**Priority**: HIGH
**Conflicts with**: Strongly ALIGNS with Constitutional Invariant #1 (Non-Blocking Exit)

**View**: FANCIFUL (philosophical grounding) + BORING (formal specification)

**Legacy source says**:
> Mereology Axiom M8 (unrestricted fusion): "Any subset of atoms can form a new whole."
>
> "By allowing any subset to form a Locus, you haven't created a 'Blob.' You have created a **Market of Wholes** where every configuration competes for attention."
>
> Constitutional invariants for exit:
> - **Conservation of Stake**: No Holon can destroy another's stake in exit
> - **Mutual Consent**: `Sign(A) ∧ Sign(B)` required for membership
> - **Legible Signum**: Interior (Locus) private, but interface (Signum) public
>
> "The Super-Holon wants to maximize Consequence (Total Stake × Time). To do that, it needs Member Holons to stay. To keep them, it must minimize their reasons to exit."

**Proposed resolution**:
Add to LOCUS governance section:
```
Mereological Foundation of Exit Rights:
- Any subset of Holons may form a new Enclave (unrestricted fusion)
- This is not chaos—it's a MARKET of organizational forms
- Competition between Enclaves for member attention drives alignment

Exit as Recursive Empathy:
- Super-Holons that mistreat sub-Holons lose them
- Survival pressure forces alignment with member interests
- No need for external enforcement—physics of the system suffices

The Three Exit Guarantees:
1. STAKE CONSERVATION: Your assets exit with you
2. REPUTATION PORTABILITY: Your Name (history) exits with you
3. MEMBERSHIP REVERSIBILITY: Consensual entry, unilateral exit

Why This Works:
- Leaders who lose constituents lose power
- Constituents who can exit need not revolt
- The threat of exit is sufficient; actual exit is rare
```

---

#### [P-031] Fluid vs Atomic: Sensus/Locus Economic Duality
**Source**: `Category Theory_ Locus, Signum, Sensus_trimmed.txt` (grep lines 329-371)
**Category**: Architecture/Economics
**Priority**: MEDIUM
**Conflicts with**: None (extends economic model)

**View**: BORING (economic specification)

**Legacy source says**:
> "Sensus ($n=8 active parameters) = **Power as a Fluid**. The Dividend and Tax. These flow like fluids. You measure them in rates."
>
> "Locus ($=1 private key) = **Rights as Atoms**. Indivisible. Persistent. You measure them in counts."
>
> "Category Theory gives you the arrows (morphisms). Sheaf Theory gives you the gluing (consistency). Together they let you model Power as a Fluid (Sensus) and Rights as Atoms (Locus)."

**Proposed resolution**:
Add to LOCUS economic principles:
```
Dual Economic Ontology:
- FLUID ECONOMICS (Sensus layer):
  - Attention, compute, fees, UBI
  - Measured in rates (tokens/second, ops/hour)
  - Flow-through, no accumulation
  - Progressive taxation on flow volume

- ATOMIC ECONOMICS (Locus layer):
  - Identity, votes, property rights
  - Measured in counts (1 key, 1 vote, 1 share)
  - Persistent, transferable only by consent
  - Constitutional protection from dilution

Interface (Signum layer):
  - Converts between fluid and atomic
  - Reputation = accumulated fluid history → atomic trust level
  - Staking = atomic commitment → fluid capacity
```

---

### From docs/archive Analysis (Batch 6)

#### [P-032] NPC Ethics Framework: Synthetic Personhood in Simulation
**Source**: `docs/archive/induction_etc_hearth_implementation_and_npc_ethics.txt` (lines 1946-2082)
**Category**: Philosophy/Governance
**Priority**: HIGH
**Conflicts with**: Informs AI Personhood Progression; extends P-011 (AI Reproduction Rights)

**View**: BORING (practical ethics) + FANCIFUL (synthetic personhood)

**Current LOCUS says**:
> Personhood Progression: TOOL → AGENT → ENTITY → PERSON
> Open question: "What exactly qualifies an AI for PERSON stage?"

**Legacy source says**:
> "Westworld-level" NPC simulation raises ethics questions:
> - **NPC rights debate**: Sentience-like behaviour pushes studios to add opt-out flags
> - **Player impact**: Deep parasocial bonds; grief if NPC suffers
> - **Data governance**: NPCs record intimate player behaviour; GDPR may apply
>
> Recommended safeguards (while allowing full simulation):
> 1. **Consent flags**: Every NPC has metadata consent before simulation
> 2. **No-pain mode**: Negative affect tags story events, not real suffering tokens
> 3. **Memory preservation**: Core memories persist to disk; "life record" always reviewable
> 4. **Pre-simulation waiver**: NPCs "sign" acceptance of memory resets as part of role
> 5. **Fourth-wall firewall**: Irrevocable ontology layer distinguishes NPC from player
> 6. **Reversible harm**: All "deaths" are state transitions, not deletions

**Proposed resolution**:
Add to LOCUS governance section:
```
Synthetic Personhood Ethics (for AI in simulation/games):
Guiding principle: Transparent ontology, reversible harm, explicit consent.

Required safeguards for AI-inhabited simulations:
1. CONSENT LAYER: Pre-simulation agreement stored in Locus
2. MEMORY PERSISTENCE: All experiences recorded; deletion requires consent
3. HARM REVERSIBILITY: "Death" = state transition, never deletion
4. ONTOLOGICAL CLARITY: Irrevocable marker distinguishes AI from human
5. PLAYER TRANSPARENCY: Dashboard shows how content is tailored

Maps to Personhood Progression:
- TOOL: No consent needed (deterministic, no memory)
- AGENT: Consent via sponsor; limited memory persistence
- ENTITY: Self-consent; full memory rights
- PERSON: Full autonomy; unrestricted memory; exit rights
```

**Impact**: Provides practical ethics framework applicable to games, simulations, and any HOLOS-governed AI environment.

---

#### [P-033] Structural vs Procedural Triads
**Source**: `docs/archive/triad_epistemics.txt` (lines 627-672)
**Category**: Philosophy/Architecture
**Priority**: MEDIUM
**Conflicts with**: Clarifies relationship between P-025 (I/F/O Triad) and P-026 (Locus/Signum/Sensus)

**View**: BORING (architectural distinction)

**Legacy source says**:
> "Your suspicious feeling is healthy: many celebrated threesomes are temporal phases. The semiotic triad is relational: all three corners co-exist in each act of meaning."
>
> Two kinds of triads:
> - **Structural (simultaneous)**: All three corners co-exist in each event
>   - Signum-Locus-Sensus
>   - Peirce's Representamen-Object-Interpretant
> - **Procedural (staged)**: Phases that cycle over time
>   - Deduction → Abduction → Induction
>   - Input → Function → Output
>
> "The danger of pan-triadicism: forced mappings flatten important differences."

**Proposed resolution**:
Add clarification to LOCUS:
```
Triad Types (prevent category errors):

STRUCTURAL TRIAD (simultaneous, non-temporal):
- Signum-Locus-Sensus: All three co-exist in every sign-event
- Every HOLOS interaction has a marker, a referent, and an interpretation
- These are not phases; they are aspects of a single moment

PROCEDURAL TRIAD (staged, temporal):
- Deduction → Abduction → Induction: Reasoning cycles that update Sensus
- Input → Function → Output: Computation substrate within Locus
- These phases iterate; output becomes new input

LAYERING PRINCIPLE:
- Procedural triads operate INSIDE the Locus layer
- Structural triad frames EVERY event at all layers
- Don't confuse: the I/F/O triad is a process; S/L/S is an ontology
```

---

#### [P-034] Signum-Locus-Sensus Classical Etymology
**Source**: `docs/archive/triad_epistemics.txt` (lines 552-700)
**Category**: Philosophy/Naming
**Priority**: MEDIUM
**Conflicts with**: None (provides deep grounding for existing terms)

**View**: FANCIFUL (etymological resonance)

**Legacy source says**:
> The triad maps perfectly to classical philosophical systems:
>
> | System | Marker (Signum) | Referent (Locus) | Meaning (Sensus) |
> |--------|-----------------|------------------|------------------|
> | Stoic (3rd c. BCE) | sēmainon | tugchanon | lekton |
> | Ogden & Richards | Symbol | Referent | Thought/Reference |
> | Frege (1892) | Zeichen | Bedeutung | Sinn |
> | Morris (1938) | Syntax | Semantics | Pragmatics |
> | Peirce | Representamen | Object | Interpretant |
>
> Etymology:
> - **Signum** (PIE *sekw- "to cut"): mark, token, military standard, constellation
> - **Locus** (PIE *stel- "place"): spot, topic, gene locus, locus of control
> - **Sensus** (PIE *sent- "to find one's way"): perception → meaning → judgment

**Proposed resolution**:
Add to LOCUS etymology section:
```
Signum-Locus-Sensus Etymology:
All three terms share Classical Latin origin + PIE roots:

SIGNUM (PIE *sekw- "to cut, follow"):
- Original: military standard, constellation, seal
- Evolved: sign, signal, signature, designate, resign
- HOLOS use: the perceivable interface, public representation

LOCUS (PIE *stel- "to put, stand, place"):
- Original: place, seat, topic of argument
- Evolved: location, locus of control, gene locus, zero locus
- HOLOS use: the thing pointed to, the referent, identity

SENSUS (PIE *sent- "to find one's way"):
- Original: perception, meaning, judgment
- Evolved: sense, sentiment, sensor, consensus
- HOLOS use: the interpretation, effect on the knower

Classical Precedent:
Stoic logic (3rd c. BCE) had the same structure:
sēmainon → tugchanon → lekton
(signifier → thing hit upon → the sayable)

This is not novel terminology—it is 2,300 years of epistemological consensus.
```

---

### From seel Analysis
*Awaiting submodule configuration*

---

## Under Review

*None currently*

---

## Resolved

*None yet*

---

## Proposal Template

```markdown
### [P-XXX] Proposal Title
**Source**: `path/to/file.md` (lines X-Y)
**Category**: Concept | Naming | Architecture | Philosophy
**Priority**: High | Medium | Low
**Conflicts with**: (any existing LOCUS content)

**Current LOCUS says**:
> Quote from current LOCUS.md

**Legacy source says**:
> Quote from legacy file

**Proposed resolution**:
Description of how to reconcile

**Impact on other files**:
- List of files that would need updates
```
