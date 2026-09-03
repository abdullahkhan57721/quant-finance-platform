# Architecture Index

## Status

This document records durable architecture guardrails for the Quantitative Finance
Research & Validation Platform. M1 has supplied the first concrete finance boundaries;
it still intentionally does **not** define a complete package hierarchy in advance.

The architecture should continue to grow from real quantitative consumers.

## Governing extraction rule

```text
one consumer
→ keep concrete/local

two real consumers
→ compare semantics

same responsibility
→ consider extracting shared abstraction

different responsibility
→ keep separate
```

A future use case that can merely be imagined is not sufficient justification for an
abstraction.

## Protected conceptual distinctions

### Market observations vs valuation state

```text
MarketSnapshot != MarketEnvironment
```

M1 establishes `MarketEnvironment` as valuation-ready state. It owns an explicit
valuation date, spot, and deterministic discounting capabilities required by the first
valuation consumer. M1 does not create `MarketSnapshot` because there is no observed,
provenance-bearing market-data consumer yet.

When M4 introduces observations, expected meaning remains:

- `MarketSnapshot`: observed/provenance-bearing market information;
- `MarketEnvironment`: valuation-ready interpretation/construction from market inputs.

Construction, interpolation, cleaning, or convention choices must not silently rewrite
historical observations.

### Financial contract vs ownership context

```text
Instrument != Trade != Portfolio
```

M1 `EuropeanOption` contains only contract semantics: expiry, strike, and exercise
right. Do not add quantity, book, counterparty, or portfolio fields until real ownership
or aggregation consumers exist.

### Model structure vs parameters

```text
model structure != model parameters
```

M1 makes this distinction concretely: `BlackScholesParameters` owns annualized
volatility, while the model structure/assumptions are expressed by the concrete
Black-Scholes valuation implementation and mathematical traceability documentation.
A ceremonial `BlackScholesModel` object was not required.

A calibrated parameter set is not a different model type. Calibration should later
produce parameter evidence/results rather than mutate conceptual model identity.

### Financial model vs numerical method

```text
MarketModel != ValuationMethod
financial model != numerical method
```

Black-Scholes provides financial/model assumptions and an analytical reference result.
Future CRR, Monte Carlo, Fourier, or PDE algorithms must not be mislabeled as financial
models merely because they can value claims under a model.

Do not create a universal `FinancialModel` base class joining Black-Scholes, Heston,
Monte Carlo, VaR, CVA, calibration, or unrelated concepts.

### Valuation vs calibration vs risk vs validation

```text
MarketModel
!= ValuationMethod
!= CalibrationMethod
!= RiskMeasure
!= ValidationMethod
```

M1 keeps theoretical validation as executable tests and traceability documentation;
there is not yet a repeated runtime validation responsibility that warrants a generic
validation interface.

### Calibration problem vs optimizer

```text
calibration problem != numerical optimizer
```

Financial calibration owns fitted observations, model outputs, errors, weights,
constraints/transforms, and diagnostics. A numerical optimizer owns search. Keep these
separate when calibration arrives.

### Request/configuration vs committed result

```text
configuration/request != immutable result
```

M1 inputs are immutable value objects. Its only completed valuation output is one
scalar present value, so no generic `ValuationResult` exists yet. Reconsider a result
contract only when later consumers require shared result metadata/evidence.

### Production library vs research study vs presentation

```text
production library != research study != presentation
```

Notebooks, reports, and future UI may orchestrate or display stable APIs; they must not
be the only implementation of core quantitative logic.

## M1 concrete dependency shape

```text
EuropeanOption      BlackScholesParameters
        \              /
         \            /
          valuation method
                ↑
        MarketEnvironment
                ↑
    DiscountFactorProvider
                ↑
 FlatContinuousDiscountCurve
```

Important interpretation:

- instruments do not depend on valuation;
- market state does not depend on instruments;
- volatility/model parameters do not live in `MarketEnvironment`;
- `DiscountFactorProvider` is narrow maturity-dependent valuation input, not a general
  rates framework;
- risk-free and dividend/carry inputs share a discount-factor responsibility but retain
  distinct economic roles;
- valuation owns no hidden mutable state or cache.

## Broader dependency direction

Treat this as guidance, not permission to create empty packages:

```text
interfaces / research presentation
              ↓
studies / experiments
              ↓
validation / calibration / local risk analysis
              ↓
valuation
              ↓
instruments + model semantics
              ↓
valuation-ready market environment
              ↓
market observations / provenance

numerical utilities are used selectively by valuation,
calibration, and studies but must not own finance-domain policy.
```

## Market-data and provenance direction

Expected later flow:

```text
external/raw data
       ↓
normalized observations
       ↓
MarketSnapshot
       ↓
construction / conventions
       ↓
MarketEnvironment
```

Core tests must not depend on live data services. Research data should preserve source,
as-of/retrieval timestamps, hashes, transformation version, and licensing information
where applicable and legally permitted.

## Reproducibility and RNG

Stochastic calculations must use explicitly owned randomness rather than ambient global
state. Studies should record seed/RNG choice, paths/discretization, numerical/model
configuration, data provenance, and code/software revision as applicable.

Do not couple future C++ code to NumPy RNG internals merely to make equal integer seeds
emit equal streams. For strict kernel parity, feed the same pre-generated numerical
inputs to both implementations.

## Validation as architecture

Validation is not a final report-writing step. Relevant evidence categories include:

1. software correctness;
2. theoretical/no-arbitrage correctness;
3. numerical convergence/stability;
4. stochastic/statistical correctness;
5. cross-method validation;
6. calibration recovery/stability/identifiability;
7. empirical/out-of-sample validation;
8. model-risk evidence;
9. backend parity;
10. performance evidence.

M1 concretely supplies the first two through domain tests, a published benchmark,
put-call parity, no-arbitrage bounds, limiting cases, and convention-discriminating
tests. Independent implementations agreeing are useful but are not automatically proof
of conceptual correctness.

Every nontrivial numerical tolerance should have a documented rationale.

## Python/C++ execution boundary

Long-term target:

```text
Python
────────────────────────
financial objects
market data
configuration
calibration orchestration
research
validation
presentation

        ↓

narrow numerical boundary

        ↓

Python reference kernel
        OR
C++ accelerated kernel
```

Python remains the reference/correctness implementation. Profile before selecting
native work. Do not introduce backend registries or C++ abstractions until a second real
implementation and measured hotspot reveal a common responsibility.

## Explicit traps

Avoid:

- universal `FinancialModel` inheritance trees;
- god-model objects that price, calibrate, simulate, hedge, plot, and validate;
- scalar-rate assumptions embedded throughout public APIs;
- treating the concrete flat continuous curve as a universal interest-rate model;
- volatility treated as an intrinsic market-environment field;
- conflating instruments, trades, positions, and portfolios;
- calibration implemented as `model.calibrate(...)` with hidden optimizer semantics;
- treating Monte Carlo as a financial model;
- premature universal stochastic-process interfaces;
- designing rates, XVA, or market-risk abstractions before real consumers;
- one giant result object with many optional unrelated fields;
- generic experiment engines before multiple studies reveal shared semantics;
- fake Python/C++ backend architectures before native code exists;
- optimization motivated by intuition rather than profiling evidence.

## ADR policy

Create a dedicated ADR only when a decision is durable, consequential, and difficult to
infer from code plus this index and the quantitative-convention register.

M1 required no ADR: its date, discounting, parameter-ownership, and result-scope
rationale is recoverable from the concrete contracts, this index,
`docs/quantitative_conventions.md`, Issue #5, and the Black-Scholes model note.
