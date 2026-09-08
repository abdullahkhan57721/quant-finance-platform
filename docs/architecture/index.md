# Architecture Index

## Status

This document records durable architecture guardrails for the Quantitative Finance Research & Validation Platform.

M0A establishes two things:

1. a production mathematical asset-pricing composition core; and
2. a platform-wide mathematical taxonomy for organizing future quantitative problems without pre-building their operational frameworks.

ADR 0002 is the current authority for this doctrine. ADR 0001 remains the historical record for the pricing-specific foundation that was implemented first.

The repository still intentionally does **not** define a complete package hierarchy or universal finance framework in advance.

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

A future use case that can merely be imagined is not sufficient justification for an operational abstraction.

### Foundational mathematical exception

ADR 0002 supersedes the pricing-only formulation of the exception.

Foundational mathematical domain distinctions may be represented explicitly from the outset when their distinctness follows from the mathematical question itself rather than from speculative software reuse.

This does **not** authorize generic runtime frameworks for every named problem family.

The durable doctrine is:

```text
Foundational mathematical domain distinctions
may be represented explicitly from the outset.

Problem-specific software frameworks
should remain narrow and evidence-driven.

Mathematical generality
does not imply
universal operational APIs.
```

## Mathematical taxonomy

The platform is organized conceptually as:

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

analytic
lattice / tree
Monte Carlo
Fourier
finite difference / PDE
root finding
optimization
regression / filtering
scenario generation
statistical tests
and other problem-appropriate algorithms

        ↓

SPECIFIC IMMUTABLE RESULTS / EVIDENCE
```

This is a mathematical responsibility map, not a required software inheritance tree.

## Problem → Method → Result

Across problem families, use the conceptual pattern:

```text
Problem
   +
supported Method
   ↓
specific immutable Result
```

A **Problem** states the quantitative question and the domain semantics required to make it well-defined.

A **Method** states how a supported instance of that problem is solved or approximated.

A **Result** records the committed output/evidence of the execution.

Do not create universal `Problem`, `Method`, or `Result` base classes merely because this conceptual pattern is shared. Shared software behavior must still be demonstrated by real consumers.

Protect:

```text
problem != solution method
request/configuration != immutable result
```

## Problem families

### Forward / pricing

A pricing problem asks for financial value under specified contract, model, numeraire, and pricing-measure semantics.

The foundational pricing problem is:

```math
\mathfrak P_{\mathrm{price}}
=
(\mathcal X,\mathcal L_\theta,\mathcal C,N,\mathbb Q^N)
```

with theoretical valuation:

```math
\Pi_t
=
N_t E_t^{\mathbb Q^N}\left[
    \sum_i \frac{C_i(X_{[0,\tau_i]})}{N_{\tau_i}}
\right].
```

An analytic or numerical method is separate:

```math
\mathcal A(\mathfrak P_{\mathrm{price}})
\approx
\Pi_t.
```

The production `PricingProblem`, `ValuationMethod`, and `ValuationResult` contracts implement this family today.

Protect:

```text
pricing problem != valuation method
stochastic law != valuation method
contract != pricing model
```

### Inverse / inference

An inverse problem asks which latent quantities make a model consistent, in an explicit sense, with observations or target quantities.

Conceptually:

```text
observations / targets
+
model structure
+
parameter/state domain
+
comparison / error semantics
+
constraints
        ↓
inference question
```

Examples include implied-volatility inversion, parameter calibration, filtering, and state estimation.

Protect:

```text
inverse problem != optimizer / root finder
observations != inferred parameters
model structure != fitted parameter values
```

An optimizer or root finder is a solution method. It does not own the financial meaning of the inverse problem.

No generic production `InverseProblem` framework exists yet.

### Sensitivity

A sensitivity problem asks how a specified quantitative output changes under selected perturbations of states, inputs, parameters, or conventions.

The perturbation may be differential, finite, directional, pathwise, functional, or otherwise explicitly defined.

Protect:

```text
sensitivity problem != differentiation method
analytic Greek != finite-difference algorithm
sensitivity != risk by definition
```

Risk workflows may consume sensitivities, but local response and loss/exposure are not the same responsibility.

No generic production `SensitivityProblem` framework exists yet.

### Prediction

A prediction problem asks for a future quantity or distribution conditional on specified information under explicit probability semantics.

Conceptually:

```text
conditioning information
+
stochastic law / parameters
+
probability semantics
+
horizon / target
        ↓
predictive distribution or forecast
```

Prediction is not automatically pricing. Physical-measure forecasting and pricing-measure valuation answer different questions even when they share state variables or stochastic structures.

Protect:

```text
prediction problem != pricing problem
physical measure P != pricing measure Q^N
forecast target != financial contract
```

No generic production `PredictionProblem` framework exists yet.

### Control / optimization

A control problem asks which admissible action, policy, hedge, allocation, or stopping rule best achieves a stated objective subject to dynamics and constraints.

Conceptually:

```text
state / dynamics
+
admissible controls
+
objective functional
+
constraints
        ↓
optimal-control question
```

Protect:

```text
control problem != optimizer
objective/constraints != search algorithm
policy/result != mutable solver state
```

Dynamic programming, stochastic control, mathematical programming, or other optimizers are methods for concrete control problems.

No generic production `ControlProblem` framework exists yet.

### Risk

A risk problem asks for a specified characterization of loss, exposure, uncertainty, or adverse outcomes for a defined financial object, horizon, scenario/probability semantics, and conditioning information.

Conceptually:

```text
position / exposed quantity
+
state / market information
+
horizon
+
probability or scenario semantics
+
loss/exposure definition
        ↓
risk question
```

Protect:

```text
risk problem != risk-measure implementation
risk measure != stochastic law
risk result != trade / portfolio by definition
```

VaR, expected shortfall, stress loss, exposure profiles, and sensitivity-based approximations may eventually be distinct concrete questions/methods. This architecture does not force them into one engine.

No generic production `RiskProblem` framework exists yet.

### Validation

A validation problem asks whether a specified model, implementation, method, result, calibration, or empirical claim satisfies explicit criteria and what evidence supports that conclusion.

Conceptually:

```text
object / claim under review
+
validation criteria
+
reference / independent evidence
+
tolerances or statistical decision semantics
        ↓
validation question
```

Protect:

```text
validation problem != validation method
validation evidence != model output itself
self-agreement != independent validation
```

Validation may invoke pricing, inference, sensitivity, prediction, control, or risk capabilities to gather evidence. That orchestration does not make those responsibilities one framework.

No generic production `ValidationProblem` framework exists yet.

## Observations and model boundary

Observed information and modeled quantities remain distinguishable even when both are represented by similar numeric objects.

Real-world information flows conceptually as:

```text
real world
    ↓
observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready information
```

Separately, model semantics are composed from:

```text
modeled state
+
stochastic law
+
parameter values
+
probability semantics
```

A specific problem may combine problem-ready observed information with model semantics when required.

Protect:

```text
market observation != modeled state
observed quote != model-implied quantity
raw observation != normalized input
normalization != calibration / inference
```

Construction, interpolation, cleaning, convention application, or model fitting must not silently rewrite historical observations.

The expected later market-data distinction remains:

```text
MarketSnapshot != MarketEnvironment
```

- `MarketSnapshot`: provenance-bearing observations;
- `MarketEnvironment`: valuation/problem-ready interpretation or construction.

M0A creates neither merely because future observed-market workflows are foreseeable.

## Production pricing composition

The implemented pricing architecture preserves:

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

Protect:

```text
stochastic law structure != parameter values
```

Parameter value objects should be immutable/value-like where appropriate. Calibration/inference may later produce new parameter values; it must not turn fitted values into a new model type.

### Financial contracts and cash flows

`FinancialContract` maps a modeled path to a realized immutable `CashFlowStream`.

The current foundational `CashFlow` contains only:

```text
payment time
amount
```

The contract owns contingent payment semantics, not valuation, inference/calibration, observed market data, trade/portfolio ownership, hedging/P&L, plotting/presentation, or numerical algorithms.

A terminal-payoff contract is a specialization of contract-to-stream responsibility, not a reason to collapse contract and valuation method.

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

Concrete specializations may include:

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

It is intentionally not a universal container for Greeks, Monte Carlo diagnostics/confidence intervals, calibration diagnostics, hedging/P&L evidence, validation evidence, or benchmark/performance metadata.

Those receive specific result structures when real consumers arrive.

## Additional protected distinctions

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

A calibrated parameter set is not a different model type. Calibration/inference should produce parameter evidence/results rather than mutate the conceptual identity of the stochastic law.

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

### Inverse problem vs optimizer

```text
inverse / calibration problem != numerical optimizer
```

Financial inference owns which observations/targets are fitted, what comparison/error is defined, parameter/state domains and constraints, weighting, and diagnostics/failure interpretation.

A numerical optimizer/root finder owns the search algorithm.

### Request/configuration vs committed result

```text
configuration/request != immutable result
```

Prefer immutable result/value objects where practical. Mutable orchestration, solver state, caches, and work buffers belong outside committed results.

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

The broader conceptual dependency direction is:

```text
observations/provenance ──→ normalization / problem-ready information

modeled state / stochastic law / parameters / probability semantics
financial contracts / cash flows / numeraires / conventions
                         ↓
                 specific Problem
                         ↓
                  supported Method
                         ↓
              specific immutable Result
                         ↓
          validation / research / presentation
```

This is guidance, not a mandated package tree.

Guardrails:

- financial contracts must not depend on valuation implementations;
- market observations/environment must not depend on contracts;
- stochastic-law semantics must not own inference/calibration orchestration;
- numerical utilities may be used by methods but must not own finance-domain policy;
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
problem-ready inputs / MarketEnvironment where earned
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
- pricing/inference/risk/control configuration;
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

Validation is a problem family and not merely a final report-writing step. The platform should make evidence reproducible.

Relevant evidence categories include:

1. **Software correctness** — unit tests, typing, invariants, boundary behavior.
2. **Theoretical/financial correctness** — no-arbitrage identities, bounds, limiting cases.
3. **Numerical correctness** — convergence, stability, error behavior.
4. **Stochastic correctness** — statistical error, confidence intervals, seeded reproducibility.
5. **Cross-method validation** — independent valuation/sensitivity methods.
6. **Inference/calibration validation** — parameter recovery, residuals, stability, identifiability.
7. **Empirical/out-of-sample validation** — evidence on observations not used to fit the model.
8. **Model-risk evidence** — assumption violations, sensitivities, hedging/P&L effects, failure modes.
9. **Backend parity** — Python/C++ numerical/statistical equivalence.
10. **Performance evidence** — profiling, runtime, memory, scaling.

Independent implementations agreeing are useful evidence but are not automatically proof of conceptual correctness.

Every nontrivial numerical tolerance should have a documented rationale.

Do not create a generic validation engine before concrete validation workflows reveal stable shared behavior.

## Python/C++ execution boundary

Long-term target:

```text
Python
────────────────────────
financial semantics
market data
configuration
inference/calibration orchestration
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

M1 specializes the existing pricing problem family; it does not need to implement the other six families.

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
        ↓
theoretical validation evidence
```

M1 owns concrete decisions for dates/year fractions, day count, rate/compounding representation, dividend/carry, spot semantics, volatility units, option-right encoding, formula traceability, limits, parity, bounds, and benchmark values.

M0A does not decide those merely because its generic types can carry them.

The pre-M0A M1 draft that returned a scalar directly and avoided `ValuationMethod`/`ValuationResult` is superseded by the merged pricing foundation.

## Explicit traps

Avoid:

- treating the mathematical taxonomy as permission to create universal runtime frameworks;
- universal `FinancialModel` inheritance trees;
- universal `Problem` / `Method` / `Result` base classes before shared behavior exists;
- god-model objects that price, calibrate, predict, simulate, hedge, plot, validate, and measure risk;
- forcing all stochastic laws into drift/diffusion;
- generic measure objects that pretend to transform arbitrary dynamics between P and Q;
- scalar-rate assumptions embedded throughout public pricing APIs;
- volatility treated as intrinsic observed-market state rather than model information;
- conflating observations with modeled/implied values;
- conflating contracts, trades, positions, and portfolios;
- calibration implemented as `model.calibrate(...)` with hidden objective/optimizer semantics;
- treating Monte Carlo/Fourier/PDE/optimization as financial models;
- designing rates, XVA, prediction, control, or market-risk frameworks before those domains have real consumers;
- one giant result object with many optional unrelated fields;
- generic experiment engines before multiple studies reveal shared semantics;
- fake Python/C++ backend architectures before native code exists;
- optimization motivated by intuition rather than profiling evidence.

## ADR policy

Create a dedicated ADR only when a decision is durable, consequential, and difficult to infer from code plus this index.

ADR 0001 is the historical authority for the pricing-specific foundational decision. ADR 0002 supersedes it as the current authority for the broader mathematical problem architecture.

Do not rewrite historical ADRs to hide later changes. Supersede them with a new ADR when architecture materially changes.
