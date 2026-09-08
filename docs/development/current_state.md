# Current State

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Quant-Finance Architecture Foundation is complete.**

**M1 — European Options & Black-Scholes Reference Vertical is complete.**

M1 is the first concrete specialization of the M0A pricing architecture. ADR 0002 remains the current platform-wide architectural authority; ADR 0001 remains the historical record for the pricing-specific foundation introduced before the broader mathematical taxonomy was adopted.

The next finance milestone is **M2 — Independent Valuation and Sensitivity/Greeks**.

## What exists

The repository establishes:

- a `src/`-layout Python package;
- pytest, Ruff, and strict Pyright configuration;
- GitHub Actions CI invoking the canonical `./scripts/check_all` quality gate;
- an evidence-based validation cadence in `docs/development/validation_cadence.md`;
- repository-native Issue → branch → early PR → CI → exact-head → squash-merge workflow;
- architecture, quantitative-convention, engineering, provenance, reproducibility/RNG, validation, and future Python/C++ guidance;
- ADR 0002 for the mathematical problem architecture and ADR 0001 for the historical pricing-composition decision;
- the M0A production pricing core under `qf_platform.pricing`; and
- the M1 European-option / Black-Scholes analytical reference specialization.

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

This is architectural, not a universal runtime hierarchy. The repository still intentionally contains no generic production `InverseProblem`, `SensitivityProblem`, `PredictionProblem`, `ControlProblem`, `RiskProblem`, or `ValidationProblem` framework.

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

`BlackScholesClosedForm` is therefore a valuation method for a supported `PricingProblem`; it is not the stochastic model itself.

## M1 concrete capabilities

M1 adds:

- immutable non-negative finite `EquityState(spot)` and `EquityStateSpace`;
- explicit `OptionRight.CALL` / `OptionRight.PUT` semantics;
- immutable `EuropeanOption` terminal contingent cash-flow semantics;
- Actual/365 Fixed calendar-date-to-model-time conversion;
- `FlatMoneyMarketNumeraire` with a finite continuously compounded annualized decimal rate and support for negative rates;
- immutable `BlackScholesParameters` containing annualized decimal volatility and continuous proportional dividend/carry yield;
- `BlackScholesLaw` as the GBM / Black-Scholes law identity, separate from parameter values;
- `BlackScholesClosedForm` as a narrow M0A `ValuationMethod` specialization; and
- formula traceability in `docs/models/black_scholes.md`.

The risk-free accumulation rate is not duplicated inside `BlackScholesParameters`; closed-form valuation obtains risk-free discounting from the pricing problem's numeraire. Continuous proportional dividend/carry remains a model parameter because it enters the concrete equity dynamics and analytical specialization.

## M1 quantitative conventions

M1 commits only the conventions needed by this vertical:

- valuation and expiry are `datetime.date` calendar dates, not datetimes;
- Actual/365 Fixed model time uses actual calendar days divided by exactly 365;
- no business-day adjustment or time-of-day expiry semantics are introduced;
- spot is an explicit modeled spot input, not a forward and not a market-observation/provenance container;
- spot and strike are finite and non-negative, with zero admitted as a degenerate boundary;
- volatility is a finite non-negative annualized decimal standard deviation (`0.20` means 20%);
- the M1 money-market rate is a finite continuously compounded annualized decimal rate; negative rates are allowed;
- dividend/carry is a finite continuously compounded proportional annualized decimal yield;
- completed analytical output continues to use `ValuationResult.present_value` terminology.

These conventions do not create a general rates framework, curve hierarchy, discrete-dividend engine, market snapshot/environment, forward-input API, or trade/portfolio layer.

## M1 quantitative evidence

The executable evidence includes:

- the published one-year benchmark `S=K=100`, `r=5%`, `q=0`, `sigma=20%` with call PV `10.450583572185565` and put PV `5.573526022256971`;
- put-call parity across multiple parameter cases, including a negative-rate case;
- discounted European call/put no-arbitrage bounds;
- expiry intrinsic-value behavior;
- zero-volatility deterministic valuation;
- zero-spot and zero-strike limits;
- continuous-compounding discrimination;
- Actual/365 Fixed leap-day discrimination;
- positive-dividend carry direction;
- input/domain/immutability checks;
- explicit rejection of expired or otherwise unsupported pricing problems through the valuation-method support boundary; and
- dependency-direction tests keeping concrete state/contract/law/parameter/date/numeraire semantics upstream of valuation.

See `docs/models/black_scholes.md` for source references, notation mapping, assumptions, formulas, limits, tolerance rationale, and the executable evidence map.

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

M1's `EquityState.spot` is intentionally valuation-ready modeled state. Real quote provenance and market-data normalization remain future M4 concerns rather than being smuggled into the M1 pricing specialization.

## Quality-tool maturity

The canonical gate remains intentionally lean:

```text
Ruff lint
Ruff format check
strict Pyright
pytest
```

The complete gate is still cheap enough that the repository deliberately does **not** have a second fast/checkpoint command or a draft-fast/final-full CI split. The current development cadence is:

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

`scripts/fix` should be used proactively before broader validation and before CI-triggering pushes after coherent Python changes. CI is confirmation of a checkpoint, not the normal formatting/debug loop. See `docs/development/validation_cadence.md` for the measured rationale, quality-gate classification, and future revisit triggers.

Coverage thresholds, broader import-linter contracts, strict docs builds, benchmark/profile infrastructure, and release smoke checks should still be added only when concrete code gives them meaningful enforcement targets.

## Deliberately absent

The following remain absent from merged project truth until their milestones land:

- CRR/binomial valuation;
- Monte Carlo valuation and sampling-error results;
- Greeks/sensitivity production structures;
- dynamic hedging/control production structures;
- live market-data ingestion and implied-volatility inference;
- calibration/inverse-problem production structures;
- prediction frameworks;
- generic risk or validation frameworks;
- market snapshots/environments;
- trade/portfolio infrastructure;
- Heston;
- native/C++ backends.

## Next objective

Begin **M2 — Independent Valuation and Sensitivity/Greeks** from current `main` after M1 is merged and verified.

M2 should use the *same* M1 financial semantics as the analytical reference while adding genuinely independent methods:

```text
same Black-Scholes PricingProblem
        ↓
BlackScholesClosedForm
CRR / binomial
Monte Carlo
        ↓
cross-method evidence
```

and introduce the first concrete sensitivity pressure:

```text
valuation map F
    ↓
differentiate
    ↓
analytic Greeks ↔ finite-difference Greeks
```

M2 must keep financial model error, tree discretization error, Monte Carlo sampling error, finite-difference truncation/cancellation, and floating-point error distinct. It should not create universal sensitivity, portfolio, risk, calibration, or hedging frameworks before real consumers justify them.
