# M7 — Empirical Validation and Model Risk

## Status

**M7 is complete.**

M7 establishes validation as a concrete mathematical problem family rather than a final-report helper. Its first specialization compares a fairly fitted one-volatility Black-Scholes benchmark with Heston on a predeclared same-date SPX cross-sectional holdout while retaining calibration conditioning, parameter stability, model-misspecification boundaries, and representative computational workloads.

Protect:

```text
validation problem != validation method != validation evidence
calibration != validation
training fit != held-out evaluation
model residual != quote width != numerical error
price fit != parameter identification
optimizer convergence != model validity
same-date cross-sectional holdout != temporal out-of-sample forecasting
```

## Why this milestone exists

M4 established that one constant Black-Scholes volatility cannot reconcile the selected SPX strike/maturity observations. M5 introduced Heston as a richer stochastic-volatility forward model. M6 showed that Heston can be calibrated and also demonstrated that low calibration loss does not imply unique or trustworthy parameters.

M7 asks the next question:

> Does the extra Heston state, parameterization, calibration complexity, and computational burden buy measurable predictive adequacy on observations that were not used to fit the model?

That question is neither pricing nor calibration. It is validation.

## Concrete Problem → Method → Evidence composition

```text
NormalizedOptionObservation(s)
+ explicit TRAINING / EVALUATION partition
+ fixed spot / rate / q convention
+ one-volatility Black-Scholes benchmark domain
+ Heston calibration domain and Fourier forward map
        ↓
BlackScholesHestonValidationProblem
        +
CrossSectionalBlackScholesHestonValidation
        ↓
BlackScholesHestonValidationEvidence
```

The problem owns the observations, partition, fixed financial inputs, model domains, and comparison semantics. The method owns numerical starts/tolerances. The immutable evidence owns fitted training models, contract-level residuals, partition metrics, Heston conditioning/stability evidence, workload structure, and the bounded conclusion.

M7 does **not** introduce universal `ValidationProblem`, `ValidationMethod`, metric-registry, risk-engine, or model-registry abstractions.

## Empirical sample and predeclared partition

The available M4 empirical evidence contains one market date, January 4, 2023, with 14 selected OTM-side SPX/SPXW contracts across two expiries. That sample cannot support a later-date forecasting claim.

M7 therefore predeclares a same-date cross-sectional holdout before fitting:

```text
sort the 14 contracts by (expiry, strike)

zero-based index % 3 == 2  -> EVALUATION
otherwise                  -> TRAINING
```

This produces 10 training observations and 4 held-out evaluation observations.

The held-out contracts are:

```text
2023-02-03  put   K=3850
2023-02-03  call  K=3970
2023-04-28  put   K=3800
2023-04-28  call  K=4075
```

A regression test enforces the no-leakage invariant: changing only held-out target prices cannot change either fitted training model or their held-out model prices. It may change held-out residuals and the deliberately later full-sample stability calibration.

## Fair Black-Scholes benchmark

The benchmark is **not** one implied volatility per held-out option. Such a benchmark would invert each evaluation target and leak the answer.

Instead M7 fits one constant annualized volatility to exactly the same 10 training prices used by Heston:

```text
10 training observations
        ↓
half-spread-standardized price residuals
        ↓
one fitted Black-Scholes sigma
        ↓
freeze sigma
        ↓
price all 4 held-out contracts
```

The fitted reference volatility is approximately:

```text
sigma_BS = 0.20891
```

The scalar numerical fit is study-local. It does not turn `BlackScholesLaw` into a calibration object and does not justify a generic inverse framework.

## Heston training fit

Heston reuses the M6 calibration contracts with:

- the same 10 training observations;
- fixed observed spot `S0 = 3853.39`;
- continuously compounded flat risk-free rate `r = 0.045`;
- continuous dividend yield `q = 0.017`;
- ACT/365F;
- bid/ask-half-spread-standardized price residuals;
- M6 financial bounds;
- `HestonFourierEuropeanOption` with upper integration bound `100` and 256 Simpson intervals; and
- three materially different predeclared starts.

All three starts converge to an extremely tight cluster. A representative selected training estimate is approximately:

```text
v0      = 0.04425
kappa   = 3.4968
theta   = 0.06436
xi      = 0.59557
rho     = -0.81317
```

The training standardized residual objective is about `4.77`. The domain-scaled local Jacobian is full rank with condition number about `425`: locally informative, but not well enough conditioned to support a global-identification claim.

## Evaluation metrics

M7 keeps option-price space primary because both model fits are defined there. Each contract/model comparison retains:

- model-minus-observed price residual;
- absolute price error;
- relative absolute price error;
- observed bid/ask half-spread;
- half-spread-standardized residual;
- expiry, strike, option right, and log-forward-moneyness.

Aggregates retain mean residual, MAE, RMSE, relative MAE, standardized MAE, standardized RMSE, and maximum absolute standardized residual.

Reference evidence:

| Partition / model | Price MAE | Price RMSE | Relative MAE | Standardized RMSE | Max |standardized residual| |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train — Black-Scholes | 7.299 | 9.504 | 11.95% | 22.61 | 49.45 |
| Train — Heston | 0.300 | 0.376 | 0.44% | 0.691 | 1.50 |
| Held out — Black-Scholes | 7.456 | 8.412 | 8.27% | 20.61 | 27.21 |
| Held out — Heston | 0.564 | 0.671 | 0.66% | 1.649 | 2.49 |

On this predeclared holdout Heston materially lowers both raw-price RMSE and half-spread-standardized RMSE relative to the fairly fitted one-volatility Black-Scholes benchmark.

That is a sample-bounded empirical result, not a universal model ranking.

## Parameter stability and identifiability

After held-out predictions are already fixed, M7 calibrates Heston to all 14 observations solely as stability evidence. The full-sample reference is approximately:

```text
v0      = 0.04447
kappa   = 3.2575
theta   = 0.06622
xi      = 0.62715
rho     = -0.77937
```

The maximum training-to-full parameter movement is about `0.017` when each coordinate is scaled by its explicit M6 financial-domain width. The three training starts themselves are much more tightly clustered.

This evidence must be read together with M6's deliberately underdetermined thin-slice counterexample, where near-zero price loss coexists with materially different parameter estimates and a rank-deficient local Jacobian.

Therefore:

```text
good held-out prices
!= globally identified parameters

multiple-start convergence
!= posterior certainty

full local rank
!= model validity
```

## M3 hedging and model-misspecification evidence

M7 integrates the existing M3 control evidence without relabeling it.

M3 established, for its committed Black-Scholes model-generated pricing-measure studies, that:

- more frequent rebalancing reduced replication error under the correctly specified model;
- volatility misspecification materially worsened replication error; and
- proportional transaction costs introduced a separate drag/accounting effect.

Those studies are **not historical trading backtests**.

M7 does not fabricate a Heston hedge comparison. `SimulatedEquityPath` has explicit Black-Scholes/GBM provenance, and the repository does not yet own an authoritative Heston path + Delta + hedge-accounting composition. Passing a Heston story through M3's Black-Scholes path type would destroy provenance rather than validate the model.

Thus:

```text
Heston held-out pricing advantage
!= demonstrated Heston hedging advantage
```

## Error and uncertainty taxonomy

M7 preserves distinct mechanisms:

```text
market quote width / asynchronous-data noise
!= model residual
!= Black-Scholes/Heston misspecification
!= Heston Fourier truncation/quadrature error
!= Heston Monte Carlo sampling error
!= Heston Monte Carlo timestep bias
!= calibration conditioning
!= optimizer convergence
```

Half-spread is a comparison scale in this study. It is not asserted to be a probability variance, likelihood, confidence interval, or universal acceptance threshold.

## Reproducibility and evidence lineage

`scripts/m7_model_validation.py` performs no network retrieval. It reuses the pinned M4/M6 local raw-artifact workflow:

```text
local pinned CSV
→ exact Git-blob verification + local SHA-256
→ M4 raw observations + provenance
→ M4 midpoint normalization
→ same 14 selected OTM-side contracts
→ predeclared 10/4 partition
→ fit Black-Scholes + Heston on TRAIN only
→ freeze estimates
→ evaluate held-out contracts
→ post-evaluation full-sample Heston stability fit
→ derived M7 evidence
```

Raw rows are not redistributed. The compact committed reference is `docs/evidence/m7_spx_bs_vs_heston_validation_reference.json`; the raw replay script remains the authoritative path from the pinned source artifact.

## M8 profiling handoff

M7 defines representative workloads but performs no optimization and sets no performance threshold:

```text
1. one BlackScholesClosedForm valuation
2. one HestonFourierEuropeanOption valuation (upper=100, intervals=256)
3. one seeded HestonMonteCarloEuropeanOption valuation
   (20,000 paths, 252 timesteps, seed=20260910)
4. 10-target / 3-start Heston training calibration
5. 14-target / 3-start Heston stability calibration
6. full M7 10-train / 4-evaluation validation study
```

M8 must profile these workloads before choosing any C++ boundary or other optimization. Python remains the reference correctness implementation.

## Bounded conclusion

The supported conclusion is:

> Under this predeclared same-date cross-sectional holdout, explicit rate/carry convention, price-space objective, and selected observations, Heston improves held-out price and half-spread-standardized RMSE relative to the one-volatility Black-Scholes benchmark. This does not establish temporal generalization or model validity; calibration conditioning, limited date/maturity coverage, numerical cost, and unsupported Heston hedging remain material limitations.

Unsupported stronger claims include:

- “Heston is better” in general;
- temporal forecasting success;
- physical-measure predictive validity;
- unique/global Heston parameter identification;
- historical trading profitability;
- Heston hedge superiority; or
- a performance/C++ optimization conclusion.

## Limitations

The first M7 empirical result is intentionally narrow:

- one market date;
- two expiries;
- four held-out contracts;
- flat `r` and `q` research assumptions;
- same-date cross-sectional rather than temporal evaluation;
- derived public-source evidence with raw rows intentionally not redistributed;
- nontrivial Heston calibration conditioning;
- no physical-measure forecasting/filtering; and
- no authoritative Heston dynamic-hedging study.

These limitations are part of the validation result, not footnotes to be hidden by the better Heston residuals.
