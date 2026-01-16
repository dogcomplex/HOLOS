# HOLO-POLY

A Harberger Tax Monopoly simulation for testing HOLOS economic principles.

## Overview

HOLO-POLY modifies classic Monopoly with:
- **Harberger Tax**: Self-assessed property valuations with forced sales
- **UBI Dividend**: Tax revenue redistributed to all players
- **Private Cash**: Opponents can't see your balance (only solvency status)
- **LLM Agents**: AI players powered by Gemini 2.0 Flash

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with stub LLM (no API key needed)
python main.py

# Run with verbose output
python main.py -v

# Run with specific seed for reproducibility
python main.py --seed 42
```

## Configuration

Edit `config.yaml` to customize:

```yaml
# Economic timing modes
economics:
  tax_timing: "on_go"      # "on_go" or "per_turn"
  dividend_timing: "on_go"  # "on_go" or "per_turn"

# Enable real LLM
llm:
  stub_mode: false
  model: "gemini-2.0-flash-exp"
```

Set your API key:
```bash
export GEMINI_API_KEY="your-key-here"
```

## Project Structure

```
holopoly/
├── main.py              # Entry point
├── config.yaml          # Configuration
├── kernel/              # Game engine
│   ├── models.py        # Data classes
│   ├── game.py          # Game orchestrator
│   ├── economics.py     # Tax, rent, dividend
│   ├── harberger.py     # Forced sales
│   └── board_data.py    # Monopoly board
├── agents/              # LLM agents
│   ├── agent.py         # Agent logic
│   ├── llm_client.py    # Gemini API
│   └── prompts/         # Archetype prompts
├── ledger/              # Database
│   ├── db.py            # SQLite operations
│   └── schema.sql       # Database schema
└── tests/               # Test suite
```

## Agent Archetypes

1. **Slumlord**: Aggressive property accumulator, high valuations
2. **Squatter**: Dividend parasite, avoids owning assets
3. **Flipper**: Market maker, buys low and welcomes forced sales
4. **Developer**: Vertical integrator, focuses on monopolies

## Economic Timing Modes

Four combinations of tax/dividend timing:

| Mode | Tax | Dividend | Character |
|------|-----|----------|-----------|
| A | on_go | on_go | Events cluster at GO |
| B | on_go | per_turn | Tax bursts, steady income |
| C | per_turn | on_go | Steady drain, income bursts |
| D | per_turn | per_turn | Uniform cash flow |

## Core Rules

1. **Self-Assessment**: Owners declare property valuations
2. **Forced Sale**: Anyone can buy at declared price (no refusal)
3. **Tax**: 10% of total valuations (timing configurable)
4. **Rent**: 10% of property valuation when landed on
5. **Dividend**: Share of tax pot distributed equally

## Multi-Board Support

The system supports N players on M boards:
- Players cycle to next board after passing GO
- Properties identified by (board_id, tile_id)
- Default: 4 players, 1 board

## Testing Hypotheses

1. **Does Harberger prevent monopolies?** → Measure property turnover
2. **Does UBI keep poor alive?** → Track Squatter survival
3. **Do valuations converge?** → Analyze pricing over time
4. **Do strategies differentiate?** → Compare archetype outcomes
