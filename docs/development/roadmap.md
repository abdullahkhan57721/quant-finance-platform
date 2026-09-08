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
        │                               │
        └───────────────┬───────────────┘
                        ↓
Heston stochastic volatility
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

Implemented outputs:

- source-layout Python package;
- pytest, Ruff, Pyright;
- GitHub Actions CI;
- `AGENTS.md`;
- current-state and roadmap docs;
- architecture index and guardrails;
- reproducibility/RNG and future Python/C++ policy.

---

## M0A — Mathematical Quant-Finance Architecture Foundation

**Status: complete.**

**Question:** Can the platform encode the stable mathematical distinctions of quantitative finance directly enough that later workflows compose around well-defined questions, without turning those distinctions into universal software frameworks?

M0A established the platform-wide taxonomy:

```text
financial / mathematical foundations
        ↓
problem family
        ↓
supported solution method
        ↓
specific immutable result / evidence
```

and the conceptual execution pattern:

```text
Problem + supported Method -> specific immutable Result
```

The first production problem family is pricing:

```text
state / stochastic law / parameters
+
contract / cash flows
+
numeraire / pricing-measure semantics
        ↓
PricingProblem
        +
supported ValuationMethod
        ↓
ValuationResult
```

M0A also established the observation/model boundary and the rule that mathematical generality does not imply universal operational APIs.

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

Capabilities and evidence include:

- explicit CRR step configuration and finite-tree no-arbitrage support semantics;
- CRR convergence toward the Black-Scholes analytical reference;
- explicit Monte Carlo path count and RNG seed ownership;
- exact terminal GBM sampling for the supported European payoff;
- immutable Monte Carlo present value, standard error, 95% normal-approximation confidence interval, path count, and seed;
- approximate `O(n^-1/2)` Monte Carlo standard-error evidence;
- analytic Delta, Gamma, Vega, Theta, and Rho;
- explicit variable, derivative-order, sign, units, and scaling semantics;
- central finite-difference cross-validation;
- multi-bump evidence separating truncation from cancellation/floating-point degradation; and
- dependency protection keeping pricing upstream of sensitivity.

M2 made one minimal correction to the M0A valuation contract: `evaluate()` preserves a method's specific immutable `ValuationResult` subtype, allowing Monte Carlo uncertainty to remain method-specific instead of becoming optional fields on every valuation result.

M2 does **not** create a universal sensitivity engine, compatibility registry, solver hierarchy, generic risk framework, or portfolio layer.

Keep distinct:

```text
financial model error
CRR discretization / approximation error
Monte Carlo sampling error
finite-difference truncation error
finite-difference cancellation / floating-point error
```

---

## M3 — Dynamic hedging / control

**Status: next; may run in parallel with M4.**

**Question:** Does the replication logic behind Black-Scholes work dynamically, and how does replication degrade when implementation/model assumptions are weakened?

Primary study: **discrete delta hedging / replication error**.

Expected pressure:

```text
modeled path / dynamics
+
contract liability
+
hedge action rule
+
rebalance schedule
+
financing / cash account
+
objective / terminal replication error
        ↓
concrete control / hedging question
```

Expected experiments include:

- idealized Black-Scholes/GBM world;
- discrete rebalancing frequency;
- volatility misspecification;
- transaction-cost sensitivity where justified;
- delta-hedged P&L / terminal replication error;
- later stochastic-volatility misspecification once richer model support exists.

M3 may consume merged M2 pricing and sensitivity capabilities, especially Delta, but must preserve:

```text
pricing problem != sensitivity problem != control problem
hedge policy != Greek
replication evidence != theoretical price
```

Do not create a generic portfolio/VaR/scenario engine from this first control consumer.

---

## M4 — Market evidence / inverse problems

**Status: next; may run in parallel with M3.**

**Question:** What does the observed option market do that constant-volatility Black-Scholes cannot represent, and can the first inverse quantity—implied volatility—be inferred with explicit observation semantics?

Expected capabilities:

- provenance-aware option observations / chain ingestion for research;
- deterministic curated fixtures/snapshots for CI and reproducibility;
- explicit timestamp/timezone, quote selection, normalization, missing/bad-quote policy, and licensing/provenance semantics where real data requires them;
- narrow implied-volatility inverse problem;
- root-finding as a method separate from the inverse financial question;
- strike/maturity smile/skew/surface evidence;
- data-quality and appropriate static-arbitrage diagnostics.

Protect:

```text
observed quote != modeled state
observed price != model-implied value
implied volatility != observed volatility
inverse problem != root finder
normalization != inference
```

Scientific purpose:

```text
constant-volatility model assumption
        ↓
observed market contradiction
        ↓
smile / skew evidence
        ↓
motivation for richer volatility dynamics
```

Core CI must not depend on live external APIs.

---

## M5 — Heston model and independent valuation

**Question:** Can a stochastic-volatility model represent behavior Black-Scholes structurally cannot, and can we value it by independent methods?

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

PDE valuation is optional future evidence, not a v0.1 requirement unless a real validation need justifies it.

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
real volatility-surface calibration
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
- hedging error;
- parameter stability;
- parameter identifiability;
- sensitivity to inputs/parameters;
- calibration instability;
- model-price residuals;
- computational cost;
- documented failure modes and assumptions.

M7 creates direct pressure for concrete validation and potentially risk problem semantics. Keep them scoped to the model-comparison evidence unless multiple workflows demonstrate a reusable operational boundary.

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

Expected outputs:

- one-command or clearly scripted reproducible flagship study;
- polished README and architecture navigation;
- market-data/provenance instructions;
- validation and model-risk report(s);
- high-quality plots/tables generated from committed result artifacts or reproducible runs;
- performance evidence before/after native acceleration;
- documented assumptions, limitations, and non-claims;
- release tag.

A technically sophisticated reader should be able to answer:

> Why should I trust these implementations and conclusions?

without relying on plausible-looking prices alone.

## Post-v0.1

### v0.2 — Modern research replication

Review the then-current literature and select a small number of research models/methods based on a demonstrated limitation of the classical platform. Rough volatility is a promising direction, not a pre-committed paper/model.

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

M0A, M1, and M2 are complete. M2 has stabilized the pricing/sensitivity contracts enough for M3 and M4 to proceed in parallel with explicit ownership boundaries:

```text
M3
owns dynamic hedging / control studies
consumes pricing + sensitivity
must not own market observations / implied-vol inference

M4
owns market observations / provenance + implied-vol inference
consumes pricing
must not own dynamic hedging / control
```

Neither branch should redefine merged M2 pricing/sensitivity contracts merely for convenience. If either discovers a real defect in those contracts, coordinate the correction explicitly rather than letting parallel branches diverge.

Shared current-state/roadmap/README/application-facing files should be coordinated to avoid documentation or UI conflicts.

Do **not** begin a parallel C++ workstream before profiling creates a concrete native-acceleration task.
