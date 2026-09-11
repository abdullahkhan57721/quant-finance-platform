# Architecture Index

## Status

This document records durable architecture guardrails for the Quantitative Finance Research & Validation Platform.

Implemented pressure now includes:

- M0A — mathematical problem architecture and pricing foundation;
- M1 — Black-Scholes / European-option specialization;
- M2 — independent valuation and sensitivity;
- M3 — control / dynamic replication;
- M4 — observed-market boundary and scalar inverse problem;
- M5 — Heston stochastic-volatility forward model with independent valuation;
- M6 — noisy multi-parameter calibration and identifiability evidence; and
- M7 — predeclared empirical validation / model-risk comparison.

ADR 0002 is the platform-wide mathematical architecture authority. ADR 0003 governs the native PySide6 + Qt Quick/QML workbench boundary.

The repository intentionally does **not** define a universal finance framework in advance.

## Governing extraction rule

```text
one concrete consumer
→ keep operational code local

two real consumers
→ compare responsibilities

same responsibility and lifecycle
→ consider extraction

different responsibility
→ keep separate
```

### Foundational mathematical exception

Stable mathematical domain distinctions may be represented explicitly from the outset when their separation follows from the mathematics rather than speculative software reuse.

```text
Foundational mathematical distinctions
may be explicit early.

Operational frameworks
must remain evidence-driven.

Mathematical generality
!= universal runtime API.
```

## Mathematical taxonomy

```text
FINANCIAL / MATHEMATICAL FOUNDATIONS
state / state space
stochastic law
model parameters
probability / measure semantics
numeraire
market observations + provenance
contracts / cash flows
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
analytic / lattice / Monte Carlo / Fourier / finite difference
root finding / optimization / regression / filtering / scenarios / tests
        ↓
SPECIFIC IMMUTABLE RESULTS / EVIDENCE
```

The reusable conceptual pattern is:

```text
Problem + supported Method -> specific immutable Result / Evidence
```

Do not create universal `Problem`, `Method`, or `Result` base classes merely because the conceptual pattern is shared.

## Protected distinctions

```text
problem != solution method
request/configuration != immutable result
market observation != modeled state
raw observation != normalized observation != model output
state != stochastic law != parameters != fitted estimate
pricing != sensitivity != control != inverse != validation
contract != pricing model
numeraire != pricing measure
Delta != hedge policy != realized hedge action
calibration objective / weighting != optimizer configuration
financial domain != numerical bound mechanism != transform
calibration != validation
training fit != held-out evaluation
model residual != quote width != numerical error
optimizer convergence != parameter identification != model validity
same-date cross-sectional holdout != temporal forecasting
```

## Pricing architecture

```text
ModeledState / StateSpace / StatePath
+
StochasticLaw + separate parameters
+
FinancialContract -> CashFlowStream
+
Numeraire + PricingMeasureSemantics
        ↓
PricingProblem
        +
compatible ValuationMethod
        ↓
ValuationResult or specific subtype
```

Black-Scholes and Heston are concrete stochastic-law specializations. Monte Carlo, Fourier, CRR, and closed form are valuation methods, not models.

M5 keeps Heston current variance in `HestonEquityState`, structural parameters in `HestonParameters`, and risk-free rate ownership in the money-market numeraire. M6 calibration returns fitted coordinates without mutating Heston law identity.

## Observed-market boundary

```text
real world
    ↓
raw observations + provenance
    ↓
explicit normalization
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

M4 productionizes this boundary. M6 and M7 consume `NormalizedOptionObservation` rather than inventing calibration- or validation-specific market-data types.

## Inverse / inference architecture

Two concrete inverse consumers exist.

### M4 scalar Black-Scholes inversion

```text
NormalizedOptionObservation
+
BlackScholesImpliedVolatilityProblem
+
BisectionImpliedVolatility
        ↓
ImpliedVolatilityResult
```

The financial problem owns feasibility, model inputs, observed target, and admissible volatility domain. Bisection owns scalar root-search mechanics.

### M6 Heston calibration

```text
HestonPriceCalibrationTarget(s)
+ fixed financial inputs
+ HestonCalibrationBounds
+ price-space residual / weighting
+ Heston Fourier forward map
        ↓
HestonCalibrationProblem
+
ScipyLeastSquaresHestonCalibration
        ↓
HestonCalibrationResult
```

The financial problem owns residual/objective/weighting/domain meaning. The optimizer owns numerical search mechanics. Results retain objective/residual evidence and local Jacobian identification diagnostics.

M4 and M6 share the conceptual inverse Problem → Method → Result distinction but do not share enough operational behavior to justify a universal runtime inverse/optimizer hierarchy.

## Sensitivity architecture

```text
BlackScholesSensitivityProblem
+
AnalyticBlackScholesSensitivity
or FiniteDifferenceBlackScholesSensitivity
        ↓
BlackScholesSensitivityResult
```

Pricing is upstream. Sensitivity does not own hedging policy or risk semantics.

## Control architecture

M3 provides the first control specialization:

```text
Black-Scholes pricing problem
+
exact-transition GBM path
+
explicit rebalance schedule
+
AnalyticDeltaHedgePolicy consuming M2 Delta
+
stock/cash financing and transaction-cost semantics
        ↓
DeltaHedgeResult
        ↓
ReplicationErrorSummary
```

The path's Black-Scholes/GBM provenance is part of the evidence. M7 therefore cannot reuse an M3 `SimulatedEquityPath` while pretending it represents a Heston world.

## Validation architecture — M7

M7 is the first production specialization in which validation is the organizing mathematical problem family.

```text
NormalizedOptionObservation(s)
+ explicit TRAINING / EVALUATION partition
+ fixed rate/carry/spot semantics
+ fair Black-Scholes benchmark domain
+ Heston calibration domain / Fourier forward dependency
        ↓
BlackScholesHestonValidationProblem
        +
CrossSectionalBlackScholesHestonValidation
        ↓
BlackScholesHestonValidationEvidence
```

### Problem ownership

`BlackScholesHestonValidationProblem` owns:

- normalized observations;
- immutable training/evaluation contract identities;
- numeraire and pricing-measure semantics;
- fixed dividend/carry input;
- Black-Scholes admissible volatility domain;
- Heston calibration bounds; and
- the Heston Fourier forward dependency.

The partition is part of the validation question, not an after-the-fact reporting choice.

### Method ownership

`CrossSectionalBlackScholesHestonValidation` owns:

- one Black-Scholes initial volatility;
- explicit Heston initial guesses;
- optimizer tolerances; and
- maximum function-evaluation budget.

It does not own market observations, financial model meaning, objective semantics, or presentation state.

### Evidence ownership

`BlackScholesHestonValidationEvidence` retains:

- one fitted constant-volatility Black-Scholes benchmark;
- every explicit Heston training start outcome;
- selected Heston training calibration;
- contract-level residuals for both models;
- training and held-out metrics separately;
- post-evaluation full-sample Heston stability calibration;
- local Jacobian rank/condition evidence;
- domain-scaled parameter-stability evidence;
- structural M8 workload evidence; and
- a bounded conclusion.

This is validation evidence, not an optional extension of `ValuationResult` or `HestonCalibrationResult`.

### No-leakage architecture

The M7 execution order is semantically important:

```text
predeclare partition
        ↓
fit both models on TRAIN only
        ↓
freeze fitted training estimates
        ↓
compute held-out predictions + metrics
        ↓
only then run full-sample Heston stability calibration
```

A regression test perturbs evaluation targets and proves that training estimates and held-out model prices do not change.

### Why there is no generic validation framework

One validation consumer is enough to establish the mathematical distinction but not enough to justify universal software abstractions.

M7 therefore does **not** add:

- `ValidationProblem` / `ValidationMethod` / `ValidationResult` base classes;
- metric registries;
- generic model registries;
- scenario/risk engines; or
- report/workflow frameworks.

Later validation consumers may reopen extraction only if repeated operational responsibilities appear.

## Dependency direction

The durable quantitative direction remains:

```text
pricing foundations / contracts / laws
        ↓
pricing methods/results
        ↓
consumer problem families as mathematically required
```

Current concrete relationships include:

```text
qf_platform.pricing
        ↓
qf_platform.sensitivity
        ↓
qf_platform.control
```

and:

```text
qf_platform.market_data       qf_platform.pricing
             \                  /
              \                /
               qf_platform.inference
                         \
                          \
                    qf_platform.validation
```

M7 validation consumes market observations, pricing, and inference. Those lower layers must not depend on validation.

Guardrails:

- `qf_platform.pricing` must not import sensitivity, control, market-data, inference, validation, application, presentation, or desktop layers;
- sensitivity may consume pricing but not control/validation;
- control may consume pricing/sensitivity because its concrete policy requires both;
- inference may consume normalized market data and forward pricing;
- validation may consume pricing, normalized observations, inference/calibration, and pre-existing evidence;
- application/presentation/desktop code remains downstream of all quantitative semantics;
- finance-domain objective/weighting/domain policy must not be hidden inside numerical optimizers; and
- validation calculations must not be pushed into QML.

The M7 dependency-direction test explicitly prevents `qf_platform.validation` from importing application, presentation, or desktop modules.

## Identifiability and model-risk evidence

M6 established that a low Heston price objective can coexist with rank deficiency and materially different parameters. M7 retains that distinction while adding held-out pricing evidence.

```text
better held-out prices
!= globally identified parameters
!= temporal forecasting success
!= lower risk in every use case
```

M7's training calibration is full local rank but nontrivially conditioned. Stable multiple starts and small train→full movement are evidence, not proof of global uniqueness.

## Validation evidence ladder

The project now distinguishes:

1. software correctness;
2. theoretical/financial identities and limits;
3. numerical convergence/stability;
4. stochastic sampling/reproducibility;
5. independent cross-method validation;
6. inverse/calibration recovery, residual, perturbation and identification evidence;
7. predeclared held-out empirical validation;
8. model-risk evidence and unsupported-comparison boundaries;
9. future Python/C++ backend parity; and
10. measured performance evidence.

Self-agreement, optimizer convergence, or a small residual is never sufficient by itself.

## Native workbench boundary

```text
Qt Quick / QML
        ↓
curated PySide6 controller / item-model boundary
        ↓
frontend-neutral application + presentation semantics
        ↓
public quantitative APIs
        ↓
production quantitative core
```

UI4 may consume M5/M6 Heston and calibration behavior. It must not encode M7 validation calculations/conclusions inside QML. Later UI milestones may consume M7 evidence through downstream application/presentation adapters.

## Python/C++ execution boundary

M8 is now the next quantitative pressure:

```text
correct Python reference
        ↓
profile M7-defined representative workloads
        ↓
identify measured hotspot
        ↓
choose narrow numerical boundary
        ↓
targeted C++ implementation
        ↓
Python/C++ parity evidence
```

Python remains the semantic/correctness authority. Do not create backend registries or rewrite research orchestration in C++ before profiling proves a benefit.

## Explicit traps

Avoid:

- universal finance/problem/result inheritance trees;
- god-model objects that price, calibrate, hedge, validate, and plot;
- observations silently turned into modeled state;
- pricing, sensitivity, control, inverse, risk, and validation conflation;
- calibration methods hanging off stochastic-law objects;
- optimizer convergence presented as parameter trustworthiness;
- better in-sample fit presented as held-out adequacy;
- a same-date holdout presented as temporal forecasting;
- Heston pricing evidence presented as Heston hedge evidence;
- Monte Carlo/Fourier/optimization treated as financial models;
- validation metrics moved into QML;
- generic experiment/risk/model registries before consumers justify them; and
- C++ architecture selected by intuition rather than profiling.

## ADR policy

Create an ADR when a decision is durable, consequential, and difficult to infer from code plus this index. M2–M7 are concrete extensions of ADR 0002 rather than architectural contradictions requiring a superseding ADR.

Do not rewrite historical ADRs to hide evolution; supersede them only when architecture truly changes.
