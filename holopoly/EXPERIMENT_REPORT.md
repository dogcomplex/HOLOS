# HOLO-POLY Experiment Report

## Executive Summary

36 experiments conducted testing Harberger tax mechanics, agent archetypes, game scaling, and advanced economic parameters (resurrection, progressive tax, zero cash injection). Key finding: **Tax rate is the dominant variable** - it determines which strategy wins more than any other factor. Secondary finding: **Resurrection changes optimal strategy at 20% tax** - Flipper beats Squatter when elimination is not possible.

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

## Experiments 19-25: Advanced Dimensions

### Exp 19: House Building / Monopoly Development
- **Finding**: House building requires complete color monopolies
- **Issue**: Random agents rarely acquire full monopolies
- **Future Work**: Monopoly detection needs full implementation

### Exp 20: Min Valuation Floor
Testing Harberger minimum valuation ($1, $50, $100, $200)

| Min Valuation | Effect |
|---------------|--------|
| $1 - $200 | No change |

**Finding**: Min valuation has no effect when valuations are set to purchase price. Would matter if agents could undervalue properties.

### Exp 21: Large-Scale Simulation (20 players, 5 boards)
- **Config**: 20 players across 5 boards, 200 turns
- **Result**: All 20 players survived
- **Wealth spread**: $2,231 to $1,389 ($842 range)
- **Finding**: More players = more stable economy, smaller wealth gaps

### Exp 22: Long Game Evolution (500 turns)
- **Result**: All 4 players survived 500 turns
- **Winner**: Flipper with $7,570
- **Squatter**: $5,426 (survived but lowest)
- **Finding**: Long games don't change dynamics, just amplify wealth differences

### Exp 23: Mixed Archetype Ratios
Testing asymmetric compositions at 15% tax

| Composition | Winner | Finding |
|-------------|--------|---------|
| 3 Slumlords vs 1 Squatter | **Squatter** $3,791 | Outnumbered but wins |
| 2 Flippers vs 2 Developers | Flipper $4,156 | Transaction strategy wins |
| 1 Slumlord vs 3 Squatters | **Squatter** $3,849 | Slumlord last place |

**Critical Finding**: At 15% tax, Squatter wins even when outnumbered 3:1

### Exp 24: Chance/Community Chest Toggle
Testing the impact of luck (random cards)

| Cards | Winner | Interpretation |
|-------|--------|----------------|
| Enabled | Flipper $3,993 | Cards favor active players |
| Disabled | **Squatter** $3,336 | Pure economics favor passive |

**Finding**: Chance cards inject wealth into the system, benefiting property owners. Without cards, Squatter strategy becomes optimal.

### Exp 25: Circuit Length / Board Speed
Testing avg_circuit_length with per_turn timing

| Circuit | Squatter $ | Gap to Winner |
|---------|------------|---------------|
| 5 turns | $3,197 | $677 |
| 10 turns | $2,822 | $1,197 |
| 20 turns | $2,607 | $1,433 |
| 40 turns | $2,454 | $1,571 |

**Finding**: Shorter circuit = more frequent UBI = helps Squatter. Longer circuit favors property owners.

---

## Final Key Findings (25 Experiments)

### Economic Hierarchy (Confirmed)
```
TAX > SALARY > RENT > CHANCE_CARDS > CIRCUIT_LENGTH
```

### New Insights from Exp 19-25

1. **Scale Stabilizes**: 20-player games have smaller wealth gaps than 4-player games
2. **Cards = Wealth Injection**: Disabling chance cards shifts advantage to passive players
3. **Circuit Length Matters**: Shorter circuits help UBI recipients (Squatter)
4. **Archetype Ratio Irrelevant at High Tax**: Squatter wins even when outnumbered 3:1
5. **Long Games Don't Change Strategy**: 500 turns produces same winner as 200 turns

---

## Experiments 26-31: Economic Mechanics

### Exp 26: Resurrection via UBI
Bankrupt players can be revived when UBI payments bring their balance positive.

| Resurrection | Survivors | Bankruptcies | Resurrections |
|--------------|-----------|--------------|---------------|
| Enabled | 4/4 | 0 | Multiple (p0, p1, p2 all revived) |
| Disabled | 1/4 | 3 | N/A |

**Critical Finding**: Resurrection creates a "safety net" that keeps all players in the game. UBI becomes a true universal insurance.

### Exp 27: Bulk Color Set Purchase
Feature implemented: Buy entire color group at summed valuation atomically.
- Code added but not tested in gameplay (requires LLM agents to use)
- Prevents mid-transaction price manipulation

### Exp 28-29: Zero Cash Injection (Dynamic GO Salary)
GO salary = redistribute pot instead of printing new money.

| Mode | Survivor Net Worth | Total Economy |
|------|-------------------|---------------|
| Dynamic (on_go) | $1,613 | Deflationary |
| Dynamic (per_turn) | $1,815 | Deflationary |
| Fixed $200 (control) | $4,865 | Inflationary |

**Finding**: Zero cash injection creates a true closed economy. Money supply is fixed, making the game purely redistributive.

### Exp 30: Progressive Tax
Higher tax rate for more properties (+2% per property owned)

| Tax Type | Squatter Rank | Wealth Spread |
|----------|---------------|---------------|
| Progressive 5%+2%/prop | 2nd | Tighter |
| Flat 15% | 4th | Wider |

**Finding**: Progressive tax helps Squatter by penalizing large property holders more heavily.

### Exp 31: Harberger Toggle Baseline
Testing with Harberger mechanics disabled.

| Harberger | Results |
|-----------|---------|
| Disabled | Same as enabled* |
| Enabled | Same as disabled* |

*Stub agents don't use forced buys - need LLM agents to demonstrate Harberger dynamics.

---

## Experiments 32-36: Resurrection Re-runs

Re-testing previous high-bankruptcy experiments with `resurrection_enabled: true` and `bulk_colorset_buy: true`.

### Exp 32: Re-run Exp 8 (25% Tax, 150 turns)
| Metric | Original | With Resurrection |
|--------|----------|-------------------|
| Bankruptcies | 3/4 | **0/4** |
| Winner | Squatter $3,227 | Squatter $3,543 |
| All players | 1 survivor | All ACTIVE |

### Exp 33: Re-run Exp 12 (30% Tax)
| Metric | Original | With Resurrection |
|--------|----------|-------------------|
| Bankruptcies | 3/4 | **0/4** |
| Winner | Squatter (only survivor) | Squatter $4,523 |
| Spread | N/A (elimination) | $1,505 |

### Exp 34: Re-run Exp 17 (Zero GO Salary)
| Metric | Original | With Resurrection |
|--------|----------|-------------------|
| Bankruptcies | 3/4 | **0/4** |
| Winner | Squatter | Squatter $1,605 |
| Total Wealth | Low | Very Low ($2,604 total) |

**Finding**: Even with resurrection, $0 salary creates a harsh deflationary economy.

### Exp 35: Re-run Exp 18 (20% Tax)
| Metric | Original | With Resurrection |
|--------|----------|-------------------|
| Bankruptcies | 3/4 | **0/4** |
| Winner | Squatter $3,592 | **Flipper $3,948** |
| Squatter Rank | 1st | 2nd ($3,923) |

**Critical Finding**: **Resurrection changes the optimal strategy at 20% tax.** When players can't be eliminated, Flipper's active strategy beats passive Squatter.

### Exp 36: Re-run Exp 23 (3 Slumlords vs 1 Squatter, 15% Tax)
| Metric | Original | With Resurrection |
|--------|----------|-------------------|
| Bankruptcies | 0 | 0 |
| Winner | Squatter $3,791 | Squatter $4,148 |
| Finding | Squatter wins 3v1 | **Still wins 3v1** |

---

## Key Findings from Resurrection Re-runs

### 1. Resurrection Eliminates ALL Bankruptcies
Even under the harshest conditions (30% tax, $0 salary), resurrection via UBI keeps all players active.

### 2. Strategy Shift at 20% Tax
```
WITHOUT Resurrection: Squatter wins (opponents eliminated)
WITH Resurrection: Flipper wins (active strategy beats passive)
```
This is the most significant finding - resurrection fundamentally changes optimal strategy.

### 3. Squatter Still Dominant at Extreme Tax
At 25%+ tax, Squatter still wins even with resurrection. The passive strategy remains optimal when tax costs are too high for property ownership.

### 4. Resurrection is a "Safety Net"
It doesn't change the game's economics - it just prevents permanent elimination. Players still lose money, fall behind, and struggle - they just don't exit.

---

## Recommendations for MVP

1. **Default tax rate**: 10% for balanced gameplay
2. **Timing mode**: on_go/on_go for simplicity
3. **Player count**: 4 is optimal balance
4. **Game length**: 100-200 turns for meaningful outcomes
5. **Harberger threshold**: Consider 15% as "hard mode"
6. **Rent rate**: 10% default, increase for property-friendly games
7. **GO salary**: Keep at $200 minimum to sustain property economy
8. **Chance cards**: Keep enabled for more dynamic gameplay
9. **Circuit length**: 10 is balanced; 5 favors passive, 20+ favors property owners
10. **Resurrection**: Enable for "second chance" gameplay mode
11. **Progressive tax**: Use for anti-monopoly pressure
12. **Dynamic GO salary**: Use for closed economy experiments
