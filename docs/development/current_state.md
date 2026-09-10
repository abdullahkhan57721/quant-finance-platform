# Current State

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Quant-Finance Architecture Foundation is complete.**

**M1 — European Options & Black-Scholes Reference Vertical is complete.**

**M2 — Independent Valuation and Sensitivity/Greeks is complete.**

**M3 — Dynamic Hedging / Control is complete.**

**M4 — Market Evidence / Inverse Problems is complete.**

**M5 — Heston Model and Independent Valuation is complete.** M5 establishes the first stochastic-volatility pricing specialization with explicit spot/instantaneous-variance state, immutable Heston parameter values, characteristic-function/Fourier valuation, independent full-truncation Euler Monte Carlo valuation, explicit numerical diagnostics, limiting-case evidence, and cross-method validation.

**M6 — Heston Calibration / Inverse Problem is complete.** M6 establishes the first multi-parameter noisy financial inverse problem with explicit price targets, problem-owned objective/weighting, admissible financial bounds, a separate SciPy bound-constrained least-squares method, synthetic truth recovery, multiple-start/perturbation evidence, local Jacobian identifiability diagnostics, and a provenance-preserving SPX calibration workflow.

**UI1 — Native Quant Research Workbench Architecture & Black-Scholes Vertical Slice is complete and establishes the current desktop architecture.**

**UI2 — M2 Valuation Comparison, Convergence, Uncertainty & Greeks Workbench is complete.** UI2 extends the existing Black-Scholes Study over the actual merged M2 pricing and sensitivity contracts without adding UI-owned finance semantics or a generic desktop framework.

**UI3 — Dynamic Hedging, Market Evidence & Inverse-Problem Workbench is complete.** UI3 adds separate native M3 control and M4 observed-market/inference workflows, a three-question workflow home, paired hedge-comparison evidence, raw/normalized/inferred observation inspection, provenance, conditioning, discrete smile/skew evidence, and route-specific mathematical inspectors without adding UI-owned finance semantics or a generic workflow framework.

ADR 0002 remains the platform-wide mathematical architecture authority. M2 pressure-tested the M0A/M1 pricing boundary with independent numerical methods and established the first concrete production sensitivity family. M3 established the first concrete control/dynamic-replication family. M4 established the first production observed-market boundary and scalar inverse-problem specialization. M5 proved that the pricing architecture can host a materially richer two-factor stochastic law and independent valuation methods. M6 now proves that calibration can consume those forward-model and observation semantics while remaining a separate financial inverse problem whose objective, admissible domain, numerical method, result, and identifiability evidence remain distinct. ADR 0003 remains the native PySide6 + Qt Quick/QML authority.

The next finance-model milestone is **M7 — Empirical Validation, Model Risk, and Black-Scholes vs Heston Comparison**. The next desktop milestone is **UI4**, which may now consume stable M5 Heston forward-pricing contracts and, after M6 is merged, authoritative M6 calibration outputs rather than speculating about calibration semantics in QML.

## What exists

The repository now establishes:

- a `src/`-layout Python package with pytest, Ruff, strict Pyright, GitHub Actions CI, NumPy, and SciPy;
- the M0A production pricing composition under `qf_platform.pricing`;
- M1 European call/put, Black-Scholes/GBM, ACT/365F, money-market numeraire, and closed-form valuation semantics;
- three valuation methods over the same M1 `PricingProblem`: `BlackScholesClosedForm`, `CoxRossRubinstein`, and `MonteCarloEuropeanOption`;
- method-specific Monte Carlo uncertainty through immutable `MonteCarloValuationResult`;
- the first concrete sensitivity family under `qf_platform.sensitivity` with analytic and finite-difference Black-Scholes Delta, Gamma, Vega, Theta, and Rho;
- the first concrete control/dynamic-replication package under `qf_platform.control`, including exact-transition pricing-measure GBM paths, Delta hedge policy, self-financing accounting, misspecification studies, and transaction-cost evidence;
- the first production observed-market package under `qf_platform.market_data`, with immutable raw observations, provenance, explicit midpoint normalization, and narrow strike-slice diagnostics;
- M4's Black-Scholes implied-volatility inverse problem, separate bisection method, immutable result, feasibility checks, M2-Vega conditioning evidence, deterministic CI fixture, and pinned SPX strike/maturity evidence;
- `HestonEquityState`, `HestonStateSpace`, `HestonLaw`, and immutable `HestonParameters` under the existing pricing architecture;
- reuse of the existing `EuropeanOption` contract under Heston rather than a model-specific duplicate;
- `HestonFourierEuropeanOption` with explicit integration domain/resolution, stable characteristic-function branch semantics, and immutable quadrature diagnostics;
- `HestonMonteCarloEuropeanOption` with explicit paths, timesteps, integer seed, local RNG ownership, correlated shocks, full-truncation Euler variance dynamics, sampling uncertainty, and negative-variance proposal diagnostics;
- exact deterministic-variance handling at `xi = 0`, validated against the independent Black-Scholes closed form using integrated deterministic variance;
- M5 evidence covering state/parameter domains, Feller-diagnostic semantics, boundaries, parity, Fourier convergence, seeded Monte Carlo reproducibility, variance-boundary pressure, and Fourier ↔ Monte Carlo agreement;
- `HestonPriceCalibrationTarget`, `HestonCalibrationCoordinates`, `HestonCalibrationBounds`, `HestonCalibrationProblem`, `HestonCalibrationResidual`, `HestonCalibrationConditioning`, and `HestonCalibrationResult` under `qf_platform.inference`;
- `ScipyLeastSquaresHestonCalibration`, a concrete bounded trust-region-reflective nonlinear least-squares method that consumes problem-owned standardized price residuals rather than owning finance-domain semantics;
- synthetic M6 recovery evidence across multiple strikes/maturities and materially different starts, controlled target perturbation evidence, and a deliberately rank-deficient low-loss counterexample;
- a reproducible M4-derived SPX Heston calibration script and derived reference artifact retaining source/provenance assumptions without redistributing the raw source rows;
- the native PySide6 + Qt Quick/QML Quant Research Workbench through UI3; and
- dedicated desktop validation including offscreen/QML smoke and standalone build/launch proof.

## Mathematical architecture

The platform-wide conceptual pattern remains:

```text
Problem + supported Method -> specific immutable Result
```

This is a responsibility pattern, not a universal runtime inheritance tree.

### Pricing

For Black-Scholes:

```text
same PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
        ↓
ValuationResult or method-specific subtype
```

For Heston:

```text
HestonEquityState(spot, instantaneous variance)
+
HestonLaw + HestonParameters
+
existing EuropeanOption
+
existing money-market numeraire + pricing measure
        ↓
PricingProblem
        ├── HestonFourierEuropeanOption
        └── HestonMonteCarloEuropeanOption
        ↓
method-specific immutable valuation evidence
```

### Sensitivity

```text
BlackScholesSensitivityProblem
        +
supported sensitivity method
        ↓
BlackScholesSensitivityResult
```

### Control / dynamic replication

```text
Black-Scholes pricing problem
        +
model-generated path semantics
        +
rebalance schedule
        +
AnalyticDeltaHedgePolicy
        +
stock/cash financing and cost convention
        ↓
DeltaHedgeResult
        ↓
ReplicationErrorSummary
```

### Scalar inverse inference — M4

```text
raw option + underlying observations
        +
provenance
        ↓
explicit normalization
        ↓
NormalizedOptionObservation
        +
BlackScholesImpliedVolatilityProblem
        +
BisectionImpliedVolatility
        ↓
ImpliedVolatilityResult
```

### Multi-parameter calibration — M6

```text
synthetic target
or
NormalizedOptionObservation + provenance
        ↓
HestonPriceCalibrationTarget
        +
fixed spot / rate / q
        +
financial calibration bounds
        +
price-space objective / weighting
        ↓
HestonCalibrationProblem
        +
ScipyLeastSquaresHestonCalibration
        ↓
HestonCalibrationResult
        +
per-target residual evidence
        +
domain-scaled Jacobian conditioning
```

M4 and M6 now provide two real inverse consumers. What is genuinely shared is the conceptual ADR-0002 split:

```text
financial inverse problem
!= numerical solution method
!= immutable completed result/evidence
```

Their operational responsibilities are still materially different. M4 owns scalar financial feasibility/bracketing/root semantics; M6 owns weighted multi-target mismatch, a five-coordinate admissible domain, bound-constrained least squares, and local identifiability evidence. The repository therefore still intentionally has **no universal runtime `InverseProblem`, optimizer, or inference hierarchy**.

Protect:

```text
pricing problem != sensitivity problem != control problem != inverse problem
financial model != numerical method != path simulation
raw observation != normalized observation != modeled state
observed price != model price != implied volatility != calibrated parameter estimate
inverse financial problem != root finder / optimizer != inverse result
calibration objective / weighting != optimizer configuration
financial/model-domain constraint != optimizer bound mechanism != parameter transform
Delta sensitivity != hedge policy != realized hedge action
replication error != model error by definition
Heston state != Heston law != Heston parameter values != calibrated estimate
optimizer converged != inverse problem reliably identified != model valid
```

## M3 dynamic hedging / control

M3 turns Black-Scholes Delta from a static sensitivity into a dynamic policy input while preserving the responsibility boundary:

```text
Delta = dV/dS
        ↓
current-state policy evaluation
        ↓
target stock units
        ↓
explicit rebalance action
        ↓
realized stock/cash hedge trajectory
```

`BlackScholesPathSimulation` / `simulate_black_scholes_path` sample exact adjacent-date GBM transitions under the configured M1 money-market pricing measure. Observation dates are sample/output dates rather than Euler timesteps and remain distinct from hedge rebalance dates.

The first problem is one short European option. Initial hedge wealth equals the hedging-model Black-Scholes value; stock targets are M2 analytic Delta and residual cash earns through the existing money-market account. M3 evidence establishes seeded reproducibility, no-lookahead behavior, self-financing identities, rebalance-frequency effects, volatility misspecification, transaction-cost drag, and replicate-integrity rules. Hedge execution currently requires zero continuous dividend yield until dividend/carry cash-flow accounting is explicit.

See `docs/models/m3_dynamic_delta_hedging.md`.

## M4 observed market evidence / scalar inverse problem

M4 productionizes the observation/model boundary:

```text
real market
    ↓
RawOptionQuote + RawUnderlyingObservation
    + ObservationProvenance
    ↓
normalize_european_option_midpoint
    ↓
NormalizedOptionObservation
    ↓
BlackScholesImpliedVolatilityProblem
    + BisectionImpliedVolatility
    ↓
ImpliedVolatilityResult
```

Raw option quotes retain source/provenance and bad finite raw observations; normalization decides admissibility. The first normalization policy requires matching underlying/date, European exercise, PM-compatible date-only settlement semantics, positive present bid/ask, a non-crossed market, and positive observed spot.

M4 solves Black-Scholes price for `sigma` with the financial inverse problem separate from bisection. European price bounds are checked before numerical solving. Financial inconsistency, an unbracketed admissible interval, and numerical non-convergence are distinct failures. M2 analytic Vega supplies local conditioning evidence after inference.

The pinned January 4, 2023 SPX evidence shows persistent downside strike skew in approximately 30-day and 114-day slices plus maturity dependence under explicit flat rate/carry assumptions. One constant Black-Scholes volatility cannot reconcile the selected observed option set. M4 records narrow static quote violations rather than repairing a surface.

See `docs/models/m4_market_evidence_and_implied_volatility.md` and `docs/evidence/m4_spx_implied_volatility_evidence.json`.

## M5 Heston stochastic volatility / independent valuation

M5 responds to M4's observed strike-skew/maturity-dependence pressure with a richer forward model:

```text
dS_t = (r - q) S_t dt + sqrt(v_t) S_t dW^S_t

dv_t = kappa (theta - v_t) dt + xi sqrt(v_t) dW^v_t

d<W^S, W^v>_t = rho dt
```

`HestonEquityState` carries spot and instantaneous annualized variance. `HestonParameters` carries `kappa`, `theta`, `xi`, `rho`, and continuous dividend yield while the numeraire owns the risk-free accumulation rate. The Feller condition is diagnostic rather than universally enforced.

`HestonFourierEuropeanOption` owns characteristic-function quadrature configuration; `HestonMonteCarloEuropeanOption` owns stochastic simulation configuration and full-truncation Euler. At `xi = 0`, the model follows the exact deterministic-variance boundary and reduces to Black-Scholes using integrated deterministic variance. Validation includes parity, limits, numerical convergence, seeded MC reproducibility, boundary pressure, and Fourier/MC agreement.

See `docs/models/m5_heston_stochastic_volatility.md`.

## M6 Heston calibration / multi-parameter inverse problem

M6 treats calibration as a financial inverse problem rather than a method on `HestonLaw`.

The five inferred financial coordinates are:

```text
(v0, kappa, theta, xi, rho)
```

`v0` remains state-like and is returned separately from a new immutable `HestonParameters`. Observed/model spot, flat risk-free rate, and continuous dividend yield remain fixed explicit inputs for this first calibration consumer.

The first target representation is option price. The implemented standardized residual is

```text
(model price - target price) / residual scale
```

with only two problem-owned weighting policies:

```text
UNIFORM_PRICE
    scale = 1

BID_ASK_HALF_SPREAD
    scale = (ask - bid) / 2
```

The second policy requires a normalized market target with strictly positive spread. Implied-volatility-space calibration is intentionally not treated as equivalent and remains deferred.

`HestonCalibrationBounds` records named finite financial-domain bounds on all five coordinates. These are distinct from broader M5 model validity and from optimizer mechanics. The Feller condition remains diagnostic rather than becoming an optimizer constraint. No parameter transform is used in the first method.

`ScipyLeastSquaresHestonCalibration` owns only numerical search strategy/configuration: SciPy trust-region-reflective bounded least squares, two-point numerical Jacobian, initial guess, tolerances, and maximum function evaluations. The problem owns what is fitted and how mismatch is interpreted.

### Synthetic recovery and stability evidence

The primary deterministic study generates a 20-option surface from known truth:

```text
v0    = 0.04
kappa = 2.0
theta = 0.04
xi    = 0.5
rho   = -0.7
q     = 0.01
```

across four maturities and five strikes per maturity. Multiple materially different non-truth starts recover the known coordinates to tight numerical tolerance with essentially zero price residual. Controlled target-price perturbations move recovered coordinates while retaining a small objective, exposing target sensitivity explicitly.

A deliberately underdetermined three-quote/one-maturity study produces the opposite evidence: multiple starts obtain near-zero price loss but materially different five-parameter estimates. The local Jacobian is rank deficient. This is a regression-level demonstration that:

```text
small objective
!= unique parameters
!= trustworthy parameters
```

### Conditioning evidence

For the problem-standardized residual Jacobian `J`, M6 reports singular values of

```text
J_scaled = J D
```

where `D` scales columns by the corresponding finite calibration-domain widths. Rank and a finite largest/smallest singular-value condition number are reported only when the five-coordinate Jacobian has full column rank. This is local first-order identification evidence, not posterior uncertainty or proof of global uniqueness.

### Real SPX calibration

`scripts/m6_heston_calibration.py` consumes the same pinned local raw SPX artifact and 14 selected M4 contracts through:

```text
raw local CSV
→ M4 raw observations + provenance
→ M4 midpoint normalization
→ M6 market targets
→ half-spread-standardized price calibration
```

The three-start reference fit clusters near:

```text
v0      ≈ 0.04447
kappa   ≈ 3.2575
theta   ≈ 0.06622
xi      ≈ 0.62715
rho     ≈ -0.77937
```

with standardized sum-squared objective around `12.56`. The local domain-scaled Jacobian is full rank but has condition number about `404`: optimizer convergence is stable for this selected sample, while parameter conditioning remains nontrivial. This is calibration evidence, not a claim that Heston is correct or superior.

See `docs/models/m6_heston_calibration.md` and `docs/evidence/m6_spx_heston_calibration_reference.json`.

## Native Workbench boundary

The durable desktop dependency direction remains:

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

QML owns no pricing, inference, quote normalization, calibration objective/weighting, constraints, optimizer, conditioning, sensitivity, hedging, or validation semantics. The Python/application side owns quantitative normalization, compatibility, execution, results, diagnostics, and provenance interpretation.

UI1 remains the first Black-Scholes analytical vertical. UI2 adds M2 valuation comparison/convergence/uncertainty/Greeks over authoritative backend contracts. UI3 adds separate dynamic-hedging and market-evidence/implied-volatility workflows while preserving their distinct mathematical questions and provenance/evidence semantics.

The later UI4 milestone should consume actual M5/M6 outputs. In particular, calibration target construction, weighting, bounds, optimizer logic, and identifiability calculations must remain outside QML.

See `docs/architecture/native_quant_workbench.md` and ADR 0003.

## Error and evidence taxonomy

The accumulated evidence keeps different mechanisms separate:

```text
financial model / misspecification effect
CRR discretization / approximation error
Fourier truncation / quadrature error
complex characteristic-function numerical stability
Monte Carlo valuation sampling error
Heston time-discretization bias
variance-boundary discretization effect
finite-difference truncation error
finite-difference cancellation / floating-point error
discrete hedge-rebalancing error
stochastic hedge-replicate variation
transaction-cost effect
observed quote width / data-quality effect
implied-volatility inverse conditioning through Vega
calibration target / weighting choice
optimizer convergence failure
calibration initialization dependence
calibration target-perturbation sensitivity
local parameter rank deficiency / ill-conditioning
calibration residual
analytical floating-point error
```

A terminal hedging discrepancy is not automatically model error. A Monte Carlo interval is not a deterministic pricing tolerance. Fourier/MC disagreement is not automatically model error. A converged implied-volatility root is not automatically well conditioned. A converged low-loss Heston calibration is not automatically uniquely identified, economically stable, or evidence that Heston is valid.

## Quality and development cadence

The canonical core gate remains:

```text
Ruff lint
Ruff format check
strict Pyright
pytest
```

Desktop dependencies/checks remain isolated in the dedicated Desktop workflow. `scipy-stubs` is a development-only dependency so SciPy-backed M6 code remains covered by strict Pyright rather than weakening type checking.

At the first fully green M6 implementation candidate on September 10, 2026, hosted core CI reported Ruff clean, 106 tracked Python files formatted, strict Pyright with zero errors/warnings, and **177 passing tests with 4 desktop tests skipped** in core CI because PySide6 is an optional desktop dependency. Final documentation/reconciliation heads must still pass the same canonical gates before merge.

## Deliberately absent

The following remain absent until later milestones create real consumers:

- generic stochastic-control, trading-strategy, execution, trade, or portfolio frameworks;
- physical-measure forecasting/path semantics for M3;
- nonzero-dividend hedge cash-flow accounting;
- generic/live market-data-provider framework;
- generic quote-cleaning or staleness framework;
- generic volatility-surface construction/interpolation/repair framework;
- universal inverse/inference or optimizer framework despite M4 and M6;
- Bayesian Heston inference, filtering, or physical-measure Heston estimation;
- generic calibration weighting/loss or parameter-transform framework;
- Heston calibration UI/QML ownership;
- generic Fourier/quadrature or stochastic-simulator/factor-model infrastructure;
- discount/dividend curve inference from option chains;
- full put-call-parity forward extraction infrastructure;
- native/C++ quantitative backends before M8 profiling; and
- generic UI schema/form generation, node editors, plugin architecture, universal plotting grammar, or universal background-job infrastructure.

## Next objectives

### M7 — Empirical Validation, Model Risk, and Black-Scholes vs Heston Comparison

M7 should ask whether Heston's added flexibility earns its place relative to Black-Scholes under evidence that was unavailable before M6.

It should consume, not redefine:

- M4 raw/normalized option observations and provenance;
- M4 Black-Scholes implied-volatility evidence;
- M5 independent Heston forward valuation;
- M6 calibrated Heston coordinates, per-target residuals, multi-start evidence, and local conditioning diagnostics;
- M3 hedging evidence only where the comparison is mathematically/operationally valid.

The comparison should distinguish at least:

```text
in-sample fit
out-of-sample pricing performance
residual structure
parameter stability / identifiability
input / quote perturbation sensitivity
calibration convergence
computational cost
model assumptions / failure modes
```

Protect:

```text
better in-sample fit != better out-of-sample model
optimizer convergence != trustworthy calibration
more flexible model != lower model risk
calibrated parameter stability != model validity
```

M7 owns the actual Black-Scholes-versus-Heston model-risk conclusion.

### UI4 — Heston valuation and calibration workspace

UI4 may now be designed from actual merged M5/M6 backend contracts. It may visualize forward Heston prices, targets versus model prices, residuals, parameter estimates, multiple-start outcomes, and conditioning evidence, but must not reimplement calibration objectives, weighting, constraints, optimization, or diagnostics in QML.
