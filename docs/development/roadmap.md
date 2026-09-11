# Development Roadmap

## Mission

Build a professional quantitative-finance research and model-validation platform whose first specialization is **equity derivatives and volatility modeling**.

The platform should demonstrate mathematical modeling, pricing, numerical methods, sensitivity, dynamic replication, observed-market inference, calibration, validation/model-risk reasoning, reproducible research, performance engineering, Python, modern C++, testing, typing, documentation, CI, and a native research UI.

The project is not a feature checklist. ADR 0002 permits stable mathematical distinctions to be explicit early, while operational frameworks must still be earned by concrete behavior.

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
M7         empirical validation / BS vs Heston model risk    in progress
                      ↓
M8         profile measured bottlenecks / targeted C++       planned
                      ↓
M9         portfolio-quality v0.1 release                    planned
```

The earned research story is:

```text
theory
→ independent numerical evidence
→ sensitivity / replication pressure
→ observed-market falsification pressure
→ richer stochastic-volatility forward model
→ calibrated inverse problem with identifiability evidence
→ out-of-sample / model-risk comparison
→ measured optimization
→ release
```

## Completed quantitative milestones

### M0 — Engineering bootstrap

Established repository truth, source-layout packaging, pytest/Ruff/strict-Pyright CI, operating rules, durable docs, and reproducibility/native-backend guardrails.

### M0A — Mathematical Quant-Finance Architecture Foundation

Established the conceptual organization:

```text
financial / mathematical foundations
        ↓
problem family
        ↓
supported method
        ↓
specific immutable result / evidence
```

and the observation/model boundary. This is a responsibility taxonomy, not a universal runtime hierarchy.

### M1 — European options and Black-Scholes reference vertical

Established the first concrete `PricingProblem` specialization with European call/put contracts, Black-Scholes/GBM semantics, ACT/365F, a flat continuously compounded money-market numeraire, continuous dividend/carry, analytic valuation, and theoretical validation evidence.

### M2 — Independent valuation and sensitivity/Greeks

Added independent CRR and seeded Monte Carlo valuation over the same Black-Scholes pricing problem plus analytic/finite-difference Delta, Gamma, Vega, Theta, and Rho.

Evidence distinguishes lattice approximation, Monte Carlo sampling uncertainty, finite-difference truncation, and cancellation/floating-point effects.

### M3 — Dynamic hedging / control

Turned analytic Delta into an explicit dynamic replication policy over model-generated GBM paths with stock/cash financing, rebalance schedules, volatility misspecification, transaction costs, and replicate evidence.

### M4 — Market evidence / scalar inverse problems

Established immutable raw option/underlying observations with provenance, explicit midpoint normalization, Black-Scholes implied-volatility inversion with separate bisection, conditioning evidence, and pinned SPX strike/maturity evidence.

### M5 — Heston stochastic volatility and independent valuation

Added:

```text
HestonEquityState(spot, instantaneous variance)
+ HestonLaw
+ HestonParameters(kappa, theta, xi, rho, q)
+ existing EuropeanOption
        ↓
PricingProblem
        ├── HestonFourierEuropeanOption
        └── HestonMonteCarloEuropeanOption
```

with explicit Fourier quadrature evidence, seeded full-truncation-Euler Monte Carlo evidence, variance-boundary diagnostics, Feller diagnostics, exact deterministic-variance handling at `xi=0`, and independent cross-method validation.

### M6 — Heston calibration, parameter recovery, and inverse-problem evidence

Established the first noisy multi-parameter financial inverse problem:

```text
HestonPriceCalibrationTarget(s)
+ fixed spot / rate / q
+ HestonCalibrationBounds
+ price-space residual / weighting semantics
+ M5 Fourier forward method
        ↓
HestonCalibrationProblem
+ ScipyLeastSquaresHestonCalibration
        ↓
HestonCalibrationResult
+ residuals
+ optimizer termination
+ local Jacobian identifiability evidence
```

M6 estimates direct financial coordinates `(v0, kappa, theta, xi, rho)`. `v0` remains state-like; no optimizer-only transform is exposed. The problem owns residual weighting; the optimizer owns search mechanics.

Evidence includes known-truth recovery, multiple starts, controlled target perturbation, a deliberately rank-deficient three-target counterexample, and a provenance-preserving 14-contract SPX calibration reference.

M4 and M6 provide two real inverse consumers but still do not justify a universal runtime inverse/optimizer framework.

## M7 — Empirical Validation, Model Risk, and Black-Scholes vs Heston

**Status: active independent workstream; not authoritative until merged.**

Central question:

> Does Heston's additional stochastic-volatility structure earn its place relative to Black-Scholes?

M7 should consume merged M3–M6 capabilities and produce the first explicit comparative validation/model-risk result.

Required pressure includes, where supported by evidence:

- fair in-sample comparison;
- out-of-sample option pricing error;
- residual structure across strike/maturity;
- parameter stability and identifiability;
- calibration/input sensitivity;
- multiple-start/failure behavior;
- assumptions and failure modes;
- hedging evidence only where M3 semantics support the comparison;
- computational cost.

Protect:

```text
better in-sample fit != better out-of-sample model
optimizer convergence != reliable identification
more flexible model != lower model risk
model fits prices != model is valid
```

UI4 runs in parallel but must not encode M7 conclusions before M7 lands.

## M8 — Performance engineering and targeted C++

**Status: planned after M7.**

Required order:

```text
correct Python reference
        ↓
representative workload
        ↓
profile
        ↓
measured hotspot
        ↓
narrow C++ acceleration
        ↓
Python/C++ parity
        ↓
re-measure
```

Do not create a native backend framework before a real hotspot earns it.

Candidate workloads should come from actual M5–M7 computation, such as repeated Heston forward valuation or calibration objective evaluation, rather than from synthetic microbenchmarks disconnected from the research workflow.

## M9 — v0.1 flagship release

**Status: planned.**

Productize the coherent research story without adding another major model.

Expected outputs include:

- a reproducible flagship study;
- clear market-data/provenance instructions;
- explicit validation/model-risk conclusions and non-claims;
- polished plots/tables/navigation;
- measured performance evidence;
- tested standalone native application artifact;
- release documentation/tag.

A technically sophisticated reader should be able to answer:

> Why should I trust these implementations and conclusions?

without relying on plausible-looking prices alone.

## Native UI track

```text
UI1  native architecture + Black-Scholes analytic vertical       complete
UI2  valuation comparison / convergence / uncertainty / Greeks  complete
UI3  dynamic hedging + market evidence / implied volatility     complete
UI4  Heston forward valuation + calibration / identifiability   complete
UI5  validation/model-risk + performance/release evidence       gated
```

### UI1 — architecture and first vertical

Established PySide6 + Qt Quick/QML with a curated controller boundary, Qt-free finance core, frontend-neutral application/presentation semantics, local QThread execution, offscreen QML smoke, and standalone deployment proof.

### UI2 — M2 Workbench

Extended the same Black-Scholes Study to analytic/CRR/Monte Carlo comparison, convergence and sampling uncertainty, plus analytic-vs-finite-difference Greeks.

### UI3 — M3/M4 Workbench

Added separate dynamic-control and observed-market/scalar-inverse workflows. Preserved model-generated paths versus observed market provenance, hedge path versus replicate evidence, and raw/normalized/inferred market layers.

### UI4 — Heston and rich inverse-problem Workbench

UI4 consumes only authoritative merged M5/M6 contracts.

Forward valuation exposes the model change explicitly:

```text
Black-Scholes: S_t + constant volatility
Heston:        (S_t, v_t) + stochastic variance + correlated shocks
```

while preserving the European-option contract and forward-pricing question.

The same Heston `PricingProblem` is evaluated with authoritative Fourier and Monte Carlo methods. Method-specific evidence remains specific: Fourier integration/resolution/work counts versus MC sampling uncertainty, timesteps, variance scheme, and negative-variance proposal diagnostics.

Calibration is a separate inverse workspace over actual M6 price-space contracts. It exposes direct financial coordinates/bounds, target/objective/weighting semantics, optimizer starts/configuration, truth recovery, residuals, multiple starts, rank/conditioning evidence, the thin non-identifiability counterexample, and the committed derived SPX calibration reference/provenance.

UI4 deliberately does **not** invent:

- implied-volatility-space Heston calibration;
- Heston path trajectories absent from merged M5 results;
- optimizer progress absent from M6;
- hidden transformed parameters;
- posterior uncertainty;
- M7 model-comparison conclusions.

Heavier Heston work reuses QThread and earns one narrow addition: concrete job identity plus stale-result rejection when relevant draft inputs change. It does not create a scheduler/cancellation framework.

### UI5 — handoff

**Status: gated on merged evidence.**

UI5 should be designed only after M7 is squash-merged and verified on `main`. It may then expose actual comparative validation/model-risk evidence. M8 may add measured performance/profiling/release pressure if those capabilities are also merged.

UI5 must not pre-build generic model-comparison, validation, risk, performance-dashboard, optimizer, plugin, or reporting frameworks merely because later milestones can be imagined.

## Parallelism guidance

Current ownership boundaries allow:

```text
M7 validation/model risk     ||     UI4 desktop completion
```

because UI4 consumes only merged M5/M6 behavior and M7 owns new validation evidence.

After UI4 merges, M7 may reconcile shared status/roadmap documentation with its final merged state. UI5 should wait for M7 authority rather than consuming M7's open branch.

Do **not** begin C++ acceleration before M8 produces a measured hotspot.

## Post-v0.1 directions

Potential later specializations include rates, XVA/counterparty credit, and portfolio market risk. The mathematical taxonomy can organize them, but it does not justify implementing their operational infrastructure before concrete research/product pressure exists.

A later v0.2 may replicate a modern research direction, including possibly rough volatility, only after reviewing then-current literature and the demonstrated limitations of v0.1.
