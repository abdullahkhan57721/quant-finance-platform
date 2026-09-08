# Architecture Index

## Status

This document records durable architecture guardrails for the Quantitative Finance Research & Validation Platform.

M0A establishes the first production finance architecture: a narrow mathematical asset-pricing composition core. The repository still intentionally does **not** define a complete package hierarchy or universal finance framework in advance.

The architecture should grow from real quantitative consumers, subject to the foundational exception in ADR 0001.

## Governing extraction rule

For ordinary application abstractions:

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

### Foundational pricing-semantic exception

ADR 0001 intentionally supersedes that two-consumer rule **only** for the stable mathematical responsibilities of asset pricing:

```text
state / state space / path
stochastic law
model parameter values
financial contract
cash-flow stream
numeraire
physical- and pricing-measure semantics
pricing problem
valuation method
completed valuation result
```

These are represented explicitly because they are mathematically distinct responsibilities of the pricing problem, not because a future second consumer is merely imaginable.

The exception does **not** apply to calibration, risk, market-data architecture, rates curves, portfolios, studies, validation frameworks, native backends, registries, or unrelated domains.

## Mathematical pricing composition

The conceptual pricing problem is

```math
\mathfrak P = (\mathcal X,\mathcal L_\theta,\mathcal C,N,\mathbb Q^N)
```

with theoretical valuation

```math
\Pi_t = N_t E_t^{\mathbb Q^N}\left[
    \sum_i \frac{C_i(X_{[0,\tau_i]})}{N_{\tau_i}}
\right].
```

An analytic or numerical method is separate:

```math
\mathcal A(\mathfrak P) \approx \Pi_t(\mathfrak P).
```

The production architecture therefore preserves:

```text
ModeledState / StateSpace / StatePath
        ↓
StochasticLaw + separate parameter values
        +
FinancialContract → CashFlowStream
        +
Numeraire + PricingMeasureSemantics
        ↓
PricingProblem
        ↓
compatible ValuationMethod
        ↓
ValuationResult
```

### State and state space

`StateSpace[T]` supplies membership semantics. `ModeledState[Time, T]` is an immutable current modeled state plus its state-space semantics. `StatePath[Time, T]` provides point evaluation without requiring a discrete path container.

These contracts do not require a finite-dimensional state space or Markov sufficiency. A concrete modeled-state value may itself contain history/conditioning information when a model requires it.

### Stochastic law and parameter values

`StochasticLaw[State, Parameters]` exposes the state space it governs and parameter compatibility. It does not define every law through `drift()` and `diffusion()`.

The project explicitly protects:

```text
stochastic law structure != parameter values
```

Parameter value objects should be immutable/value-like where appropriate. Calibration may later produce new parameter values; it must not turn calibrated values into a new model type.

### Financial contracts and cash flows

`FinancialContract[Path, Time]` maps a modeled path to a realized immutable `CashFlowStream[Time]`.

The current foundational `CashFlow` contains only:

```text
payment time
amount
```

The contract owns contingent payment semantics, not:

- valuation;
- calibration;
- observed market data;
- trade/portfolio ownership;
- hedging/P&L;
- plotting/presentation;
- numerical algorithms.

A terminal-payoff contract is a specialization of this contract-to-stream responsibility, not a reason to collapse contract and valuation method.

### Numeraire and pricing-measure semantics

`Numeraire[Time]` represents the strictly positive denomination process. Every value consumed through the pricing core must be finite and strictly positive.

The foundational API intentionally does not spread scalar interest-rate assumptions through pricing semantics. M1 may introduce a concrete money-market-account/discounting specialization without making that specialization universal.

`PhysicalMeasureSemantics` and `PricingMeasureSemantics[Time]` are distinct. The latter is associated with a particular numeraire and means that appropriately modeled traded assets denominated by that numeraire are martingales under the supplied pricing measure.

The architecture does **not** provide a generic measure-theory engine or a method that mechanically transforms arbitrary P-dynamics into Q-dynamics. `PricingProblem` receives law structure and parameter values under the relevant pricing-measure semantics explicitly.

### Pricing problem

`PricingProblem` is immutable and answers:

> What financial value is mathematically being asked for?

It composes current modeled state, stochastic-law structure, parameter values, contract, numeraire, pricing measure, and valuation time. It does not choose an algorithm.

### Valuation method and compatibility

`ValuationMethod` answers:

> How will this supported pricing problem be evaluated?

Structural validity and implementation capability are distinct. The canonical `evaluate(problem, method)` path checks `method.supports(problem)` before applying the method and raises `UnsupportedPricingProblem` for unsupported combinations.

This is designed to permit concrete specializations such as:

```text
Black-Scholes closed form
CRR/binomial
Monte Carlo
Heston Fourier
Heston Monte Carlo
```

without treating those algorithms as stochastic models or implying universal support.

### Valuation result

`ValuationResult` is currently only an immutable finite `present_value`.

It is intentionally not a universal container for:

- Greeks;
- Monte Carlo convergence/confidence intervals;
- calibration diagnostics;
- hedging/P&L evidence;
- validation evidence;
- benchmark/performance metadata.

Those receive specific structures when real consumers arrive.

## Protected conceptual distinctions

### Market observations vs valuation state

```text
MarketSnapshot != MarketEnvironment
```

Expected meaning when M4 creates observed-data consumers:

- `MarketSnapshot`: observed/provenance-bearing market information;
- `MarketEnvironment`: valuation-ready interpretation/construction from market inputs.

M0A does not create either merely because future observed-market workflows are foreseeable.

Construction, interpolation, curve building, cleaning, or convention choices must not silently rewrite historical observations.

### Financial contract vs ownership context

```text
FinancialContract != Trade != Portfolio
```

Do not add trade/portfolio fields to contract definitions in anticipation of future XVA or market-risk work.

Introduce `Trade` only when real consumers require ownership/quantity/book/counterparty semantics. Introduce `Portfolio` only when real aggregation behavior exists.

### Model structure vs parameters

```text
stochastic law != model parameters
```

A calibrated parameter set is not a different model type. Calibration should produce parameter evidence/results rather than mutate the conceptual identity of the stochastic law.

### Financial model vs numerical method

```text
stochastic law != ValuationMethod
financial model != numerical method
```

Examples:

```text
GBM / Heston
= stochastic-law/model semantics

closed form / binomial / Monte Carlo / Fourier / PDE
= valuation methods
```

Do not put unrelated valuation algorithms behind a model merely because they can operate on that model.

### Valuation vs calibration vs risk vs validation

```text
StochasticLaw
!= ValuationMethod
!= CalibrationMethod
!= RiskMeasure
!= ValidationMethod
```

These may compose and consume one another, but they do not share one universal responsibility.

Do not create a universal `FinancialModel` joining Black-Scholes, Heston, Monte Carlo, VaR, CVA, calibration, or unrelated quantitative concepts.

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

The current pricing-core dependency direction is deliberately small:

```text
state / cash flows / measures
          ↓
contracts + stochastic-law semantics
          ↓
PricingProblem
          ↓
valuation methods/results
```

Low-level state, cash-flow, contract, measure, and stochastic-law modules must not depend on valuation implementations. `PricingProblem` must not depend on valuation methods. Focused tests enforce this boundary.

Broader future guidance remains:

```text
interfaces / research presentation
              ↓
studies / experiments
              ↓
validation / calibration / local risk analysis
              ↓
valuation methods
              ↓
pricing problems + contract/model semantics
              ↓
valuation-ready market construction when earned
              ↓
market observations / provenance when earned

numerical utilities are used selectively downstream
but must not own finance-domain policy.
```

Guardrails:

- financial contracts must not depend on valuation implementations;
- market observations/environment must not depend on contracts;
- stochastic-law semantics must not own calibration orchestration;
- validation may invoke the capabilities needed to gather independent evidence;
- high-level research/UI code must consume public library behavior rather than duplicate it.

## Market-data and provenance direction

Expected future conceptual flow:

```text
external/raw data
       ↓
normalized observations
       ↓
MarketSnapshot
       ↓
construction / conventions
       ↓
MarketEnvironment / valuation-ready inputs
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
financial semantics
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
- Do not introduce `Backend`, `CppBackend`, compiled-plan registries, or similar native abstractions until a second implementation actually exists and reveals a common responsibility.
- Prefer primitive numeric arrays/scalars across the binding boundary rather than exporting rich Python financial objects into C++.

## M1 specialization pressure

M1 should now specialize M0A rather than inventing a parallel Black-Scholes architecture:

```text
Equity state / path
+
GBM law + Black-Scholes parameters under Q
+
European terminal-payoff contract
+
money-market numeraire
        ↓
PricingProblem
        +
Black-Scholes closed-form ValuationMethod
        ↓
ValuationResult
```

M1 still owns concrete decisions for dates/year fractions, day count, rate/compounding representation, dividend/carry, spot semantics, volatility units, option-right encoding, formula traceability, limits, parity, bounds, and benchmark values.

M0A does not decide those merely because its generic types can carry them.

## Explicit traps

Avoid:

- expanding ADR 0001 into a universal quantitative-finance abstraction policy;
- universal `FinancialModel` inheritance trees;
- god-model objects that price, calibrate, simulate, hedge, plot, and validate themselves;
- forcing all stochastic laws into drift/diffusion;
- generic measure objects that pretend to transform arbitrary dynamics between P and Q;
- scalar-rate assumptions embedded throughout public pricing APIs;
- volatility treated as intrinsic observed-market state rather than model information;
- conflating contracts, trades, positions, and portfolios;
- calibration implemented as `model.calibrate(...)` with hidden objective/optimizer semantics;
- treating Monte Carlo/Fourier/PDE as financial models;
- designing rates, XVA, or market-risk abstractions before those domains have real consumers;
- one giant result object with many optional unrelated fields;
- generic experiment engines before multiple studies reveal shared semantics;
- fake Python/C++ backend architectures before native code exists;
- optimization motivated by intuition rather than profiling evidence.

## ADR policy

Create a dedicated ADR only when a decision is durable, consequential, and difficult to infer from code plus this index.

ADR 0001 is the historical authority for the foundational pricing-semantic exception. Do not rewrite it to hide later changes; supersede it with a new ADR if this architecture materially changes.
