# Architecture Index

## Status

This document records durable architecture guardrails for the Quantitative Finance Research & Validation Platform.

M0A establishes:

1. a production mathematical asset-pricing composition core; and
2. a platform-wide mathematical taxonomy for organizing quantitative problems without pre-building their operational frameworks.

M1 provides the first concrete Black-Scholes/European-option specialization. M2 pressure-tests the pricing boundary with multiple valuation methods and establishes the first concrete sensitivity family. M3 establishes the first concrete control/dynamic-replication family while deliberately remaining narrower than a generic stochastic-control, portfolio, or execution framework. ADR 0002 remains the current authority for the platform-wide doctrine; ADR 0001 remains the historical pricing-specific decision.

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

An optimizer or root finder is a solution method; it does not own the financial meaning of the inverse problem. No generic production `InverseProblem` framework exists yet. M4 is the first narrow inverse consumer through implied-volatility work.

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
control / optimization question
```

Protect:

```text
control problem != optimizer
objective/constraints != search algorithm
sensitivity value != control policy
policy != realized action / trajectory
policy/result != mutable solver state
```

M3 implements the first **concrete** control pressure through Black-Scholes dynamic Delta hedging:

```text
Black-Scholes pricing problem
+
exact-transition model-generated path
+
rebalance schedule
+
AnalyticDeltaHedgePolicy consuming M2 Delta
+
stock/cash financing and cost convention
        ↓
DeltaHedgeResult
        ↓
ReplicationErrorSummary
```

This does **not** create a generic production `ControlProblem` framework. The policy is prescribed by the Black-Scholes replication argument; M3 does not solve a universal optimization problem or introduce strategy/portfolio/execution infrastructure.

The first specialization also keeps:

```text
financial model != path simulation != hedge execution
path observation grid != hedge rebalance schedule
replication error != model error by definition
```

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

where a snapshot is provenance-bearing observations and an environment is problem-ready interpretation/construction only if earned by real consumers. M0A–M3 create neither merely because observed-market workflows are foreseeable. M3 model-generated paths are not market observations.

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

M3 consumes the existing contract to settle the terminal option payoff; it does not move hedge state or ownership into `FinancialContract`.

### Numeraire and pricing-measure semantics

`Numeraire[Time]` represents the strictly positive denomination process. `PhysicalMeasureSemantics` and `PricingMeasureSemantics[Time]` remain distinct. The architecture does not provide a generic change-of-measure engine.

M3 uses the existing flat money-market numeraire both for the pricing problem and for explicit hedge cash-account financing. That reuse does not turn the numeraire into a portfolio or execution object.

### Pricing problem

`PricingProblem` is immutable and answers:

> What financial value is mathematically being asked for?

It composes current modeled state, stochastic-law structure, parameter values, contract, numeraire, pricing measure, and valuation time. It does not choose an algorithm or own dynamic hedge state.

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

These fields do **not** become optional members of every valuation result. Greeks, calibration diagnostics, hedging/P&L evidence, validation evidence, and benchmark/performance metadata remain separate specific results/evidence. M3 therefore commits `DeltaHedgeResult` and `ReplicationErrorSummary` separately rather than extending `ValuationResult`.

## M3 control / dynamic-replication boundary

M3 establishes a concrete downstream package:

```text
qf_platform.pricing
        ↓
qf_platform.sensitivity
        ↓
qf_platform.control
```

The conceptual data flow is not a claim that every control workflow must depend on sensitivity. It records the actual first consumer: the Black-Scholes hedge policy uses M2 Delta.

The package contains two separate responsibilities that happen to cooperate in M3:

```text
BlackScholesPathSimulation
→ exact model-generated path evidence

BlackScholesDeltaHedgeProblem + AnalyticDeltaHedgePolicy
→ dynamic hedge question / policy
→ realized hedge accounting evidence
```

The path configuration is not a `ValuationMethod`, and the hedge problem is not a `SensitivityProblem`.

M3's exact-transition GBM setup means observation dates are output/sample dates rather than Euler discretization steps. A future stochastic law that requires numerical path discretization must introduce that method/configuration explicitly instead of generalizing M3's dates into a universal simulator clock.

Mutable local execution state is permitted while a hedge trajectory is being constructed, but completed `SimulatedEquityPath`, `DeltaHedgeResult`, and aggregate evidence are immutable/value-like.

## Additional protected distinctions

### Financial contract vs ownership context

```text
FinancialContract != Trade != Portfolio
```

Introduce trade/portfolio structures only when real aggregation/ownership consumers exist. M3's convention of one short option is local to its control problem and does not create a general `Trade` abstraction.

### Model structure vs parameters

```text
stochastic law != model parameters
```

A calibrated parameter set is not a different model type. M3 likewise represents generating volatility and hedging volatility as parameter values under the same Black-Scholes law rather than inventing different model classes.

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

M3 adds another protected distinction:

```text
stochastic law != path-generation procedure != control policy
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

Mutable orchestration, solver state, caches, work buffers, path-generation scratch state, and hedge-execution scratch state belong outside committed results.

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

M3 adds a further downstream concrete control package:

```text
pricing + sensitivity
          ↓
Black-Scholes path/control/accounting/evidence
```

Guardrails:

- low-level state, cash-flow, contract, measure, and stochastic-law modules must not depend on valuation implementations;
- `PricingProblem` must not depend on valuation methods;
- `qf_platform.pricing` must not depend on `qf_platform.sensitivity` or `qf_platform.control`;
- `qf_platform.sensitivity` may consume pricing but must not depend on `qf_platform.control`;
- M3 control may consume pricing and sensitivity because its concrete policy uses both;
- dynamic hedge state/evidence must not be pushed back into pricing or sensitivity result contracts;
- market observations/environment must not depend on contracts merely for convenience;
- stochastic-law semantics must not own inference/calibration orchestration or hedge execution;
- numerical utilities may be used by methods but must not own finance-domain policy;
- validation may invoke capabilities needed to gather independent evidence;
- high-level research/UI code must consume public library behavior rather than duplicate it.

## Market-data and provenance direction

Expected conceptual flow for M4 and later observed-data work:

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

M3 synthetic/model-generated paths remain outside this observation/provenance flow.

## Reproducibility and RNG

Stochastic calculations must use explicitly owned randomness rather than ambient global state.

M2 concretely exercises this rule: `MonteCarloEuropeanOption` owns explicit path count and integer seed and creates a fresh local Python RNG for each application. The immutable result retains path count and seed.

M3 exercises it again: `BlackScholesPathSimulation` owns an explicit seed, exact-transition path generation creates fresh local RNG state, and the realized immutable path retains the generating configuration. Aggregate replication summaries require distinct seeds rather than silently counting duplicate-seed runs as independent stochastic replicates.

Equal integer seeds across future Python/C++ implementations are not a cross-language random-stream contract. Use shared pre-generated numeric/random inputs when strict kernel parity is required.

## Validation as architecture

Relevant evidence categories include:

1. **Software correctness** — unit tests, typing, invariants, boundary behavior.
2. **Theoretical/financial correctness** — no-arbitrage identities, bounds, limiting cases, self-financing identities.
3. **Numerical correctness** — convergence, stability, error behavior.
4. **Stochastic correctness** — statistical error, confidence intervals, seeded reproducibility, replicate integrity.
5. **Cross-method validation** — independent valuation/sensitivity methods.
6. **Inference/calibration validation** — parameter recovery, residuals, stability, identifiability.
7. **Empirical/out-of-sample validation** — evidence on observations not used to fit the model.
8. **Model-risk evidence** — assumption violations, sensitivities, hedging/P&L effects, failure modes.
9. **Backend parity** — Python/C++ numerical/statistical equivalence.
10. **Performance evidence** — profiling, runtime, memory, scaling.

M2 explicitly distinguishes financial-model error, CRR discretization/model-approximation error, Monte Carlo sampling error, finite-difference truncation error, cancellation/floating-point error, and analytical floating-point error.

M3 adds concrete evidence distinguishing discrete hedge-rebalancing error, stochastic replicate variation, volatility misspecification effect, and transaction-cost drag. A terminal replication discrepancy is not labeled "model error" merely because it is nonzero.

Independent implementations agreeing are useful evidence but are not automatically proof of conceptual correctness. Every nontrivial numerical tolerance or statistical/comparative criterion should have a documented rationale.

## Python/C++ execution boundary

Long-term target:

```text
Python
────────────────────────
financial semantics
market data
configuration
inference/calibration orchestration
control/research orchestration
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

M3 creates no native acceleration claim. Exact-transition path generation and hedge execution remain readable Python reference behavior until profiling later demonstrates a worthwhile numerical boundary.

## M1/M2/M3 specialization pressure

M1 specializes the pricing problem family with European options and Black-Scholes closed form.

M2 proves that the same financial problem can support independent analytic/tree/Monte Carlo methods while method-specific uncertainty remains specific evidence. It also proves that sensitivity deserves a separate concrete problem family rather than being hidden as methods on a pricer.

M3 proves that a sensitivity can be **consumed** by a dynamic policy without becoming that policy or owning its state, and that path simulation/accounting/control evidence deserves a separate downstream boundary.

```text
same financial PricingProblem
        ├── analytic
        ├── CRR
        └── Monte Carlo

separately

BlackScholesSensitivityProblem
        ├── analytic differentiation
        └── finite differences

then consumed downstream by

BlackScholesDeltaHedgeProblem
        +
AnalyticDeltaHedgePolicy
        +
model-generated path
        ↓
DeltaHedgeResult / ReplicationErrorSummary
```

None of these pressures justifies a universal solver registry, model god object, generic sensitivity/control engine, strategy hierarchy, portfolio layer, execution engine, or risk engine.

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
- treating Delta as synonymous with a hedge policy or realized hedge action;
- treating a path observation grid as automatically synonymous with a numerical SDE discretization grid;
- treating every terminal hedging discrepancy as financial model error;
- treating Monte Carlo/Fourier/PDE/optimization as financial models;
- one giant result object with many optional unrelated fields;
- generic experiment engines before multiple studies reveal shared semantics;
- fake Python/C++ backend architectures before native code exists;
- optimization motivated by intuition rather than profiling evidence.

## ADR policy

Create a dedicated ADR only when a decision is durable, consequential, and difficult to infer from code plus this index.

ADR 0001 is the historical authority for the pricing-specific foundational decision. ADR 0002 supersedes it as the current authority for the broader mathematical problem architecture. M2 and M3 are concrete extensions of ADR 0002 rather than contradictions requiring a superseding ADR. M3 therefore records its local control/path/accounting conventions in code, tests, the quantitative-convention register, and `docs/models/m3_dynamic_delta_hedging.md` rather than creating a generic-control ADR.

Do not rewrite historical ADRs to hide later changes. Supersede them when architecture truly changes.
