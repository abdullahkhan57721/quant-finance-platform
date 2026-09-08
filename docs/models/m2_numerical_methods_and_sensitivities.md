# M2 Numerical Valuation and Black-Scholes Sensitivities

## Purpose

M2 adds two independent valuation methods to the same financial pricing problem established by M1, and introduces the platform's first production sensitivity specialization.

```text
same M1 PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
        ↓
method-specific evidence
```

separately:

```text
BlackScholesSensitivityProblem
        ├── AnalyticBlackScholesSensitivity
        └── FiniteDifferenceBlackScholesSensitivity
        ↓
BlackScholesSensitivityResult
```

The architecture therefore continues to protect:

```text
financial problem != solution method != completed result
pricing problem != sensitivity problem
GBM stochastic law != Monte Carlo valuation method
simulated states != theoretical price
```

M1's assumptions, notation, pricing-measure semantics, and formula references remain documented in `docs/models/black_scholes.md`.

## CRR: model and approximation are related but distinct interpretations

For maturity `T`, `n` tree steps, and `dt = T/n`, M2 uses the Cox-Ross-Rubinstein construction

```text
u = exp(sigma * sqrt(dt))
d = 1 / u
g = exp((r - q) * dt)
p = (g - d) / (u - d)
```

with one-step money-market discount

```text
exp(-r * dt).
```

At a **fixed finite** `n`, this is a discrete-time complete-market financial model only when

```text
d < g < u,
```

which is equivalent here to the risk-neutral probability satisfying

```text
0 < p < 1.
```

M2 exposes failure of that configured finite model through the valuation-method support boundary. A pricing problem can remain structurally valid and analytically priceable even when a particular coarse CRR configuration is unsupported.

Across increasing `n`, M2 also uses the CRR construction as a numerical approximation to the continuous Black-Scholes limit. The convergence tests therefore measure **tree discretization/model-approximation error**, not a change in the underlying M1 contract or market inputs.

The implementation uses terminal European payoffs followed by backward induction. Expiry and zero-volatility limits are handled directly rather than forcing the non-degenerate tree formulas through singular cases.

## Monte Carlo: exact terminal distribution and sampling uncertainty

Under the M1 money-market pricing measure,

```text
S_T = S_0 * exp(
    (r - q - 0.5 * sigma^2) * T
    + sigma * sqrt(T) * Z
)
```

with

```text
Z ~ N(0, 1).
```

Because the supported M2 contract is European and depends only on terminal state, `MonteCarloEuropeanOption` samples this exact terminal GBM distribution. It deliberately does **not** add a time-discretized path engine merely to call the method Monte Carlo. This removes path-discretization error from this particular estimator while retaining Monte Carlo sampling error.

Each method application constructs a fresh local `random.Random(seed)` from the explicit configured integer seed. There is no module-global RNG and no mutable RNG shared across method calls. Repeating the same M2 method configuration in the same Python implementation therefore reproduces the same stream and result. This does not establish cross-language RNG parity.

For discounted payoff samples `X_i`, M2 reports

```text
PV_hat = sample mean of X_i
SE     = sample_standard_deviation(X_i) / sqrt(n)
```

and the explicitly labeled normal-approximation 95% interval

```text
PV_hat ± 1.959963984540054 * SE.
```

`MonteCarloValuationResult` is a specific immutable subtype of `ValuationResult`. The base result remains the narrow common present-value contract; Monte Carlo diagnostics are not optional fields added to every valuation result.

The executable evidence checks that the Black-Scholes analytical reference is consistent with the reported estimator uncertainty for a fixed seeded study, and that increasing path count from `n` to `4n` approximately halves the standard error, consistent with the `O(n^-1/2)` Monte Carlo convergence rate.

## Sensitivity problem semantics

For valuation map

```text
V = F(x),
```

M2 asks for a specific derivative of that map. It does not redefine pricing and does not attach a general-purpose Greek dictionary to `ValuationResult`.

The supported sensitivities are:

| Sensitivity | Mathematical variable | Order | M2 core units / sign convention |
| --- | --- | ---: | --- |
| Delta | `S` | 1 | `dV/dS`, PV units per spot unit |
| Gamma | `S` | 2 | `d²V/dS²`, PV units per spot-unit squared |
| Vega | annualized decimal `sigma` | 1 | `dV/dsigma` per `1.00` volatility decimal |
| Theta | valuation time `t`, expiry fixed | 1 | `dV/dt` per ACT/365F model year |
| Rho | continuously compounded annualized decimal `r` | 1 | `dV/dr` per `1.00` rate decimal |

Thus M2 core Vega and Rho are **not** scaled per one percentage point. A presentation layer may later display scaled values, but it must label that transformation rather than reinterpret the quantitative result.

Theta uses the standard passage-of-calendar-time sign convention: valuation time increases while expiry and the other differentiation inputs are held fixed. The result is per ACT/365F model year, not per day.

## Analytic formulas

For positive interior inputs and `T > 0`, define

```text
d1 = [ln(S/K) + (r - q + 0.5 sigma^2) T] / (sigma sqrt(T))
d2 = d1 - sigma sqrt(T)
```

with standard-normal CDF `Phi` and density `phi`.

Then:

```text
Delta_call = exp(-qT) Phi(d1)
Delta_put  = exp(-qT) [Phi(d1) - 1]

Gamma = exp(-qT) phi(d1) / [S sigma sqrt(T)]
Vega  = S exp(-qT) phi(d1) sqrt(T)

Theta_call = -S exp(-qT) phi(d1) sigma / [2 sqrt(T)]
             - r K exp(-rT) Phi(d2)
             + q S exp(-qT) Phi(d1)

Theta_put  = -S exp(-qT) phi(d1) sigma / [2 sqrt(T)]
             + r K exp(-rT) Phi(-d2)
             - q S exp(-qT) Phi(-d1)

Rho_call =  K T exp(-rT) Phi(d2)
Rho_put  = -K T exp(-rT) Phi(-d2)
```

M2 deliberately supports analytic sensitivities only on the differentiable interior `T>0`, `S>0`, `K>0`, `sigma>0`. M1 boundary prices remain valid; they are not falsely promised to have smooth finite Greeks under this API.

## Finite differences and bump ownership

`FiniteDifferenceBlackScholesSensitivity` is a separate sensitivity method. It uses explicit native-unit configuration:

```text
spot_bump
volatility_bump
rate_bump
theta_day_bump
```

Delta, Vega, and Rho use central first differences. Gamma uses the central second difference. Theta moves the valuation calendar date backward and forward by the configured integer number of days and divides by the corresponding ACT/365F model-time displacement.

A configured method is unsupported when its central bump would cross the relevant domain, such as `S-h <= 0`, `sigma-h <= 0`, or a forward Theta bump reaching expiry.

There is intentionally no project-wide magic epsilon. Finite-difference error has competing mechanisms:

```text
large bump
    -> truncation error dominates

intermediate bump
    -> useful numerical agreement

extremely small bump
    -> subtraction cancellation / floating-point error dominates
```

The M2 Gamma test makes this visible by comparing a coarse bump, a well-resolved intermediate bump, and an extremely small bump. The intermediate bump is materially more accurate than both extremes.

## Error taxonomy

M2 keeps the following sources conceptually distinct:

| Error / uncertainty | Meaning in M2 | Evidence |
| --- | --- | --- |
| Financial model error | Black-Scholes/GBM assumptions differ from reality | Not estimated by M2; later market evidence/model-risk work |
| CRR discretization/model-approximation error | finite tree differs from continuous Black-Scholes limit | increasing-step convergence study |
| Monte Carlo sampling error | finite random sample differs from the exact model expectation | standard error, confidence interval, `n^-1/2` study |
| Finite-difference truncation error | bump is too large for local derivative approximation | multi-bump Greek study |
| Cancellation / floating-point error | bump is too small for stable subtraction | multi-bump Gamma study |
| Analytical floating-point error | finite-precision evaluation of closed formulas | tight local benchmark tolerances |

A discrepancy between two methods is therefore not automatically evidence of financial model error.

## Executable evidence map

`tests/pricing/test_m2_independent_valuation.py` establishes:

- CRR configuration/domain behavior;
- CRR convergence toward the M1 analytical reference;
- the finite-step no-arbitrage support boundary;
- expiry and zero-volatility limits;
- explicit Monte Carlo path/seed ownership;
- concrete uncertainty-result typing through `evaluate`;
- seeded reproducibility;
- Black-Scholes consistency with Monte Carlo uncertainty;
- approximate inverse-square-root standard-error scaling; and
- zero sampling uncertainty for deterministic limits.

`tests/sensitivity/test_black_scholes_sensitivity.py` establishes:

- analytical call/put Delta, Gamma, Vega, Theta, and Rho reference values;
- explicit variable/order/unit metadata;
- Problem/Method/Result separation and immutability;
- analytic-vs-finite-difference cross-validation for every supported Greek;
- the truncation-to-cancellation bump-size tradeoff; and
- method support boundaries for non-differentiable or bump-invalid cases.

`tests/sensitivity/test_dependency_direction.py` prevents the pricing package from depending back on sensitivity.
