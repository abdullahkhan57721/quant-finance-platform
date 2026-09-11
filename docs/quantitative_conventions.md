# Quantitative Conventions

## Purpose

This is the authoritative register for quantitative representation conventions in the project.

A convention is either:

- **Committed** — cross-cutting rule expected across public quantitative boundaries;
- **Local** — deliberately specific to a method/study/specialization; or
- **Deferred** — not yet justified by a concrete consumer.

Consequential conventions must not remain implicit.

ADR 0002 is the mathematical architecture authority. M1–M7 specialize it without turning the conceptual taxonomy into universal runtime APIs.

## Committed cross-cutting conventions

### Problem-family distinction

```text
foundations
    ↓
problem family
    ↓
supported solution method
    ↓
specific immutable result / evidence
```

Recognized problem families are:

```text
pricing
inverse / inference
sensitivity
prediction
control / optimization
risk
validation
```

Protect:

```text
problem != solution method
pricing problem != valuation method
inverse problem != optimizer/root finder
sensitivity problem != differentiation method
control problem != optimizer
validation problem != validation method
request/configuration != immutable result/evidence
```

This is a mathematical responsibility map, not a universal base-class hierarchy.

### Observation/model separation

```text
raw market observation
    ↓
explicit normalization / construction
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
raw observation != normalized target
normalized target != model price
model price != inferred/calibrated parameter
```

M4 establishes provenance-bearing raw and normalized observation semantics. M6 and M7 consume them rather than creating calibration/validation substitutes.

### State, law, parameters, contract, measure

```text
modeled state / state space
!= stochastic law
!= parameter values
!= contract / cash-flow stream
!= numeraire
!= physical measure P
!= pricing measure Q^N
!= pricing problem
!= valuation method
!= completed result
```

Probability semantics are part of the question. A pricing-measure result must not be silently presented as a physical-world forecast.

### Numeraire positivity

At every supported pricing access:

```math
N_t > 0
```

with finite value. Concrete rate/curve representations remain consumer-specific.

### Result specificity

Completed evidence remains narrow and truthful to the problem/method that produced it. Method-specific evidence belongs in specific immutable result types rather than giant optional-field containers.

Examples:

- `MonteCarloValuationResult` adds sampling uncertainty/seed/path count;
- `HestonFourierValuationResult` adds quadrature configuration/evaluations;
- `HestonMonteCarloValuationResult` adds timestep/variance-scheme diagnostics;
- `HestonCalibrationResult` adds calibration residual/termination/conditioning evidence;
- `BlackScholesHestonValidationEvidence` adds fitted benchmark/calibration, partitioned residual/metric, stability, workload, and bounded-conclusion evidence.

### Volatility / variance units

A public value named **annualized volatility** is a decimal annualized standard deviation unless explicitly documented otherwise:

```text
0.20 = 20% annualized volatility
```

Variance remains distinct. Under Heston, `instantaneous_variance = 0.04` corresponds to instantaneous volatility `sqrt(0.04)=0.20`; it is not a 4% volatility input.

### No hidden universal tolerance

There is no project-wide magic numerical tolerance. Tolerances must be justified by the relevant mechanism:

- analytical floating-point error;
- tree/finite-difference/quadrature discretization;
- Monte Carlo standard error;
- optimizer/root convergence;
- market quote precision;
- backend parity; or
- explicitly defined validation criteria.

### Stochastic ownership

Production stochastic methods own explicit RNG configuration and must not depend on ambient global RNG state.

M2 Black-Scholes Monte Carlo, M3 path simulation, and M5 Heston Monte Carlo use explicit integer seeds and fresh local RNG state. Equal seeds across future Python/C++ implementations do not promise identical random streams.

### Reproducible core tests

Core CI must not require live market services. Use deterministic synthetic fixtures or curated derived snapshots. Real research workflows retain source/hash/licensing lineage and may require a local pinned raw artifact.

## M1 local Black-Scholes / European-option conventions

| Convention | Decision |
| --- | --- |
| Time | `datetime.date` |
| Day count | ACT/365F |
| Rate | continuously compounded decimal annual rate through `FlatMoneyMarketNumeraire` |
| Carry | finite continuous dividend yield `q` |
| Volatility | non-negative annualized decimal `sigma` |
| Spot / strike | finite, non-negative; zero admitted as deterministic boundary |
| Option right | explicit call / put |
| Price output | present value |
| Measure | explicit money-market pricing-measure semantics |
| Business-day/calendar layer | absent until a real consumer requires it |

See `docs/models/black_scholes.md`.

## M2 local numerical valuation / sensitivity conventions

### CRR

- explicit positive integer `steps`;
- finite-tree support requires valid risk-neutral probability (`0 < p < 1`);
- a finite tree is a discrete model and is not silently identified with continuous Black-Scholes.

### Monte Carlo

- explicit `paths >= 2`;
- explicit integer seed;
- exact terminal GBM sampling for the European terminal-payoff specialization;
- sampling standard error and normal-approximation 95% interval retained separately from deterministic valuation error.

### Greeks

```text
Delta = dV/dS
Gamma = d²V/dS²
Vega  = dV/dsigma   per 1.00 volatility decimal
Theta = dV/dt       per ACT/365F model year
Rho   = dV/dr       per 1.00 continuously compounded rate decimal
```

Finite-difference bumps use native units and explicit local sizes; there is no universal epsilon.

See `docs/models/m2_numerical_methods_and_sensitivities.md`.

## M3 local dynamic-hedging conventions

| Convention | Decision |
| --- | --- |
| Liability | one short European option |
| Terminal replication error | `hedge value - option payoff` |
| Initial hedge wealth | hedging-model Black-Scholes PV |
| Policy input | M2 analytic Delta |
| Path | exact-transition GBM under configured pricing measure |
| Observation grid | explicit path output dates |
| Rebalance grid | explicit, distinct from observation grid |
| Financing | existing money-market numeraire ratio |
| Transaction cost | proportional rate × absolute stock-trade notional |
| Dividend support | hedge execution currently requires `q=0` |
| Misspecification study | generating volatility and hedging volatility explicitly separated |
| Aggregate evidence | mean/median error, SD, MAE, RMSE across distinct seeds |

M3 evidence is model-generated replication evidence, not a historical trading backtest.

See `docs/models/m3_dynamic_delta_hedging.md`.

## M4 local market-observation / implied-volatility conventions

| Convention | Decision |
| --- | --- |
| Raw vs normalized | immutable raw evidence; separate normalized observation |
| Provenance | provider/source, market date, retrieval time, optional observation time/hash/license notes |
| Quote target | strictly positive non-crossed bid/ask midpoint |
| Exercise | European only for first inverse consumer |
| Settlement | explicit PM settlement under date-only contract semantics |
| Implied-volatility target | existing Black-Scholes forward map solved for annualized decimal `sigma` |
| Financial feasibility | discounted European bounds checked before root search |
| Numerical method | deterministic bracketed bisection |
| Conditioning | M2 analytic Vega and local inverse sensitivity |
| Moneyness | `log(K/F)`, `F=S exp((r-q)T)` under same explicit inputs |
| Static diagnostics | same-right strike monotonicity / discrete convexity reporting only |
| Real SPX study | explicit flat `r=0.045`, `q=0.017`; these are research assumptions |

Implied volatility is model-dependent inference, not directly observed or physical volatility.

See `docs/models/m4_market_evidence_and_implied_volatility.md`.

## M5 local Heston / valuation conventions

Heston dynamics use:

```text
state: (S, v)
parameters: kappa, theta, xi, rho, q
risk-free rate: owned by money-market numeraire
```

Local conventions:

- `v >= 0` instantaneous variance;
- `kappa > 0` mean-reversion speed;
- `theta >= 0` long-run variance;
- `xi >= 0` variance diffusion coefficient;
- `rho in [-1,1]` spot/variance Brownian correlation;
- Feller discriminant `2*kappa*theta - xi^2` is diagnostic, not universal constructor validity;
- Fourier valuation uses explicit positive lower frequency, finite upper bound, even Simpson interval count, and documented complex-square-root branch;
- `xi=0` uses exact deterministic integrated variance and independent Black-Scholes reduction;
- Heston Monte Carlo uses explicit paths/timesteps/seed and full-truncation Euler for `xi>0`;
- negative raw variance proposals are discretization-pressure evidence, not continuous-model negative variance;
- Monte Carlo confidence interval is sampling uncertainty only and does not cover timestep bias or model error.

See `docs/models/m5_heston_stochastic_volatility.md`.

## M6 local Heston calibration conventions

The first Heston calibration inverse problem is **option-price space**.

Unknown direct financial coordinates:

```text
(v0, kappa, theta, xi, rho)
```

Fixed in the first consumer:

```text
spot, flat money-market rate, q
```

Residual:

```text
(model price - target price) / residual scale
```

Supported local scales:

```text
UNIFORM_PRICE           -> 1
BID_ASK_HALF_SPREAD     -> (ask - bid)/2
```

Half-spread scaling is an economic quote-width scale, not asserted to be a statistical variance or universal likelihood.

Additional conventions:

- named finite `HestonCalibrationBounds` own the financial admissible domain;
- Feller is not imposed as an optimizer constraint;
- no parameter transform is used;
- SciPy trust-region-reflective bounded least squares is the concrete numerical method;
- initial guess/tolerances/max evaluations/numerical Jacobian belong to the method;
- invalid financial problem, invalid start, and numerical nonconvergence are distinct failures;
- per-target raw and standardized residuals are retained;
- local identifiability uses singular values/rank of the standardized-residual Jacobian with columns scaled by explicit financial-domain widths;
- a finite five-coordinate condition number is reported only for full column rank;
- synthetic truth recovery precedes market calibration;
- multiple starts and controlled perturbations are evidence, not proof of global uniqueness.

See `docs/models/m6_heston_calibration.md`.

## M7 local empirical-validation / model-risk conventions

M7 is the first concrete validation specialization. These conventions are **local to the Black-Scholes-vs-Heston SPX study unless explicitly identified as cross-cutting**.

### Empirical sample and split

The current empirical sample is one January 4, 2023 SPX market date with 14 selected OTM-side contracts across two expiries.

Predeclared partition:

```text
order by (expiry, strike)
evaluation iff zero-based index % 3 == 2
training otherwise
```

This yields 10 training and 4 evaluation contracts.

This is **same-date cross-sectional held-out evidence**, not temporal out-of-sample forecasting.

### Fair benchmark

Black-Scholes fits **one** constant annualized volatility to the 10 training prices. It does not invert one implied volatility per evaluation quote.

Both Black-Scholes and Heston use the same training observations and the same price-space residual scale:

```text
bid/ask half-spread
```

### Heston training fit

- same 10 training observations;
- same fixed spot / flat `r` / `q` convention;
- M6 direct financial coordinates and bounds;
- M6 `BID_ASK_HALF_SPREAD` weighting;
- M5 Heston Fourier forward map;
- three explicit predeclared starts;
- lowest-objective converged training result selected only from those starts.

### No-leakage invariant

```text
held-out target changes
must not change
training-fitted Black-Scholes sigma
or training-fitted Heston coordinates
or held-out model prices
```

A full-14-contract Heston fit occurs **only after** held-out predictions/metrics are fixed and is used solely for parameter-stability evidence.

### Per-contract evidence

For each model/contract retain:

- model-minus-observed price residual;
- absolute price error;
- relative absolute price error using positive observed target as denominator;
- observed bid/ask half-spread;
- half-spread-standardized residual;
- strike, expiry, right, and log-forward-moneyness;
- training/evaluation partition.

### Aggregate metrics

For each model and partition retain:

```text
mean residual
price MAE
price RMSE
relative MAE
standardized MAE
standardized RMSE
maximum absolute standardized residual
```

These metrics are descriptive evidence. M7 defines no universal pass/fail threshold.

### Parameter stability / identification

Retain:

- successful/failed predeclared training starts;
- maximum start-to-start parameter spread scaled by M6 domain widths;
- training Jacobian rank and condition number;
- full-sample stability-fit rank/condition number; and
- train→full coordinate movements scaled by M6 domain widths.

Protect:

```text
price identification != parameter identification
stable starts != global uniqueness
full local rank != posterior certainty
```

### Hedging boundary

M3 Black-Scholes replication/misspecification evidence may inform the M7 model-risk discussion. It must not be relabeled as Heston-world evidence.

```text
M3 Black-Scholes/GBM path provenance
!= Heston path provenance
```

No Heston hedge comparison is supported until an authoritative Heston path + Delta + hedge-accounting boundary exists.

### Workload / performance evidence

M7 records structural workload definitions and optimizer evaluation counts. Environment-dependent wall-clock timing from the research script is exploratory only and is **not** a CI threshold or portable benchmark.

M8, not M7, owns profiling and acceleration decisions.

### Bounded conclusion rule

M7 conclusions must name the sample/design assumptions and unsupported claims. The current evidence supports only the statement that Heston improves the specified held-out pricing metrics on this predeclared same-date sample under the explicit financial inputs/objective.

It does not establish:

- temporal generalization;
- physical-measure forecast quality;
- global parameter identification;
- historical trading profitability;
- Heston hedge superiority; or
- universal Heston model superiority.

See `docs/models/m7_empirical_validation_and_model_risk.md` and `docs/evidence/m7_spx_bs_vs_heston_validation_reference.json`.

## Explicitly deferred conventions

These remain deferred until real consumers force decisions:

| Convention | Guidance |
| --- | --- |
| General business-day/calendar framework | M1–M7 use local date/ACT-365F semantics; do not universalize. |
| General discount/dividend curves | Current studies use a flat money-market numeraire and continuous `q`; no curve hierarchy yet. |
| Discrete dividends/corporate actions | Do not reinterpret continuous `q` as a discrete schedule. |
| Generic forward-market observations | M4/M7 construct model forwards from explicit `r/q`; these are not observed forward quotes. |
| Generic array axis/order conventions | Wait for M8 measured vectorized/native-kernel boundary. |
| Intraday/exchange-session timestamps | Current market studies are date-valued; no generic session framework. |
| Generic quote cleaning | M4 midpoint normalization remains concrete/local. |
| Heston implied-volatility-space calibration | Must define separate target/weighting/conditioning semantics if added. |
| Generic calibration weighting/loss framework | M6 policies remain local. |
| Generic parameter transforms | M6 direct coordinates establish no universal transform. |
| Arbitrage-free surface repair/interpolation | M4/M6/M7 do not silently repair/interpolate the selected sample. |
| Prediction probability semantics | A future prediction consumer must state conditioning information, horizon and P/Q/scenario semantics. |
| Risk horizon / loss / scenario semantics | A future risk consumer must make all three explicit. |
| Generic validation thresholds | Each validation consumer must justify its own evidence and error/statistical rationale. |
| Heston dynamic hedging | Requires authoritative Heston path, hedge sensitivity/policy, and accounting semantics. |
| Native backend array/random conventions | M8 must profile first and define only the boundary actually required. |

## Formula / evidence traceability

Important quantitative implementations and studies should document enough information to recover:

- source/reference or derivation;
- notation mapping;
- assumptions and parameter domain;
- units/conventions;
- probability/measure semantics;
- numerical error mechanisms;
- limiting cases/identities;
- observation/provenance lineage where empirical data is involved; and
- tests/evidence that distinguish plausible wrong interpretations.

M1–M7 each have dedicated model/evidence documentation following this rule.

## Market-data provenance

Preserve as applicable and legally permitted:

- provider/source;
- market/as-of date;
- retrieval timestamp;
- optional source observation timestamp;
- raw artifact/content hash;
- normalization/transformation lineage; and
- licensing/redistribution notes.

If raw data cannot be redistributed or licensing is unclear, prefer a reproducible acquisition/replay recipe plus pinned hash and derived evidence. Core CI remains deterministic and network-independent.

## Changing a convention

A committed convention may change when evidence justifies it. Changes should normally include:

1. motivation and affected public contracts;
2. migration/compatibility consequences;
3. discriminating tests when executable behavior changes;
4. documentation in the same PR; and
5. an ADR only when the decision is sufficiently durable/consequential to require historical rationale.

Repository truth should evolve rather than preserving a bad convention for historical consistency.
