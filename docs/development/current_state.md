# Current State

## Status

The quantitative-finance platform has completed **M0, M0A, M1, M2, M3, M4, M5, M6, M7, and M8**.

Completed quantitative milestones:

- **M0 — Engineering Bootstrap**;
- **M0A — Mathematical Quant-Finance Architecture Foundation**;
- **M1 — European Options & Black-Scholes Reference Vertical**;
- **M2 — Independent Valuation and Sensitivity/Greeks**;
- **M3 — Dynamic Hedging / Control**;
- **M4 — Market Evidence / Implied-Volatility Inference**;
- **M5 — Heston Stochastic Volatility & Independent Valuation**;
- **M6 — Heston Calibration / Multi-Parameter Inverse Problem**;
- **M7 — Empirical Validation, Model Risk & Black-Scholes vs Heston**; and
- **M8 — Performance Engineering & Measured Native-Acceleration Decision**.

Completed native milestones:

- **UI1 — Native Workbench Architecture & Black-Scholes Vertical**;
- **UI2 — Valuation Comparison, Numerical Evidence & Greeks**;
- **UI3 — Dynamic Hedging, Market Evidence & Scalar Inference**;
- **UI4 — Heston Forward Valuation, Calibration & Identifiability Workbench**; and
- **UI5 — Validation, Model Risk & Product Hardening**.

ADR 0002 remains the mathematical architecture authority. ADR 0003 remains the native PySide6 + Qt Quick/QML authority.

The next milestone is **M9 — Portfolio-Quality v0.1 Release**. M8 profiling established that a C++ numerical kernel is **not justified for the current v0.1 representative workloads** after Python/NumPy algorithmic optimization. UI5 now presents the authoritative M7 validation/model-risk evidence and the revision-pinned M8 before/after performance/parity evidence while preserving that measured no-C++ result rather than fabricating a native backend.

## Mathematical organization

```text
FINANCIAL / MATHEMATICAL FOUNDATIONS
state / state space
stochastic law
parameters
probability / measure semantics
numeraire
market observations + provenance
contracts / cash flows
quantitative conventions
        ↓
PROBLEM FAMILIES
pricing
inverse / inference
sensitivity
prediction
control / optimization
risk
validation
        ↓
METHODS
analytic / tree / Monte Carlo / Fourier / finite difference
root finding / optimization / filtering / regression / scenarios / tests
        ↓
SPECIFIC IMMUTABLE RESULTS / EVIDENCE
```

The durable execution pattern is:

```text
Problem + supported Method -> specific immutable Result / Evidence
```

Protect:

```text
financial state != market observation
raw observation != normalized observation != modeled value
state != stochastic law != parameters != calibrated estimate
contract != cash-flow stream
numeraire != pricing measure
pricing != sensitivity != control != inverse != validation
Delta sensitivity != hedge policy != realized hedge action
calibration != validation
training fit != held-out evaluation
model residual != quote width != numerical error
optimizer convergence != parameter identification != model validity
same-date holdout != temporal forecasting
Python financial semantics != accelerated numerical execution
```

## Quantitative capabilities

### Black-Scholes / M1–M2

The first pricing vertical supports European calls/puts, ACT/365F, a flat continuously compounded money-market numeraire, Black-Scholes closed form, CRR, seeded Monte Carlo, and analytic/finite-difference Delta, Gamma, Vega, Theta, and Rho.

### Dynamic hedging / M3

M3 consumes analytic Delta as a hedge-policy input over exact-transition pricing-measure GBM paths with explicit rebalance schedules, stock/cash self-financing accounting, volatility misspecification, proportional transaction costs, and replication-error summaries. These are model-generated replication experiments, not historical trading backtests.

### Market evidence / M4

M4 establishes provenance-bearing raw option/underlying observations, explicit midpoint normalization, Black-Scholes implied-volatility inversion with separate bisection, conditioning evidence, static quote diagnostics, and pinned January 4, 2023 SPX evidence showing strike skew and maturity dependence.

### Heston forward model / M5

M5 adds `HestonEquityState`, `HestonLaw`, immutable `HestonParameters`, independent characteristic-function/Fourier valuation, seeded full-truncation Euler Monte Carlo, Feller diagnostics, exact deterministic-variance handling at `xi=0`, and Fourier↔Monte-Carlo validation.

### Heston calibration / M6

M6 calibrates direct financial coordinates `(v0, kappa, theta, xi, rho)` in option-price space while keeping spot, flat rate and `q` explicit and fixed for the first consumer.

```text
HestonPriceCalibrationTarget(s)
+ financial bounds
+ price-space residual / weighting semantics
+ Heston Fourier forward map
        ↓
HestonCalibrationProblem
+ ScipyLeastSquaresHestonCalibration
        ↓
HestonCalibrationResult
```

Synthetic truth recovery, multiple starts, target perturbation, per-target residuals, and local domain-scaled Jacobian diagnostics establish that small objective and optimizer convergence do not imply unique or trustworthy parameters.

The committed full-sample SPX reference clusters near `v0≈0.04447`, `kappa≈3.2575`, `theta≈0.06622`, `xi≈0.62715`, `rho≈-0.77937`, with a full-rank but nontrivially conditioned local Jacobian.

## M7 validation / model-risk specialization

M7 is the first production specialization organized explicitly around **validation**.

```text
NormalizedOptionObservation(s)
+ predeclared TRAINING / EVALUATION partition
+ fixed financial inputs
+ one-volatility Black-Scholes benchmark domain
+ Heston calibration domain / Fourier forward map
        ↓
BlackScholesHestonValidationProblem
        +
CrossSectionalBlackScholesHestonValidation
        ↓
BlackScholesHestonValidationEvidence
```

No universal validation/risk/metric framework was introduced.

### Predeclared empirical design

The current real sample contains 14 selected SPX/SPXW contracts from one market date across two expiries, so M7 uses a same-date cross-sectional holdout rather than claiming temporal forecasting.

```text
sort by (expiry, strike)
evaluation iff zero-based index % 3 == 2
```

This yields **10 training / 4 held-out evaluation** observations. Both models consume the same training prices and bid/ask-half-spread residual scaling. Black-Scholes fits one constant annualized volatility; Heston uses the M6 five-coordinate calibration with three predeclared starts. Both fitted training models are frozen before held-out evaluation.

A regression test changes only held-out targets and verifies that the fitted training models and held-out model prices do not change.

### Reference result

The fitted Black-Scholes training volatility is approximately `0.20891`.

A representative selected Heston training estimate is approximately:

```text
v0      = 0.04425
kappa   = 3.4968
theta   = 0.06436
xi      = 0.59557
rho     = -0.81317
```

Held-out price-space evidence:

```text
                         Black-Scholes      Heston
price RMSE                   8.412           0.671
half-spread std. RMSE       20.613           1.649
relative MAE                 8.27%            0.66%
```

Within this predeclared sample and explicit assumptions, Heston materially improves held-out pricing metrics relative to the fairly fitted one-volatility Black-Scholes benchmark.

The conclusion is deliberately bounded. It does not establish temporal generalization, physical-measure forecasting skill, global Heston identification, historical trading profitability, or Heston hedge superiority.

### Stability / identification

The three Heston training starts converge to a tight cluster. The selected training Jacobian is full rank with domain-scaled condition number around `425`. A post-evaluation full-sample stability fit has condition number around `404`, with maximum train→full movement about `0.017` of the corresponding explicit M6 domain width.

This evidence must be read together with M6's deliberately rank-deficient thin-slice counterexample.

### M3 hedge boundary

M7 integrates M3 misspecification evidence but does not fabricate a Heston hedge study. M3 `SimulatedEquityPath` has explicit Black-Scholes/GBM provenance and the production backend does not yet own an authoritative Heston path + Delta + hedge-accounting composition.

```text
Heston held-out pricing advantage
!= demonstrated Heston hedging advantage
```

### Reproducible evidence

- `scripts/m7_model_validation.py` replays the pinned M4/M6 local raw-artifact path without network retrieval or raw-row redistribution;
- `docs/evidence/m7_spx_bs_vs_heston_validation_reference.json` is the compact derived reference artifact;
- `docs/models/m7_empirical_validation_and_model_risk.md` records design, evidence, limitations and the M8 handoff;
- deterministic CI fixtures cover the partition, comparison, no-leakage invariant, immutability and dependency direction.

## M8 performance engineering result

M8 profiled the six workloads predeclared by M7 before choosing any implementation target:

1. one Black-Scholes closed-form valuation;
2. one Heston Fourier valuation (`upper=100`, `intervals=256`);
3. one seeded Heston Monte Carlo valuation (`20,000` paths, `252` timesteps, seed `20260910`);
4. 10-target / 3-start Heston training calibration;
5. 14-target / 3-start Heston stability calibration; and
6. the complete M7 validation study.

Measured baseline hotspots were:

- scalar Python Heston Monte Carlo path propagation plus `10,080,000` scalar Gaussian draws; and
- repeated maturity-invariant Heston characteristic-function work across strikes during calibration.

M8 addressed those costs in Python first:

- Heston path state is propagated across NumPy arrays with a fresh local `PCG64` generator;
- compatible Heston Fourier prices are evaluated through a stateless maturity-batched numerical path;
- scalar Heston Fourier remains the readable correctness reference;
- calibration uses batching only in repeated optimizer residual evaluation, while final evidence is reconstructed through the scalar reference; and
- the exact `xi=0` deterministic-variance boundary explicitly falls back to the scalar reference.

Same-run baseline→optimized median evidence on the committed reference environment:

```text
Heston MC, 20k x 252                 3.3673 s -> 0.1230 s   27.38x
10-target / 3-start calibration      2.2919 s -> 0.4971 s    4.61x
14-target / 3-start calibration      3.2752 s -> 0.5454 s    6.01x
complete M7 validation study         5.4136 s -> 1.0819 s    5.00x
```

Deterministic financial parity checks pass. Because the MC implementation now uses NumPy PCG64 rather than the old scalar Python RNG, M8 uses statistical parity rather than equal-stream parity; the reference old/new MC values differ by only about `0.853` combined standard errors.

**No C++ kernel is retained in M8.** After the measured Python/algorithmic fixes, the remaining absolute cost does not justify a compiler/binding/cross-platform packaging and parity surface for v0.1. This result preserves Python as the financial-semantic/reference implementation and avoids a speculative backend abstraction.

See `docs/models/m8_performance_engineering.md`, `docs/evidence/m8_performance_reference.json`, `scripts/m8_profile_workloads.py`, and `scripts/m8_compare_performance.py`.

## Native Workbench through UI5

The durable dependency direction remains:

```text
Qt Quick / QML
        ↓
curated PySide6 controller / item models
        ↓
frontend-neutral application + presentation semantics
        ↓
public quantitative APIs + committed derived evidence
        ↓
production quantitative core
```

UI4 remains the authoritative Heston forward-valuation and calibration/identifiability workspace. UI5 adds a validation-first shell over M7, keeping training versus held-out evidence, residual structure, Heston stability/conditioning, unsupported Heston-hedging claims, and the mathematics inspector explicit.

UI5 also presents the merged M8 performance story through a package-safe mirror of the committed reference evidence: before/after representative workload timings, parity semantics, revision/environment provenance, and the measured negative C++ decision. It exposes no backend selector because M8 deliberately did not add a native backend.

Product hardening includes keyboard navigation, accessibility names, responsive layouts, explicit empty/running/result/warning/error boundaries, truthful busy-state-only long-running UX, a concrete copyable M7/M8 evidence report, process-isolated Qt controller tests, and continued standalone package/build/launch proof.

Generic saved-project/fork/document infrastructure remains absent because the repository still has no authoritative persisted study/workspace identity. Signing, notarization, installers and cross-platform release guarantees remain M9 release-target decisions.

`docs/architecture/native_quant_workbench.md` is authoritative for the detailed desktop architecture; `docs/models/ui5_validation_model_risk_and_product_hardening.md` records the UI5 scientific/product boundary.

## M9 next: portfolio-quality v0.1 release

M9 should consume the already-earned quantitative, validation, performance, and native-product evidence rather than add broad new model scope. Its performance story is fixed:

```text
representative M7 workloads
        ↓
profiled bottlenecks
        ↓
Python / algorithmic optimization
        ↓
4.61x–27.38x heavy-workload improvement
        ↓
parity retained
        ↓
C++ not justified for v0.1
```

M9 should package the flagship research narrative, reproducibility/provenance instructions, validation/model-risk conclusions and non-claims, measured M8 evidence, the completed UI5 Workbench, and release documentation.

## Deliberately absent

The repository intentionally still lacks:

- a generic validation/model-risk engine;
- generic VaR/ES/scenario/portfolio infrastructure;
- physical-measure Heston filtering/forecasting;
- Bayesian Heston inference;
- a generic optimizer/inverse hierarchy;
- arbitrage-free surface construction/repair infrastructure;
- Heston dynamic-hedging evidence;
- a generic model/plugin registry;
- a generic numerical-backend registry;
- a C++ numerical kernel for the current v0.1 workloads, because M8 measurements did not justify one;
- a generic persisted study/workspace/fork document model; and
- signed/notarized multi-platform installers before M9 selects a concrete release target.
