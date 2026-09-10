# Architecture Index

## Status

This document records durable architecture guardrails for the Quantitative Finance Research & Validation Platform.

M0A establishes:

1. a production mathematical asset-pricing composition core; and
2. a platform-wide mathematical taxonomy for organizing quantitative problems without pre-building their operational frameworks.

M1 provides the first concrete Black-Scholes/European-option specialization. M2 pressure-tests the pricing boundary with multiple valuation methods and establishes the first concrete sensitivity family. M3 establishes the first concrete control/dynamic-replication family. M4 establishes the first production observed-market boundary and scalar inverse specialization. M5 adds Heston as a two-factor stochastic-volatility forward model with independent Fourier and Monte Carlo valuation. M6 adds the first noisy multi-parameter calibration inverse problem and directly tests whether any shared inverse runtime abstraction is earned.

ADR 0002 remains the current authority for the platform-wide doctrine; ADR 0001 remains the historical pricing-specific decision. ADR 0003 governs the native PySide6 + Qt Quick/QML workbench boundary.

The repository intentionally does **not** define a complete package hierarchy or universal finance framework in advance.

## Governing extraction rule

For ordinary application abstractions:

```text
one consumer
→ keep concrete/local

two real consumers
→ compare semantics

same operational responsibility
→ consider extracting shared abstraction

different operational responsibility
→ keep separate
```

A future use case that can merely be imagined is not sufficient justification for an operational abstraction.

### Foundational mathematical exception

Foundational mathematical domain distinctions may be represented explicitly from the outset when their distinctness follows from the mathematical question itself rather than speculative software reuse.

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

The production `PricingProblem`, valuation methods, and method-specific valuation results implement this family today for Black-Scholes and Heston.

Protect:

```text
pricing problem != valuation method
stochastic law != valuation method
contract != pricing model
```

### Inverse / inference

An inverse problem asks which latent quantity or parameter/state vector makes a model consistent, under explicit comparison semantics, with observations or target quantities.

```text
observations / targets
+
model structure / forward dependency
+
unknown financial coordinates
+
admissible domain
+
comparison / residual semantics
+
weighting / constraints when applicable
        ↓
financial inverse question
        +
separate numerical method
        ↓
immutable inferred result + diagnostics
```

Protect:

```text
inverse problem != optimizer / root finder
inverse problem != objective function implementation detail
objective / weighting != optimizer configuration
financial/model-domain constraint != numerical bound mechanism != parameter transform
observations != inferred parameters
model structure != fitted parameter values
optimizer converged != reliable identification != model validity
```

Two concrete inverse consumers now exist.

#### M4 scalar inversion

```text
NormalizedOptionObservation
+
BlackScholesImpliedVolatilityProblem
+
BisectionImpliedVolatility
        ↓
ImpliedVolatilityResult
```

M4 owns financial feasibility bounds, an admissible volatility interval, the observed target, and Black-Scholes forward semantics. Bisection owns scalar root-search mechanics. M2 analytic Vega supplies local conditioning evidence.

#### M6 multi-parameter calibration

```text
synthetic price target
or
M4 NormalizedOptionObservation + provenance
        ↓
HestonPriceCalibrationTarget
+
fixed spot / rate / dividend yield
+
HestonCalibrationBounds
+
explicit price-space residual / weighting semantics
        ↓
HestonCalibrationProblem
+
ScipyLeastSquaresHestonCalibration
        ↓
HestonCalibrationResult
+
per-target residuals
+
domain-scaled Jacobian identifiability evidence
```

M6 estimates `(v0, kappa, theta, xi, rho)` while keeping `v0` state-like and separate from immutable structural `HestonParameters`. The first numerical method uses direct financial coordinates and bounded trust-region-reflective nonlinear least squares. The Feller condition remains a model diagnostic, not an optimizer constraint.

M4 and M6 prove the **conceptual** inverse Problem → Method → Result split, but their operational responsibilities remain materially different: scalar feasibility/bracketing/root semantics versus weighted multi-target residuals, multidimensional bounds, nonlinear optimization, and identifiability diagnostics. Therefore no generic production `InverseProblem`, root/optimizer registry, or universal inference framework is extracted.

### Sensitivity

A sensitivity problem asks how a specified quantitative output changes under selected perturbations of states, inputs, parameters, or conventions.

Protect:

```text
sensitivity problem != differentiation method
analytic Greek != finite-difference algorithm
sensitivity != risk by definition
```

M2 implements the first concrete sensitivity family:

```text
BlackScholesSensitivityProblem
        +
supported Black-Scholes sensitivity method
        ↓
BlackScholesSensitivityResult
```

with analytic and finite-difference methods for Delta, Gamma, Vega, Theta, and Rho. Pricing remains upstream of sensitivity.

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

Protect:

```text
control problem != optimizer
objective/constraints != search algorithm
sensitivity value != control policy
policy != realized action / trajectory
policy/result != mutable solver state
```

M3 provides the first concrete control pressure:

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

This does not create a generic `ControlProblem`, trading strategy, portfolio, or execution framework.

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

Validation may invoke pricing, inference, sensitivity, control, or later risk/prediction capabilities. M7 is the next major validation/model-risk pressure.

## Observations and model boundary

Observed information and modeled quantities remain distinguishable even when both use similar numeric values.

```text
real world
    ↓
raw observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready observed information

separately from

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
normalized target != calibrated parameter estimate
```

M4 productionizes this boundary. M6 consumes it: a market `HestonPriceCalibrationTarget` retains its `NormalizedOptionObservation` and therefore its raw observation/provenance lineage. Synthetic Heston targets carry a distinct explicit source and never masquerade as observations.

Construction, interpolation, cleaning, convention application, or model fitting must not silently rewrite historical observations.

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

### State, law, and parameters

`StateSpace[T]` supplies membership semantics. `ModeledState[Time, T]` is an immutable current modeled state plus state-space semantics. `StochasticLaw[State, Parameters]` exposes the state space it governs and parameter compatibility without forcing every law into a universal drift/diffusion API.

Protect:

```text
current modeled state != stochastic law structure != parameter values
```

M5 makes that distinction concrete under Heston. M6 reinforces it: calibrated `initial_variance` remains a state-like coordinate, while `(kappa, theta, xi, rho, q)` remain represented by immutable `HestonParameters`. A fitted parameter value does not create a new stochastic-law type.

### Financial contracts and cash flows

`FinancialContract` maps a modeled path to a realized immutable `CashFlowStream`. The contract owns contingent payment semantics, not valuation, inference/calibration, observations, trade/portfolio ownership, hedging/P&L, plotting, or numerical algorithms.

### Numeraire and pricing-measure semantics

`Numeraire[Time]` represents the strictly positive denomination process. `PhysicalMeasureSemantics` and `PricingMeasureSemantics[Time]` remain distinct. The architecture does not provide a generic change-of-measure engine.

M1/M4/M5/M6 currently use the concrete flat money-market pricing specialization where appropriate. M6 keeps the risk-free input in the numeraire rather than adding it to Heston's calibrated structural parameters.

### Pricing problem and valuation methods

`PricingProblem` answers what financial value is being asked for. A `ValuationMethod` answers how a supported instance is evaluated. Structural validity and method support remain distinct.

Black-Scholes currently has closed-form, CRR, and Monte Carlo valuation. Heston currently has Fourier and Monte Carlo valuation. M6 consumes the validated Heston Fourier method as its concrete forward map rather than embedding calibration into `HestonLaw` or the valuation method.

### Results stay specific

`ValuationResult` remains a narrow pricing result. Method-specific numerical evidence belongs in specific result subtypes. Sensitivity, control, inference/calibration, validation, and later risk evidence stay in their own result types.

`HestonCalibrationResult` therefore contains only calibrated coordinates, objective/residual evidence, optimizer termination diagnostics, and local Jacobian conditioning evidence. It does not absorb Greeks, hedge trajectories, presentation state, or unrelated valuation diagnostics.

## Dependency direction

The durable quantitative direction is:

```text
pricing foundations / stochastic laws / contracts
        ↓
pricing methods/results
        ↓
consumer problem families where mathematically required
```

Current concrete package relationships include:

```text
qf_platform.pricing
        ↓
qf_platform.sensitivity
        ↓
qf_platform.control
```

for the M3 Delta-policy consumer, and:

```text
qf_platform.market_data      qf_platform.pricing
             \               /
              \             /
               qf_platform.inference
```

for M4/M6 inverse consumers.

Guardrails:

- low-level state, cash-flow, contract, measure, and stochastic-law modules must not depend on valuation implementations;
- `PricingProblem` must not depend on valuation methods;
- `qf_platform.pricing` must not depend on sensitivity, control, market-data, inference, or UI layers;
- sensitivity may consume pricing but must not depend on control;
- M3 control may consume pricing and sensitivity because its concrete policy uses both;
- market observations/provenance must remain distinct from modeled state;
- inference/calibration may consume observations and forward pricing, but pricing/law modules must not own inference orchestration;
- numerical methods may use SciPy/NumPy but must not own finance-domain target/objective/weighting policy;
- dynamic hedge or calibration evidence must not be pushed into pricing result contracts;
- high-level research/UI code must consume public quantitative behavior rather than duplicate it.

## M6 optimizer and calibration boundary

M6 makes the separation executable:

```text
HestonCalibrationProblem owns
    targets
    target source / observation lineage
    unknown financial coordinates
    fixed financial inputs
    price-space residual definition
    residual weighting / scale
    admissible financial bounds
    forward pricing dependency

ScipyLeastSquaresHestonCalibration owns
    initial guess
    trust-region-reflective search
    finite-difference Jacobian mechanics
    numerical tolerances
    maximum function evaluations
    mutable optimizer state

HestonCalibrationResult owns
    completed immutable estimate
    objective value
    per-target raw/standardized residuals
    optimizer termination diagnostics
    local Jacobian rank / singular values / condition evidence
```

The first objective is option-price space. `UNIFORM_PRICE` and `BID_ASK_HALF_SPREAD` are concrete problem-owned weighting policies, not project-wide defaults. Implied-volatility-space calibration, likelihood weighting, parameter transforms, Bayesian inference, filtering, and physical-measure Heston estimation remain unimplemented.

## Identifiability is architectural evidence

M6 treats parameter identifiability as part of completed inverse evidence rather than a hidden optimizer concern.

The local standardized-residual Jacobian `J` is column-scaled by the explicit financial-domain widths `D`:

```text
J_scaled = J D
```

Singular values and numerical rank are retained. A finite five-parameter condition number is reported only for full column rank.

A deterministic three-target/five-unknown experiment intentionally demonstrates that materially different Heston parameter vectors can achieve near-zero objective values. Thus the result contract and documentation protect:

```text
low objective != unique estimate
optimizer convergence != trustworthy identification
```

## Market-data and provenance direction

Observed-data research follows:

```text
external/raw data
       ↓
immutable raw observations + provenance
       ↓
explicit normalization
       ↓
problem-ready observed targets
       ↓
model-dependent inference / calibration
```

Core tests must not depend on live services. Research data should preserve provider/source, as-of/retrieval timestamps, raw artifact/content hash where permitted, normalization version, and licensing/redistribution notes.

M6's SPX workflow reuses the M4 local pinned raw artifact and normalization lifecycle. It emits derived calibration evidence without redistributing raw source rows whose licensing is unclear.

## Reproducibility and RNG

Stochastic calculations use explicitly owned randomness rather than ambient global state. M2 valuation, M3 path simulation, and M5 Heston Monte Carlo each own their seed/configuration and retain relevant immutable evidence.

M6's first optimizer is deterministic for a fixed target set, initial guess, bounds, forward configuration, and numerical library behavior. Multiple starts are represented as explicit separate calibrations rather than hidden random restarts.

Equal integer seeds across future Python/C++ implementations are not a cross-language random-stream contract. Use shared pre-generated numeric/random inputs when strict kernel parity is required.

## Validation as architecture

Relevant evidence categories include:

1. **Software correctness** — unit tests, typing, invariants, boundary behavior.
2. **Theoretical/financial correctness** — identities, bounds, limiting cases, self-financing identities.
3. **Numerical correctness** — convergence, stability, explicit method error behavior.
4. **Stochastic correctness** — statistical error, confidence intervals, seeded reproducibility, replicate integrity.
5. **Cross-method validation** — independent valuation/sensitivity methods.
6. **Inference/calibration validation** — known-truth recovery, residuals, multiple starts, perturbation sensitivity, identifiability/conditioning, and failure semantics.
7. **Empirical/out-of-sample validation** — observations not used to fit the model.
8. **Model-risk evidence** — assumptions, instability, sensitivities, hedging/P&L effects, residual structure, failure modes.
9. **Backend parity** — Python/C++ numerical/statistical equivalence.
10. **Performance evidence** — profiling, runtime, memory, scaling.

Independent implementations agreeing are useful evidence but are not automatically proof of conceptual correctness. Likewise, optimizer convergence and small calibration residuals are useful evidence but are not automatically proof of parameter trustworthiness or model validity.

M7 should now compare Black-Scholes and calibrated Heston using this fuller evidence hierarchy.

## Native workbench boundary

The UI dependency direction remains:

```text
Qt Quick / QML
        ↓
curated PySide6 controller / item-model boundary
        ↓
frontend-neutral application + presentation semantics
        ↓
public mathematical-finance APIs
        ↓
production quantitative core
```

QML must not own pricing formulas, observation normalization, calibration targets/objectives/weighting, financial bounds, optimization, Jacobian conditioning, or model-risk conclusions. UI4 may visualize authoritative M5/M6 outputs only after consuming the public backend contracts.

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

narrow measured numerical boundary

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

M8 owns this pressure after M7 identifies the empirical/model-risk workload worth optimizing.

## Explicit traps

Avoid:

- treating the mathematical taxonomy as permission to create universal runtime frameworks;
- universal `FinancialModel`, `Problem`, `Method`, or `Result` inheritance trees before shared behavior exists;
- god-model objects that price, calibrate, predict, simulate, hedge, plot, validate, and measure risk;
- forcing all stochastic laws into one operational representation;
- generic measure objects that pretend to transform arbitrary dynamics between P and Q;
- conflating observations with modeled/implied values;
- conflating pricing, sensitivity, control, inverse, and risk questions;
- putting calibration objectives, weighting, bounds, or optimization inside `HestonLaw`;
- treating optimizer convergence or small residual as proof of parameter identifiability;
- treating every numerical optimizer bound as a financial/model-domain constraint;
- treating Delta as synonymous with a hedge policy or realized hedge action;
- treating a path observation grid as automatically synonymous with a numerical SDE grid;
- treating every terminal hedging discrepancy as financial model error;
- treating Monte Carlo/Fourier/PDE/optimization as financial models;
- one giant result object with many optional unrelated fields;
- generic experiment engines before multiple studies reveal shared semantics;
- fake Python/C++ backend architectures before native code exists; and
- optimization motivated by intuition rather than profiling evidence.

## ADR policy

Create a dedicated ADR only when a decision is durable, consequential, and difficult to infer from code plus this index.

ADR 0001 is the historical pricing-specific foundation. ADR 0002 supersedes it as the current authority for the broader mathematical problem architecture. M2 through M6 are concrete extensions of ADR 0002 rather than contradictions requiring a superseding ADR. Their local method/problem conventions belong in code, tests, `docs/quantitative_conventions.md`, and model/evidence documents unless future evidence changes the architecture itself.

Do not rewrite historical ADRs to hide later changes. Supersede them when architecture truly changes.
