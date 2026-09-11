# Current State

## Status

The quantitative and native-desktop tracks are now coherent through Heston calibration and its Workbench presentation.

Completed quantitative milestones:

- **M0 — Engineering Bootstrap**;
- **M0A — Mathematical Quant-Finance Architecture Foundation**;
- **M1 — European Options & Black-Scholes Reference Vertical**;
- **M2 — Independent Valuation and Sensitivity/Greeks**;
- **M3 — Dynamic Hedging / Control**;
- **M4 — Market Evidence / Inverse Problems**;
- **M5 — Heston Model and Independent Valuation**;
- **M6 — Heston Calibration / Multi-Parameter Inverse Problem**.

Completed native milestones:

- **UI1 — Native Workbench Architecture & Black-Scholes Vertical**;
- **UI2 — Valuation Comparison, Numerical Evidence & Greeks**;
- **UI3 — Dynamic Hedging, Market Evidence & Scalar Inference**;
- **UI4 — Heston Forward Valuation, Calibration & Identifiability Workbench**.

ADR 0002 remains the platform-wide mathematical architecture authority. ADR 0003 remains the native PySide6 + Qt Quick/QML boundary authority.

**M7 — Empirical Validation, Model Risk & Black-Scholes vs Heston** is an independent active workstream but is not authoritative until squash-merged to `main`. UI4 intentionally consumes only merged M5/M6 behavior.

The next desktop milestone, **UI5**, is gated on actual merged M7 evidence and concrete M8 performance/release pressure rather than on speculative validation conclusions.

## Current mathematical architecture

The platform-wide conceptual pattern remains:

```text
Problem + supported Method -> specific immutable Result
```

This is a mathematical responsibility pattern, not a universal runtime inheritance tree.

Protect:

```text
state != stochastic law != parameter values
financial contract != pricing model
problem != solution method
pricing != sensitivity != control != inverse inference != validation
market observation != modeled state
raw observation != normalized observation != model-implied value
inverse problem != root finder / optimizer
objective / weighting != optimizer configuration
optimizer converged != identified parameters != valid model
request / draft != immutable completed result
```

## Forward pricing capabilities

### Black-Scholes

```text
EquityState
+ BlackScholesLaw / BlackScholesParameters
+ EuropeanOption
+ money-market numeraire / pricing measure
        ↓
PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
```

M1/M2 establish analytic reference valuation, independent lattice and Monte Carlo evidence, explicit uncertainty/discretization semantics, and the first sensitivity family.

### Heston

```text
HestonEquityState(spot, instantaneous variance)
+ HestonLaw / HestonParameters(kappa, theta, xi, rho, q)
+ existing EuropeanOption
+ existing money-market numeraire / pricing measure
        ↓
PricingProblem
        ├── HestonFourierEuropeanOption
        └── HestonMonteCarloEuropeanOption
```

M5 keeps current variance `v0`, structural law, immutable parameter values, valuation method, and future calibrated estimates distinct. The Feller condition is diagnostic rather than universally enforced.

Fourier results retain integration/resolution and characteristic-function work evidence. Heston Monte Carlo results retain sampling uncertainty, paths/timesteps/seed, variance scheme, and negative-variance proposal diagnostics.

## Sensitivity and control

M2 provides Black-Scholes analytic and finite-difference Delta, Gamma, Vega, Theta, and Rho through a separate `BlackScholesSensitivityProblem` family.

M3 consumes analytic Delta as a policy input for explicit dynamic replication:

```text
model-generated GBM path
+ rebalance schedule
+ analytic-Delta hedge policy
+ stock / money-market accounting
+ optional proportional transaction cost
        ↓
DeltaHedgeResult / ReplicationErrorSummary
```

Sensitivity values, hedge policies, realized actions, and realized hedge error remain separate responsibilities.

## Observed market evidence and scalar inference

M4 establishes the production observation lifecycle:

```text
RawOptionQuote + RawUnderlyingObservation + provenance
        ↓
explicit midpoint normalization
        ↓
NormalizedOptionObservation
        ↓
BlackScholesImpliedVolatilityProblem
+ BisectionImpliedVolatility
        ↓
ImpliedVolatilityResult + conditioning evidence
```

The pinned January 4, 2023 SPX evidence exhibits strike skew and maturity dependence that one constant Black-Scholes volatility cannot reconcile under the explicit input conventions.

## Heston calibration / multi-parameter inverse inference

M6 calibrates the five direct financial coordinates:

```text
(v0, kappa, theta, xi, rho)
```

while preserving `v0` as state-like and keeping spot, risk-free accumulation, and continuous dividend yield as fixed explicit inputs for the first calibration consumer.

The production composition is:

```text
synthetic Heston price target
or
NormalizedOptionObservation + provenance
        ↓
HestonPriceCalibrationTarget
+ financial bounds
+ price-space residual / weighting semantics
+ M5 Heston Fourier forward map
        ↓
HestonCalibrationProblem
+ ScipyLeastSquaresHestonCalibration
        ↓
HestonCalibrationResult
+ per-target residual evidence
+ local Jacobian conditioning / identifiability evidence
```

M6 implements option-price-space calibration only. The problem owns mismatch/weighting semantics; the SciPy method owns numerical search configuration/state.

Synthetic evidence includes:

- known-truth recovery over four maturities and five strikes;
- multiple materially different starts;
- controlled target perturbation;
- a deliberately underdetermined three-target/five-coordinate example with tiny loss, materially different estimates, and rank-deficient local Jacobians.

The committed real-market M6 reference reuses M4 SPX observation/provenance semantics and 14 pinned OTM-side contracts. Its three starts cluster near:

```text
v0      ≈ 0.04447
kappa   ≈ 3.2575
theta   ≈ 0.06622
xi      ≈ 0.62715
rho     ≈ -0.77937
```

with half-spread-standardized objective about `12.56` and a full-rank domain-scaled local Jacobian condition number about `404`. This is calibration evidence, not a conclusion that Heston is valid or superior.

## Native Workbench through UI4

The durable dependency direction is:

```text
Qt Quick / QML
        ↓
curated PySide6 controller / item models
        ↓
frontend-neutral application + presentation semantics
        ↓
public quantitative APIs
        ↓
production quantitative core
```

The core remains Qt-independent and PySide6 remains optional.

The current Workbench exposes four mathematical workflow families:

```text
Forward valuation / sensitivity
    ├── Black-Scholes valuation & Greeks
    └── Heston forward valuation

Control / replication
    └── Black-Scholes dynamic Delta hedging

Observed-market scalar inverse inference
    └── Black-Scholes implied volatility / market evidence

Multi-parameter inverse inference
    └── Heston calibration / identifiability
```

### UI4 Heston valuation

The Heston workspace makes the model change explicit:

```text
Black-Scholes: S_t + constant volatility
Heston:        (S_t, v_t) + stochastic variance + correlated shocks
```

The European option contract and forward-pricing question remain recognizable across both models.

The same authoritative Heston `PricingProblem` is run through Fourier and Monte Carlo. The UI exposes method-specific evidence, MC confidence intervals, variance-boundary diagnostics, and Fourier-resolution stability without collapsing them into a generic error field.

Merged M5 valuation results do not retain authoritative Heston paths, so UI4 deliberately has no fabricated path display.

### UI4 Heston calibration

Calibration is a separate inverse-problem workspace rather than a model-parameter-panel action.

UI4 exposes:

- direct financial coordinates and bounds;
- price-space target/objective/weighting semantics;
- explicit optimizer initial guesses/configuration;
- synthetic truth recovery;
- multiple-start results;
- target/model-price residuals;
- optimizer termination evidence;
- Jacobian rank/singular values/condition evidence;
- the thin rank-deficient counterexample;
- the committed derived M6 SPX reference and M4 source lineage.

It does not invent IV-space Heston calibration, hidden parameter transforms, Bayesian/posterior uncertainty, or optimizer progress absent from M6.

### UI4 execution safety

Heston Monte Carlo and calibration reuse the established local `QThread` boundary. UI4 adds only concrete stale-result protection:

```text
one active heavy job
+ job/workspace identity
+ relevant input invalidation
        ↓
stale completion is discarded
```

No universal scheduler, queue, cancellation framework, persistence system, or progress protocol is introduced.

## Validation and packaging

Core validation remains:

```text
./scripts/check_all
```

which enforces Ruff lint/format, strict Pyright, and pytest.

Dedicated Desktop CI independently verifies:

- pinned PySide6;
- desktop Ruff and strict Pyright;
- application/presentation/controller tests;
- the Qt-free core dependency boundary;
- isolated QML load;
- source startup smoke;
- standalone `pyside6-deploy` build;
- packaged offscreen startup smoke;
- standalone artifact upload.

## Authoritative references

Use these durable sources rather than conversation memory:

- `AGENTS.md` — operating rules;
- `docs/architecture/index.md` — platform architecture;
- `docs/architecture/native_quant_workbench.md` — desktop architecture through UI4;
- `docs/quantitative_conventions.md` — quantitative conventions;
- `docs/decisions/0002-mathematical-problem-architecture.md` — mathematical architecture doctrine;
- `docs/decisions/0003-native-desktop-workbench.md` — native UI boundary;
- `docs/models/m3_dynamic_delta_hedging.md`;
- `docs/models/m4_market_evidence_and_implied_volatility.md`;
- `docs/models/m5_heston_stochastic_volatility.md`;
- `docs/models/m6_heston_calibration.md`;
- `docs/evidence/m4_spx_implied_volatility_evidence.json`;
- `docs/evidence/m6_spx_heston_calibration_reference.json`;
- current source/tests/Issues/PRs/CI.

## Next pressure

M7 is responsible for actual empirical Black-Scholes-versus-Heston validation/model-risk conclusions. It must remain independent of UI4 presentation convenience.

UI5 should consume M7 only after M7 is merged and verified. It may also consume concrete M8 profiling/release evidence once that exists, but it should not pre-build generic validation, risk, performance, model-plugin, or reporting frameworks.
