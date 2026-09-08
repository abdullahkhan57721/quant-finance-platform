# Current State

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Quant-Finance Architecture Foundation is complete.**

**M1 — European Options & Black-Scholes Reference Vertical is complete.**

**M2 — Independent Valuation and Sensitivity/Greeks is complete.**

**M3 — Dynamic Hedging / Control is complete.**

**UI1 — Native Quant Research Workbench Architecture & Black-Scholes Vertical Slice is complete and establishes the current desktop architecture.**

ADR 0002 remains the platform-wide mathematical architecture authority. M2 pressure-tested the M0A/M1 pricing boundary with independent numerical methods and established the first concrete production sensitivity family. M3 establishes the first concrete control/dynamic-replication family without introducing a generic stochastic-control or portfolio framework. UI1 adds ADR 0003 for the downstream native PySide6 + Qt Quick/QML boundary without changing the quantitative contracts.

**M4 — Market Evidence / Inverse Problems is active in parallel work.** The next finance model milestone after M3/M4 convergence is M5 — Heston Model and Independent Valuation. The next desktop milestone is UI2, which may consume the actual merged M2 capabilities while preserving the UI1 boundary.

## What exists

The repository now establishes:

- a `src/`-layout Python package with pytest, Ruff, strict Pyright, and GitHub Actions CI;
- the M0A production pricing composition under `qf_platform.pricing`;
- M1 European call/put, Black-Scholes/GBM, ACT/365F, money-market numeraire, and closed-form valuation semantics;
- three valuation methods over the same M1 `PricingProblem`: `BlackScholesClosedForm`, `CoxRossRubinstein`, and `MonteCarloEuropeanOption`;
- method-specific Monte Carlo uncertainty through immutable `MonteCarloValuationResult` without adding optional diagnostics to every valuation result;
- the first concrete sensitivity family under `qf_platform.sensitivity` with explicit Black-Scholes Delta, Gamma, Vega, Theta, and Rho semantics;
- analytic and finite-difference sensitivity methods with explicit variable, derivative-order, units, scaling, and support semantics;
- the first concrete control/dynamic-replication package under `qf_platform.control`;
- exact-transition pricing-measure GBM path simulation with explicit observation grids and RNG ownership;
- a Delta hedge policy that consumes M2 analytic Delta without moving hedge state into sensitivity;
- explicit stock/cash/financing/rebalance/transaction-cost/terminal-payoff accounting;
- immutable path-level hedge evidence and aggregate replication-error summaries;
- distributional evidence for rebalance frequency, volatility misspecification, and proportional transaction costs;
- the native UI1 PySide6 + Qt Quick/QML Workbench vertical over the M1 Black-Scholes analytic method; and
- dedicated desktop validation including QML/offscreen source smoke and one-platform `pyside6-deploy` standalone build/launch proof.

## Mathematical architecture

The platform-wide conceptual pattern remains:

```text
Problem + supported Method -> specific immutable Result
```

For pricing:

```text
same PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
        ↓
ValuationResult or method-specific subtype
```

The M2 correction to the original valuation boundary is deliberately small: `evaluate()` preserves the concrete result subtype produced by a method. `ValuationResult` remains the common immutable present-value contract; Monte Carlo-specific uncertainty lives only on `MonteCarloValuationResult`.

For sensitivity:

```text
BlackScholesSensitivityProblem
        +
supported sensitivity method
        ↓
BlackScholesSensitivityResult
```

with:

```text
AnalyticBlackScholesSensitivity
FiniteDifferenceBlackScholesSensitivity
```

For the first concrete control pressure:

```text
Black-Scholes pricing problem
        +
model-generated path semantics
        +
rebalance schedule
        +
AnalyticDeltaHedgePolicy
        +
stock/cash financing and cost convention
        ↓
DeltaHedgeResult
        ↓
ReplicationErrorSummary
```

This remains concrete. The repository intentionally has no universal `SensitivityProblem`, `ControlProblem`, `Strategy`, `Portfolio`, `Problem`, `Method`, or `Result` hierarchy.

Protect:

```text
pricing problem != sensitivity problem != control / hedging problem
financial model != numerical method != path simulation
GBM stochastic law != Monte Carlo valuation method
simulated states != theoretical price
Delta sensitivity != hedge policy != realized hedge action
replication error != model error by definition
sensitivity != risk by definition
```

Pricing remains upstream of sensitivity; control consumes pricing and sensitivity. Lower layers do not depend back on control.

## M3 dynamic hedging / control

M3 turns Black-Scholes Delta from a static sensitivity into a dynamic policy input while preserving the responsibility boundary:

```text
Delta = dV/dS
        ↓
current-state policy evaluation
        ↓
target stock units
        ↓
explicit rebalance action
        ↓
realized stock/cash hedge trajectory
```

### Path simulation

`BlackScholesPathSimulation` / `simulate_black_scholes_path` sample exact adjacent-date GBM transitions under the configured M1 money-market pricing measure. Each simulation owns an explicit integer seed and creates fresh local Python RNG state.

Because the transition is exact, M3's observation dates are **not** Euler timesteps. The implementation keeps distinct:

```text
path observation grid
!= numerical SDE discretization grid
!= hedge rebalance schedule
```

The first experiments use a daily path-observation grid and vary hedge frequency independently.

### Hedge accounting

The supported first problem is one short European option. Initial hedge wealth equals the hedging-model Black-Scholes present value. The target stock holding at each rebalance is M2 analytic Delta; the residual is held in the existing money-market account.

The implementation records separately:

- option value at hedge dates;
- previous and target stock units;
- signed stock trade and notional;
- financing gain;
- cash before and after rebalance;
- portfolio wealth before and after rebalance;
- optional proportional transaction cost;
- terminal stock and cash holdings;
- terminal option payoff;
- terminal hedge value; and
- replication error.

The local sign convention is:

```text
replication error = terminal hedge value - option payoff
                 = terminal hedged short-option P&L
```

Frictionless rebalancing preserves portfolio wealth at the trade time. With proportional stock-trade cost `kappa`, the explicit cash outflow is `kappa * abs(trade notional)`.

Terminal stock is marked to market rather than silently liquidated, so no hidden terminal liquidation cost is charged.

### Current support boundary

M3 hedge execution requires positive spot/strike/hedging volatility, expiry after valuation, and zero continuous dividend yield. The zero-yield restriction is intentional: nonzero continuous yield requires an explicit dividend/carry cash-flow integration convention between hedge dates, which M3 does not invent silently.

Generating volatility and hedging/pricing volatility are separate values, allowing volatility misspecification without changing the model type or the M2 sensitivity API.

### M3 evidence

Executable evidence establishes:

- seeded exact-transition path reproducibility;
- the zero-volatility deterministic GBM limit;
- exact consumption of M2 analytic Delta;
- frictionless stock/cash self-financing identities;
- explicit transaction-cost accounting and distributional cost drag;
- no-lookahead behavior;
- 64-seed distributional improvement from approximately monthly to weekly to daily rebalancing on a common daily path-observation setup;
- a distinct volatility-misspecification effect when paths are generated at 30% volatility and hedged at 20% rather than the correctly specified 30%;
- rejection of nonzero dividend yield until cash-flow accounting is explicit;
- rejection of mixed aggregate study conditions, duplicate-seed pseudo-replicates, and different observation grids.

`ReplicationErrorSummary` reports mean/median error, standard deviation, MAE, and RMSE while retaining replicate seeds and study configuration. These fields remain control evidence rather than additions to pricing or sensitivity results.

See `docs/models/m3_dynamic_delta_hedging.md` for equations, accounting identities, conventions, limitations, and the executable evidence map.

## Native Workbench boundary

UI1 establishes the downstream desktop direction:

```text
Qt Quick / QML
        ↓
curated PySide6 controller / view-model boundary
        ↓
frontend-neutral application + presentation semantics
        ↓
public mathematical-finance APIs
        ↓
production quantitative core
```

Durable rules:

- finance-domain object graphs do not cross into QML; only curated scalar values, signals/actions, typed item models, and renderer-neutral presentation values do;
- transient QML input state is not authoritative financial state;
- Python normalizes/validates Guided and Advanced inputs into the same immutable M1 composition;
- QML owns no payoff, pricing, day-count, discounting, compatibility, parity, no-arbitrage, or validation semantics;
- the controller privately owns committed `PricingProblem` / `ValuationResult` objects;
- the UI1 analytic evaluation crosses a deliberately small `QThread` worker boundary, establishing responsive ownership without a generic job framework;
- PySide6 is an optional desktop dependency and the canonical core quality gate remains Qt-independent; and
- a dedicated Desktop CI surface validates lint/type checks, architecture tests, QML load/offscreen startup, and a `pyside6-deploy` standalone launch smoke.

The implemented UI1 product proof includes Home/Study navigation, Black-Scholes composition, Guided/Advanced disclosure, a mathematical inspector, authoritative result display, payoff presentation using production contract cash-flow semantics, compatibility/validation evidence, put-call parity evidence, discounted no-arbitrage bounds, and standalone deployment proof.

UI1 deliberately remains an **M1 analytical product vertical** even though M2 and M3 are merged. CRR, Monte Carlo, and sensitivity capabilities are available to later desktop work but are not retroactively exposed by UI1. M3 likewise does not add UI-owned hedge semantics.

See `docs/architecture/native_quant_workbench.md` and ADR 0003.

## M2 valuation capabilities

### Cox-Ross-Rubinstein

`CoxRossRubinstein(steps)` is an explicitly configured valuation method.

M2 distinguishes:

```text
fixed finite steps
    = discrete-time complete-market binomial model
      when 0 < p < 1

increasing steps
    = numerical approximation converging toward
      the continuous Black-Scholes reference
```

A structurally valid Black-Scholes pricing problem may therefore be unsupported by a particular coarse CRR configuration without becoming an invalid pricing problem.

### Monte Carlo

`MonteCarloEuropeanOption(paths, seed)`:

- owns an explicit integer path count and seed;
- constructs a fresh local Python RNG on each application;
- samples the exact Black-Scholes terminal GBM distribution for the supported European payoff;
- discounts sampled payoffs through the pricing problem's numeraire semantics; and
- returns present value, estimator standard error, a normal-approximation 95% confidence interval, path count, and seed.

The confidence interval describes sampling uncertainty, not deterministic equality to Black-Scholes and not financial model error.

## M2 sensitivity capabilities

M2 commits these local Black-Scholes Greek semantics:

```text
Delta = dV/dS
Gamma = d²V/dS²
Vega  = dV/dsigma
Theta = dV/dt
Rho   = dV/dr
```

with:

- Vega reported per `1.00` annualized volatility decimal;
- Rho reported per `1.00` continuously compounded annualized rate decimal;
- Theta defined as valuation time advancing with expiry fixed and reported per ACT/365F model year;
- Gamma explicitly second order; and
- analytic sensitivities limited to the differentiable interior `T>0`, `S>0`, `K>0`, `sigma>0`.

Finite differences use explicit native-unit bumps. Delta, Vega, Theta, and Rho use central first differences; Gamma uses a central second difference. Domain-crossing bumps are unsupported rather than silently clipped or switched to a different scheme.

## Error taxonomy

The accumulated Black-Scholes evidence keeps different error mechanisms separate:

```text
financial model / misspecification effect
CRR discretization / model-approximation error
Monte Carlo valuation sampling error
finite-difference truncation error
finite-difference cancellation / floating-point error
discrete hedge-rebalancing error
stochastic hedge-replicate variation
transaction-cost effect
analytical floating-point error
```

A terminal hedging discrepancy is therefore not automatically "model error." Agreement or disagreement must be interpreted through the mechanism actually varied by the study.

## Observation/model boundary

Observed and modeled quantities remain separate:

```text
real world
    ↓
observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready information

separately from

modeled state + stochastic law + parameters + probability semantics
```

M3 adds only model-generated paths and control evidence. It does not add market-data abstractions. Active M4 work owns provenance-bearing option observations, normalization, and implied-volatility inference.

## Quality and development cadence

The canonical gate remains:

```text
Ruff lint
Ruff format check
strict Pyright
pytest
```

Use `./scripts/fix` after coherent Python batches, focused behavioral/quantitative validation during the inner loop, `./scripts/check_all` at meaningful checkpoints, and full CI on final candidates. Desktop-only dependencies/checks live in the dedicated Desktop workflow rather than the core environment. See `docs/development/validation_cadence.md`.

## Deliberately absent

The following remain absent until later milestones create real consumers:

- generic stochastic-control, trading-strategy, execution, trade, or portfolio frameworks;
- physical-measure forecasting/path semantics for M3;
- nonzero-dividend hedge cash-flow accounting;
- live market-data ingestion and option-observation provenance structures on merged `main` until M4 completes;
- implied-volatility/inverse-problem production structures on merged `main` until M4 completes;
- generic prediction, risk, or validation frameworks;
- market snapshots/environments beyond what future observed-data consumers earn;
- Heston;
- calibration infrastructure beyond future concrete inverse problems;
- native/C++ quantitative backends;
- generic UI schema/form generation, node editors, plugin architecture, or universal background-job infrastructure.

## Next objectives

### M4 — Market Evidence / Inverse Problems

Active PR #27 is establishing provenance-bearing option-market observations and the first concrete inverse problem through implied-volatility inference. Preserve:

```text
observed quote != modeled state != model-implied value
inverse problem != root-finding method
```

M4 owns market observations/provenance/normalization/inference. M3 owns model-generated paths and hedge/control evidence; neither should redefine the other's contracts for convenience.

### M5 — Heston Model and Independent Valuation

After M3 and M4 are both merged and verified, introduce Heston as the first stochastic-volatility law motivated by the observed constant-volatility limitations. Keep Heston stochastic-law semantics distinct from Fourier/Monte Carlo valuation methods. A later M7 comparison may consume M3 hedging evidence to test stochastic-volatility misspecification without rewriting the M3 baseline.

### UI2 — M2 Valuation Comparison and Sensitivity Workbench

Begin from the actual merged M2 public contracts and evidence. The earned next desktop scope is to extend the existing Black-Scholes Study so the user can compare `BlackScholesClosedForm`, `CoxRossRubinstein`, and `MonteCarloEuropeanOption`, inspect method-specific convergence/sampling uncertainty, and inspect the concrete Black-Scholes Greek family with analytic-vs-finite-difference evidence.

UI2 must preserve the UI1 QML boundary, keep compatibility/execution semantics in Python, expose Monte Carlo uncertainty without flattening it into the common valuation result, and avoid inventing a universal method registry, solver schema, sensitivity framework, job system, or future M4/Heston panels.
