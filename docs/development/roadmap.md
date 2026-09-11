# Development Roadmap

## Mission

Build a professional quantitative-finance research and model-validation platform whose first specialization is **equity derivatives and volatility modeling**.

The project is organized around mathematically meaningful problem families and evidence, not a checklist of finance keywords. Foundational mathematical distinctions may be explicit from the outset; operational frameworks must earn their abstractions from concrete consumers.

## v0.1 quantitative narrative

```text
M0 / M0A   engineering + mathematical architecture          complete
      ↓
M1         Black-Scholes reference pricing                  complete
      ↓
M2         independent valuation + Greeks                   complete
      ├───────────────────────────────┐
      ↓                               ↓
M3         dynamic hedging/control    M4 market evidence + IV
           complete                   complete
      └───────────────┬───────────────┘
                      ↓
M5         Heston forward model + independent valuation      complete
                      ↓
M6         Heston calibration + identifiability              complete
                      ↓
M7         empirical validation / BS vs Heston model risk    complete
                      ↓
M8         measured performance engineering                  complete
                      ↓
M9         portfolio-quality v0.1 release                    next
```

The earned research story is:

```text
theory
→ independent numerical evidence
→ sensitivity / replication pressure
→ observed-market falsification pressure
→ richer stochastic-volatility forward model
→ calibrated inverse problem with identifiability evidence
→ predeclared held-out model comparison
→ measured optimization
→ release
```

## Completed quantitative milestones

### M0 — Engineering bootstrap

Established repository truth, source-layout packaging, pytest/Ruff/strict-Pyright CI, operating rules, durable docs, and reproducibility/native-backend guardrails.

### M0A — Mathematical Quant-Finance Architecture Foundation

Established the mathematical problem taxonomy and the conceptual execution pattern:

```text
Problem + supported Method -> specific immutable Result / Evidence
```

This is a responsibility map, not a universal runtime hierarchy.

### M1 — European options and Black-Scholes reference vertical

Established the first concrete `PricingProblem` specialization with European call/put contracts, Black-Scholes/GBM semantics, ACT/365F, a flat continuously compounded money-market numeraire, continuous dividend/carry, analytic valuation, and theoretical validation evidence.

### M2 — Independent valuation and sensitivity/Greeks

Added independent CRR and seeded Monte Carlo valuation plus analytic/finite-difference Delta, Gamma, Vega, Theta, and Rho with explicit numerical-error evidence.

### M3 — Dynamic hedging / control

Turned analytic Delta into an explicit dynamic replication policy over model-generated GBM paths with stock/cash financing, rebalance schedules, volatility misspecification, transaction costs, and replication evidence.

### M4 — Market evidence / scalar inverse problems

Established immutable raw observations/provenance, explicit midpoint normalization, Black-Scholes implied-volatility inversion with separate bisection, conditioning evidence, and pinned SPX strike/maturity evidence.

### M5 — Heston stochastic volatility and independent valuation

Added explicit Heston state/law/parameter semantics, characteristic-function/Fourier valuation, independent seeded full-truncation Euler Monte Carlo, Feller diagnostics, exact `xi=0` handling, and cross-method validation.

### M6 — Heston calibration, recovery and identifiability

Added option-price-space calibration targets, explicit residual/weighting/domain semantics, separate bounded SciPy nonlinear least squares, known-truth recovery, multiple starts, perturbation evidence, local domain-scaled Jacobian diagnostics, a rank-deficient counterexample, and a provenance-preserving SPX calibration workflow.

M6 established:

```text
small calibration loss
!= uniquely identified parameters
!= trustworthy model
```

### M7 — Empirical Validation, Model Risk, and Black-Scholes vs Heston

**Status: complete.**

M7 is the first concrete validation specialization.

The available empirical sample contains 14 selected SPX/SPXW contracts from one market date across two expiries. M7 therefore uses a predeclared **same-date cross-sectional** holdout:

```text
sort by (expiry, strike)
evaluation iff zero-based index % 3 == 2
```

This yields 10 training and 4 held-out evaluation contracts.

Both models consume exactly the same training prices and half-spread-standardized price residual scale:

```text
10 training observations
        ├── fit one constant Black-Scholes sigma
        └── calibrate Heston (v0,kappa,theta,xi,rho)
                 from three predeclared starts
        ↓
freeze both estimates
        ↓
price the same 4 held-out contracts
```

A regression test changes only held-out targets and proves that fitted training models and held-out model prices are unchanged.

Reference held-out evidence:

```text
                         Black-Scholes      Heston
price RMSE                   8.412           0.671
half-spread std. RMSE       20.613           1.649
relative MAE                 8.27%            0.66%
```

Under this predeclared sample and explicit financial inputs/objective, Heston materially improves held-out pricing metrics relative to the one-volatility Black-Scholes benchmark.

M7 retains model-risk evidence rather than turning that result into a universal ranking:

- all contract-level residuals;
- training/evaluation metrics separately;
- three-start Heston stability;
- local Jacobian rank/singular values/condition number;
- a post-evaluation full-sample Heston stability fit;
- M6's rank-deficient low-loss counterexample as identification context;
- M3 volatility-misspecification and transaction-cost evidence;
- an explicit statement that authoritative Heston hedging is not yet supported; and
- representative M8 workload definitions.

The bounded conclusion is:

> Under this predeclared same-date cross-sectional holdout, explicit rate/carry convention, price-space objective, and selected observations, Heston improves held-out price and half-spread-standardized RMSE relative to the one-volatility Black-Scholes benchmark. This does not establish temporal generalization or model validity; calibration conditioning, limited date/maturity coverage, numerical cost, and unsupported Heston hedging remain material limitations.

See `docs/models/m7_empirical_validation_and_model_risk.md`, `docs/evidence/m7_spx_bs_vs_heston_validation_reference.json`, and `scripts/m7_model_validation.py`.

### M8 — Performance engineering and measured native decision

**Status: complete.**

M8 profiled the six workloads frozen by M7 before selecting an acceleration target. The baseline showed two dominant causes:

```text
Heston Monte Carlo
→ scalar Python path loop + 10.08 million scalar Gaussian draws

Heston calibration / M7
→ repeated strike-independent Heston characteristic-function work
   inside thousands of scalar Fourier prices
```

M8 optimized those causes in Python first:

- vectorized Heston path propagation across NumPy arrays while preserving explicit full-truncation Euler timesteps;
- fresh local NumPy `PCG64` generator ownership for reproducibility without ambient RNG state;
- stateless Heston Fourier batching by maturity so compatible strikes share characteristic-function work;
- batched calibration residual evaluation only inside repeated optimizer calls;
- scalar M5/M6 pricing/result reconstruction retained as correctness reference; and
- explicit scalar fallback for the exact `xi=0` deterministic-variance boundary.

Same-run reference medians:

```text
Heston MC, 20k x 252                 3.3673 s -> 0.1230 s   27.38x
10-target / 3-start calibration      2.2919 s -> 0.4971 s    4.61x
14-target / 3-start calibration      3.2752 s -> 0.5454 s    6.01x
complete M7 validation study         5.4136 s -> 1.0819 s    5.00x
```

Deterministic financial parity checks pass. The changed Monte Carlo RNG stream is validated statistically rather than by equal-seed stream identity; old/new estimates differ by about `0.853` combined standard errors in the reference comparison.

M8 deliberately adds **no C++ kernel**. The representative post-optimization absolute runtimes are small enough that a compiler/binding/cross-platform packaging and native-parity surface is not justified for v0.1. Python remains the financial-semantic/reference implementation, and no generic backend abstraction was introduced.

This negative native decision is part of the M8 result. Future materially larger workloads may reopen the question only after new profiling.

See `docs/models/m8_performance_engineering.md`, `docs/evidence/m8_performance_reference.json`, `scripts/m8_profile_workloads.py`, and `scripts/m8_compare_performance.py`.

## M9 — Portfolio-quality v0.1 release

**Status: next.**

M9 should consolidate rather than broaden the quantitative scope. Expected outputs include:

- a reproducible flagship study spanning the earned M1–M8 narrative;
- explicit market-data/provenance/replay instructions;
- validation/model-risk conclusions and non-claims;
- M8 same-run before/after performance evidence and the measured no-C++ decision;
- polished downstream native-workbench integration;
- release-oriented documentation and examples;
- final quality/reproducibility review; and
- the tagged v0.1 release.

M9 must not manufacture a native kernel merely to make the release sound more sophisticated. The performance result to present is that profiling found real bottlenecks, Python/NumPy changes produced 4.61×–27.38× heavy-workload improvements, parity remained strong, and native acceleration was not earned for the current workload scale.

## Native UI track

```text
UI1  native architecture + Black-Scholes analytic vertical       complete
UI2  valuation comparison / convergence / uncertainty / Greeks  complete
UI3  dynamic hedging + market evidence / implied volatility     complete
UI4  Heston forward valuation + calibration / identifiability   complete
UI5  validation/model-risk + performance/release evidence       active
```

UI4 consumes authoritative M5/M6 contracts and remains downstream of finance semantics. UI5 is a parallel active PR that consumes M7 validation/model-risk evidence and may reconcile against M8 performance evidence after M8 merges.

M8 established that there is no v0.1 native quantitative backend to expose. UI5 must therefore present the measured optimization/no-C++ result truthfully rather than inventing a backend selector or C++ execution path.

The dependency direction remains:

```text
Qt Quick / QML
        ↓
PySide6 controller / item models
        ↓
application + presentation
        ↓
public quantitative APIs
        ↓
production quantitative core
```

Finance milestones do not depend on UI completion.

## Post-v0.1 directions

Potential later specializations include rates, XVA/counterparty credit, portfolio market risk, and possibly rough-volatility research after reviewing then-current literature and the demonstrated limitations of v0.1.
