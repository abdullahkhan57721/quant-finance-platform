# M5 — Heston Stochastic Volatility and Independent Valuation

## Purpose

M4 established a concrete empirical limitation of constant-volatility Black-Scholes:
under explicit option-observation, rate, carry, and quote-selection assumptions, the
SPX evidence produces systematic strike skew and maturity dependence in
Black-Scholes implied volatility.

M5 responds to that specific pressure by adding a **stochastic-volatility law** and
then valuing the same European-option financial question by two independent methods.
It does not calibrate Heston to M4 observations. Calibration remains a separate M6
inverse problem.

Protect throughout:

```text
Heston current state
!= Heston stochastic law
!= Heston parameter values
!= Fourier valuation method
!= Monte Carlo valuation method
!= future calibrated parameter values
```

## Model semantics

Under the existing flat money-market pricing measure, M5 uses

```math
\mathrm dS_t=(r-q)S_t\,\mathrm dt+\sqrt{v_t}S_t\,\mathrm dW_t^S,
```

```math
\mathrm dv_t=\kappa(\theta-v_t)\,\mathrm dt
+\xi\sqrt{v_t}\,\mathrm dW_t^v,
```

with

```math
\mathrm d\langle W^S,W^v\rangle_t=\rho\,\mathrm dt.
```

Repository notation maps as follows:

| Mathematical object | Production meaning |
| --- | --- |
| `S_t` | `HestonEquityState.spot` |
| `v_t` | `HestonEquityState.instantaneous_variance` |
| `kappa` | `HestonParameters.mean_reversion_speed` |
| `theta` | `HestonParameters.long_run_variance` |
| `xi` | `HestonParameters.volatility_of_variance` |
| `rho` | `HestonParameters.correlation` |
| `q` | `HestonParameters.continuous_dividend_yield` |
| `r` | existing `FlatMoneyMarketNumeraire` rate |

The risk-free accumulation rate is deliberately not duplicated in
`HestonParameters`. It remains part of numeraire/pricing-measure semantics.

`HestonEquityState` refines the existing `EquityState` with instantaneous variance.
The existing `EuropeanOption` therefore remains the contract semantic; M5 does not
invent a Heston-specific option merely because the state has a second component.

## Parameter domain and the Feller condition

M5 requires:

```text
kappa > 0
theta >= 0
xi >= 0
-1 <= rho <= 1
v0 >= 0
```

The classical CIR/Heston Feller inequality is

```math
2\kappa\theta\ge \xi^2.
```

M5 exposes

```text
HestonParameters.feller_discriminant
HestonParameters.feller_condition_satisfied
```

as explicit diagnostic evidence. The inequality is a sufficient condition associated
with strict positivity of the variance process; M5 does **not** turn it into a
universal constructor-validity requirement. The production tests deliberately include
a Feller-violating parameter set that remains supported by the implemented valuation
methods.

## Fourier / characteristic-function valuation

`HestonFourierEuropeanOption` is a deterministic valuation method. It owns numerical
integration configuration and does not make quadrature part of `HestonLaw`.

For `xi > 0`, define

```math
b(u)=\kappa-\rho\xi iu,
```

```math
d(u)=\sqrt{b(u)^2+\xi^2(iu+u^2)},
```

```math
g(u)=\frac{b(u)-d(u)}{b(u)+d(u)}.
```

The implementation chooses the square-root branch so that the real part of `d` is
non-negative (and the non-negative-imaginary branch when the real part is zero). It
then uses the stable `g` representation

```math
\phi(u)=\exp\{C(u,T)+D(u,T)v_0\},
```

where

```math
C(u,T)=iu[\log S_0+(r-q)T]
+\frac{\kappa\theta}{\xi^2}
\left[(b-d)T-2\log\left(\frac{1-ge^{-dT}}{1-g}\right)\right],
```

and

```math
D(u,T)=\frac{b-d}{\xi^2}
\frac{1-e^{-dT}}{1-ge^{-dT}}.
```

The European call probabilities are evaluated as

```math
P_1=\frac12+\frac1\pi\int_0^\infty
\Re\left[
\frac{e^{-iu\log K}\phi(u-i)}{iu\phi(-i)}
\right]\,\mathrm du,
```

```math
P_2=\frac12+\frac1\pi\int_0^\infty
\Re\left[
\frac{e^{-iu\log K}\phi(u)}{iu}
\right]\,\mathrm du.
```

Then

```math
C_0=S_0e^{-qT}P_1-Ke^{-rT}P_2.
```

The put is obtained from the same `P1`/`P2` quantities,

```math
P_0=Ke^{-rT}(1-P_2)-S_0e^{-qT}(1-P_1),
```

which is algebraically consistent with put-call parity under the repository's existing
rate/carry conventions.

### Numerical integration

M5 uses composite Simpson quadrature over a configured finite positive frequency
interval. Defaults are:

```text
lower frequency = 1e-8
upper frequency = 100
intervals       = 2048 (even)
```

The lower endpoint avoids directly evaluating the removable `1/u` singularity. The
upper bound and interval count are **method configuration**, so Fourier truncation and
quadrature error remain visible rather than becoming hidden model semantics.

`HestonFourierValuationResult` records the integration bounds, interval count, and
characteristic-function evaluation count in addition to present value.

## Exact deterministic-variance boundary

When

```math
\xi=0,
```

the variance path is deterministic:

```math
v(t)=\theta+(v_0-\theta)e^{-\kappa t}.
```

Its integrated variance is

```math
I_T=\int_0^T v(t)\,\mathrm dt
=\theta T+(v_0-\theta)\frac{1-e^{-\kappa T}}{\kappa}.
```

Therefore terminal log spot is exactly Black-Scholes/lognormal with effective constant
volatility

```math
\sigma_{\mathrm{eff}}=\sqrt{I_T/T}.
```

M5 treats this as an exact model boundary, not as a fragile small-`xi` numerical
limit. The Fourier method delegates this boundary to the existing independent
Black-Scholes analytic implementation. Tests independently reconstruct `I_T` and
confirm equality.

## Independent Monte Carlo valuation

`HestonMonteCarloEuropeanOption` owns:

```text
paths
number of model-time steps
integer RNG seed
variance discretization scheme
```

Each application creates fresh local `random.Random(seed)` state. Equal method
configuration and seed therefore reproduce the current Python implementation, without
making any promise that a future native/C++ backend must share Python's random stream.

### Correlated shocks

For independent standard-normal draws `Z_v` and `Z_perp`, M5 constructs

```math
Z_S=\rho Z_v+\sqrt{1-\rho^2}Z_\perp.
```

This gives the configured instantaneous Brownian correlation while retaining explicit
local RNG ownership.

### Full-truncation Euler

For `xi > 0`, let

```math
v_n^+=\max(v_n,0).
```

The implemented variance update is

```math
v_{n+1}=v_n+\kappa(\theta-v_n^+)\Delta t
+\xi\sqrt{v_n^+}\sqrt{\Delta t}\,Z_v,
```

while log spot uses

```math
\log S_{n+1}=\log S_n
+\left(r-q-\frac12v_n^+\right)\Delta t
+\sqrt{v_n^+}\sqrt{\Delta t}\,Z_S.
```

The raw Euler variance is retained; its positive part is used in both the variance drift
and diffusion and in the spot update. The result records
`negative_variance_proposals`, the number of raw next-step variance proposals below
zero. This is **variance-boundary discretization evidence**, not model error and not a
claim that the continuous-time Heston variance became negative.

For exact `xi=0`, Monte Carlo samples terminal log spot directly from `I_T`, so that
boundary has sampling uncertainty but no Heston timestep-discretization bias.

`HestonMonteCarloValuationResult` preserves the M2 Monte Carlo fields

```text
present value
standard error
normal-approximation 95% confidence interval
paths
seed
```

and adds

```text
time_steps
negative_variance_proposals
variance_scheme
```

The confidence interval remains estimator sampling uncertainty. It does not include a
confidence statement about timestep bias or financial-model error.

## Validation evidence

M5 validation intentionally uses several logically different sources of evidence.

### Structural evidence

Tests establish:

- Heston state is immutable and refines the existing equity spot state;
- model parameters are immutable and domain-checked;
- Feller violation is diagnostic rather than structural invalidity;
- Heston valuation methods reject Black-Scholes pricing problems;
- the existing European-option contract is reused.

### Theoretical / limiting evidence

Tests establish:

- exact expiry payoff behavior;
- zero-spot discounted put behavior;
- put-call parity under the existing `r`/`q` semantics;
- exact `xi=0` agreement with independently constructed Black-Scholes effective
  volatility.

### Fourier numerical evidence

For the committed non-degenerate reference problem

```text
S0    = 100
K     = 100
T     = 1 ACT/365F model year
r     = 0.03
q     = 0.01
v0    = 0.04
kappa = 2.0
theta = 0.04
xi    = 0.50
rho   = -0.70
```

which deliberately violates the Feller inequality, the configured Fourier call value
is approximately

```text
8.2528489705
```

and the coarse/fine integration study verifies stability as the finite integration
range/resolution are increased.

### Monte Carlo evidence

Tests establish:

- exact seeded reproducibility for equal configuration;
- nonzero sampling standard error for stochastic valuation;
- explicit negative-variance proposal counts for full-truncation boundary pressure;
- exact deterministic-variance scheme labeling at `xi=0`; and
- Monte Carlo/Fourier agreement for a non-degenerate Heston problem under a tolerance
  that separately admits Monte Carlo sampling uncertainty and a small explicit
  timestep-bias allowance.

The agreement is validation evidence, not proof that either implementation is correct
by itself; parity and limiting evidence remain independent checks.

## Error taxonomy

Keep distinct:

```text
financial-model misspecification
Fourier finite-domain truncation error
Fourier quadrature error
complex-function / floating-point stability
Monte Carlo sampling error
Heston timestep-discretization bias
variance-boundary discretization effect
ordinary floating-point error
```

In particular:

```text
Fourier - Monte Carlo difference
!= financial-model error by definition
```

## Formula and method provenance

Primary model / characteristic-function source:

- Steven L. Heston, “A Closed-Form Solution for Options with Stochastic Volatility
  with Applications to Bond and Currency Options,” *The Review of Financial Studies*,
  6(2), 1993, 327–343. DOI: `10.1093/rfs/6.2.327`.

Full-truncation Euler source:

- Roger Lord, Remmert Koekkoek, and Dick van Dijk, “A comparison of biased simulation
  schemes for stochastic volatility models,” *Quantitative Finance*, 10(2), 2010,
  177–194. DOI: `10.1080/14697680802392496`.

M5 uses these as mathematical/numerical provenance, while the production notation,
ownership boundaries, deterministic `xi=0` specialization, and validation design are
repository-specific.

## Deliberate non-goals

M5 does not add:

- Heston calibration or parameter inference;
- a fit to the M4 SPX option evidence;
- a generic inverse-problem or optimizer framework;
- a generic Fourier/quadrature framework;
- a generic stochastic simulator;
- a factor-model/component registry;
- a volatility-surface object/interpolator/repairer;
- Heston hedging/control modifications to M3;
- Heston Greeks as a new production sensitivity family;
- PDE valuation;
- physical-measure forecasting;
- C++ acceleration; or
- desktop/UI behavior.

Those boundaries are intentional. M6 may consume the validated Heston valuation
methods when it introduces the distinct inverse question of inferring parameter values.
