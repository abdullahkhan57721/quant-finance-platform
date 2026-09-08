# M3 — Dynamic Delta Hedging and Replication Evidence

## Purpose

M3 is the platform's first concrete **control / dynamic-replication** specialization. It asks whether the Black-Scholes replication argument works when the M2 Delta sensitivity is used as a dynamic action rule, and how terminal replication error changes when continuous rebalancing, correct volatility, and frictionless trading are weakened.

The responsibility flow is:

```text
Black-Scholes pricing problem
        ↓
M2 analytic Delta sensitivity
        ↓
concrete Delta hedge policy
        +
explicit simulated path
        +
rebalance schedule
        +
stock/cash accounting
        ↓
immutable path-level hedge evidence
        ↓
replication-error distribution evidence
```

Protect:

```text
pricing problem != sensitivity problem != hedging/control problem
Delta != hedge policy != realized hedge action
financial model != path simulation != hedge execution
replication error != model error by definition
```

M3 does not introduce a generic `ControlProblem`, `Strategy`, `Portfolio`, execution engine, risk engine, or stochastic simulator.

## Supported first control question

`BlackScholesDeltaHedgeProblem` represents one short European option liability under the existing M1 Black-Scholes family.

The local M3 support domain is intentionally narrower than the pricing domain:

- expiry is strictly after valuation time;
- spot, strike, and hedging volatility are strictly positive;
- the hedge uses the M1 flat money-market numeraire;
- the first rebalance occurs at valuation time;
- every rebalance is strictly before expiry;
- every rebalance date must exist on the realized path;
- continuous dividend yield is currently required to be zero.

The zero-dividend restriction is deliberate. M1's continuous yield is a pricing/model input, but a self-financing stock/cash hedge with `q != 0` requires an explicit convention for dividend/carry cash flows between rebalance dates. M3 rejects that case rather than silently approximating the missing accounting rule.

## Path-generation semantics

`BlackScholesPathSimulation` is a concrete path configuration, not a valuation method and not a universal simulator.

For adjacent observation dates `t_i < t_{i+1}`, the modeled spot is sampled by the exact constant-parameter GBM transition under the configured money-market pricing measure:

```math
S_{t_{i+1}}
=
S_{t_i}
\exp\left[
\left(r-q-\tfrac12\sigma_g^2\right)\Delta t_i
+
\sigma_g\sqrt{\Delta t_i}\,Z_i
\right],
\qquad Z_i\sim N(0,1).
```

Here:

- `r` comes from `FlatMoneyMarketNumeraire`;
- `q` and generating volatility `sigma_g` come from the path simulation's `BlackScholesParameters`;
- `Delta t_i` uses ACT/365F;
- the RNG is a fresh local `random.Random(seed)` for each simulation.

Because the transition is exact, **observation dates are not Euler timesteps**. M3 therefore keeps distinct:

```text
path observation grid
!= numerical SDE discretization grid
!= hedge rebalance schedule
```

The current experiment can hold the daily observation grid fixed while changing only the rebalance schedule. A future model whose path law requires numerical time discretization must introduce that discretization explicitly rather than reinterpret M3 observation dates as an Euler grid.

## Delta as a policy input

M2 defines

```math
\Delta_t = \frac{\partial V}{\partial S}(t,S_t).
```

M3's `AnalyticDeltaHedgePolicy` consumes that existing sensitivity through:

```text
BlackScholesSensitivityProblem(DELTA)
        +
AnalyticBlackScholesSensitivity
        ↓
target underlying units
```

The policy owns no mutable hedge state. It maps the currently available pricing state to a target stock holding. Realized trades and cash balances belong to hedge execution evidence.

## Self-financing accounting

The liability convention is **one short option**. The hedge is funded initially with the Black-Scholes present value produced by `BlackScholesClosedForm` under the hedging model.

Let `phi_i` be the stock units held immediately after rebalance `i`, `B_i^-` the cash immediately before the trade after financing, `S_i` the current spot, and `kappa >= 0` the proportional transaction-cost rate.

The target stock holding is

```math
\phi_i = \Delta(t_i,S_i).
```

The signed stock trade and notional are

```math
\Delta\phi_i = \phi_i-\phi_{i-1},
\qquad
Q_i = S_i\Delta\phi_i.
```

The explicit transaction cost is

```math
c_i = \kappa |Q_i|.
```

Cash after the rebalance is

```math
B_i^+ = B_i^- - Q_i - c_i.
```

Between two hedge dates, cash compounds using the existing money-market numeraire `N`:

```math
B_{i+1}^-
=
B_i^+\frac{N_{t_{i+1}}}{N_{t_i}}.
```

Therefore, when `kappa = 0`, the rebalance itself preserves portfolio wealth:

```math
\phi_{i-1}S_i+B_i^-
=
\phi_iS_i+B_i^+.
```

With costs, wealth falls exactly by the explicit cost:

```math
\phi_iS_i+B_i^+
=
\phi_{i-1}S_i+B_i^- - c_i.
```

The implementation records financing, trade units, trade notional, transaction cost, stock holdings, and pre/post-rebalance cash/wealth separately. These quantities are not compressed into one opaque P&L number.

## Terminal objective and sign convention

At expiry `T`, the final stock holding is marked at `S_T` and the cash account is financed to `T`:

```math
H_T = \phi_T S_T + B_T.
```

The European option payoff is `C_T`. M3 defines

```math
\text{replication error} = H_T - C_T.
```

Because the position is one short option plus its hedge, the same scalar is the terminal hedged short-option P&L under this convention:

```math
\text{hedged short-option P&L} = H_T-C_T.
```

Positive error means the hedge finishes with surplus after settling the option; negative error means a shortfall.

M3 does **not** automatically liquidate the terminal stock position. Terminal hedge value marks the stock holding plus cash, so no hidden terminal liquidation transaction cost is charged.

## Volatility misspecification

M3 keeps two volatility roles explicit:

```text
generating volatility sigma_g
!=
hedging/pricing volatility sigma_h
```

The path can be generated with `sigma_g` while the option value and Delta policy use `sigma_h`. Current M3 misspecification varies volatility only; rate, carry, pricing-measure, initial spot, and contract semantics remain aligned.

This separates at least:

```text
discrete-rebalancing error
!= volatility/model misspecification effect
!= stochastic replicate variation
!= transaction-cost effect
```

## Immutable evidence

Path-level committed evidence includes:

- path-generation configuration and seed;
- all simulated path points;
- initial option value;
- every rebalance action;
- stock/cash accounting before and after each action;
- financing gains;
- transaction costs;
- terminal stock/cash holdings;
- option payoff;
- terminal hedge value;
- replication error.

`ReplicationErrorSummary` aggregates only results from one common explicit study condition. It requires:

- at least two replicates;
- distinct seeds;
- the same pricing/hedging problem;
- the same rebalance schedule and transaction-cost rate;
- the same path observation grid;
- the same generating volatility/carry, numeraire, and pricing-measure semantics.

It reports replicate count/seeds, mean and median error, error standard deviation, mean absolute error, and root-mean-square error. These are distributional experiment summaries, not additions to `ValuationResult` or `BlackScholesSensitivityResult`.

## Executable validation evidence

`tests/control/test_delta_hedging.py` and `tests/control/test_replication_summary_integrity.py` establish:

1. seeded exact-transition path reproducibility;
2. the zero-volatility deterministic GBM limit;
3. exact consumption of the merged M2 analytic Delta;
4. frictionless stock/cash self-financing identities;
5. explicit transaction-cost cash outflow and aggregate cost drag;
6. no-lookahead behavior by changing only future path points and verifying earlier actions are unchanged;
7. distributional improvement as the same daily path-observation setup is hedged approximately monthly, weekly, then daily;
8. volatility misspecification as a distinct additional error source;
9. explicit rejection of nonzero dividend yield until cash-flow accounting is defined;
10. rejection of mixed study conditions, duplicate-seed pseudo-replicates, and equal-length-but-different path grids.

The frequency and misspecification studies use 64 deterministic seeds (`0..63`) rather than representative-path anecdotes. Their assertions are deliberately comparative rather than claiming a universal numeric tolerance:

```text
RMSE(daily) < RMSE(weekly) < RMSE(monthly)
MAE(daily)  < MAE(weekly)  < MAE(monthly)
```

and, for the committed misspecification fixture,

```text
sigma_g = 0.30, sigma_h = 0.20
```

has materially larger RMSE than the otherwise comparable correctly specified `sigma_g = sigma_h = 0.30` study.

## Interpretation and limitations

M3 demonstrates the Black-Scholes replication mechanism in a model-generated pricing-measure world. It is **not** a historical trading backtest or forecast.

The evidence should be read as:

```text
Black-Scholes assumptions
        ↓
analytic pricing + Delta implication
        ↓
Delta control policy
        ↓
model-generated realized path
        ↓
discrete self-financing hedge outcome
        ↓
replication evidence / assumption stress
```

Current non-claims:

- no physical-measure forecasting claim;
- no real-market execution claim;
- no discrete-dividend or nonzero-continuous-yield hedge accounting;
- no bid/ask spread or market-impact model beyond the optional symmetric proportional stock-trade cost;
- no Heston misspecification until Heston exists on merged `main`;
- no portfolio, VaR/ES, calibration, or market-data infrastructure;
- no optimal policy search: the first policy is prescribed by the Black-Scholes replication argument.

These boundaries make M3 reusable for a later model-risk comparison without pretending that one Delta-hedging study defines a universal stochastic-control framework.
