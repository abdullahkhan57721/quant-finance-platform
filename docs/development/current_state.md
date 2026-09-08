# Current State

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Quant-Finance Architecture Foundation is complete.**

**M1 — European Options & Black-Scholes Reference Vertical is complete.**

**M2 — Independent Valuation and Sensitivity/Greeks is complete.**

**UI1 — Native Quant Research Workbench Architecture & Black-Scholes Vertical Slice is complete and establishes the current desktop architecture.**

ADR 0002 remains the platform-wide mathematical architecture authority. M2 pressure-tested the M0A/M1 pricing boundary with independent numerical methods and established the first concrete production sensitivity family. UI1 adds ADR 0003 for the downstream native PySide6 + Qt Quick/QML boundary without changing the quantitative contracts.

The next finance milestones are **M3 — Dynamic Hedging / Control** and **M4 — Market Evidence / Inverse Problems**. The next desktop milestone is **UI2**, which may now consume the actual merged M2 capabilities while preserving the UI1 boundary.

## What exists

The repository now establishes:

- a `src/`-layout Python package with pytest, Ruff, strict Pyright, and GitHub Actions CI;
- the M0A production pricing composition under `qf_platform.pricing`;
- M1 European call/put, Black-Scholes/GBM, ACT/365F, money-market numeraire, and closed-form valuation semantics;
- three valuation methods over the same M1 `PricingProblem`: `BlackScholesClosedForm`, `CoxRossRubinstein`, and `MonteCarloEuropeanOption`;
- method-specific Monte Carlo uncertainty through immutable `MonteCarloValuationResult` without adding optional diagnostics to every valuation result;
- the first concrete sensitivity family under `qf_platform.sensitivity` with explicit Black-Scholes Delta, Gamma, Vega, Theta, and Rho semantics;
- analytic and finite-difference sensitivity methods with explicit variable, derivative-order, units, scaling, and support semantics;
- cross-method convergence, stochastic-uncertainty, and finite-difference stability evidence;
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

This is a concrete Black-Scholes specialization, not a generic sensitivity engine. The repository still intentionally has no universal `SensitivityProblem`, `Problem`, `Method`, or `Result` hierarchy.

Protect:

```text
pricing problem != sensitivity problem
financial model != numerical method
GBM stochastic law != Monte Carlo valuation method
simulated states != theoretical price
sensitivity problem != differentiation method
analytic Greek != finite-difference algorithm
sensitivity != risk by definition
```

Pricing remains upstream of sensitivity; focused dependency tests prevent `qf_platform.pricing` from depending back on `qf_platform.sensitivity`.

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

UI1 deliberately remains an **M1 analytical product vertical** even though M2 is now merged. CRR, Monte Carlo, and sensitivity capabilities are available to later desktop work but are not retroactively exposed by UI1.

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

## M2 quantitative evidence

Executable evidence establishes:

- CRR convergence toward the M1 Black-Scholes analytical value as the tree is refined;
- explicit rejection of CRR configurations violating the finite-step no-arbitrage probability condition;
- seeded Monte Carlo reproducibility;
- Black-Scholes analytical values consistent with reported Monte Carlo sampling uncertainty;
- approximate `O(n^-1/2)` Monte Carlo standard-error scaling;
- analytic call/put Delta, Gamma, Vega, Theta, and Rho reference values;
- analytic-vs-finite-difference cross-validation for every supported Greek;
- a multi-bump Gamma study demonstrating truncation-to-cancellation tradeoffs; and
- pricing-to-sensitivity dependency direction.

See `docs/models/m2_numerical_methods_and_sensitivities.md` for formulas, method interpretations, error taxonomy, and the executable evidence map.

## Error taxonomy

M2 keeps these mechanisms distinct:

```text
financial model error
CRR discretization / model-approximation error
Monte Carlo sampling error
finite-difference truncation error
finite-difference cancellation / floating-point error
analytical floating-point error
```

Agreement or disagreement between methods must be interpreted through the relevant mechanism rather than one universal tolerance.

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

M2 adds no market-data abstraction. M4 is the first planned consumer that should create provenance-bearing option observations and a narrow implied-volatility inverse problem.

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

- dynamic hedging/control production structures;
- live market-data ingestion and option-observation provenance structures;
- implied-volatility/inverse-problem production structures;
- generic prediction, risk, or validation frameworks;
- market snapshots/environments beyond what future observed-data consumers earn;
- trade/portfolio infrastructure;
- Heston;
- calibration infrastructure beyond future concrete inverse problems;
- native/C++ quantitative backends;
- generic UI schema/form generation, node editors, plugin architecture, or universal background-job infrastructure.

## Next objectives

### M3 — Dynamic Hedging / Control

Use merged M2 pricing and Delta semantics to test dynamic replication under explicit path, rebalance, transaction-cost, and misspecification assumptions. Keep the control question separate from pricing and sensitivity.

### M4 — Market Evidence / Inverse Problems

Establish provenance-bearing option-market observations and the first concrete inverse problem through implied-volatility inference. Preserve:

```text
observed quote != modeled state != model-implied value
inverse problem != root-finding method
```

M3 and M4 may proceed in parallel provided neither redefines the merged M2 pricing/sensitivity contracts and shared documentation/application files are coordinated.

### UI2 — M2 Valuation Comparison and Sensitivity Workbench

Begin from the actual merged M2 public contracts and evidence. The earned next desktop scope is to extend the existing Black-Scholes Study so the user can compare `BlackScholesClosedForm`, `CoxRossRubinstein`, and `MonteCarloEuropeanOption`, inspect method-specific convergence/sampling uncertainty, and inspect the concrete Black-Scholes Greek family with analytic-vs-finite-difference evidence.

UI2 must preserve the UI1 QML boundary, keep compatibility/execution semantics in Python, expose Monte Carlo uncertainty without flattening it into the common valuation result, and avoid inventing a universal method registry, solver schema, sensitivity framework, job system, or future M3/M4 panels.