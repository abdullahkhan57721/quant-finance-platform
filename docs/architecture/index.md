# Architecture Index

## Status

This document records durable architecture guardrails for the Quantitative Finance Research & Validation Platform.

M0A establishes:

1. a production mathematical asset-pricing composition core; and
2. a platform-wide mathematical taxonomy for organizing quantitative problems without pre-building their operational frameworks.

M1 provides the first concrete Black-Scholes/European-option specialization. M2 pressure-tests the pricing boundary with multiple valuation methods and establishes the first concrete sensitivity family. ADR 0002 remains the current authority for the platform-wide doctrine; ADR 0001 remains the historical pricing-specific decision.

The repository intentionally does **not** define a complete package hierarchy or universal finance framework in advance.

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

Foundational mathematical domain distinctions may be represented explicitly from the outset when their distinctness follows from the mathematical question itself rather than speculative software reuse.

This does **not** authorize generic runtime frameworks for every named problem family.

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

Across problem families:

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

Protect:

```text
inverse problem != optimizer / root finder
observations != inferred parameters
model structure != fitted parameter values
```

An optimizer or root finder is a solution method; it does not own the financial meaning of the inverse problem. No generic production `InverseProblem` framework exists yet. M4 is expected to create the first narrow inverse consumer through implied volatility.

### Sensitivity

A sensitivity problem asks how a specified quantitative output changes under selected perturbations of states, inputs, parameters, or conventions.

Protect:

```text
sensitivity problem != differentiation method
analytic Greek != finite-difference algorithm
sensitivity != risk by definition
```

M2 implements the first **concrete** sensitivity family:

```text
BlackScholesSensitivityProblem
        +
supported Black-Scholes sensitivity method
        ↓
BlackScholesSensitivityResult
```

with analytic and finite-difference methods for Delta, Gamma, Vega, Theta, and Rho. This is not a generic production `SensitivityProblem` framework. Pricing remains upstream of sensitivity; `qf_platform.pricing` must not depend back on `qf_platform.sensitivity`.

### Prediction

A prediction problem asks for a future quantity or distribution conditional on specified information under explicit probability semantics.

Protect:

```text
prediction problem != pricing problem
physical measure P != pricing measure Q^N
forecast target != financial contract
```

No generic production `PredictionProblem` framework exists yet.

### Control / optimization

A control problem asks which admissible action, policy, hedge, allocation, or stopping rule best achieves a stated objective subject to dynamics and constraints.

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

No generic production `ControlProblem` framework exists yet. M3 is expected to create the first concrete pressure through dynamic delta hedging/replication.

### Risk

A risk problem asks for a specified characterization of loss, exposure, uncertainty, or adverse outcomes for a defined financial object, horizon, scenario/probability semantics, and conditioning information.

Protect:

```text
risk problem != risk-measure implementation
risk measure != stochastic law
risk result != trade / portfolio by definition
```

No generic production `RiskProblem` framework exists yet.

### Validation

A validation problem asks whether a specified model, implementation, method, result, calibration, or empirical claim satisfies explicit criteria and what evidence supports that conclusion.

Protect:

```text
validation problem != validation method
validation evidence != model output itself
self-agreement != independent validation
```

Validation may invoke pricing, inference, sensitivity, prediction, control, or risk capabilities to gather evidence. No generic production `ValidationProblem` framework exists yet.

## Observations and model boundary

Observed information and modeled quantities remain distinguishable even when both are represented by similar numeric objects.

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

Protect:

```text
market observation != modeled state
observed quote != model-implied quantity
raw observation != normalized input
normalization != calibration / inference
```

Construction, interpolation, cleaning, convention application, or model fitting must not silently rewrite historical observations.

The expected later distinction remains:

```text
MarketSnapshot != MarketEnvironment
```

where a snapshot is provenance-bearing observations and an environment is problem-ready interpretation/construction only if earned by real consumers. M0A–M2 create neither merely because future observed-market workflows are foreseeable.

## Production pricing composition

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
ValuationResult or specific subtype
```

### State and state space

`StateSpace[T]` supplies membership semantics. `ModeledState[Time, T]` is an immutable current modeled state plus its state-space semantics. `StatePath[Time, T]` provides point evaluation without requiring a discrete path container.

These contracts do not require a finite-dimensional state space or Markov sufficiency.

### Stochastic law and parameter values

`StochasticLaw[State, Parameters]` exposes the state space it governs and parameter compatibility. It does not define every law through `drift()` and `diffusion()`.

Protect:

```text
stochastic law structure != parameter values
```

Calibration/inference may later produce new parameter values; it must not turn fitted values into a new model type.

### Financial contracts and cash flows

`FinancialContract` maps a modeled path to a realized immutable `CashFlowStream`. The contract owns contingent payment semantics, not valuation, inference/calibration, observed market data, trade/portfolio ownership, hedging/P&L, plotting/presentation, or numerical algorithms.

### Numeraire and pricing-measure semantics

`Numeraire[Time]` represents the strictly positive denomination process. `PhysicalMeasureSemantics` and `PricingMeasureSemantics[Time]` remain distinct. The architecture does not provide a generic change-of-measure engine.

### Pricing problem

`PricingProblem` is immutable and answers:

> What financial value is mathematically being asked for?

It composes current modeled state, stochastic-law structure, parameter values, contract, numeraire, pricing measure, and valuation time. It does not choose an algorithm.

### Valuation method and compatibility

`ValuationMethod` answers:

> How will this supported pricing problem be evaluated?

Structural validity and implementation capability are distinct. `evaluate(problem, method)` checks `method.supports(problem)` before application and raises `UnsupportedPricingProblem` for unsupported combinations.

M2 proves three concrete methods over the same M1 pricing family:

```text
BlackScholesClosedForm
CoxRossRubinstein
MonteCarloEuropeanOption
```

The finite CRR model and the continuous Black-Scholes model are not silently identified; a CRR configuration can be unsupported when its finite-step no-arbitrage probability condition fails.

### Valuation result

`ValuationResult` remains the narrow common immutable result with finite `present_value`.

M2 demonstrates one stable extension rule: a concrete valuation method may return a **specific immutable subtype** when it genuinely produces additional method evidence. `MonteCarloValuationResult` therefore adds standard error, a labeled 95% normal-approximation confidence interval, path count, and seed.

These fields do **not** become optional members of every valuation result. Greeks, calibration diagnostics, hedging/P&L evidence, validation evidence, and benchmark/performance metadata remain separate specific results/evidence.

## Additional protected distinctions

### Financial contract vs ownership context

```text
FinancialContract != Trade != Portfolio
```

Introduce trade/portfolio structures only when real aggregation/ownership consumers exist.

### Model structure vs parameters

```text
stochastic law != model parameters
```

A calibrated parameter set is not a different model type.

### Financial model vs numerical method

```text
stochastic law != ValuationMethod
financial model != numerical method
```

```text
GBM / Heston
= stochastic-law/model semantics

closed form / binomial / Monte Carlo / Fourier / PDE
= valuation methods
```

### Inverse problem vs optimizer

```text
inverse / calibration problem != numerical optimizer
```

Financial inference owns observations/targets, comparison/error semantics, domains/constraints, weighting, and diagnostics. A root finder/optimizer owns search mechanics.

### Request/configuration vs committed result

```text
configuration/request != immutable result
```

Mutable orchestration, solver state, caches, and work buffers belong outside committed results.

### Production library vs research study vs presentation

```text
production library != research study != presentation
```

Research studies should execute against production library behavior; presentation must not become the authority for quantitative meaning.

## Dependency direction

The pricing-core direction remains:

```text
state / cash flows / measures
          ↓
contracts + stochastic-law semantics
          ↓
PricingProblem
          ↓
valuation methods/results
```

M2 adds a downstream sensitivity package:

```text
pricing foundations + supported valuation semantics
          ↓
Black-Scholes sensitivity problem/method/result
```

Guardrails:

- low-level state, cash-flow, contract, measure, and stochastic-law modules must not depend on valuation implementations;
- `PricingProblem` must not depend on valuation methods;
- `qf_platform.pricing` must not depend on `qf_platform.sensitivity`;
- sensitivity may consume pricing because the concrete question differentiates a valuation map;
- market observations/environment must not depend on contracts merely for convenience;
- stochastic-law semantics must not own inference/calibration orchestration;
- numerical utilities may be used by methods but must not own finance-domain policy;
- validation may invoke capabilities needed to gather independent evidence;
- high-level research/UI code must consume public library behavior rather than duplicate it.

## Market-data and provenance direction

Expected future conceptual flow:

```text
external/raw data
       ↓
normalized observations
       ↓
provenance-bearing snapshot/observations
       ↓
construction / conventions
       ↓
problem-ready inputs
```

Core tests must not depend on live data services. Research data should preserve provider/source, as-of/retrieval timestamps, raw artifact or content hash where permitted, normalization version, and licensing/redistribution notes.

## Reproducibility and RNG

Stochastic calculations must use explicitly owned randomness rather than ambient global state.

M2 concretely exercises this rule: `MonteCarloEuropeanOption` owns explicit path count and integer seed and creates a fresh local Python RNG for each application. The immutable result retains path count and seed. Equal integer seeds across future Python/C++ implementations are not a cross-language random-stream contract.

Use shared pre-generated numeric/random inputs when strict kernel parity is required.

## Validation as architecture

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

M2 explicitly distinguishes financial-model error, CRR discretization/model-approximation error, Monte Carlo sampling error, finite-difference truncation error, cancellation/floating-point error, and analytical floating-point error.

Independent implementations agreeing are useful evidence but are not automatically proof of conceptual correctness. Every nontrivial numerical tolerance should have a documented rationale.

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
- Do not introduce backend registries before a second real implementation exists.
- Prefer primitive numeric arrays/scalars across a native boundary rather than exporting rich Python financial objects into C++.

## M1/M2 specialization pressure

M1 specializes the pricing problem family with European options and Black-Scholes closed form.

M2 proves that the same financial problem can support independent analytic/tree/Monte Carlo methods while method-specific uncertainty remains specific evidence. It also proves that sensitivity deserves a separate concrete problem family rather than being hidden as methods on a pricer.

```text
same financial PricingProblem
        ├── analytic
        ├── CRR
        └── Monte Carlo

separately

BlackScholesSensitivityProblem
        ├── analytic differentiation
        └── finite differences
```

Neither pressure justifies a universal solver registry, model god object, generic sensitivity engine, portfolio layer, or risk engine.

## Explicit traps

Avoid:

- treating the mathematical taxonomy as permission to create universal runtime frameworks;
- universal `FinancialModel` inheritance trees;
- universal `Problem` / `Method` / `Result` base classes before shared behavior exists;
- god-model objects that price, calibrate, predict, simulate, hedge, plot, validate, and measure risk;
- forcing all stochastic laws into drift/diffusion;
- generic measure objects that pretend to transform arbitrary dynamics between P and Q;
- scalar-rate assumptions embedded throughout public pricing APIs;
- conflating observations with modeled/implied values;
- conflating pricing, sensitivity, control, and risk questions;
- treating Monte Carlo/Fourier/PDE/optimization as financial models;
- one giant result object with many optional unrelated fields;
- generic experiment engines before multiple studies reveal shared semantics;
- fake Python/C++ backend architectures before native code exists;
- optimization motivated by intuition rather than profiling evidence.

## ADR policy

Create a dedicated ADR only when a decision is durable, consequential, and difficult to infer from code plus this index.

ADR 0001 is the historical authority for the pricing-specific foundational decision. ADR 0002 supersedes it as the current authority for the broader mathematical problem architecture. M2's changes are concrete extensions of ADR 0002 rather than a contradiction requiring a superseding ADR.

Do not rewrite historical ADRs to hide later changes. Supersede them when architecture truly changes.
