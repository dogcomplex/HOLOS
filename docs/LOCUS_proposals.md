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
