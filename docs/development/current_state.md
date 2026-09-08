# Current State

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Quant-Finance Architecture Foundation is complete.**

**M1 — European Options & Black-Scholes Reference Vertical is complete.**

**UI1 — Native Quant Research Workbench Architecture & Black-Scholes Vertical Slice is complete on its milestone branch and is the current desktop architecture once merged.**

M1 is the first concrete specialization of the M0A pricing architecture. ADR 0002 remains the platform-wide mathematical architecture authority; ADR 0001 remains the historical pricing-composition record. UI1 adds ADR 0003 for the native desktop boundary without changing M0A/M1 quantitative contracts.

The next finance milestone remains **M2 — Independent Valuation and Sensitivity/Greeks**. M2 may proceed independently of the UI track. Later desktop work must consume only quantitative capabilities that have actually merged to `main`.

## What exists

The repository establishes:

- a `src/`-layout Python package;
- pytest, Ruff, and strict Pyright configuration;
- GitHub Actions CI invoking the canonical `./scripts/check_all` quality gate;
- an evidence-based validation cadence in `docs/development/validation_cadence.md`;
- repository-native Issue → branch → early PR → CI → exact-head → squash-merge workflow;
- architecture, quantitative-convention, engineering, provenance, reproducibility/RNG, validation, and future Python/C++ guidance;
- ADR 0002 for the mathematical problem architecture and ADR 0001 for the historical pricing-composition decision;
- the M0A production pricing core under `qf_platform.pricing`;
- the M1 European-option / Black-Scholes analytical reference specialization; and
- the UI1 native PySide6 + Qt Quick/QML Workbench vertical, documented in `docs/architecture/native_quant_workbench.md` and ADR 0003.

## Platform-wide mathematical architecture

M0A establishes the durable taxonomy:

```text
FINANCIAL / MATHEMATICAL FOUNDATIONS

state / state space
stochastic law
model parameters
probability semantics
physical measure P
pricing measure Q^N
numeraire N
market observations + provenance
financial contracts
cash flows
quantitative conventions

        ↓

PROBLEM FAMILIES

forward / pricing
inverse / inference
sensitivity
prediction
control / optimization
risk
validation

        ↓

SOLUTION METHODS

analytic / tree / Monte Carlo / Fourier / finite difference
root finding / optimization / filtering / regression / scenario methods / tests

        ↓

SPECIFIC IMMUTABLE RESULTS / EVIDENCE
```

The platform-wide conceptual pattern remains:

```text
Problem + supported Method -> specific immutable Result
```

This is architectural, not a universal runtime hierarchy. The repository still intentionally contains no generic production `InverseProblem`, `PredictionProblem`, `ControlProblem`, `RiskProblem`, or `ValidationProblem` framework. Sensitivity remains absent from merged truth until M2 lands.

## Implemented pricing boundary

The production pricing core remains:

```text
state space / modeled state / state path
        +
stochastic law + separate parameter values
        +
financial contract → immutable cash-flow stream
        +
strictly-positive numeraire
        +
physical vs numeraire-associated pricing-measure semantics
        ↓
immutable PricingProblem
        +
compatible ValuationMethod
        ↓
immutable ValuationResult(present_value)
```

M1 specializes that composition without bypassing it:

```text
EquityState / EquityStateSpace
+
BlackScholesLaw + BlackScholesParameters
+
EuropeanOption → terminal CashFlowStream
+
FlatMoneyMarketNumeraire + PricingMeasureSemantics
        ↓
PricingProblem
        +
BlackScholesClosedForm
        ↓
ValuationResult(present_value)
```

The important responsibility split is preserved:

```text
state
!= stochastic law
!= model parameter values
!= contract
!= cash flows
!= numeraire
!= pricing-measure semantics
!= valuation method
!= valuation result
```

`BlackScholesClosedForm` is a valuation method for a supported `PricingProblem`; it is not the stochastic model itself.

## Native Workbench boundary

UI1 adds a downstream desktop product layer:

```text
Qt Quick / QML
        ↓
curated PySide6 controller / view-model boundary
        ↓
frontend-neutral application + presentation semantics
        ↓
M0A/M1 public mathematical-finance APIs
        ↓
production quantitative core
```

Durable rules:

- finance-domain object graphs do not cross into QML; only curated scalar values, signals/actions, list models, and renderer-neutral presentation values do;
- transient QML input state is not authoritative financial state;
- Python normalizes/validates Guided and Advanced inputs into the same immutable M1 composition;
- QML owns no payoff, Black-Scholes, day-count, discounting, compatibility, parity, no-arbitrage, or validation semantics;
- the controller privately owns committed `PricingProblem` / `ValuationResult` objects;
- the M1 evaluation call crosses a deliberately small `QThread` worker boundary, establishing responsive ownership without a generic job framework;
- PySide6 is an optional desktop dependency and the canonical core quality gate remains Qt-independent; and
- a dedicated Desktop CI surface validates typing/linting, architecture tests, QML load/offscreen startup, and a `pyside6-deploy` standalone artifact launch smoke.

The implemented UI1 product proof includes Home/Study navigation, Black-Scholes composition, Guided/Advanced disclosure, a mathematical inspector, authoritative result display, payoff presentation using production contract cash-flow semantics, compatibility/validation evidence, put-call parity evidence, discounted no-arbitrage bounds, and standalone deployment proof.

## M1 concrete capabilities and conventions

M1 provides:

- immutable non-negative finite `EquityState(spot)` and `EquityStateSpace`;
- explicit `OptionRight.CALL` / `OptionRight.PUT` semantics;
- immutable `EuropeanOption` terminal contingent cash-flow semantics;
- `datetime.date` valuation/expiry with Actual/365 Fixed model time;
- `FlatMoneyMarketNumeraire` with a finite continuously compounded annualized decimal rate, including negative rates;
- immutable `BlackScholesParameters` containing annualized decimal volatility and continuous proportional dividend/carry yield;
- `BlackScholesLaw` as the GBM / Black-Scholes law identity, separate from parameter values;
- `BlackScholesClosedForm` as a narrow M0A `ValuationMethod`; and
- formula traceability in `docs/models/black_scholes.md`.

The risk-free accumulation rate is not duplicated inside `BlackScholesParameters`; discounting comes from the pricing problem's numeraire. Continuous proportional dividend/carry remains a model parameter because it enters the concrete equity dynamics and analytical specialization.

M1 does not create business-day/time-of-day expiry semantics, a general rates framework, curve hierarchy, discrete-dividend engine, market snapshot/environment, forward-input API, or trade/portfolio layer.

## M1 quantitative evidence

Executable evidence includes:

- the published one-year benchmark `S=K=100`, `r=5%`, `q=0`, `sigma=20%` with call PV `10.450583572185565` and put PV `5.573526022256971`;
- put-call parity across multiple parameter cases, including a negative-rate case;
- discounted European call/put no-arbitrage bounds;
- expiry intrinsic-value behavior;
- zero-volatility deterministic valuation;
- zero-spot and zero-strike limits;
- continuous-compounding and Actual/365 Fixed convention discrimination;
- positive-dividend carry direction;
- input/domain/immutability checks; and
- explicit rejection of unsupported pricing problems through the method support boundary.

See `docs/models/black_scholes.md` for references, notation, assumptions, formulas, limits, tolerance rationale, and the executable evidence map.

## Observation/model boundary

Observed and modeled quantities remain conceptually separate:

```text
real world
    ↓
observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready information
```

separately from:

```text
modeled state
+
stochastic law
+
parameter values
+
probability semantics
```

M1's `EquityState.spot` is valuation-ready modeled state. Real quote provenance and market-data normalization remain future M4 concerns.

## Quality-tool maturity

The canonical gate remains intentionally lean:

```text
Ruff lint
Ruff format check
strict Pyright
pytest
```

The development cadence is:

```text
coherent implementation batch
        ↓
./scripts/fix
        ↓
focused behavioral / quantitative validation
        ↓
./scripts/check_all at a meaningful checkpoint
        ↓
full CI for pushed candidates
        ↓
ticket-specific final quantitative/manual evidence
        ↓
exact-head review → squash merge → verify main
```

Desktop-only dependencies and checks live in the dedicated Desktop CI surface rather than bloating `./scripts/check_all` for core-only development. See `docs/development/validation_cadence.md` for the measured rationale and revisit triggers.

## Deliberately absent

Until their own milestones merge, project truth still excludes:

- CRR/binomial valuation;
- Monte Carlo valuation and sampling-error results;
- Greeks/sensitivity production structures;
- dynamic hedging/control production structures;
- live market-data ingestion and implied-volatility inference;
- calibration/inverse-problem production structures;
- generic risk or validation frameworks;
- market snapshots/environments;
- trade/portfolio infrastructure;
- Heston;
- native/C++ quantitative backends; and
- generic UI schema/form generation, node editors, plugin architecture, or universal background-job infrastructure.

## Next objectives

The finance track proceeds with **M2 — Independent Valuation and Sensitivity/Greeks** from current `main`.

The desktop track proceeds only from merged quantitative truth. UI2 must inspect the actual merged M2 public contracts, tests, and evidence before deciding which additional methods, sensitivity views, compatibility semantics, or execution/result presentation are justified. It must not pre-build CRR, Monte Carlo, or Greek panels while M2 remains unmerged.
