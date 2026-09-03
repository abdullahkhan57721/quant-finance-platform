# Architecture Index

## Status

This document records durable bootstrap guardrails for the Quantitative Finance Research & Validation Platform. It intentionally does **not** define a complete package hierarchy in advance.

The architecture should grow from real quantitative consumers.

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

A future use case that can merely be imagined is not sufficient justification for an abstraction.

## Protected conceptual distinctions

### Market observations vs valuation state

```text
MarketSnapshot != MarketEnvironment
```

Expected meaning to evaluate when M1/M4 create real consumers:

- `MarketSnapshot`: observed/provenance-bearing market information;
- `MarketEnvironment`: valuation-ready interpretation/construction from market inputs.

Construction, interpolation, curve building, cleaning, or convention choices should not silently rewrite historical observations.

### Financial contract vs ownership context

```text
Instrument != Trade != Portfolio
```

Do not add trade/portfolio fields to instrument definitions in anticipation of future XVA or market-risk work.

Introduce `Trade` only when real consumers require ownership/quantity/book/counterparty or related semantics. Introduce `Portfolio` only when real aggregation behavior exists.

### Model structure vs parameters

```text
model structure != model parameters
```

A calibrated parameter set is not a different model type. Calibration should produce parameter evidence/results rather than mutate the conceptual identity of the stochastic model.

### Financial model vs numerical method

```text
MarketModel != ValuationMethod
financial model != numerical method
```

Examples of the intended distinction:

```text
Heston
= stochastic/financial model

Monte Carlo
Fourier integration
PDE
= numerical valuation/execution methods
```

Do not put unrelated valuation algorithms behind a model merely because they can operate on that model.

### Valuation vs calibration vs risk vs validation

```text
MarketModel
!= ValuationMethod
!= CalibrationMethod
!= RiskMeasure
!= ValidationMethod
```

These may compose and consume one another, but they do not share one universal responsibility.

Do not create a universal `FinancialModel` base class joining Black-Scholes, Heston, Monte Carlo, VaR, CVA, calibration, or unrelated quantitative concepts.

### Calibration problem vs optimizer

```text
calibration problem != numerical optimizer
```

Financial calibration owns questions such as:

- which observations are fitted;
- which model outputs are compared;
- error definition;
- weighting;
- parameter constraints and transforms;
- diagnostics and failure interpretation.

A numerical optimizer owns the search algorithm. Keep these concerns separable when calibration arrives.

### Request/configuration vs committed result

```text
configuration/request != immutable result
```

Prefer immutable result/value objects where practical. Mutable orchestration belongs outside committed results.

### Production library vs research study vs presentation

```text
production library != research study != presentation
```

Notebooks and reports may orchestrate or display stable APIs; they must not be the only implementation of core quantitative logic.

Research studies should become reproducible executions against the production library, with study-specific result structures kept concrete until repetition justifies extraction.

## Dependency direction

Treat this as guidance, not as permission to create empty packages:

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

Guardrails:

- instruments must not depend on valuation implementations;
- market observations/environment must not depend on instruments;
- model semantics must not own calibration orchestration;
- validation may invoke the capabilities needed to gather independent evidence;
- high-level research/UI code must consume public library behavior rather than duplicate it.

## Market-data and provenance direction

Expected conceptual flow:

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

Core tests must not depend on live data services.

Research data should preserve, where licensing permits:

- provider/source;
- as-of timestamp;
- retrieval timestamp;
- raw artifact or content hash;
- normalization/transformation version;
- license/redistribution notes.

If data may not legally be redistributed, commit a reproducible retrieval/processing recipe and deterministic synthetic/curated fixtures instead of copying restricted market data into the repository.

## Reproducibility and RNG

Stochastic calculations must use explicitly owned randomness rather than ambient global state.

Studies should be able to record as applicable:

- seed;
- RNG/bit-generator choice;
- number of paths;
- timestep/discretization configuration;
- valuation/calibration configuration;
- input-data provenance/hash;
- code revision and software environment.

Do not couple future C++ code to NumPy RNG internals merely to make equal integer seeds emit equal streams.

Use two forms of cross-backend evidence when appropriate:

```text
normal stochastic parity
→ statistically equivalent seeded calculations

strict kernel parity
→ same pre-generated numeric/random inputs
   sent to Python and C++ implementations
```

## Validation as architecture

Validation is not a final report-writing step. The platform should make evidence reproducible.

Relevant evidence categories include:

1. **Software correctness** — unit tests, typing, invariants, boundary behavior.
2. **Theoretical/financial correctness** — no-arbitrage identities, bounds, limiting cases.
3. **Numerical correctness** — convergence, stability, error behavior.
4. **Stochastic correctness** — statistical error, confidence intervals, seeded reproducibility.
5. **Cross-method validation** — independent valuation/Greek methods.
6. **Calibration validation** — parameter recovery, residuals, stability, identifiability.
7. **Empirical/out-of-sample validation** — evidence on observations not used to fit the model.
8. **Model-risk evidence** — assumption violations, sensitivities, hedging/P&L effects, failure modes.
9. **Backend parity** — Python/C++ numerical/statistical equivalence.
10. **Performance evidence** — profiling, runtime, memory, scaling.

Independent implementations agreeing are useful evidence but are not automatically proof of conceptual correctness.

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

Rules:

- Python remains the reference/correctness implementation.
- Profile before selecting native work.
- Accelerate measured numerical hotspots rather than rewriting financial orchestration in C++.
- Do not introduce `Backend`, `CppBackend`, `CompiledValuationPlan`, registries, or similar native abstractions until a second implementation actually exists and reveals a common responsibility.
- Prefer primitive numeric arrays/scalars across the binding boundary rather than exporting rich Python financial objects into C++.

## Early hypotheses to evaluate, not yet committed APIs

M1 is expected to test several architectural hypotheses:

- represent contract expiry as a date and make year-fraction/day-count treatment explicit rather than encoding all maturities as anonymous floats;
- represent discounting through a narrow maturity-dependent capability instead of making every API permanently depend on scalar `r`;
- keep volatility/model parameters out of `MarketEnvironment` so competing models can interpret the same market state;
- use immutable domain/result objects where that improves ownership and reproducibility.

These are intentionally not implemented during M0. The first real Black-Scholes consumers should determine the exact contracts.

## Explicit traps

Avoid:

- universal `FinancialModel` inheritance trees;
- god-model objects that price, calibrate, simulate, hedge, plot, and validate themselves;
- scalar-rate assumptions embedded throughout public APIs;
- volatility treated as an intrinsic market-environment field rather than model information;
- conflating instruments, trades, positions, and portfolios;
- calibration implemented as `model.calibrate(...)` with hidden objective/optimizer semantics;
- treating Monte Carlo as a financial model;
- premature universal stochastic-process interfaces, especially assumptions that would later constrain rough/non-Markovian volatility models;
- designing rates, XVA, or market-risk abstractions before those domains have real consumers;
- one giant result object with many optional unrelated fields;
- generic experiment engines before multiple studies reveal shared semantics;
- fake Python/C++ backend architectures before native code exists;
- optimization motivated by intuition rather than profiling evidence.

## ADR policy

Create a dedicated ADR only when a decision is durable, consequential, and difficult to infer from code plus this index.

Do not create ADRs for routine implementation choices or speculative future architecture.
