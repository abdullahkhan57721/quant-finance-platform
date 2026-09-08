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
Heston stochastic volatility                             ← M5 next
        ↓
independent Heston valuation methods
        ↓
calibration / inverse problem
        ↓
parameter recovery + stability
        ↓
out-of-sample/model-risk validation
        ↓
profile actual bottlenecks
        ↓
targeted C++ acceleration
        ↓
portfolio-quality release
```

## M0 — Engineering bootstrap

**Status: complete.**

**Purpose:** Establish repository truth and quality gates without inventing finance abstractions.

Implemented outputs include the source-layout package, pytest/Ruff/Pyright, GitHub Actions CI, repository operating rules, architecture/current-state/roadmap documentation, and reproducibility/native-backend guardrails.

---

## M0A — Mathematical Quant-Finance Architecture Foundation

**Status: complete.**

**Question:** Can the platform encode the stable mathematical distinctions of quantitative finance directly enough that later workflows compose around well-defined questions, without turning those distinctions into universal software frameworks?

M0A established the platform-wide taxonomy and the conceptual execution pattern:

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

**Question:** Can the platform specialize the M0A pricing semantics to represent and analytically value its first concrete financial instrument correctly?

Implemented composition:

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

M1 committed explicit calendar/date, ACT/365F, continuously compounded money-market rate, continuous dividend/carry, annualized decimal volatility, call/put, and present-value semantics, with benchmark, parity, bounds, limiting-case, and formula-traceability evidence.

---

## M2 — Independent valuation and sensitivity/Greeks

**Status: complete.**

**Question:** Can independent methods reproduce the analytical reference, and can local sensitivities be established independently for the right reasons?

Implemented valuation plurality:

```text
same M1 PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
```

Implemented sensitivity specialization:

```text
BlackScholesSensitivityProblem
        ├── AnalyticBlackScholesSensitivity
        └── FiniteDifferenceBlackScholesSensitivity
        ↓
BlackScholesSensitivityResult
```

Evidence includes CRR convergence/support semantics, seeded Monte Carlo uncertainty and convergence, analytic Greeks, finite-difference cross-validation, and bump-size studies. M2 does not create a universal sensitivity, solver, risk, or portfolio framework.

---

## M3 — Dynamic hedging / control

**Status: complete.**

**Question:** Does the replication logic behind Black-Scholes work dynamically, and how does replication degrade when implementation/model assumptions are weakened?

Implemented concrete composition:

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

Evidence includes exact-path reproducibility, self-financing identities, no-lookahead behavior, rebalance-frequency comparisons, volatility misspecification, transaction-cost drag, and replicate-integrity checks. M3 deliberately remains narrower than a generic control, strategy, execution, portfolio, or physical-forecast framework.

---

## M4 — Market evidence / inverse problems

**Status: complete.**

**Question:** What does the observed option market do that constant-volatility Black-Scholes cannot represent, and can the first inverse quantity—implied volatility—be inferred with explicit observation semantics?

Implemented composition:

```text
real option market
        ↓
RawOptionQuote + RawUnderlyingObservation
        +
ObservationProvenance
        ↓
explicit midpoint normalization
        ↓
NormalizedOptionObservation
        ↓
BlackScholesImpliedVolatilityProblem
        +
BisectionImpliedVolatility
        ↓
ImpliedVolatilityResult
        ↓
strike / maturity evidence + conditioning diagnostics
```

M4 establishes:

- immutable raw option and underlying observations with provenance;
- explicit raw-versus-normalized lifecycle and versioned midpoint policy;
- rejection of missing/nonpositive/crossed quotes and unsupported contract semantics;
- European option price-bound feasibility checks before numerical inversion;
- a concrete Black-Scholes implied-volatility inverse problem separate from its numerical root finder;
- deterministic bisection with explicit volatility domain, tolerances, and failure semantics;
- M2-Vega conditioning evidence including local inverse-Vega and half-spread IV sensitivity;
- deterministic synthetic strike/maturity fixtures for CI;
- narrow monotonicity/convexity quote diagnostics without surface repair; and
- a pinned SPX derived-evidence artifact with reproducible source provenance and explicit model assumptions.

Protect:

```text
raw observation != normalized observation != modeled state
observed price != model-implied value
implied volatility != observed/physical volatility
inverse financial problem != root-finding method != inverse result
normalization != inference
solver failure != poor inverse conditioning
```

Empirical result: under the documented flat rate/carry and OTM quote-selection assumptions, the January 4, 2023 SPX evidence shows persistent downside strike skew in both an approximately 30-day and approximately 114-day expiry, plus maturity dependence. One constant Black-Scholes volatility cannot reconcile the observed option set.

The evidence also contains discrete convexity violations in same-right midpoint slices. M4 treats those as data-quality evidence rather than silently constructing an arbitrage-repaired surface.

Core CI remains independent of live external APIs. The empirical artifact records derived/model outputs and pinned source provenance without redistributing raw rows whose licensing is unclear.

M4 does **not** create a generic provider framework, generic quote-cleaning/staleness framework, arbitrage-free volatility-surface framework, physical volatility forecast, Heston model, Heston calibration, or generic inverse engine.

---

## M5 — Heston model and independent valuation

**Status: next; unblocked by merged/verified M3 and M4.**

**Question:** Can a stochastic-volatility model represent behavior Black-Scholes structurally cannot, and can we value it by independent methods?

M5 is now motivated by two different falsification pressures:

```text
M3:
continuous frictionless replication assumptions
        ↓
discrete hedging / misspecification / transaction-cost evidence

M4:
one constant volatility scalar
        ↓
observed SPX strike skew + maturity dependence
```

Expected capabilities:

- Heston state/law structure and parameter object(s) specialized through the M0A pricing core;
- characteristic-function/Fourier valuation method;
- Monte Carlo valuation method;
- parameter-domain validation;
- Fourier ↔ Monte Carlo comparison;
- convergence/stability and limiting/sanity studies.

Keep separate:

```text
Heston stochastic law
!= Heston parameter values
!= Fourier valuation method
!= Monte Carlo valuation method
```

Do not fold calibration into M5 merely because M4 introduced an inverse problem. M6 owns Heston calibration.

---

## M6 — Calibration / inverse problem

**Question:** Can Heston parameters be inferred from known and observed targets, and how trustworthy is that inference?

Progression:

```text
synthetic parameter recovery
        ↓
calibration / inverse problem
        ↓
objective + weighting + constraints
        ↓
numerical optimization method
        ↓
real volatility-structure calibration
        ↓
residual diagnostics
```

Protect:

```text
inverse / calibration problem != numerical optimizer
observations != inferred parameters
stochastic law != calibrated parameter values
```

Expected evidence includes synthetic parameter recovery, residual analysis, multiple starts/optimizer robustness where justified, parameter stability, and identifiability concerns where observed.

---

## M7 — Empirical/model-risk comparison

**Question:** Does Heston's added complexity earn its place relative to Black-Scholes?

Compare where data and methods support it:

- in-sample fit;
- out-of-sample pricing error;
- hedging error, reusing the M3 control/accounting boundary where semantically valid;
- parameter stability and identifiability;
- sensitivity to inputs/parameters;
- calibration instability;
- model-price residuals;
- computational cost; and
- documented failure modes and assumptions.

M7 should consume M4's observation/provenance semantics rather than introduce a parallel market-data lifecycle.

---

## M8 — Performance engineering and targeted C++

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

No native backend framework should precede the second real implementation.

---

## M9 — v0.1 flagship release

**Purpose:** Productize the coherent research story without adding another major model.

Expected outputs include a reproducible flagship study, polished navigation/docs, market-data/provenance instructions, validation/model-risk reports, high-quality plots/tables, measured performance evidence, documented assumptions/non-claims, and a release tag.

A technically sophisticated reader should be able to answer:

> Why should I trust these implementations and conclusions?

without relying on plausible-looking prices alone.

## Post-v0.1

### v0.2 — Modern research replication

Review the then-current literature and select a small number of research models/methods based on demonstrated limitations of the classical platform. Rough volatility is a promising direction, not a pre-committed paper/model.

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

M0A through M4 are complete. Their production ownership boundaries are now settled:

```text
pricing
    ↑
sensitivity
    ↑
control / dynamic replication        observation / normalization
                                      ↓
                                inverse inference
```

M3 owns model-generated dynamic paths, hedge actions/accounting, and replication evidence. M4 owns external observations, provenance, normalization, implied-volatility inference, conditioning, and market-evidence diagnostics. Neither should redefine the other's contracts for convenience.

M5 may now begin from merged M3/M4 truth. M6 remains downstream of a validated Heston valuation implementation. UI2 may proceed against merged M2 behavior while later UI work can consume M3/M4 only after the product semantics are deliberately designed.

Do **not** begin a parallel C++ workstream before profiling creates a concrete native-acceleration task.
