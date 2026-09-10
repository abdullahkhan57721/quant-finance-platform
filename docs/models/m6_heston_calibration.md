# M6 — Heston Calibration, Parameter Recovery, and Inverse-Problem Evidence

## Question

Can the platform infer Heston financial coordinates from known and observed option-price targets without collapsing the financial inverse problem into its numerical optimizer?

M6 preserves:

```text
Heston stochastic law
!= Heston structural parameter values
!= current variance state
!= calibrated estimate

calibration problem
!= residual/objective semantics
!= numerical optimizer
!= optimizer configuration/state
!= completed calibration result
```

## Financial coordinates

M5 established spot and instantaneous variance as current modeled state, while `HestonParameters` contains `kappa`, `theta`, `xi`, `rho`, and continuous dividend yield `q`. A same-date option cross-section depends materially on current variance, so M6 calibrates the five coordinates

```text
(v0, kappa, theta, xi, rho)
```

while keeping observed spot fixed, `q` fixed as an explicit calibration input, and risk-free accumulation in the existing money-market numeraire. A successful result therefore contains a calibrated `initial_variance` plus a **new immutable `HestonParameters` value**. M6 does not move `v0` into `HestonParameters` and never mutates `HestonLaw`.

## Target representation

The first calibration target space is **option price**, not implied volatility.

This choice is deliberate:

- M4 normalization produces observed option prices directly;
- M5 forward methods produce option prices directly;
- price-space calibration avoids embedding a Black-Scholes implied-volatility root solve inside every Heston objective evaluation;
- price-space and implied-volatility-space objectives are not equivalent because the Black-Scholes inverse map is Vega-conditioned;
- observed bid/ask widths can provide an explicit economic scale for price residuals.

Implied-volatility-space Heston calibration is deferred until a second real consumer justifies its exact semantics.

Synthetic model-generated price targets and normalized market targets are distinct immutable target sources. Synthetic prices never masquerade as observed data. A normalized market target keeps its M4 `NormalizedOptionObservation` and therefore its raw quote/underlying/provenance lineage.

## Objective and weighting

For target price `Y_i`, Heston model price `F_i(theta)`, and problem-owned price scale `s_i`, M6 minimizes

```math
L(theta) = sum_i ((F_i(theta) - Y_i) / s_i)^2.
```

Two policies are implemented because they answer concrete M6 questions:

1. `UNIFORM_PRICE`: `s_i = 1`, used for noiseless/synthetic truth recovery;
2. `BID_ASK_HALF_SPREAD`: `s_i = (ask_i - bid_i)/2`, used for normalized market calibration.

The scale/weighting is part of `HestonCalibrationProblem`. It is not an optimizer option. Bid/ask weighting requires normalized market targets with a strictly positive observed spread.

## Admissible financial domain

`HestonCalibrationBounds` records explicit bounds in the direct financial coordinate order

```text
v0, kappa, theta, xi, rho.
```

The default M6 research domain is:

```text
v0      in [0.0001, 1.0]
kappa   in [0.05,   15.0]
theta   in [0.0001, 1.0]
xi      in [0.0001, 5.0]
rho     in [-0.999, 0.999]
```

These are calibration-domain bounds, not a redefinition of M5 structural model validity. The Feller condition remains diagnostic and is not imposed as a calibration constraint.

The first optimizer uses direct financial coordinates. There is no optimizer-only parameter transform, so calibrated results never expose hidden transformed coordinates.

## Numerical method

`ScipyLeastSquaresHestonCalibration` is one concrete numerical method backed by `scipy.optimize.least_squares` with the trust-region reflective (`trf`) bound-constrained algorithm.

The method owns:

- initial guess;
- `ftol`, `xtol`, and `gtol`;
- maximum function evaluations;
- two-point numerical Jacobian construction;
- mutable optimizer iteration state;
- algorithm-level convergence/failure.

The problem owns targets, residual scaling, fixed financial inputs, admissible financial bounds, and the configured M5 Heston Fourier forward method.

SciPy/NumPy are introduced as M6's first core numerical dependencies because this is the first concrete multi-parameter nonlinear least-squares consumer. M6 does not introduce a generic optimizer framework.

## Completed result

`HestonCalibrationResult` is narrow and immutable. It retains:

- calibrated `initial_variance` and immutable `HestonParameters`;
- sum-squared standardized objective value;
- per-target model price, raw price residual, residual scale, and standardized residual;
- function/Jacobian evaluation counts;
- optimizer termination status/message;
- local Jacobian rank, singular values, and condition-number evidence.

It does not contain unrelated Greeks, hedge paths, portfolios, UI state, or market-data repair outputs.

## Identifiability / conditioning

Optimizer convergence is not sufficient evidence that parameters are trustworthy.

M6 takes the optimizer Jacobian of the **problem-standardized residual vector** and rescales each parameter column by that parameter's financial-domain width. If `J` is the weighted residual Jacobian and `D` is the diagonal matrix of calibration-domain widths, the reported singular values are those of

```math
J_scaled = J D.
```

This removes the most obvious arbitrary-unit effect when comparing the five financial coordinates. M6 reports numerical rank and, only for full column rank, the largest-to-smallest singular-value ratio as a local condition-number diagnostic.

This remains a local first-order diagnostic. It is not a posterior uncertainty distribution and not a proof of global identification.

## Synthetic truth recovery

M6 follows the required scientific order:

```text
choose known Heston truth
        ↓
generate option prices with validated M5 Fourier valuation
        ↓
construct M6 inverse problem without exposing truth to the optimizer
        ↓
calibrate from materially different starts
        ↓
compare estimated financial coordinates with known truth
```

The primary deterministic study uses

```text
v0    = 0.04
kappa = 2.0
theta = 0.04
xi    = 0.5
rho   = -0.7
q     = 0.01
```

across four maturities and five strikes per maturity. Multiple non-truth starts recover the known five coordinates to tight numerical tolerance with essentially zero price residual. This validates the complete forward-map -> residual -> bounded optimization -> immutable result path under a truth-known experiment.

A controlled alternating `+/- 0.02` price perturbation moves the recovered coordinates while retaining a small objective, explicitly demonstrating target sensitivity rather than treating the new estimate as optimizer noise.

## Non-identifiability experiment

A deliberately thin three-quote, one-maturity problem has only three residual equations for five unknown financial coordinates. Multiple starts converge to near-zero price loss but materially different Heston coordinates.

The local weighted Jacobian is rank deficient and therefore has no finite five-parameter condition number in M6's result semantics.

This is the milestone's direct demonstration that

```text
small calibration loss
!= unique parameter estimate
!= trustworthy parameter estimate.
```

## Real SPX calibration

`scripts/m6_heston_calibration.py` is the reproducible raw-data workflow. It performs no network retrieval. Given the same local pinned CSV used by M4, it executes:

```text
local raw SPX CSV
        ↓
RawOptionQuote + RawUnderlyingObservation + ObservationProvenance
        ↓
M4 normalize_european_option_midpoint
        ↓
same 14 pinned M4 OTM-side contracts
        ↓
HestonPriceCalibrationTarget
        ↓
bid/ask-half-spread price-space objective
        ↓
three predeclared starts
        ↓
best converged HestonCalibrationResult
```

The study keeps M4's January 4, 2023 SPX snapshot, expiries February 3 and April 28, flat continuously compounded rate `0.045`, continuous dividend yield `0.017`, ACT/365F time, and documented SPXW European/PM settlement semantics.

Raw rows are not committed because the pinned public source repository did not contain a license file when the evidence was produced. The script records a local SHA-256 and emits only derived/model evidence.

`docs/evidence/m6_spx_heston_calibration_reference.json` is a compact review artifact reconstructed from M4's already-published derived evidence. It does not replace the raw-artifact replay script.

The three-start reference fit clusters tightly around approximately

```text
v0    = 0.04447
kappa = 3.2575
theta = 0.06622
xi    = 0.62715
rho   = -0.77937
```

with a half-spread-standardized sum-squared objective around `12.56`. The local domain-scaled Jacobian is full rank but has condition number about `404`, so stable optimizer convergence coexists with nontrivial parameter conditioning.

That evidence is a calibration result, not a claim that Heston is valid or superior. M7 owns comparative model-risk conclusions.

## M4 vs M6: is a shared inverse runtime abstraction earned?

M4 and M6 now provide two real inverse consumers:

```text
M4
scalar monotone Black-Scholes volatility inversion
financial feasibility bounds + root bracketing + root convergence

M6
five-coordinate noisy Heston calibration
weighted residual semantics + bound-constrained least squares + identifiability evidence
```

What is genuinely shared is the **conceptual** responsibility split already supplied by ADR 0002:

```text
financial inverse question
!= numerical solution method
!= immutable completed result/evidence.
```

The operational responsibilities are still materially different. Extracting a universal runtime `InverseProblem`/`InverseMethod` hierarchy would currently hide more semantics than it would clarify. M6 therefore keeps M4 and M6 concrete and separate. A later third inverse consumer may reopen that decision if real duplicated behavior appears.

## Error / evidence taxonomy

M6 keeps distinct:

```text
observed quote uncertainty
price-target weighting choice
forward Heston numerical error
optimizer convergence failure
local calibration conditioning
rank deficiency / non-identifiability
initialization dependence
quote-perturbation sensitivity
calibration residual
model misspecification
```

In particular:

```text
optimizer converged
!= inverse problem reliably identified
!= model explains market well
!= model is valid.
```

## M7 handoff pressure

M6 leaves M7 with:

- one validated Heston forward model from M5;
- one explicit price-space Heston calibration problem;
- a provenance-preserving real-market calibration workflow;
- per-contract residuals;
- multi-start stability evidence;
- local conditioning evidence;
- a concrete non-identifiability counterexample.

M7 should now ask whether Heston's added flexibility earns its place relative to Black-Scholes under in-sample fit, out-of-sample pricing, stability, residual structure, hedging evidence where semantically valid, and computational cost.
