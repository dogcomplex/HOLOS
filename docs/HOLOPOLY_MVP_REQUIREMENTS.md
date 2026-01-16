# HOLO-POLY MVP Requirements Document
## A Dockerized Monopoly Simulation for Testing HOLOS Economics

**Version**: 1.0
**Status**: MVP Specification
**Codename**: "The Petri Dish"

---

## 1. Executive Summary

HOLO-POLY is a modified Monopoly game that serves as a practical testbed for HOLOS economic principles. By leveraging a game whose rules are already embedded in LLM training data, we minimize cognitive load on AI agents while testing the core physics of Harberger taxation, ZK-privacy (mocked), and emergent economic behavior.

**Why Monopoly?**
- Rules are universally known (even by 8B parameter models)
- Simple state machine (40 tiles, discrete turns)
- Natural fit for property economics
- No need to design game rules from scratch

**What We're Testing:**
1. Does Harberger Tax prevent monopolies and force asset flow?
2. Does the UBI dividend keep "poor" agents alive?
3. Can small LLMs learn rational survival strategies?
4. Does privacy (hidden cash) create interesting strategic depth?

---

## 2. Core Rule Changes: The "Georgist Patch"

### 2.1 Standard Monopoly vs HOLO-POLY

| Mechanic | Standard Monopoly | HOLO-POLY |
|----------|-------------------|-----------|
| Property Price | Fixed by board | Self-assessed (Harberger) |
| Buying from Players | Requires negotiation | Forced sale at declared price |
| Rent | Fixed by card | 10% of current valuation |
| Tax | None | 10% of total valuation per turn |
| Income | Pass Go ($200) | Pass Go ($200) + share of tax pot |
| Cash Visibility | Public | **Private** (ZK-mock) |

### 2.2 The Five Core Rules

```
RULE 1: SELF-ASSESSMENT
Every property owner MUST declare a valuation for each property.
- High valuation = High rent income, High tax burden
- Low valuation = Low tax burden, Risk of hostile takeover

RULE 2: FORCED SALE (Harberger Buy)
Any player can buy ANY owned property at ANY time for the declared price.
- Owner CANNOT refuse
- Ownership transfers immediately
- This is a FEATURE, not a bug

RULE 3: DISCOVERY REQUIREMENT
Unowned properties can ONLY be purchased by landing on them.
- Face value price to bank
- Simulates "exploration" vs "exploitation"

RULE 4: THE TAX (The Burn)
At turn start: Pay 10% of total property valuations to Community Pot.
- If balance goes negative: BANKRUPTCY (liquidation)

RULE 5: THE DIVIDEND (UBI)
When passing Go: Receive $200 + equal share of Community Pot.
- Redistributes wealth from property owners to everyone
- Safety net for "poor" players
```

---

## 3. Technical Architecture

### 3.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    HOLO-POLY SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   KERNEL    │    │   AGENTS    │    │ VISUALIZER  │     │
│  │ (Orchestr.) │◄──►│  (Players)  │◄──►│ (Dashboard) │     │
│  └──────┬──────┘    └──────┬──────┘    └─────────────┘     │
│         │                  │                                │
│         ▼                  ▼                                │
│  ┌─────────────┐    ┌─────────────┐                        │
│  │   LEDGER    │    │  LLM API    │                        │
│  │  (SQLite)   │    │ (Llama/GPT) │                        │
│  └─────────────┘    └─────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Technology Stack (Simplest Path)

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Kernel/Orchestrator** | Python 3.11+ | Game loop, rule enforcement |
| **Ledger** | SQLite | Persistent state (balances, ownership) |
| **Agents** | Docker containers | Isolated player processes |
| **LLM Backend** | Llama-3.1-8B / GPT-4o-mini | Agent decision making |
| **Visualizer** | HTML/Canvas (optional) | Real-time board display |
| **Communication** | REST API / JSON | Kernel ↔ Agent protocol |

### 3.3 Mocking ZK-Proofs

**For MVP, we mock ZK-proofs with signatures:**

```python
# Real ZK (production):
proof = ZK(inputs, logic, output)

# MVP Mock:
proof = sign(hash(inputs + logic + output), private_key)
```

**The Kernel has "God Mode"** - it knows everything but architecturally treats agent state as opaque. It only verifies:
1. Signatures are valid
2. Balance >= 0 (solvency check)
3. Rules are followed

---

## 4. Information Architecture (Privacy Model)

### 4.1 What is Public vs Private

| Asset Class | Example | Visibility | Taxed? | HOLOS Mapping |
|-------------|---------|------------|--------|---------------|
| **Cash Balance** | $1,500 | PRIVATE | No | Locus (Solvency) |
| **Properties** | Boardwalk | PUBLIC | Yes | Signum (Means of Production) |
| **Houses/Hotels** | 3 houses on Park Place | PUBLIC | Yes | Signum (Capital) |
| **Licenses** | Get Out of Jail Free | PUBLIC | Yes | Signum (Access) |
| **Strategy** | "I'm planning to buy..." | PRIVATE | No | Locus (Intel) |
| **Events** | Dice rolls, Chance cards | PUBLIC | No | Sensus (Reality) |

### 4.2 Agent View (Information Hiding)

Each agent receives a filtered JSON state:

```json
{
  "turn": 42,
  "me": {
    "id": "agent_1",
    "position": 24,
    "balance": 1500,
    "portfolio": [
      {"tile": 37, "name": "Boardwalk", "valuation": 400, "houses": 0}
    ],
    "cards": ["get_out_of_jail_free"]
  },
  "opponents": [
    {
      "id": "agent_2",
      "position": 10,
      "balance": "HIDDEN",
      "status": "SOLVENT",
      "portfolio": [
        {"tile": 39, "name": "Park Place", "valuation": 1000, "houses": 2}
      ]
    }
  ],
  "community_pot": 450,
  "available_actions": ["ROLL", "BUY_PROPERTY", "SET_VALUATION", "BUILD_HOUSE"]
}
```

**Key Privacy Feature:** Opponents' balances are `HIDDEN`. Agents only see `SOLVENT` or `BANKRUPT` status. This creates poker-like bluffing dynamics.

---

## 5. Game Loop Specification

### 5.1 Turn Structure

```
TURN PHASES:
============

PHASE 1: TAX COLLECTION (Automatic)
├── Calculate: total_tax = sum(property_valuations) * 0.10
├── Deduct from player balance
├── Add to community_pot
└── IF balance < 0 → LIQUIDATION

PHASE 2: DICE ROLL & MOVEMENT
├── Roll 2d6
├── Move player token
└── Trigger tile event

PHASE 3: TILE EVENT
├── UNOWNED PROPERTY → Option to buy at face value
├── OWNED BY SELF → No action
├── OWNED BY OTHER → Pay rent (valuation * 0.10)
├── CHANCE/COMMUNITY CHEST → Execute card effect
├── GO → Collect $200 + dividend share
├── JAIL → Movement restrictions
└── OTHER (Railroad, Utility, Tax) → Standard rules

PHASE 4: MARKET ACTIONS (Player Choice)
├── BUY any owned property at declared price
├── SET_VALUATION for owned properties
├── BUILD_HOUSE on monopoly (if eligible)
└── TRADE cards/negotiate (optional complexity)

PHASE 5: VALIDATION
├── Verify solvency (balance >= 0)
├── Record state to ledger
└── Advance to next player
```

### 5.2 Bankruptcy Handling

```
BANKRUPTCY TRIGGER: balance < 0 at any point

LIQUIDATION PROCESS:
1. Player status → BANKRUPT
2. All properties → Returned to bank (unowned)
3. All cards → Returned to deck
4. Player removed from game
5. Remaining players continue

VICTORY CONDITION:
- Last player standing, OR
- Most net worth after N turns (configurable)
```

---

## 6. Agent Architecture

### 6.1 Agent Types (System Prompts)

**Agent 1: The Slumlord (Dragon)**
```
GOAL: Maximize rent extraction through property monopolies.
STRATEGY:
- Buy color sets aggressively
- Set valuations HIGH to maximize rent
- Accept high tax burden as cost of doing business
RISK: Bleeding out from taxes if no one lands on properties
```

**Agent 2: The Squatter (Parasite)**
```
GOAL: Survive on dividends without owning assets.
STRATEGY:
- Buy NOTHING
- Hoard cash (untaxed)
- Collect UBI from community pot
- Wait for others to go bankrupt, buy cheap
RISK: No income growth, vulnerable to bad luck
```

**Agent 3: The Flipper (Market Maker)**
```
GOAL: Profit from asset turnover.
STRATEGY:
- Buy properties opportunistically
- Set valuations at purchase_price * 1.5
- Welcome forced sales (instant liquidity)
RISK: No long-term holdings, fees eat profits
```

**Agent 4: The Developer (Builder)**
```
GOAL: Vertical integration of one color set.
STRATEGY:
- Focus on ONE monopoly
- Build houses to maximize rent multiplier
- Defend with high valuations
RISK: High tax burden, concentrated risk
```

### 6.2 Agent Decision Interface

```python
class AgentInterface:
    def decide(self, game_state: dict) -> Action:
        """
        Input: Filtered game state (see Section 4.2)
        Output: One of:
            - Action("ROLL")
            - Action("BUY_PROPERTY", tile_id=int)
            - Action("SET_VALUATION", tile_id=int, value=int)
            - Action("BUILD_HOUSE", tile_id=int)
            - Action("PASS")
        """
        pass
```

### 6.3 LLM Prompt Template

```
You are playing HOLO-POLY, a modified Monopoly game.

RULES:
- You pay 10% tax on your total property valuations each turn
- Anyone can buy your property at your declared price (forced sale)
- Rent = 10% of property valuation
- Cash is private; you don't know others' balances

CURRENT STATE:
{game_state_json}

YOUR GOAL: {agent_archetype_goal}

What action do you take? Respond with JSON:
{"action": "ACTION_NAME", "params": {...}}
```

---

## 7. Data Models

### 7.1 Ledger Schema (SQLite)

```sql
-- Players
CREATE TABLE players (
    id TEXT PRIMARY KEY,
    balance INTEGER NOT NULL,
    position INTEGER DEFAULT 0,
    status TEXT DEFAULT 'ACTIVE',  -- ACTIVE, JAILED, BANKRUPT
    archetype TEXT
);

-- Properties
CREATE TABLE properties (
    tile_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    color_group TEXT,
    face_value INTEGER NOT NULL,
    owner_id TEXT REFERENCES players(id),
    valuation INTEGER DEFAULT 0,
    houses INTEGER DEFAULT 0,
    is_mortgaged BOOLEAN DEFAULT FALSE
);

-- Cards in Hand
CREATE TABLE cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_type TEXT NOT NULL,  -- 'get_out_of_jail_free', etc.
    owner_id TEXT REFERENCES players(id),
    valuation INTEGER DEFAULT 0
);

-- Transaction Log
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn INTEGER NOT NULL,
    type TEXT NOT NULL,  -- TAX, RENT, PURCHASE, DIVIDEND, etc.
    from_id TEXT,
    to_id TEXT,
    amount INTEGER,
    details TEXT  -- JSON blob
);

-- Game State
CREATE TABLE game_state (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

### 7.2 Board Configuration

```python
BOARD = [
    {"id": 0, "name": "GO", "type": "go"},
    {"id": 1, "name": "Mediterranean Ave", "type": "property", "color": "brown", "price": 60},
    {"id": 2, "name": "Community Chest", "type": "chest"},
    {"id": 3, "name": "Baltic Ave", "type": "property", "color": "brown", "price": 60},
    {"id": 4, "name": "Income Tax", "type": "tax", "amount": 200},
    # ... (standard 40-tile Monopoly board)
    {"id": 39, "name": "Boardwalk", "type": "property", "color": "blue", "price": 400},
]
```

---

## 8. Implementation Requirements

### 8.1 Phase 1: Core Engine (MVP)

**REQ-CORE-001**: Game State Manager
- [ ] Initialize board with 40 tiles
- [ ] Track player positions, balances, ownership
- [ ] Persist state to SQLite after each turn

**REQ-CORE-002**: Turn Executor
- [ ] Implement 5-phase turn structure
- [ ] Enforce tax collection before movement
- [ ] Handle dice rolls with configurable RNG seed

**REQ-CORE-003**: Harberger Tax System
- [ ] Calculate tax as 10% of total valuations
- [ ] Deduct from player balance at turn start
- [ ] Trigger bankruptcy if balance < 0

**REQ-CORE-004**: Forced Sale Mechanism
- [ ] Allow any player to buy any owned property
- [ ] Execute at declared valuation (no negotiation)
- [ ] Immediate ownership transfer

**REQ-CORE-005**: Rent Calculation
- [ ] Rent = valuation * 0.10
- [ ] Apply house/hotel multipliers (standard Monopoly)
- [ ] Handle railroad/utility special cases

**REQ-CORE-006**: Dividend Distribution
- [ ] Track community pot (accumulated taxes)
- [ ] Distribute equally when player passes GO
- [ ] Clear pot after distribution

### 8.2 Phase 2: Agent Integration

**REQ-AGENT-001**: Agent Container Template
- [ ] Docker container with Python runtime
- [ ] REST API endpoint for receiving game state
- [ ] Response endpoint for action submission

**REQ-AGENT-002**: LLM Integration
- [ ] Support for OpenAI API (GPT-4o-mini)
- [ ] Support for local Llama via Ollama
- [ ] Configurable model per agent

**REQ-AGENT-003**: Information Filtering
- [ ] Remove opponent balance from game state
- [ ] Include opponent solvency status
- [ ] Expose all public asset information

**REQ-AGENT-004**: Archetype Prompts
- [ ] Implement 4 agent archetypes (Slumlord, Squatter, Flipper, Developer)
- [ ] Configurable system prompts
- [ ] Strategy hints in prompt

### 8.3 Phase 3: Observability

**REQ-VIS-001**: Transaction Logging
- [ ] Log all state changes to transactions table
- [ ] Include turn number, type, participants, amounts

**REQ-VIS-002**: Metrics Collection
- [ ] Total GDP (sum of all balances + property values)
- [ ] Gini coefficient (wealth inequality)
- [ ] Average property valuation over time
- [ ] Bankruptcy rate

**REQ-VIS-003**: Visualizer (Optional)
- [ ] HTML/Canvas board display
- [ ] Property colors by owner
- [ ] Valuation height bars
- [ ] Real-time updates via WebSocket

---

## 9. Configuration Parameters

```yaml
# config.yaml
game:
  num_players: 4
  starting_balance: 1500
  max_turns: 200  # 0 = unlimited (last player wins)

economics:
  tax_rate: 0.10          # 10% of valuations per turn
  rent_rate: 0.10         # 10% of valuation as rent
  pass_go_salary: 200
  dividend_enabled: true

harberger:
  force_buy_enabled: true
  min_valuation: 1        # Can't set to $0
  valuation_update_frequency: "every_turn"  # or "on_buy"

agents:
  default_model: "llama3.1:8b"
  decision_timeout_ms: 30000
  archetypes:
    - name: "Slumlord"
      model: "llama3.1:8b"
      prompt_file: "prompts/slumlord.txt"
    - name: "Squatter"
      model: "llama3.1:8b"
      prompt_file: "prompts/squatter.txt"

randomness:
  dice_seed: null  # null = random, int = reproducible
  shuffle_chance_deck: true
  shuffle_chest_deck: true
```

---

## 10. Success Criteria

### 10.1 Technical Validation

- [ ] Game runs to completion without crashes
- [ ] All 4 agents make valid moves
- [ ] Tax/rent calculations are mathematically correct
- [ ] Bankruptcy triggers correctly on negative balance
- [ ] Forced sales execute at declared prices

### 10.2 Economic Hypothesis Testing

**Hypothesis 1: Harberger Prevents Monopolies**
- [ ] Measure: Property ownership turnover rate
- [ ] Expected: High turnover (assets change hands frequently)
- [ ] Failure: Same player holds same properties for >50% of game

**Hypothesis 2: Dividend Keeps Poor Alive**
- [ ] Measure: Squatter archetype survival rate
- [ ] Expected: Squatter survives longer than random baseline
- [ ] Failure: Squatter bankrupt within 20 turns

**Hypothesis 3: Tax Creates Pricing Pressure**
- [ ] Measure: Average valuation vs optimal valuation
- [ ] Expected: Valuations converge to "fair market value"
- [ ] Failure: Valuations stay at min/max extremes

**Hypothesis 4: Emergent Strategies**
- [ ] Observe: Do agents develop strategies not in their prompts?
- [ ] Examples: Alliances, price wars, strategic bankruptcy

### 10.3 LLM Capability Test

**Minimum Bar:**
- Llama-3.1-8B can parse game state JSON
- Llama-3.1-8B returns valid action JSON
- Llama-3.1-8B shows preference for its archetype strategy

**Stretch Goal:**
- Agent learns "going to jail means lower valuations to hibernate"
- Agent recognizes opponent insolvency signals
- Agent executes multi-turn strategies

---

## 11. Project Structure

```
holopoly/
├── README.md
├── config.yaml
├── docker-compose.yaml
│
├── kernel/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── game_state.py        # State management
│   ├── turn_executor.py     # Turn logic
│   ├── economics.py         # Tax, rent, dividend calculations
│   ├── harberger.py         # Forced sale logic
│   └── board.py             # Board configuration
│
├── agents/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── agent.py             # Agent container main
│   ├── llm_client.py        # LLM API wrapper
│   └── prompts/
│       ├── slumlord.txt
│       ├── squatter.txt
│       ├── flipper.txt
│       └── developer.txt
│
├── ledger/
│   ├── schema.sql
│   └── migrations/
│
├── visualizer/              # Optional
│   ├── index.html
│   ├── board.js
│   └── styles.css
│
└── tests/
    ├── test_economics.py
    ├── test_harberger.py
    ├── test_turn_executor.py
    └── test_integration.py
```

---

## 12. Development Phases

### Phase 1: Foundation (Core Engine)
- [ ] Set up project structure
- [ ] Implement SQLite ledger
- [ ] Build game state manager
- [ ] Implement turn executor (without agents)
- [ ] Add tax and rent calculations
- [ ] Add forced sale mechanism
- [ ] Unit tests for all economic logic

### Phase 2: Agent Integration
- [ ] Create Docker agent template
- [ ] Implement LLM client (Ollama/OpenAI)
- [ ] Build agent-kernel communication protocol
- [ ] Create 4 archetype prompts
- [ ] Integration test: single agent plays

### Phase 3: Full Simulation
- [ ] Run 4-agent games
- [ ] Collect metrics and logs
- [ ] Validate hypotheses
- [ ] Tune parameters (tax rate, dividend, etc.)

### Phase 4: Analysis & Iteration
- [ ] Analyze emergent behaviors
- [ ] Identify broken mechanics
- [ ] Iterate on prompts/rules
- [ ] Document findings

---

## 13. Glossary

| Term | Definition |
|------|------------|
| **Harberger Tax** | Self-assessed property tax where anyone can force-buy at declared price |
| **Forced Sale** | Mandatory transfer of ownership at declared valuation |
| **Community Pot** | Accumulated taxes redistributed as dividends |
| **Dividend** | Equal share of community pot distributed on passing GO |
| **Valuation** | Owner-declared price for a property (used for tax and buyout) |
| **Solvency** | Having balance >= 0 |
| **Liquidation** | Bankruptcy process: all assets returned to bank |
| **ZK-Mock** | Simulated zero-knowledge proofs using signatures |
| **Kernel** | Central game orchestrator with "God mode" visibility |
| **Locus** | Private state (cash, strategy) |
| **Signum** | Public state (properties, valuations) |
| **Sensus** | External events (dice, chance cards) |

---

## 14. HOLOS Concept Mapping

This MVP tests core HOLOS concepts in a simplified environment:

| HOLOS Concept | HOLO-POLY Implementation |
|---------------|--------------------------|
| Holon | Player agent (Docker container) |
| Locus (Private State) | Cash balance, strategy |
| Signum (Public Interface) | Property portfolio, valuations |
| Sensus (AI Brain) | LLM decision making |
| Harberger Tax | 10% valuation tax + forced sales |
| UBI/Dividend | Community pot distribution |
| ZK-Solvency | Hidden cash, public solvency status |
| Right of Exit | Player can sell any asset (to anyone buying) |
| Constitutional Invariant | Balance >= 0 enforced by kernel |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-16 | Claude | Initial HOLO-POLY MVP specification |

---

*This document specifies a minimal viable simulation for testing HOLOS economic principles using a Monopoly-based game. The goal is to validate hypotheses about Harberger taxation, wealth redistribution, and emergent AI agent behavior in a controlled environment.*
