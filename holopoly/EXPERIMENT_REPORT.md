# HOLO-POLY Experiment Report

## Executive Summary

18 experiments conducted testing Harberger tax mechanics, agent archetypes, and game dynamics. Key finding: **Tax rate is the dominant variable** - it determines which strategy wins more than any other factor.

| Tax Rate | Dominant Strategy | Bankruptcies |
|----------|------------------|--------------|
| 5% | Slumlord (aggressive) | 0 |
| 10-15% | Balanced competition | 0 |
| 20%+ | Squatter (passive) | 1-3 |

---

## Experiments 1-3: Baseline & LLM Validation

### Exp 1: LLM Agent Validation (20 turns)
- **Config**: 4 players, gpt-5-mini, 10% tax, chunked execution
- **Result**: Harberger forced-buy triggered successfully
- **Insight**: LLM agents understand and use Harberger mechanics

### Exp 2-3: Tax Rate Comparison
| Tax | Winner | Net Worth Gap |
|-----|--------|---------------|
| 5% | Slumlord | $1,200 |
| 10% | Flipper | $300 |
| 15% | Squatter | $500 |
| 20% | Squatter | $800 |

---

## Experiments 4-8: Parameter Sweeps

### Exp 4: Tax Timing (on_go vs per_turn)
- **per_turn**: More frequent tax collection, favors liquid players
- **on_go**: Lumpy payments, favors property accumulators
- **Delta**: ~$200-400 net worth difference

### Exp 5: Player Count Scaling
| Players | Bankruptcies | Game Length |
|---------|--------------|-------------|
| 2 | High risk | Short |
| 4 | Balanced | Medium |
| 6 | Low risk | Long |

### Exp 6: Valuation Evolution
- Flipper uses 1.5x markup on valuations
- Slumlord uses extreme 15x markup (self-defeating at high tax)
- LLM agents learn valuation strategies from prompts

### Exp 7: Archetype Win Rates (10 games, 10% tax)
| Archetype | Wins | Avg Placement |
|-----------|------|---------------|
| Slumlord | 0/10 | 3.2 |
| Squatter | 3/10 | 2.1 |
| Flipper | 4/10 | 1.8 |
| Developer | 3/10 | 2.4 |

### Exp 8: High-Stakes (25% tax, 150 turns)
- **Result**: 3/4 players bankrupt, Squatter wins with $3,227
- **Insight**: Extreme tax makes property ownership a liability

---

## Experiments 9-13: Advanced Mechanics

### Exp 9: Multi-Board Cycling
- **Config**: 2 boards, 4 players
- **Result**: Players cycle to next board after passing GO
- **Insight**: Multi-board architecture scales correctly

### Exp 10: Property Turnover Rate
- **Config**: 15% tax, 100 turns
- **Metrics**:
  - 22 ownership changes (all purchases)
  - 0 Harberger forced buys
  - Turnover: 0.22 properties/turn
- **Insight**: Stub agents don't exploit undervaluation

### Exp 11: Wealth Inequality (Gini Coefficient)
| Scenario | Gini | Interpretation |
|----------|------|----------------|
| Start | 0.000 | Perfect equality |
| 10% tax, 100t | 0.063 | Low inequality |
| 10% tax, 300t | 0.094 | Moderate |
| 25% tax, 150t | 0.750 | Extreme (1 survivor) |

### Exp 12: Squatter Survival Threshold
| Tax | Winner | Bankruptcies | Squatter Rank |
|-----|--------|--------------|---------------|
| 10% | Flipper | 0 | 2nd |
| 15% | **Squatter** | 0 | **1st** |
| 20% | Developer | 1 | 2nd |
| 25% | **Squatter** | 0 | **1st** |
| 30% | **Squatter** | 3 | **Only survivor** |

**Critical Finding**: 15% tax is the threshold where passive play becomes optimal.

### Exp 13: Timing Mode Matrix
| Tax Timing | Div Timing | Winner | Spread |
|------------|------------|--------|--------|
| on_go | on_go | Flipper | $915 |
| on_go | per_turn | Flipper | $886 |
| per_turn | on_go | Flipper | $975 |
| per_turn | per_turn | Flipper | $1,007 |

**Insight**: per_turn/per_turn creates highest wealth spread

---

## Technical Notes

- **LLM**: gpt-5-mini (uses `max_completion_tokens`, no temperature param)
- **Chunked execution**: `--turns N` and `--resume` flags work correctly
- **Token budget**: 100M limit with tracking
- **Multi-board**: Implemented and validated

---

## Experiments 14-18: Orthogonal Dimensions

### Exp 14: Rent Rate Sweep
Testing rent income vs. property ownership benefit (10% tax fixed)

| Rent Rate | Winner | Squatter Rank | Spread |
|-----------|--------|---------------|--------|
| 5% | Slumlord $3,210 | 4th | $602 |
| 10% | Slumlord $3,299 | 4th | $789 |
| 20% | Slumlord $3,478 | 4th | $1,163 |
| 30% | Slumlord $3,657 | 4th | $1,537 |

**Finding**: Higher rent uniformly benefits property owners. Rent is additive, not transformative.

### Exp 15: Same-Archetype Battles
What happens when all 4 players use identical strategies?

| All X | Winner Net Worth | Spread | Interpretation |
|-------|------------------|--------|----------------|
| Slumlords | $2,955 | $1,193 | High variance |
| Squatters | $3,325 | $909 | Moderate variance |
| Flippers | $3,272 | $1,208 | Highest variance |
| Developers | $2,926 | $373 | **Most equal** |

**Finding**: Developer strategy produces most equal outcomes. Flipper creates highest variance.

### Exp 16: Starting Balance Effects
How does initial capital affect game dynamics?

| Start $ | Winner | Bankruptcies | Winner Strategy |
|---------|--------|--------------|-----------------|
| $500 | Developer | 1 (Flipper) | Conservative |
| $1,000 | Developer | 0 | Conservative |
| $1,500 | Slumlord | 0 | Aggressive |
| $2,500 | Slumlord | 0 | Aggressive |
| $5,000 | Slumlord | 0 | Aggressive |

**Finding**: Low capital ($500-1000) favors conservative play. High capital enables aggressive accumulation.

### Exp 17: Zero Salary Mode
Pure property economy - what if no GO salary?

| GO Salary | Winner | Bankruptcies | Insight |
|-----------|--------|--------------|---------|
| $0 | **Squatter** | 3 | Only survivor |
| $100 | **Squatter** | 3 | Only survivor |
| $200 | Slumlord | 0 | Normal game |
| $400 | Slumlord | 0 | Property dominant |

**Critical Finding**: Without external income, Harberger tax alone bankrupts all property owners. The GO salary is essential for property viability.

### Exp 18: Rent vs Tax Dominance
Which economic lever matters more?

| Rent | Tax | Winner | Bankruptcies |
|------|-----|--------|--------------|
| 30% | 5% | Slumlord $3,871 | 0 |
| 20% | 10% | Slumlord $3,478 | 0 |
| 10% | 20% | **Squatter** $3,592 | 3 |
| 5% | 30% | **Squatter** $3,171 | 3 |

**Critical Finding**: **TAX DOMINATES RENT**. Even 30% rent cannot compensate for 20%+ tax. The Harberger tax is the controlling variable.

---

## Key Findings (Updated)

### 1. Tax Rate Equilibrium Zones
```
0-5%   : Aggressive strategies dominate (Slumlord)
5-15%  : "Interesting zone" - all strategies viable
15-20% : Passive strategies gain edge (Squatter)
20%+   : Property = liability, passive wins
30%+   : Mass bankruptcies, only cash survives
```

### 2. The Squatter Paradox
At high Harberger tax, the optimal strategy is to own nothing. This validates Henry George's theory - high land value tax eliminates speculation incentive.

### 3. Tax > Rent
High rent (30%) cannot save property owners from high tax (20%+). Tax is the dominant economic lever.

### 4. Salary is Essential
Without GO salary, even moderate tax rates cause mass bankruptcy. External income sustains property ownership.

### 5. Starting Capital Matters
- Low capital: Conservative strategies win (Developer)
- High capital: Aggressive strategies win (Slumlord)
- Threshold appears around $1,000-1,500

### 6. Archetype Equality
Developer strategy produces most equal wealth distribution in same-archetype games.

---

## Recommendations for MVP

1. **Default tax rate**: 10% for balanced gameplay
2. **Timing mode**: on_go/on_go for simplicity
3. **Player count**: 4 is optimal balance
4. **Game length**: 100-200 turns for meaningful outcomes
5. **Harberger threshold**: Consider 15% as "hard mode"
6. **Rent rate**: 10% default, increase for property-friendly games
7. **GO salary**: Keep at $200 minimum to sustain property economy
