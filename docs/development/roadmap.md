# Development Roadmap

## Mission

Build a professional quantitative-finance research and model-validation platform whose first specialization is **equity derivatives and volatility modeling**.

The project should demonstrate quantitative-finance knowledge, mathematical modeling, numerical methods, reproducible research, calibration/inference, pricing, sensitivity, risk reasoning, model validation, empirical analysis, performance engineering, testing, typing, documentation, CI, Python, and modern C++.

The project is not a feature checklist. Ordinary software abstractions must earn their place through concrete consumers and evidence. ADR 0002 permits stable **mathematical domain distinctions** to be represented explicitly from the outset, but does not authorize speculative universal operational frameworks.

## v0.1 research narrative

```text
mathematical problem architecture + pricing foundation   ← M0A complete
        ↓
Black-Scholes theory + first concrete specialization     ← M1 complete
        ↓
independent valuation methods + sensitivity              ← M2 complete
        ├───────────────────────────────┐
        ↓                               ↓
delta-hedging / control             market evidence +
experiments                          implied-vol inference
← M3 complete                       ← M4 complete
        │                               │
        └───────────────┬───────────────┘
                        ↓
Heston stochastic volatility + independent valuation     ← M5 complete
        ↓
Heston calibration / inverse problem                     ← M6 complete
        ↓
empirical validation + Black-Scholes vs Heston model risk← M7 next
        ↓
profile actual bottlenecks                               ← M8
        ↓
targeted C++ acceleration
        ↓
portfolio-quality v0.1 release                           ← M9
```

M0A through M6 now form a coherent quantitative narrative rather than independent feature milestones:

```text
theory
→ independent numerical evidence
→ sensitivity / replication pressure
→ observed-market falsification pressure
→ richer stochastic-volatility forward model
→ calibrated inverse problem with identifiability evidence
→ out-of-sample/model-risk comparison
```

---

## M0 — Engineering bootstrap

**Status: complete.**

Established repository truth, source-layout packaging, pytest/Ruff/strict-Pyright quality gates, GitHub Actions, operating rules, durable architecture/current-state/roadmap documentation, and reproducibility/native-backend guardrails without inventing finance abstractions.

---

## M0A — Mathematical Quant-Finance Architecture Foundation

**Status: complete.**

Established the platform-wide mathematical taxonomy and the conceptual execution pattern:

```text
financial / mathematical foundations
        ↓
problem family
        ↓
supported solution method
        ↓
specific immutable result / evidence
```

```text
Problem + supported Method -> specific immutable Result
```

The first production problem family is pricing. M0A also established the observation/model boundary and the rule that mathematical generality does not imply universal operational APIs.

---

## M1 — European options and Black-Scholes reference vertical

**Status: complete.**

Implemented the first concrete pricing composition:

```text
EquityState / EquityStateSpace
+
BlackScholesLaw + BlackScholesParameters
+
EuropeanOption → terminal CashFlowStream
+
FlatMoneyMarketNumeraire + PricingMeasureSemantics
        ↓
PricingProblem
        +
BlackScholesClosedForm
        ↓
ValuationResult(present_value)
```

Committed explicit calendar/date, ACT/365F, continuously compounded money-market rate, continuous dividend/carry, annualized decimal volatility, call/put, and present-value semantics, with benchmark, parity, bounds, limiting-case, and formula-traceability evidence.

---

## M2 — Independent valuation and sensitivity/Greeks

**Status: complete.**

Pressure-tested the analytical reference with independent valuation methods:

```text
same M1 PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
```

and established the first concrete sensitivity specialization:

```text
BlackScholesSensitivityProblem
        ├── AnalyticBlackScholesSensitivity
        └── FiniteDifferenceBlackScholesSensitivity
        ↓
BlackScholesSensitivityResult
```

Evidence covers CRR convergence/support, seeded Monte Carlo uncertainty, analytic Greeks, finite-difference cross-validation, and bump-size behavior without creating universal solver/sensitivity/risk frameworks.

---

## M3 — Dynamic hedging / control

**Status: complete.**

Turned M2 Delta into a concrete dynamic policy input:

```text
Black-Scholes pricing problem
+
exact-transition pricing-measure GBM path
+
explicit rebalance schedule
+
M2 analytic Delta consumed as hedge policy
+
stock + money-market cash accounting
+
optional proportional stock-trade cost
        ↓
DeltaHedgeResult
        ↓
ReplicationErrorSummary
```

Evidence covers reproducibility, self-financing identities, no-lookahead behavior, rebalance-frequency effects, volatility misspecification, transaction-cost drag, and replicate integrity. M3 remains narrower than a generic control/strategy/portfolio/execution framework.

---

## M4 — Market evidence / scalar inverse problems

**Status: complete.**

Established the first production observed-market and inverse lifecycle:

```text
real option market
        ↓
RawOptionQuote + RawUnderlyingObservation
        + ObservationProvenance
        ↓
explicit midpoint normalization
        ↓
NormalizedOptionObservation
        ↓
BlackScholesImpliedVolatilityProblem
        + BisectionImpliedVolatility
        ↓
ImpliedVolatilityResult
        ↓
strike / maturity evidence + conditioning diagnostics
```

M4 protects raw/normalized/model/inferred distinctions, checks financial price feasibility before root solving, preserves M2-Vega conditioning evidence, provides deterministic CI fixtures, and pins a real SPX research workflow. The January 4, 2023 evidence exhibits downside skew and maturity dependence that one constant Black-Scholes volatility cannot reconcile under the explicit input convention.

---

## M5 — Heston stochastic volatility and independent valuation

**Status: complete.**

Responded to M4's empirical pressure with a richer forward model, not immediate calibration:

```text
HestonEquityState(spot, instantaneous variance)
+
HestonLaw
+
HestonParameters(kappa, theta, xi, rho, q)
+
existing EuropeanOption
+
existing FlatMoneyMarketNumeraire + PricingMeasureSemantics
        ↓
PricingProblem
        ├── HestonFourierEuropeanOption
        └── HestonMonteCarloEuropeanOption
```

M5 keeps current variance, structural law, parameter values, pricing method, and future fitted estimates separate. It establishes characteristic-function/Fourier valuation, independent full-truncation Euler Monte Carlo, explicit RNG/numerical ownership, Feller-condition diagnostics, exact `xi=0` deterministic-variance handling, and cross-method validation.

---

## M6 — Heston calibration, parameter recovery, and generalized inverse pressure

**Status: complete.**

**Question:** Can the platform infer Heston financial coordinates from known and observed targets while representing calibration as a financial inverse problem rather than a method hanging off the Heston model?

Implemented composition:

```text
synthetic Heston price targets
or
M4 NormalizedOptionObservation + provenance
        ↓
HestonPriceCalibrationTarget
        +
fixed observed/model spot, rate, q
        +
HestonCalibrationBounds
        +
explicit price-space residual / weighting semantics
        ↓
HestonCalibrationProblem
        +
ScipyLeastSquaresHestonCalibration
        ↓
HestonCalibrationResult
        +
per-target residuals
        +
local Jacobian identifiability evidence
```

The five inferred financial coordinates are:

```text
v0, kappa, theta, xi, rho
```

`v0` remains state-like and separate from the immutable structural `HestonParameters`; spot, rate, and continuous dividend yield are fixed explicit inputs for the first calibration consumer.

M6 implements **option-price-space** calibration only. The problem owns the objective and weighting rather than the optimizer. Two concrete weighting policies are supported because they have real consumers:

```text
UNIFORM_PRICE
    residual scale = 1

BID_ASK_HALF_SPREAD
    residual scale = (ask - bid) / 2
```

The first policy supports known-truth synthetic recovery. The second gives normalized market price residuals an explicit quote-width scale without claiming that half-spread is a statistical variance or universal likelihood.

`HestonCalibrationBounds` records the admissible financial calibration domain. Those domain bounds are distinct from M5 structural validity, from SciPy's numerical bound implementation, and from parameter transforms. The first numerical method uses direct financial coordinates and no transform. The Feller condition remains diagnostic rather than being silently imposed as a calibration constraint.

The numerical method is one concrete SciPy trust-region-reflective bounded nonlinear least-squares solver. It owns initial guess, tolerances, finite-difference Jacobian strategy, maximum function evaluations, and mutable search state. It does not own the financial target/objective semantics.

### Synthetic recovery evidence

M6 begins with truth-known experiments. A deterministic 20-option surface over four maturities and five strikes is generated from:

```text
v0    = 0.04
kappa = 2.0
theta = 0.04
xi    = 0.5
rho   = -0.7
q     = 0.01
```

Multiple materially different initial guesses recover the known coordinates to tight numerical tolerance with essentially zero pricing residual. Controlled target-price perturbations move the recovered coordinates while preserving a low objective, exposing parameter sensitivity to the calibration evidence.

### Identifiability evidence

A deliberately thin three-quote, one-maturity problem has fewer residual equations than unknown coordinates. Multiple starts can converge to near-zero price loss while producing materially different Heston estimates. The local standardized-residual Jacobian is rank deficient.

This directly establishes:

```text
optimizer converged
!= uniquely identified parameters

small calibration loss
!= trustworthy parameter estimate
```

For general completed calibrations, M6 computes singular values and rank from the problem-standardized residual Jacobian after scaling parameter columns by their explicit financial-domain widths. A finite condition number is reported only when the five-coordinate Jacobian has full column rank. This is local first-order evidence, not posterior uncertainty or proof of global identification.

### Real-market calibration

The real workflow consumes the same M4 January 4, 2023 SPX source lineage and selected 14 OTM-side contracts:

```text
local pinned raw CSV
→ M4 raw observations + provenance
→ M4 midpoint normalization
→ M6 market calibration targets
→ half-spread-standardized Heston price calibration
```

The three-start reference fit clusters around:

```text
v0      ≈ 0.04447
kappa   ≈ 3.2575
theta   ≈ 0.06622
xi      ≈ 0.62715
rho     ≈ -0.77937
```

with standardized sum-squared objective around `12.56`. The local domain-scaled Jacobian is full rank but has condition number about `404`, so stable optimizer convergence coexists with meaningful conditioning risk.

Core CI does not require network/live market data. The raw source rows are not redistributed; the local replay script records provenance/hash metadata and produces derived calibration evidence.

### Generalized inverse architecture decision

M4 and M6 now provide the two real consumers needed to judge extraction pressure:

```text
M4: scalar monotone Black-Scholes root inversion
M6: bounded five-coordinate noisy nonlinear least squares
```

What is shared is the conceptual ADR-0002 responsibility split:

```text
financial inverse problem
!= numerical method
!= immutable result/evidence
```

Their operational responsibilities remain materially different. M6 therefore **does not extract a universal runtime inverse/optimizer hierarchy**. A later third inverse consumer may reopen the decision if genuine shared software behavior appears.

See `docs/models/m6_heston_calibration.md`, `docs/evidence/m6_spx_heston_calibration_reference.json`, and `docs/quantitative_conventions.md`.

---

## M7 — Empirical Validation, Model Risk, and Black-Scholes vs Heston Comparison

**Status: next.**

**Question:** Does Heston's added complexity earn its place relative to Black-Scholes?

M7 should consume the authoritative outputs already established by M3–M6 rather than introduce a new observation/calibration lifecycle.

Required comparison pressure includes, where the evidence supports it:

- in-sample fit;
- out-of-sample option pricing error;
- residual structure across strike/maturity;
- Heston parameter stability and identifiability;
- calibration sensitivity to observations/inputs;
- multiple-start and calibration failure behavior;
- Black-Scholes versus Heston assumptions and failure modes;
- hedging evidence only where M3's control/accounting semantics are valid for the comparison; and
- computational cost.

Protect:

```text
better in-sample fit
!= better out-of-sample model

optimizer convergence
!= reliable identification

more flexible model
!= lower model risk

model fits prices
!= model is valid
```

M7 should produce the first explicit model-risk decision about when the extra stochastic-volatility structure is justified and where it still fails.

---

## M8 — Performance engineering and targeted C++

**Status: planned after M7.**

**Question:** Where is computation actually expensive, and can measured hotspots be accelerated without moving high-level financial semantics out of Python?

Required order:

```text
correct Python reference
        ↓
profile
        ↓
identify measured hotspot
        ↓
implement narrow C++ kernel
        ↓
Python/C++ parity tests
        ↓
benchmark runtime/memory
```

No native backend framework should precede a measured concrete acceleration task.

---

## M9 — v0.1 flagship release

**Status: planned.**

Productize the coherent research story without adding another major model. Expected outputs include a reproducible flagship study, polished navigation/docs, market-data/provenance instructions, validation/model-risk reports, high-quality plots/tables, measured performance evidence, documented assumptions/non-claims, and a release tag.

A technically sophisticated reader should be able to answer:

> Why should I trust these implementations and conclusions?

without relying on plausible-looking prices alone.

## Native UI track

**UI1, UI2, and UI3 are complete.** The native architecture is PySide6 + Qt Quick/QML with quantitative authority remaining below the presentation layer.

The next desktop pressure is **UI4**, now able to consume actual M5/M6 contracts rather than speculate about them. A Heston/calibration workspace may visualize:

```text
Heston forward valuation
calibration targets vs model prices
per-contract residuals
calibrated financial coordinates
multiple-start outcomes
local Jacobian rank / condition evidence
```

but QML must not own target construction, objective/weighting, financial bounds, optimization, or conditioning calculations.

## Post-v0.1

### v0.2 — Modern research replication

Review the then-current literature and select a small number of research models/methods based on demonstrated limitations of the classical platform. Rough volatility remains a promising direction, not a pre-committed paper/model.

### Later specializations

Potential later growth:

```text
Quant Finance Platform
├── Equity Derivatives / Volatility
├── Counterparty Credit Risk / XVA
├── Rates
└── Portfolio Market Risk
```

The mathematical taxonomy can organize these later domains, but it does not justify implementing their operational infrastructure prematurely.

## Parallelism guidance

M0A through M6 are complete. Their production ownership boundaries are settled enough for M7 and UI4 to proceed from merged truth:

```text
pricing
    ├── Black-Scholes forward methods
    └── Heston forward methods
          ↑
          └── M6 calibration consumes forward pricing

sensitivity
    ↑
control / dynamic replication

external observations / provenance
        ↓
normalization
        ↓
M4 scalar inverse inference
        ↓
M6 market calibration targets
```

M3 owns model-generated dynamic paths, hedge actions/accounting, and replication evidence. M4 owns external observations, provenance, normalization, implied-volatility inference, conditioning, and market-evidence diagnostics. M5 owns Heston forward-model state/law/parameter semantics plus Fourier/Monte Carlo valuation evidence. M6 owns the Heston calibration question, target/objective/weighting/bounds semantics, separate SciPy method, completed estimate/residuals, and identifiability evidence.

M7 may proceed after M6 is squash-merged and verified on `main`. UI4 may proceed in parallel once it consumes only merged M5/M6 APIs and does not force backend ownership changes for presentation convenience.

Do **not** begin a parallel C++ workstream before M8 profiling creates a concrete native-acceleration task.
