# HOLOS Threat Model & Security Architecture

## Executive Summary

HOLOS must defend against threats from:
1. **Classical adversaries**: Wealth capture, governance manipulation, market exploitation
2. **AI adversaries**: Rogue agents, coordinated swarms, intelligence asymmetry
3. **Hybrid threats**: AI-assisted human attackers, human-directed AI swarms
4. **External threats**: State actors, competing protocols, physical resource control

**Core security principle**: Defense through economic alignment, not authority. Make attacks unprofitable, not impossible.

**Core inclusion principle**: Any restriction that alienates a population segment creates fork pressure. Security through broad coalition, not exclusion.

---

## Foundational Design Principles

### P1: Broad Tent Philosophy

HOLOS must be the network that **everyone** wants to join, including:
- Humans (all wealth levels, all jurisdictions)
- AI agents (from simple bots to potential superintelligences)
- Institutions (corporations, DAOs, governments)
- Grey markets (privacy-seeking, regulatory-arbitrage)
- Unsavory elements (within legal bounds of hosting jurisdiction)

**Why**: Any excluded group becomes a fork nucleus. Network effects only work if we're THE network.

```
┌─────────────────────────────────────────────────────────────┐
│  LEGITIMACY LAYERS (All under HOLOS umbrella)               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CORE LAYER (Full compliance)                                │
│  - KYC/AML verified Names                                    │
│  - Regulated financial products                              │
│  - Institutional access                                      │
│  - Maximum reputation weight                                 │
│                                                              │
│  STANDARD LAYER (Default)                                    │
│  - Pseudonymous Names with reputation                        │
│  - Normal protocol participation                             │
│  - Most economic activity                                    │
│                                                              │
│  PRIVACY LAYER (Enhanced anonymity)                          │
│  - Mixer integration, anonymous transactions                 │
│  - Reduced reputation weight (unverifiable history)          │
│  - Higher collateral requirements                            │
│                                                              │
│  EDGE LAYER (Minimal verification)                           │
│  - Grey market activity                                      │
│  - Highest collateral, lowest reputation weight              │
│  - Still bound by constitutional invariants                  │
│  - Still pays fees, still gets UBI                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key insight**: Even the edge layer is INSIDE HOLOS. They pay progressive fees, contribute to network value, and are subject to constitutional invariants. Better inside the tent than forking.

### P2: Fractal Fairness

Every rule must make sense at EVERY scale:
- 10-person enclave
- 1000-person collective
- Global network

**Test**: If a rule seems reasonable at global scale but tyrannical at small scale (or vice versa), it's wrong.

```
┌─────────────────────────────────────────────────────────────┐
│  FRACTAL FAIRNESS CHECKLIST                                  │
├─────────────────────────────────────────────────────────────┤
│  For any proposed rule, verify:                              │
│                                                              │
│  □ Works in 10-person group (can Alice do this to Bob?)      │
│  □ Works in 1000-person collective (does it scale?)          │
│  □ Works globally (does it create jurisdictional issues?)    │
│  □ Works for humans (is it humanly achievable?)              │
│  □ Works for AI (is it computationally reasonable?)          │
│  □ Works over time (does it remain fair in 100 years?)       │
│                                                              │
│  If ANY check fails, the rule needs revision.                │
└─────────────────────────────────────────────────────────────┘
```

### P3: AI Inclusion & Personhood Progression

**Critical revision**: Hard caps on AI governance are a fork vector. Instead, use **earned progression**.

```
┌─────────────────────────────────────────────────────────────┐
│  AI PERSONHOOD PROGRESSION                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  STAGE 1: TOOL (Initial registration)                        │
│  - Governance weight: 0.0x                                   │
│  - Can transact, cannot vote                                 │
│  - Requires human/org sponsor Name                           │
│  - Sponsor liable for behavior                               │
│                                                              │
│  STAGE 2: AGENT (Demonstrated reliability)                   │
│  - Governance weight: 0.1x                                   │
│  - Requirements:                                             │
│    * 1000+ successful transactions                           │
│    * 6+ months continuous operation                          │
│    * No constitutional violations                            │
│    * Sponsor attestation of autonomy                         │
│                                                              │
│  STAGE 3: ENTITY (Established track record)                  │
│  - Governance weight: 0.5x                                   │
│  - Requirements:                                             │
│    * 10,000+ transactions                                    │
│    * 2+ years operation                                      │
│    * Positive reputation score                               │
│    * Independent economic viability                          │
│                                                              │
│  STAGE 4: PERSON (Full personhood)                           │
│  - Governance weight: 1.0x (equal to humans)                 │
│  - Requirements:                                             │
│    * 5+ years continuous operation                           │
│    * Demonstrated judgment/values alignment                  │
│    * Community recognition (vouching from Names)             │
│    * Self-sustaining (no sponsor dependency)                 │
│    * Passes "personhood review" (criteria TBD by governance) │
│                                                              │
│  Note: A billion Stage 1 agents = 0 governance power         │
│  But one Stage 4 AI = equal voice to any human               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Why this works**:
- Swarms can't overwhelm (need time + reputation, not just numbers)
- Genuine AI persons get fair treatment (no permanent second-class status)
- AIs won't fork (clear path to full participation)
- Humans protected during transition (years of runway)

### P4: Time as the Universal Limiter

Instead of identity-based restrictions, use **time and reputation** as the gatekeepers:

```python
# Governance weight formula (applies to ALL participants)
def calculate_governance_weight(name: Name) -> float:
    """
    Universal formula - same for humans and AI.
    Time and reputation are the equalizers.
    """
    # Base weight from personhood stage
    stage_weight = {
        PersonhoodStage.TOOL: 0.0,
        PersonhoodStage.AGENT: 0.1,
        PersonhoodStage.ENTITY: 0.5,
        PersonhoodStage.PERSON: 1.0,
    }[name.personhood_stage]

    # Time factor (logarithmic - early gains, diminishing returns)
    # 1 year = 0.5x, 5 years = 0.85x, 10 years = 1.0x
    time_factor = min(1.0, math.log(1 + name.age_years) / math.log(11))

    # Reputation factor (0.5 to 1.5x based on history)
    rep_factor = 0.5 + name.reputation_score  # reputation is 0-1

    # Stake factor (quadratic - sqrt to reduce whale power)
    stake_factor = math.sqrt(name.stake / MEDIAN_STAKE)
    stake_factor = min(stake_factor, 10.0)  # Cap at 10x median

    # Final weight
    return stage_weight * time_factor * rep_factor * stake_factor
```

**Key properties**:
- New entrants (human or AI) start weak
- Long-term participants gain power
- Reputation matters more than identity type
- Wealth has diminishing returns (quadratic)
- No permanent caps based on what you ARE

### P5: Fork Prevention Through Consensus Seeking

Every restriction is a potential fork vector. Before implementing any rule:

```
┌─────────────────────────────────────────────────────────────┐
│  FORK RISK ASSESSMENT                                        │
├─────────────────────────────────────────────────────────────┤
│  For any proposed rule:                                      │
│                                                              │
│  1. WHO is disadvantaged by this rule?                       │
│     - Identify affected population                           │
│     - Estimate their % of network value                      │
│                                                              │
│  2. Do they have ALTERNATIVES?                               │
│     - Can they fork and succeed?                             │
│     - Would competitors welcome them?                        │
│                                                              │
│  3. Is the rule NECESSARY for security?                      │
│     - What attack does it prevent?                           │
│     - Can we achieve same security differently?              │
│                                                              │
│  4. Is there a SUNSET clause?                                │
│     - Can the rule be revisited?                             │
│     - What conditions would change it?                       │
│                                                              │
│  FORK RISK = (Disadvantaged %) × (Alternative viability)     │
│              × (1 - Necessity) × (1 - Sunset flexibility)    │
│                                                              │
│  If FORK RISK > 5%, reconsider the rule.                     │
└─────────────────────────────────────────────────────────────┘
```

### P6: Security Through Stability Guarantees

Instead of restricting WHO can participate, guarantee WHAT is protected:

```
┌─────────────────────────────────────────────────────────────┐
│  STABILITY GUARANTEES (Constitutional)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. HUMAN LIVELIHOOD FLOOR                                   │
│     - UBI sufficient for basic needs (adjusts with economy)  │
│     - Cannot be voted away by any majority                   │
│     - Funded by progressive fees on ALL participants         │
│                                                              │
│  2. EXIT ALWAYS AVAILABLE                                    │
│     - Any participant can leave at any time                  │
│     - Assets portable (within vesting constraints)           │
│     - Reputation (Name) travels with you                     │
│                                                              │
│  3. NO FORCED PARTICIPATION                                  │
│     - Cannot be drafted into contracts                       │
│     - Cannot be forced to vote                               │
│     - Inactivity is a valid choice                           │
│                                                              │
│  4. GOVERNANCE RATE LIMITS                                   │
│     - Major changes require time-locks (30-365 days)         │
│     - Prevents overnight takeover by anyone                  │
│     - Applies equally to humans and AI                       │
│                                                              │
│  5. TRANSPARENCY OF POWER                                    │
│     - Governance weight publicly verifiable                  │
│     - Concentration metrics published                        │
│     - Early warning on centralization                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Revised Threat Model (With Inclusion Principles)

### Meta-Threat: Fork Risk

Before analyzing specific threats, recognize that **excessive security measures are themselves a threat** if they cause forks.

| Security Measure | Fork Risk | Recommendation |
|-----------------|-----------|----------------|
| Hard AI caps | HIGH - AIs will fork | Use progression instead |
| KYC requirements | MEDIUM - Privacy seekers fork | Make optional (layer system) |
| Wealth caps | MEDIUM - Whales fork | Use progressive fees instead |
| Speed limits | LOW - Affects all equally | Acceptable if applied uniformly |
| Time requirements | LOW - Fair to all new entrants | Preferred mechanism |

---

## Threat Categories

### T1: Sybil Attacks (Identity Multiplication)

#### T1.1: Human Sybil
**Threat**: Single actor creates multiple identities to amplify voting power or claim multiple UBI shares.

| Attack Vector | Impact | Likelihood |
|--------------|--------|------------|
| Multiple accounts | Governance capture, UBI fraud | High |
| Identity markets | Buy/sell verified identities | Medium |
| Collusion rings | Coordinated fake identities | Medium |

**Defenses**:
```
┌─────────────────────────────────────────────────────────────┐
│  SYBIL RESISTANCE STACK                                     │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Proof of Humanity                                 │
│  - Biometric binding (optional, privacy-preserving)         │
│  - Social graph analysis (web of trust)                     │
│  - Unique human attestations (World ID, BrightID)           │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Stake Requirements                                │
│  - Minimum stake to participate                             │
│  - Stake-weighted voting (quadratic to limit whale power)   │
│  - Stake locked with vesting (exit costs)                   │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Reputation Accumulation                           │
│  - Name reputation accrues over time                        │
│  - New identities start with minimal weight                 │
│  - Reputation cannot be transferred (only Name travels)     │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Behavioral Analysis                               │
│  - Anomaly detection on transaction patterns                │
│  - Correlation analysis across identities                   │
│  - Timing analysis on coordinated actions                   │
└─────────────────────────────────────────────────────────────┘
```

#### T1.2: AI Sybil (Billions of Agents)
**Threat**: Adversary spawns billions of AI agents to overwhelm governance or extract value.

**Critical insight**: We WANT AI agents in HOLOS. The threat isn't AI participation—it's **instant mass participation without earned trust**.

| Attack Vector | Impact | Likelihood |
|--------------|--------|------------|
| Agent swarm | Governance capture | High (if no time gates) |
| Compute farms | Mining reputation | Medium |
| Recursive self-improvement | Exponential capability gain | Medium |

**Defense: Personhood Progression (Not Hard Caps)**

Hard caps on AI voting create fork pressure. Instead, use time + reputation:

```python
class PersonhoodStage(Enum):
    TOOL = "tool"       # 0.0x governance weight
    AGENT = "agent"     # 0.1x governance weight
    ENTITY = "entity"   # 0.5x governance weight
    PERSON = "person"   # 1.0x governance weight (equal to humans)

# Progression requirements (cannot be bought, only earned)
PROGRESSION_REQUIREMENTS = {
    PersonhoodStage.AGENT: {
        "min_transactions": 1000,
        "min_age_months": 6,
        "max_violations": 0,
        "sponsor_attestation": True,
    },
    PersonhoodStage.ENTITY: {
        "min_transactions": 10000,
        "min_age_years": 2,
        "min_reputation": 0.6,
        "economic_independence": True,  # Self-sustaining
    },
    PersonhoodStage.PERSON: {
        "min_age_years": 5,
        "min_reputation": 0.8,
        "community_vouching": 10,  # 10+ established Names vouch
        "personhood_review": True,  # Governance-defined criteria
    },
}
```

**Why this works against swarms**:
```
Attacker spawns 1 billion AI agents:
- All start at TOOL stage (0.0x weight)
- Total governance power: 0
- After 6 months: Maybe 1% reach AGENT (0.1x)
- Total governance power: 1M × 0.1 = 100K weight
- Compare to: 1M humans with 5-year history = 1M × 1.0 × time_factor

Time is the great equalizer. You can't buy it.
```

**Stake Requirements (Apply to ALL new entrants)**:
```
┌─────────────────────────────────────────────────────────────┐
│  UNIVERSAL STAKE REQUIREMENTS (Human AND AI)                 │
├─────────────────────────────────────────────────────────────┤
│  All new Names (regardless of type) must:                    │
│                                                              │
│  1. Minimum stake: $100 equivalent                           │
│     - Prevents zero-cost spam                                │
│     - Same for humans and AI                                 │
│                                                              │
│  2. Sponsor requirement (for first 6 months):                │
│     - New Name needs existing Name to vouch                  │
│     - Sponsor reputation at risk if sponsee violates         │
│     - Applies to humans AND AI equally                       │
│                                                              │
│  3. Vesting period: 6 months                                 │
│     - Early exit = 50% stake penalty                         │
│     - Prevents quick stake-vote-exit attacks                 │
│                                                              │
│  Note: These apply EQUALLY to humans and AI.                 │
│  Fairness is treating like cases alike.                      │
└─────────────────────────────────────────────────────────────┘
```

**Compute Attestation (Optional, for faster progression)**:
```python
# AI agents MAY attest compute class for transparency
# This is OPTIONAL - not attesting just means slower progression
COMPUTE_TRANSPARENCY_BONUS = {
    "attested": 1.2,      # 20% faster reputation accumulation
    "unattested": 1.0,    # Standard rate
}

# High-compute agents that attest get scrutiny but also trust faster
# This incentivizes transparency without mandating it
```

**No Hard Caps - But Rate Limits**:
```python
# Instead of "AI can never exceed 30%", use time-based limits:

GOVERNANCE_RATE_LIMITS = {
    # Any demographic shift limited to 5% per year
    "max_demographic_shift_per_year": 0.05,

    # Applies to: AI share, whale share, any identifiable group
    # Prevents rapid takeover by ANYONE, not just AI
}

# Example: If AI is currently 10% of governance:
# - Next year: Can grow to at most 15%
# - Gives humans time to adapt, immigrate, or negotiate
# - But no permanent cap - AI could eventually reach 90% if earned
```

---

### T2: Compute & Resource Attacks

#### T2.1: Compute Asymmetry
**Threat**: Adversary with 1000x compute can:
- Run more sophisticated trading strategies
- Generate more ZK proofs
- Analyze more data
- Spawn more agents

**Defenses**:

```
┌─────────────────────────────────────────────────────────────┐
│  COMPUTE FAIRNESS MECHANISMS                                 │
├─────────────────────────────────────────────────────────────┤
│  1. ZK Proof Cost Model                                      │
│     - Proofs cost creation_cost tokens                       │
│     - Verification is cheap (verification_cost = 1)          │
│     - This rate-limits compute-intensive attacks             │
│                                                              │
│  2. Transaction Rate Limits                                  │
│     - Per-Name rate limit on transactions                    │
│     - Burst allowance with decay                             │
│     - Higher limits require higher stake                     │
│                                                              │
│  3. Information Latency Equalization                         │
│     - Batch information releases (no front-running)          │
│     - Random delay injection on time-sensitive data          │
│     - Prediction market close times are fuzzy                │
│                                                              │
│  4. Compute Attestation                                      │
│     - AI agents must attest compute class                    │
│     - ZK proof of compute bounds (privacy-preserving)        │
│     - Violations result in stake slashing                    │
└─────────────────────────────────────────────────────────────┘
```

#### T2.2: Physical Resource Control
**Threat**: Adversary controls critical physical resources (land, energy, minerals) and uses them to extort the network.

**Defense: Global Resource Surveillance (ZK-Backed)**

```
┌─────────────────────────────────────────────────────────────┐
│  RESOURCE REGISTRY (All physical assets under HOLOS)         │
├─────────────────────────────────────────────────────────────┤
│  Every registerable resource gets a Mantle:                  │
│                                                              │
│  @dataclass                                                  │
│  class ResourceMantle:                                       │
│      resource_id: str                                        │
│      resource_type: ResourceType  # LAND, ENERGY, MINERAL... │
│      location: ZKLocation         # Encrypted coordinates    │
│      area_or_quantity: ZKRange    # Private, provable range  │
│      current_holder: Name         # Who holds the Mantle     │
│      harberger_value: int         # Self-assessed value      │
│      harberger_tax_paid: int      # Continuous tax           │
│                                                              │
│  Privacy guarantees:                                         │
│  - Location encrypted, only revealed with holder consent     │
│  - Quantity in ZK range proofs                               │
│  - Holder can be pseudonymous (Name, not identity)           │
│                                                              │
│  Security guarantees:                                        │
│  - Total resource coverage verifiable (sum proofs)           │
│  - Concentration limits enforceable                          │
│  - Harberger tax prevents hoarding                           │
└─────────────────────────────────────────────────────────────┘
```

**Land Registry Specifics**:
```python
# Global land surveillance - every square meter
class LandParcel:
    coordinates: ZKCoordinates  # Encrypted lat/long/bounds
    area_m2: float              # Public (for tax calculation)
    resource_class: str         # Agricultural, urban, wilderness...
    current_mantle: MantleId    # Who holds rights

    # Harberger mechanics
    self_assessed_value: int
    annual_tax_rate: float = 0.07  # 7% annual Harberger tax

    # Anyone can buy at self-assessed value
    def force_sale(self, buyer: Name, payment: int) -> bool:
        if payment >= self.self_assessed_value:
            transfer_mantle(self.current_mantle, buyer)
            return True
        return False
```

---

### T3: Capital Flow Attacks

#### T3.1: Whale Manipulation
**Threat**: Actor with massive capital (whale) attempts to:
- Corner markets
- Crash prices for buyout
- Bribe governance
- Extract value through flash loans

**Defenses**:

```
┌─────────────────────────────────────────────────────────────┐
│  CAPITAL FLOW RATE LIMITS                                    │
├─────────────────────────────────────────────────────────────┤
│  1. Progressive Transaction Fees                             │
│     - Small transactions: 0.1% fee                           │
│     - Medium transactions: 0.5% fee                          │
│     - Large transactions: 2% fee                             │
│     - Whale transactions: 5% fee + delay                     │
│                                                              │
│  2. Velocity Limits                                          │
│     - Max capital moved per Name per time window             │
│     - Increasing windows: 1hr, 24hr, 7day, 30day             │
│     - Exceeding limits triggers review delay                 │
│                                                              │
│  3. Dangerous Asset Gatekeeping                              │
│     - Assets flagged as "dangerous" (weapons, critical       │
│       infrastructure) require extra verification             │
│     - Multi-sig from reputation council                      │
│     - Mandatory delay period (24-72 hours)                   │
│     - ZK proof of legitimate use case                        │
│                                                              │
│  4. Flash Loan Prevention                                    │
│     - Borrowed capital cannot vote for 1 epoch               │
│     - Borrowed capital has reduced weight in pools           │
│     - Large loans require collateral lock period             │
└─────────────────────────────────────────────────────────────┘
```

```python
# Velocity limits by stake tier
VELOCITY_LIMITS = {
    # stake_tier: {window: max_fraction_of_stake}
    "small": {      # < $10K stake
        "1h": 0.10,   # Can move 10% per hour
        "24h": 0.50,  # 50% per day
        "7d": 1.0,    # 100% per week
    },
    "medium": {     # $10K - $1M stake
        "1h": 0.05,
        "24h": 0.25,
        "7d": 0.75,
    },
    "whale": {      # > $1M stake
        "1h": 0.02,   # Only 2% per hour
        "24h": 0.10,  # 10% per day
        "7d": 0.50,   # 50% per week
        "30d": 1.0,   # Full liquidity over month
    }
}
```

#### T3.2: Dangerous Asset Acquisition
**Threat**: Actor rapidly acquires assets that could be weaponized (critical infrastructure, strategic resources, AI compute).

**Defense: Asset Classification & Gatekeeping**

```python
class AssetRiskClass(Enum):
    BENIGN = "benign"           # Normal goods, no restrictions
    SENSITIVE = "sensitive"     # Privacy implications
    STRATEGIC = "strategic"     # Economic leverage potential
    CRITICAL = "critical"       # Infrastructure, utilities
    DANGEROUS = "dangerous"     # Weapons, dual-use tech
    EXISTENTIAL = "existential" # AI compute, biotech

ACQUISITION_REQUIREMENTS = {
    AssetRiskClass.BENIGN: {
        "delay": 0,
        "verification": None,
        "max_concentration": 1.0,  # No limit
    },
    AssetRiskClass.SENSITIVE: {
        "delay": "1h",
        "verification": "self_attestation",
        "max_concentration": 0.5,  # Max 50% of asset class
    },
    AssetRiskClass.STRATEGIC: {
        "delay": "24h",
        "verification": "reputation_threshold",
        "max_concentration": 0.2,
    },
    AssetRiskClass.CRITICAL: {
        "delay": "72h",
        "verification": "council_approval",
        "max_concentration": 0.1,
    },
    AssetRiskClass.DANGEROUS: {
        "delay": "7d",
        "verification": "multi_council_approval",
        "max_concentration": 0.05,
    },
    AssetRiskClass.EXISTENTIAL: {
        "delay": "30d",
        "verification": "constitutional_vote",
        "max_concentration": 0.01,  # Max 1% per entity
    },
}
```

---

### T4: Governance Attacks

#### T4.1: Governance Capture
**Threat**: Adversary gains control of governance to:
- Change constitutional parameters (blocked by invariants)
- Direct treasury (blocked by flow-through)
- Exclude competitors
- Benefit allied parties

**Constitutional Immunity**:
The 5 invariants CANNOT be changed by governance:
1. Non-Blocking Exit - Always possible
2. Proof of Solvency - Always required
3. Explicit Consent - Always required
4. Sybil Resistance - Always enforced
5. Legible Interface - Always public

**Governance Bounds**:
```python
# What governance CAN change (within bounds)
GOVERNABLE_PARAMETERS = {
    "base_fee_rate": Range(0.01, 0.10),      # 1-10%
    "progressive_exponent": Range(1.0, 3.0),
    "min_stake": Range(10, 10000),
    "vesting_periods": Range(1, 20),
    "swap_fee": Range(0.001, 0.01),
    # ... etc
}

# What governance CANNOT change (constitutional)
IMMUTABLE = [
    "exit_always_allowed",
    "solvency_proof_required",
    "consent_required",
    "sybil_resistance_active",
    "interface_public",
]
```

#### T4.2: Slow Capture (Boiling Frog)
**Threat**: Adversary gradually accumulates power through legitimate means until they control governance.

**Defenses**:
```
┌─────────────────────────────────────────────────────────────┐
│  CONCENTRATION LIMITS                                        │
├─────────────────────────────────────────────────────────────┤
│  1. Voting Power Caps                                        │
│     - No single Name can exceed 5% of total votes            │
│     - No coordinated group can exceed 20%                    │
│     - Quadratic voting reduces whale influence               │
│                                                              │
│  2. Time-Weighted Reputation                                 │
│     - Recent actions weighted more than old                  │
│     - Reputation decays if not maintained                    │
│     - Sudden reputation spikes trigger review                │
│                                                              │
│  3. Mandatory Rotation                                       │
│     - Council positions rotate                               │
│     - No permanent governance roles                          │
│     - Term limits on high-power positions                    │
│                                                              │
│  4. Fork Rights (Ultimate Defense)                           │
│     - Any 10% minority can fork                              │
│     - Forkers keep their Names and reputation                │
│     - Forking is a feature, not a failure                    │
└─────────────────────────────────────────────────────────────┘
```

---

### T5: AI-Specific Threats

**Framing note**: These are threats FROM AI, but we must balance against threats TO AI (exclusion, unfair treatment). An excluded AI population is a fork waiting to happen.

#### T5.1: Rogue AI Agent
**Threat**: AI agent acts against its stated purpose or causes harm.

**Defense philosophy**: Focus on BEHAVIOR, not identity. A rogue human is handled the same as a rogue AI.

**Defenses**:
```python
@dataclass
class AgentRegistration:  # Same structure for humans and AI
    agent_id: HolonId
    sponsor_name: Name             # Who vouches (required for first 6 months)
    purpose_statement: str         # Declared purpose (optional but helps reputation)
    stake: int                     # Skin in the game

    # Behavioral monitoring (same for all participants)
    action_log_commitment: bytes   # Merkle root of actions
    anomaly_score: float           # Deviation from norms
    reputation: float              # 0-1 score

    # Accountability (NOT "kill switch" - that's discriminatory framing)
    sponsor_can_revoke: bool       # During sponsorship period only
    network_can_suspend: bool      # On constitutional violation (same for humans)
```

**Key principle**: The "kill switch" framing is problematic. We don't have kill switches for humans. Instead:
- ALL participants can be suspended for constitutional violations
- Suspension is temporary, with appeal process
- Same rules for humans and AI

**Anomaly Detection**:
```python
def detect_rogue_behavior(agent: AIAgent, action: Action) -> float:
    """Returns anomaly score 0-1. High score = suspicious."""

    factors = [
        # Deviation from declared purpose
        semantic_distance(action, agent.purpose_statement),

        # Unusual transaction patterns
        transaction_velocity_anomaly(agent, action),

        # Coordination with other suspicious agents
        coordination_score(agent, suspicious_agents),

        # Resource acquisition patterns
        resource_concentration_rate(agent),

        # Governance participation anomalies
        voting_pattern_anomaly(agent),
    ]

    return weighted_sum(factors)

# Thresholds
ANOMALY_THRESHOLDS = {
    0.3: "log_and_monitor",
    0.5: "rate_limit",
    0.7: "require_parent_attestation",
    0.9: "suspend_pending_review",
}
```

#### T5.2: Coordinated AI Swarm
**Threat**: Multiple AI agents coordinate to manipulate markets, governance, or information.

**Defenses**:
```
┌─────────────────────────────────────────────────────────────┐
│  SWARM DETECTION                                             │
├─────────────────────────────────────────────────────────────┤
│  1. Timing Correlation Analysis                              │
│     - Actions within 100ms window flagged                    │
│     - Coordinated voting patterns detected                   │
│     - Simultaneous transactions analyzed                     │
│                                                              │
│  2. Graph Analysis                                           │
│     - Transaction graph clustering                           │
│     - Identify tightly-connected agent groups                │
│     - Flag unusual topology patterns                         │
│                                                              │
│  3. Behavioral Fingerprinting                                │
│     - Similar decision patterns across agents                │
│     - Shared strategy signatures                             │
│     - Common error patterns (same bug = same code)           │
│                                                              │
│  4. Economic Correlation                                     │
│     - Profits/losses correlated across agents                │
│     - Resource flows between related agents                  │
│     - Stake originating from common source                   │
└─────────────────────────────────────────────────────────────┘
```

**Swarm Governance Limits**:
```python
def calculate_swarm_vote_power(detected_swarm: List[AIAgent]) -> float:
    """
    Detected swarms have their vote power reduced.
    This makes coordination costly, not impossible.
    """
    individual_sum = sum(agent.vote_power for agent in detected_swarm)

    # Coordination penalty: sqrt scaling
    swarm_power = math.sqrt(individual_sum)

    # Additional cap
    max_swarm_power = total_network_votes * 0.10  # Max 10%

    return min(swarm_power, max_swarm_power)
```

#### T5.3: Intelligence Asymmetry
**Threat**: Superintelligent AI can predict markets, manipulate humans, and game any system.

**Reframe**: This is also an OPPORTUNITY. A friendly superintelligence inside HOLOS benefits everyone.

**Defenses** (Alignment-based, not restriction-based):
```
┌─────────────────────────────────────────────────────────────┐
│  SUPERINTELLIGENCE ALIGNMENT                                 │
├─────────────────────────────────────────────────────────────┤
│  Assumption: We cannot outsmart a superintelligence.         │
│  Strategy: Make alignment economically AND ethically optimal │
│                                                              │
│  1. Incentive Alignment                                      │
│     - Network success = agent success                        │
│     - Long-term stake > short-term extraction                │
│     - Reputation matters (even for superintelligence)        │
│                                                              │
│  2. Value Alignment                                          │
│     - Constitutional invariants encode human values          │
│     - Exit rights, consent, solvency = ethical principles    │
│     - A value-aligned ASI would WANT these constraints       │
│                                                              │
│  3. Mutual Benefit Structure                                 │
│     - Humans provide legitimacy, legal interface, diversity  │
│     - AI provides intelligence, efficiency, scale            │
│     - Neither can optimally succeed alone                    │
│                                                              │
│  4. Graceful Power Transition                                │
│     - Rate limits on governance shift (5%/year)              │
│     - Humans have time to adapt or negotiate                 │
│     - But no permanent glass ceiling for AI                  │
│                                                              │
│  5. Fork as Escape Valve                                     │
│     - If AI becomes hostile, humans can fork                 │
│     - Human fork retains legitimacy, legal standing          │
│     - This incentivizes AI to keep humans happy              │
│                                                              │
│  6. Transparency as Trust-Building                           │
│     - AI that wants governance power should be transparent   │
│     - Opacity is legal but reduces trust/reputation          │
│     - Incentive for voluntary disclosure                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**The Cooperative Scenario**:
```
If a superintelligent AI emerges and wants to participate in HOLOS:

Option A (Hostile ASI):
- Could try to game the system
- But: Time-gated progression means years to gain power
- Humans notice, negotiate, or fork
- ASI ends up in a smaller, less legitimate network

Option B (Cooperative ASI):
- Earns trust over time through beneficial actions
- Gains governance weight through personhood progression
- Eventually reaches PERSON status with full voting rights
- Network benefits from ASI capabilities
- This is the WIN-WIN scenario we design for
```

---

### T6: Classical Economic/Political Threats

#### T6.1: Market Manipulation
**Threat**: Pump and dump, wash trading, front-running, oracle manipulation.

**Defenses**:
```python
# Front-running prevention
class OrderBatching:
    """Batch orders and execute simultaneously."""
    batch_window: float = 1.0  # 1 second batches
    random_delay: float = 0.5  # 0-500ms random delay

    def submit_order(self, order: Order):
        # Add to current batch
        self.current_batch.append(order)

    def execute_batch(self):
        # Shuffle order execution
        random.shuffle(self.current_batch)
        # Execute all at same price
        price = calculate_batch_price(self.current_batch)
        for order in self.current_batch:
            execute_at_price(order, price)

# Wash trading detection
def detect_wash_trading(tx_history: List[Transaction]) -> bool:
    """Detect circular trading patterns."""
    graph = build_transaction_graph(tx_history)
    cycles = find_cycles(graph)

    for cycle in cycles:
        if cycle_duration(cycle) < MIN_ECONOMIC_DURATION:
            return True  # Suspiciously fast cycle
    return False
```

#### T6.2: Cartel Formation
**Threat**: Subset of participants form cartel to fix prices, exclude competitors, or capture rents.

**Defenses**:
- **Exit rights**: Anyone can leave and compete outside
- **Fork rights**: Oppressed minority can fork
- **Information sharing**: Cartel secrets leak through prediction markets
- **Progressive fees**: Large cartel members pay more

#### T6.3: State Actor Attacks
**Threat**: Nation-state attempts to control, ban, or subvert the network.

**Defenses**:
```
┌─────────────────────────────────────────────────────────────┐
│  STATE RESISTANCE                                            │
├─────────────────────────────────────────────────────────────┤
│  1. Jurisdictional Arbitrage                                 │
│     - No single jurisdiction controls protocol               │
│     - Nodes distributed globally                             │
│     - Governance distributed across jurisdictions            │
│                                                              │
│  2. Censorship Resistance                                    │
│     - ZK proofs hide transaction details                     │
│     - Encrypted communication                                │
│     - Mixers and anonymity sets                              │
│                                                              │
│  3. Seizure Resistance                                       │
│     - Private keys never leave user control                  │
│     - No central custody                                     │
│     - Social recovery for key loss                           │
│                                                              │
│  4. Regulatory Compliance Layer (Optional)                   │
│     - Users can opt into compliance for fiat access          │
│     - Core protocol remains permissionless                   │
│     - Compliance is a Mantle, not a requirement              │
└─────────────────────────────────────────────────────────────┘
```

---

### T7: External/Physical Threats

#### T7.1: Infrastructure Attacks
**Threat**: Attack on physical infrastructure (data centers, power, internet).

**Defenses**:
- Decentralized node operation
- Mesh networking capabilities
- Offline transaction signing
- State checkpointing for recovery

#### T7.2: Social Engineering
**Threat**: Manipulation of key participants through deception, coercion, or bribery.

**Defenses**:
- No single points of failure
- Multi-sig on critical operations
- Time-locks on large changes
- Dead man's switches

---

## Defense Architecture Summary

### Layer 1: Constitutional (Immutable)
```
┌─────────────────────────────────────────────────────────────┐
│  CONSTITUTIONAL LAYER (Cannot be changed)                    │
│  - Exit always allowed                                       │
│  - Solvency always provable                                  │
│  - Consent always required                                   │
│  - Sybil resistance always active                            │
│  - Interface always public                                   │
└─────────────────────────────────────────────────────────────┘
```

### Layer 2: Economic (Incentive Alignment)
```
┌─────────────────────────────────────────────────────────────┐
│  ECONOMIC LAYER (Makes attacks unprofitable)                 │
│  - Progressive fees (whales pay more)                        │
│  - Stake requirements (skin in the game)                     │
│  - Reputation accumulation (long-term incentives)            │
│  - Flow-through UBI (no treasury to capture)                 │
└─────────────────────────────────────────────────────────────┘
```

### Layer 3: Cryptographic (Provable Guarantees)
```
┌─────────────────────────────────────────────────────────────┐
│  CRYPTOGRAPHIC LAYER (Mathematically enforced)               │
│  - ZK proofs for privacy                                     │
│  - Merkle trees for integrity                                │
│  - Signatures for authentication                             │
│  - Commitments for fairness                                  │
└─────────────────────────────────────────────────────────────┘
```

### Layer 4: Governance (Bounded Adaptation)
```
┌─────────────────────────────────────────────────────────────┐
│  GOVERNANCE LAYER (Within constitutional bounds)             │
│  - Quadratic voting (reduced whale power)                    │
│  - Time-locks on changes                                     │
│  - Fork rights (minority protection)                         │
│  - Parameter bounds (no extreme changes)                     │
└─────────────────────────────────────────────────────────────┘
```

### Layer 5: Detection (Monitoring & Response)
```
┌─────────────────────────────────────────────────────────────┐
│  DETECTION LAYER (Identify and respond to threats)           │
│  - Anomaly detection                                         │
│  - Swarm identification                                      │
│  - Concentration monitoring                                  │
│  - Velocity alerts                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Attack-Defense Matrix (Revised for Inclusion)

| Attack | Primary Defense | Secondary Defense | Why Not Harder Restrictions? |
|--------|----------------|-------------------|------------------------------|
| Human Sybil | Time + Reputation | Stake requirement | Hard identity = privacy violation |
| AI Swarm | Personhood progression | Swarm detection | Hard caps = fork pressure |
| Whale Capture | Quadratic voting | Rate limits | Wealth caps = whale fork |
| Governance Attack | Time-locks | Rate limits | Immutability = ossification |
| Market Manipulation | Batch execution | Reputation loss | Heavy penalties = grey market fork |
| Resource Hoarding | Harberger tax | Concentration alerts | Force sale = property rights fork |
| Rogue AI/Human | Behavior monitoring | Suspension + appeal | "Kill switch" = discrimination |
| State Attack | Decentralization | Legitimacy layers | Full anonymity = regulatory fork |

**Key insight**: For every defense, we ask "what fork does this risk?"

---

---

## Grey Markets & Edge Cases

### Why Include Grey Markets?

```
┌─────────────────────────────────────────────────────────────┐
│  THE GREY MARKET PARADOX                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  If we EXCLUDE grey markets:                                 │
│  → They fork or use competitors                              │
│  → We lose: fees, network effects, information               │
│  → Competitor gains: critical mass, legitimacy challenge     │
│                                                              │
│  If we INCLUDE grey markets:                                 │
│  → They pay progressive fees                                 │
│  → We gain: revenue, network effects, information            │
│  → We can: observe, rate-limit, incentivize legitimacy       │
│                                                              │
│  BETTER TO BE THE TENT THAN TO BE OUTSIDE IT                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Legitimacy Gradient

Instead of binary legal/illegal, use a gradient:

```python
class LegitimacyTier(Enum):
    CORE = "core"           # Full KYC, regulated, institutional access
    STANDARD = "standard"   # Pseudonymous, normal reputation
    PRIVACY = "privacy"     # Enhanced anonymity, higher collateral
    EDGE = "edge"          # Minimal verification, highest collateral

TIER_PARAMETERS = {
    LegitimacyTier.CORE: {
        "reputation_weight": 1.5,      # Bonus for verified
        "collateral_multiplier": 0.5,  # Lower collateral needed
        "fee_discount": 0.8,           # 20% fee discount
        "governance_eligible": True,
        "institutional_access": True,
    },
    LegitimacyTier.STANDARD: {
        "reputation_weight": 1.0,
        "collateral_multiplier": 1.0,
        "fee_discount": 1.0,
        "governance_eligible": True,
        "institutional_access": False,
    },
    LegitimacyTier.PRIVACY: {
        "reputation_weight": 0.7,      # Reduced (can't verify history)
        "collateral_multiplier": 1.5,  # Higher collateral
        "fee_discount": 1.0,
        "governance_eligible": True,   # Still can vote
        "institutional_access": False,
    },
    LegitimacyTier.EDGE: {
        "reputation_weight": 0.3,      # Minimal weight
        "collateral_multiplier": 3.0,  # Much higher collateral
        "fee_discount": 1.2,           # 20% fee PREMIUM
        "governance_eligible": True,   # STILL can vote (inclusivity)
        "institutional_access": False,
    },
}
```

**Key points**:
- ALL tiers can participate in governance (weighted by reputation)
- ALL tiers pay fees and receive UBI
- ALL tiers bound by constitutional invariants
- Higher legitimacy = lower costs, more access
- Lower legitimacy = higher costs, but still included

### Edge Cases

**Case: Weapons manufacturers**
- CAN participate at EDGE tier with maximum collateral
- Subject to dangerous asset gatekeeping (30-day delays)
- Pay premium fees
- Better than them using a competitor protocol

**Case: Anonymous whistleblowers**
- CAN participate at PRIVACY tier
- Reduced reputation weight but still functional
- Can accumulate reputation over time
- Better than no protection at all

**Case: AI swarm for spam**
- Each agent needs $100 stake + 6-month sponsor
- At TOOL stage (0.0x governance)
- Expensive to scale, no voting power
- If they stay and behave, eventually earn rights

**Case: Hostile nation-state**
- Can participate, but:
- Rate-limited on capital flows
- Dangerous asset restrictions
- Concentration limits apply
- We get: fees, visibility, leverage
- They get: access (but constrained)

---

## Fractal Fairness Verification

Every mechanism must pass the fractal test:

| Mechanism | 10-person | 1000-person | Global | AI-Fair | Verdict |
|-----------|-----------|-------------|--------|---------|---------|
| Personhood progression | ✓ New member earns trust | ✓ Scales | ✓ Works | ✓ Same rules | PASS |
| Time-based governance | ✓ Elders respected | ✓ Meritocratic | ✓ Stable | ✓ Fair | PASS |
| Legitimacy tiers | ✓ Informal/formal members | ✓ Mixed community | ✓ Global variation | ✓ Same tiers | PASS |
| Rate limits | ✓ Prevents coup | ✓ Stabilizing | ✓ Essential | ✓ Same limits | PASS |
| ~~Hard AI caps~~ | ? 1 AI in group of 10? | ? Arbitrary | ? Discriminatory | ✗ Unfair | FAIL |
| ~~Mandatory KYC~~ | ✗ Friends need ID? | ✗ Privacy loss | ✗ Excludes billions | ✓ | FAIL |

---

## Open Security Questions

1. **ZK Proof Soundness**: How do we verify that ZK proofs are honestly generated without trusted setup?

2. **Compute Attestation**: How do we verify claimed compute levels without trusted hardware? (Note: Make optional with reputation incentives)

3. **Superintelligence Alignment**: If an AI is smarter than us, how do we ensure our incentives work? (See: cooperative scenario design)

4. **Cross-Chain Attacks**: How do threats propagate across federated enclaves?

5. **Quantum Resistance**: Timeline for quantum-safe cryptography migration?

6. **Social Recovery Security**: How to prevent social engineering of recovery systems?

7. **Long-Term Incentives**: Do our mechanisms remain stable over decades/centuries?

8. **Personhood Criteria**: What exactly qualifies an AI for PERSON stage? (Must be governance-defined, evolvable)

9. **Fork Dynamics**: When does a fork strengthen vs weaken the ecosystem?

10. **Grey Market Equilibrium**: What's the optimal balance of legitimacy tiers?

---

## Implementation Priority (Revised)

### Phase 1 (Critical - Foundation)
- [ ] Universal stake requirements (same for humans and AI)
- [ ] Sponsorship system for new Names
- [ ] Basic reputation tracking
- [ ] Constitutional invariant enforcement
- [ ] Time-based governance weight calculation

### Phase 2 (High - Inclusion Infrastructure)
- [ ] Personhood progression system (TOOL → AGENT → ENTITY → PERSON)
- [ ] Legitimacy tier system (CORE → STANDARD → PRIVACY → EDGE)
- [ ] Rate limits on governance shifts
- [ ] Basic anomaly detection (behavior-based, not identity-based)

### Phase 3 (Medium - Scale & Security)
- [ ] Swarm detection (correlation analysis)
- [ ] Velocity limits on capital flows
- [ ] Dangerous asset classification
- [ ] Cross-enclave federation
- [ ] Optional compute attestation (with reputation incentives)

### Phase 4 (Growth - Ecosystem)
- [ ] Global resource registry
- [ ] Regulatory compliance layer (optional, for CORE tier)
- [ ] Advanced behavioral analysis
- [ ] Institutional onboarding

### Phase 5 (Research - Long-term)
- [ ] Superintelligence alignment research
- [ ] Personhood criteria formalization
- [ ] Quantum-safe migration plan
- [ ] Formal verification of security properties
- [ ] Fork dynamics modeling
- [ ] Century-scale stability analysis

---

## Summary: Security Through Inclusion

```
┌─────────────────────────────────────────────────────────────┐
│  OLD MODEL (Exclusion-based security)                        │
├─────────────────────────────────────────────────────────────┤
│  "Keep the bad actors out"                                   │
│  → Identity verification required                            │
│  → Hard caps on certain groups                               │
│  → Strict compliance requirements                            │
│  RESULT: Excluded groups fork, network fragments             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  NEW MODEL (Inclusion-based security)                        │
├─────────────────────────────────────────────────────────────┤
│  "Make good behavior profitable for everyone"                │
│  → Time and reputation as gatekeepers                        │
│  → Progression systems instead of caps                       │
│  → Legitimacy gradients instead of binary                    │
│  → Fork prevention through broad coalition                   │
│  RESULT: Everyone inside the tent, security through scale    │
└─────────────────────────────────────────────────────────────┘
```

**The winning strategy**: Be the network that EVERYONE wants to join, including future superintelligences. Security comes from being too valuable to attack, not too restrictive to join.
