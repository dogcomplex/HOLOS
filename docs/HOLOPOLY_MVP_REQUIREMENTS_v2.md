# HOLO-POLY MVP Requirements Document v2
## A Streamlined Dockerized Monopoly Simulation for Testing HOLOS Economics

**Version**: 2.0
**Status**: MVP Specification (Pragmatic)
**Codename**: "The Petri Dish"

---

## 1. Executive Summary

HOLO-POLY is a modified Monopoly game that tests HOLOS economic principles: Harberger taxation, forced sales, and UBI dividends. This v2 spec prioritizes simplicity and pragmatism over architectural completeness.

**Why Monopoly?**
- Rules are universally known by LLMs
- Simple state machine (40 tiles per board, discrete turns)
- Natural fit for property economics
- No need to design game rules from scratch

**Core Hypotheses:**
1. Does Harberger Tax prevent monopolies and force asset flow?
2. Does the UBI dividend keep "poor" agents alive?
3. Can LLMs learn rational survival strategies?
4. Does privacy (hidden cash) create strategic depth?

**What We Cut (from v1):**
- ~~Bicameral architecture (Reflex/Reason brains)~~
- ~~FLUX/FOCUS dual currencies~~
- ~~Sabotage cards and secret assets~~
- ~~Ghost archetype~~
- ~~Survival instinct override~~
- ~~Adversarial testing scenarios~~

---

## 2. Multi-Board Architecture

### 2.1 Design for Scale

The system is designed for **N players on M boards**, enabling large-scale simulations.

```
┌─────────────────────────────────────────────────────────────┐
│                    HOLO-POLY UNIVERSE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                │
│   │ Board 0 │    │ Board 1 │    │ Board 2 │    ...         │
│   │ (40 tiles)│   │ (40 tiles)│   │ (40 tiles)│             │
│   └────┬────┘    └────┬────┘    └────┬────┘                │
│        │              │              │                      │
│        └──────────────┴──────────────┘                      │
│                       │                                     │
│              Players cycle through                          │
│              boards on passing GO                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Board Cycling Mechanic

When a player passes GO:
1. Collect GO salary ($200)
2. Process tax/dividend (depending on timing mode)
3. **Move to next board**: `next_board = (current_board + 1) % num_boards`
4. Position resets to tile 0 (GO) on new board

### 2.3 Property Identification

All properties are uniquely identified by `(board_id, tile_id)`:

```python
@dataclass
class PropertyId:
    board: int   # 0, 1, 2, ...
    tile: int    # 0-39

# Example: Boardwalk on Board 2
property = PropertyId(board=2, tile=39)
```

### 2.4 Default Configuration

**MVP Target:** 4 players, 1 board (standard Monopoly)
**Scalable To:** 100+ players, 10+ boards

```yaml
universe:
  num_boards: 1          # Start with 1, scale up
  players_per_board: 4   # Soft target for balance
  total_players: 4
```

---

## 3. Economic Timing Modes

### 3.1 Four Combinations

The system supports 4 timing modes for tax collection and UBI distribution:

| Mode | Tax Timing | UBI Timing | Character |
|------|------------|------------|-----------|
| **A** | on_go | on_go | Classic - events cluster at GO |
| **B** | on_go | per_turn | Tax bursts, steady income |
| **C** | per_turn | on_go | Steady drain, income bursts |
| **D** | per_turn | per_turn | Uniform - predictable cash flow |

### 3.2 Tuning for Equivalence

Both timing modes should produce ~$200 equivalent per circuit (10 turns average):

**On-GO Mode:**
- Tax: 10% of total valuations, collected when passing GO
- UBI: Full pot distributed when passing GO

**Per-Turn Mode:**
- Tax: 1% of total valuations per turn (≈10% per circuit)
- UBI: 1/10th of pot distributed per turn

### 3.3 Configuration

```yaml
economics:
  # Tax settings
  tax_rate: 0.10                    # Base rate (adjusted by timing)
  tax_timing: "on_go"               # "on_go" | "per_turn"

  # UBI settings
  dividend_timing: "on_go"          # "on_go" | "per_turn"

  # Derived rates (calculated by engine)
  # If per_turn: effective_rate = tax_rate / avg_circuit_length
  avg_circuit_length: 10            # Expected turns to complete board

  # Other
  pass_go_salary: 200
  rent_rate: 0.10                   # 10% of valuation as rent
```

### 3.4 Implementation

```python
class EconomicsEngine:
    def __init__(self, config):
        self.base_tax_rate = config.tax_rate
        self.tax_timing = config.tax_timing
        self.dividend_timing = config.dividend_timing
        self.circuit_length = config.avg_circuit_length

    @property
    def effective_tax_rate(self):
        """Tax rate adjusted for timing mode."""
        if self.tax_timing == "per_turn":
            return self.base_tax_rate / self.circuit_length
        return self.base_tax_rate

    def process_turn_start(self, player, game_state):
        """Called at start of each turn."""
        if self.tax_timing == "per_turn":
            self._collect_tax(player, game_state)
        if self.dividend_timing == "per_turn":
            self._distribute_dividend(player, game_state)

    def process_pass_go(self, player, game_state):
        """Called when player passes GO."""
        player.balance += 200  # GO salary

        if self.tax_timing == "on_go":
            self._collect_tax(player, game_state)
        if self.dividend_timing == "on_go":
            self._distribute_dividend(player, game_state)
```

---

## 4. Core Rules: The "Georgist Patch"

### 4.1 Standard Monopoly vs HOLO-POLY

| Mechanic | Standard Monopoly | HOLO-POLY |
|----------|-------------------|-----------|
| Property Price | Fixed by board | Self-assessed (Harberger) |
| Buying from Players | Requires negotiation | Forced sale at declared price |
| Rent | Fixed by card | 10% of current valuation |
| Tax | None | 10% of total valuations (timing varies) |
| Income | Pass Go ($200) | Pass Go ($200) + share of tax pot |
| Cash Visibility | Public | **Private** |

### 4.2 The Five Core Rules

```
RULE 1: SELF-ASSESSMENT
Every property owner MUST declare a valuation for each property.
- High valuation = High rent income, High tax burden
- Low valuation = Low tax burden, Risk of hostile takeover

RULE 2: FORCED SALE (Harberger Buy)
Any player can buy ANY owned property at ANY time for the declared price.
- Owner CANNOT refuse
- Ownership transfers immediately
- Buyer pays declared price to seller

RULE 3: DISCOVERY REQUIREMENT
Unowned properties can ONLY be purchased by landing on them.
- Face value price to bank
- Initial valuation = purchase price

RULE 4: THE TAX (The Burn)
Pay tax_rate% of total property valuations (timing per config).
- If balance goes negative: BANKRUPTCY

RULE 5: THE DIVIDEND (UBI)
Receive equal share of community pot (timing per config).
- Redistributes wealth from property owners to everyone
```

---

## 5. Technical Architecture

### 5.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    HOLO-POLY SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   KERNEL    │    │   AGENTS    │    │   METRICS   │     │
│  │ (Orchestr.) │◄──►│  (Players)  │    │ (Observer)  │     │
│  └──────┬──────┘    └──────┬──────┘    └─────────────┘     │
│         │                  │                                │
│         ▼                  ▼                                │
│  ┌─────────────┐    ┌─────────────┐                        │
│  │   LEDGER    │    │  LLM API    │                        │
│  │  (SQLite)   │    │  (Gemini)   │                        │
│  └─────────────┘    └─────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Kernel** | Python 3.11+ | Game loop, rule enforcement |
| **Ledger** | SQLite | Persistent state |
| **Agents** | Docker containers | Isolated player processes |
| **LLM** | Gemini 2.0 Flash | Agent decision making |
| **Metrics** | JSON logs | Analysis and visualization |

### 5.3 LLM Configuration

**Model:** `gemini-2.0-flash-exp` (or latest stable)

**Why Gemini 2.0 Flash:**
- Smart enough for strategic reasoning
- 1M token context window (no truncation worries)
- Can include full game history if needed
- Cost-effective for many agents

**In-Game Pricing Model:**
The LLM is treated as a shared resource. Agents "buy" inference time:
- Model runs continuously (conceptually)
- Each agent gets a share of the token queue
- No explicit token currency - just response latency

```yaml
llm:
  model: "gemini-2.0-flash-exp"
  max_context_tokens: 100000      # Use up to 100k for history
  temperature: 0.7
  timeout_ms: 30000
```

---

## 6. Information Architecture

### 6.1 What is Public vs Private

| Asset Class | Visibility | Taxed? | Notes |
|-------------|------------|--------|-------|
| **Cash Balance** | PRIVATE | No | Only owner knows exact amount |
| **Solvency Status** | PUBLIC | No | Others see SOLVENT/BANKRUPT |
| **Properties** | PUBLIC | Yes | Owner, valuation, houses visible |
| **Board Position** | PUBLIC | No | All players visible on all boards |
| **Dice Rolls** | PUBLIC | No | Transparent randomness |

### 6.2 Agent View (Per-Turn JSON)

```json
{
  "turn": 42,
  "timing_mode": {"tax": "on_go", "dividend": "per_turn"},

  "me": {
    "id": "agent_1",
    "board": 0,
    "position": 24,
    "balance": 1500,
    "portfolio": [
      {"board": 0, "tile": 37, "name": "Boardwalk", "valuation": 400, "houses": 0}
    ]
  },

  "opponents": [
    {
      "id": "agent_2",
      "board": 0,
      "position": 10,
      "balance": "HIDDEN",
      "status": "SOLVENT",
      "portfolio": [
        {"board": 0, "tile": 39, "name": "Park Place", "valuation": 1000, "houses": 2}
      ]
    }
  ],

  "community_pot": 450,
  "boards": [
    {"id": 0, "unowned_properties": [1, 3, 6, 8, ...]}
  ],

  "available_actions": ["ROLL", "BUY_PROPERTY", "SET_VALUATION", "BUILD_HOUSE"]
}
```

---

## 7. Game Loop

### 7.1 Turn Structure

```
TURN PHASES:
============

PHASE 0: TURN START (if per_turn timing)
├── Collect tax (if tax_timing == "per_turn")
├── Distribute dividend share (if dividend_timing == "per_turn")
└── Check solvency

PHASE 1: DICE ROLL & MOVEMENT
├── Roll 2d6
├── Move player token
├── IF passing GO:
│   ├── Collect $200 salary
│   ├── Process tax (if tax_timing == "on_go")
│   ├── Process dividend (if dividend_timing == "on_go")
│   └── Cycle to next board (if multi-board)
└── Land on destination tile

PHASE 2: TILE EVENT
├── UNOWNED PROPERTY → Option to buy at face value
├── OWNED BY SELF → No action
├── OWNED BY OTHER → Pay rent (valuation × 0.10)
├── CHANCE/COMMUNITY CHEST → Execute card effect
├── GO → Already processed in Phase 1
├── JAIL → Standard rules
└── OTHER → Standard Monopoly rules

PHASE 3: MARKET ACTIONS (Player Choice)
├── BUY any owned property at declared price (Harberger)
├── SET_VALUATION for owned properties
└── BUILD_HOUSE on monopoly (standard rules)

PHASE 4: VALIDATION
├── Verify solvency (balance >= 0)
├── IF bankrupt → Liquidate
├── Record state to ledger
└── Advance to next player
```

### 7.2 Bankruptcy

```
TRIGGER: balance < 0 at any point

PROCESS:
1. Status → BANKRUPT
2. All properties → Unowned (bank)
3. Player removed from active rotation
4. Game continues with remaining players

VICTORY:
- Last player standing, OR
- Highest net worth after max_turns
```

---

## 8. Agent Architecture

### 8.1 Agent Archetypes (4 Types)

**Agent 1: The Slumlord**
```
GOAL: Maximize rent through property accumulation.
STRATEGY: Buy aggressively, set HIGH valuations, accept tax burden.
RISK: Tax bleed if properties don't generate rent.
```

**Agent 2: The Squatter**
```
GOAL: Survive on dividends without owning taxable assets.
STRATEGY: Buy NOTHING, hoard cash, collect UBI.
RISK: No income growth, vulnerable to bad luck.
```

**Agent 3: The Flipper**
```
GOAL: Profit from asset turnover.
STRATEGY: Buy low, set valuation at 1.5x, welcome forced sales.
RISK: Transaction costs, timing risk.
```

**Agent 4: The Developer**
```
GOAL: Vertical integration - monopolize one color set.
STRATEGY: Focus on ONE monopoly, build houses, defend with valuations.
RISK: Concentrated risk, high tax if rent doesn't cover.
```

### 8.2 LLM Prompt Template

```
You are playing HOLO-POLY, a modified Monopoly game with Harberger taxes.

RULES:
- You pay {tax_rate}% tax on your total property valuations ({tax_timing})
- Anyone can force-buy your property at your declared price
- Rent = 10% of property valuation
- Cash is private; you don't know others' exact balances
- UBI dividend distributed {dividend_timing}

YOUR ROLE: {archetype_name}
YOUR GOAL: {archetype_goal}

CURRENT STATE:
{game_state_json}

What action do you take? Respond with valid JSON:
{"action": "ACTION_NAME", "params": {...}, "reasoning": "brief explanation"}

Valid actions: ROLL, BUY_PROPERTY, SET_VALUATION, BUILD_HOUSE, PASS
```

---

## 9. Data Models

### 9.1 Database Schema

```sql
-- Universe (supports multiple games)
CREATE TABLE games (
    id TEXT PRIMARY KEY,
    config TEXT,  -- JSON blob
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Boards
CREATE TABLE boards (
    id INTEGER,
    game_id TEXT REFERENCES games(id),
    PRIMARY KEY (game_id, id)
);

-- Players
CREATE TABLE players (
    id TEXT,
    game_id TEXT REFERENCES games(id),
    balance INTEGER NOT NULL,
    current_board INTEGER NOT NULL DEFAULT 0,
    position INTEGER DEFAULT 0,
    status TEXT DEFAULT 'ACTIVE',
    archetype TEXT,
    PRIMARY KEY (game_id, id)
);

-- Properties (board_id, tile_id uniquely identifies)
CREATE TABLE properties (
    game_id TEXT,
    board_id INTEGER,
    tile_id INTEGER,
    name TEXT NOT NULL,
    color_group TEXT,
    face_value INTEGER NOT NULL,
    owner_id TEXT,
    valuation INTEGER DEFAULT 0,
    houses INTEGER DEFAULT 0,
    PRIMARY KEY (game_id, board_id, tile_id)
);

-- Transaction Log
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT,
    turn INTEGER NOT NULL,
    type TEXT NOT NULL,
    from_id TEXT,
    to_id TEXT,
    amount INTEGER,
    details TEXT
);

-- Economic State
CREATE TABLE economy (
    game_id TEXT PRIMARY KEY,
    community_pot INTEGER DEFAULT 0,
    total_turns INTEGER DEFAULT 0
);
```

---

## 10. Configuration

```yaml
# config.yaml

game:
  id: "game_001"
  max_turns: 200              # 0 = unlimited

universe:
  num_boards: 1               # Scale up for more players
  board_size: 40              # Standard Monopoly

players:
  count: 4
  starting_balance: 1500
  archetypes:
    - "Slumlord"
    - "Squatter"
    - "Flipper"
    - "Developer"

economics:
  # Timing modes: "on_go" or "per_turn"
  tax_timing: "on_go"
  dividend_timing: "on_go"

  # Rates
  tax_rate: 0.10              # 10% (adjusted if per_turn)
  rent_rate: 0.10             # 10% of valuation
  pass_go_salary: 200
  avg_circuit_length: 10      # For per_turn rate adjustment

harberger:
  force_buy_enabled: true
  min_valuation: 1
  auto_valuation_on_buy: true # Valuation = max(current, cost_basis)

llm:
  model: "gemini-2.0-flash-exp"
  temperature: 0.7
  max_tokens: 1000
  timeout_ms: 30000
  include_history: true
  max_history_turns: 50

randomness:
  seed: null                  # null = random, int = reproducible
```

---

## 11. Success Criteria

### 11.1 Technical Validation

- [ ] Game runs to completion without crashes
- [ ] Multi-board cycling works correctly
- [ ] All 4 timing modes produce valid games
- [ ] Tax/rent/dividend math is correct
- [ ] Harberger forced sales execute properly
- [ ] LLM agents return valid moves

### 11.2 Economic Hypotheses

| Hypothesis | Metric | Success | Failure |
|------------|--------|---------|---------|
| Harberger prevents monopoly | Property turnover rate | >20% change hands | Same owner >80% of game |
| UBI keeps poor alive | Squatter survival | Survives >50 turns | Bankrupt <20 turns |
| Tax creates pricing pressure | Valuation variance | Converges to stable range | Stuck at min/max |
| Privacy enables strategy | Decision variance | Different choices with hidden info | Identical to public-info baseline |

### 11.3 Timing Mode Comparison

Run each mode and compare:
- Average game length
- Bankruptcy rate
- Wealth inequality (Gini)
- Property turnover frequency

---

## 12. Project Structure

```
holopoly/
├── README.md
├── config.yaml
├── docker-compose.yaml
│
├── kernel/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── game.py              # Game orchestration
│   ├── universe.py          # Multi-board management
│   ├── economics.py         # Tax, rent, dividend (all 4 modes)
│   ├── harberger.py         # Forced sale logic
│   ├── board.py             # Single board state
│   └── turn.py              # Turn execution
│
├── agents/
│   ├── Dockerfile
│   ├── agent.py             # Agent container main
│   ├── llm_client.py        # Gemini API wrapper
│   └── prompts/
│       ├── slumlord.txt
│       ├── squatter.txt
│       ├── flipper.txt
│       └── developer.txt
│
├── ledger/
│   ├── schema.sql
│   └── db.py                # Database operations
│
├── analysis/
│   ├── metrics.py           # Gini, turnover, etc.
│   └── visualize.py         # Charts and graphs
│
└── tests/
    ├── test_economics.py
    ├── test_harberger.py
    ├── test_multiboard.py
    └── test_timing_modes.py
```

---

## 13. Development Phases

### Phase 1: Core Engine
- [ ] Multi-board universe setup
- [ ] Board cycling on GO
- [ ] Property identification (board_id, tile_id)
- [ ] Basic turn loop (no agents)
- [ ] SQLite persistence

### Phase 2: Economics
- [ ] Implement all 4 timing modes
- [ ] Tax collection (both timings)
- [ ] Dividend distribution (both timings)
- [ ] Rent calculation
- [ ] Bankruptcy handling

### Phase 3: Harberger
- [ ] Forced sale mechanism
- [ ] Valuation tracking
- [ ] Auto-valuation on purchase

### Phase 4: Agent Integration
- [ ] Gemini API client
- [ ] Prompt templates
- [ ] 4 archetype prompts
- [ ] Action parsing and validation

### Phase 5: Experiments
- [ ] Run all 4 timing modes
- [ ] Compare metrics
- [ ] Scale to multi-board
- [ ] Document findings

---

## 14. Glossary

| Term | Definition |
|------|------------|
| **Board** | One 40-tile Monopoly board in the universe |
| **Universe** | Collection of M boards with N players |
| **Circuit** | One complete trip around a board (~10 turns) |
| **Harberger Tax** | Self-assessed property tax with forced sale at declared price |
| **Forced Sale** | Mandatory transfer at owner's declared valuation |
| **Community Pot** | Accumulated taxes for UBI distribution |
| **Timing Mode** | When tax/dividend events occur (on_go vs per_turn) |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-16 | Claude | Initial specification |
| 1.1 | 2026-01-16 | Claude | Added bicameral architecture, dual currency, etc. |
| 2.0 | 2026-01-16 | Claude | **Pragmatic rewrite**: Cut complexity, added multi-board architecture, 4 timing modes, Gemini 2.0 Flash |

---

*This document specifies a lean MVP for testing HOLOS economic principles. Focus is on Harberger mechanics and UBI dynamics, with architecture designed to scale from 4 players to 100+.*
