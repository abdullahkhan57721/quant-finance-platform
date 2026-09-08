# Development Roadmap

## Mission

Build a professional quantitative-finance research and model-validation platform whose first specialization is **equity derivatives and volatility modeling**.

The project should demonstrate quantitative-finance knowledge, mathematical modeling, numerical methods, reproducible research, calibration, pricing, risk reasoning, model validation, empirical analysis, performance engineering, testing, typing, documentation, CI, Python, and modern C++.

The project is not a feature checklist. Each increase in model or architectural complexity must be justified by evidence, except for the narrow foundational asset-pricing semantic decomposition accepted by ADR 0001.

## v0.1 research narrative

```text
mathematical asset-pricing composition foundation
        ↓
Black-Scholes theory + first concrete specialization
        ↓
independent implementation
        ↓
numerical cross-validation
        ↓
Greeks / replication
        ↓
delta-hedging experiments
        ↓
real option-market evidence
        ↓
observe smile/skew + BS deficiencies
        ↓
Heston
        ↓
independent Heston valuation methods
        ↓
calibration
        ↓
parameter recovery + stability
        ↓
out-of-sample/model-risk comparison
        ↓
profile actual bottlenecks
        ↓
targeted C++ acceleration
        ↓
portfolio-quality release
```

## M0 — Engineering bootstrap

**Purpose:** Establish repository truth and quality gates without inventing finance abstractions.

Expected outputs:

- source-layout Python package;
- pytest, Ruff, Pyright;
- GitHub Actions CI;
- `AGENTS.md`;
- current-state and roadmap docs;
- architecture index and guardrails;
- reproducibility/RNG and future Python/C++ policy.

**Historical non-goal:** M0 itself added no Black-Scholes or finance-domain code.

---

## M0A — Mathematical pricing composition foundation

**Question:** Can the platform represent the stable mathematical responsibilities of arbitrage-free asset pricing explicitly, without turning them into a universal finance framework?

Conceptual decomposition:

```text
state space / modeled state
+
stochastic law
+
model parameter values
+
financial contract → contingent cash-flow stream
+
numeraire
+
numeraire-associated pricing-measure semantics
        ↓
PricingProblem
        +
supported ValuationMethod
        ↓
immutable ValuationResult
```

Expected capabilities:

- generic state-space, modeled-state, and path semantics that do not require finite-dimensional or Markov structure;
- stochastic-law responsibility without a universal drift/diffusion ontology;
- model-specific immutable/value-like parameter objects kept separate from law structure;
- immutable cash flows and cash-flow streams;
- contract semantics that map paths to cash flows and own no valuation/calibration/market-data/portfolio behavior;
- strictly-positive numeraire access;
- distinct physical- and pricing-measure semantics, with Q associated to its numeraire and no generic change-of-measure engine;
- immutable compositional `PricingProblem`;
- valuation-method compatibility separate from structural validity;
- narrow immutable present-value result;
- one tiny deterministic composition fixture proving the architecture without implementing M1.

Architectural rule: ADR 0001 supersedes the ordinary two-consumer extraction discipline **only** for this foundational pricing-semantic core. All unrelated application abstractions remain evidence-driven.

---

## M1 — European options and Black-Scholes reference vertical

**Question:** Can the platform specialize the M0A pricing semantics to represent and analytically value its first concrete financial instrument correctly?

Approximate composition:

```text
Equity state / path
+
GBM / Black-Scholes stochastic law
+
Black-Scholes parameters
+
European call/put contract
+
money-market numeraire
+
risk-neutral pricing semantics
        ↓
PricingProblem
        +
Black-Scholes closed-form ValuationMethod
        ↓
ValuationResult
        ↓
theoretical validation evidence
```

Expected capabilities:

- European call/put terminal cash-flow semantics;
- valuation-ready equity state with explicit date/year-fraction treatment;
- concrete money-market/risk-free discounting semantics and explicit dividend/carry treatment without creating a general rates framework;
- GBM / Black-Scholes stochastic-law structure and separate parameter values under the relevant pricing measure;
- analytic closed-form valuation as a compatible valuation method;
- put-call parity;
- arbitrage bounds;
- known limiting/sanity cases and independently justified benchmark values;
- formula traceability.

Architectural goal: make every M1-specific choice a specialization of M0A. Do not create a competing isolated Black-Scholes API, a universal `FinancialModel`, or unrelated market/rates abstractions.

---

## M2 — Independent valuation and Greeks

**Question:** Can independent methods reproduce the analytical reference and converge for the right reasons?

Expected capabilities:

- CRR/binomial valuation as another valuation method over the supported Black-Scholes problem family;
- Monte Carlo valuation with explicit RNG ownership;
- analytic Greeks;
- bump-and-revalue/finite-difference Greeks;
- convergence studies;
- cross-method validation.

Evidence:

```text
Black-Scholes analytic ↔ binomial
Black-Scholes analytic ↔ Monte Carlo
analytic Greeks ↔ numerical Greeks
```

M2 should let the second real valuation consumers pressure-test the M0A method/problem boundaries. Do not generalize Greek/result/statistics structures beyond what the actual consumers require.

---

## M3 — Black-Scholes as a falsifiable model

**Question:** Does the replication logic behind Black-Scholes work, and how does it fail as assumptions are weakened?

Primary study: **delta hedging / replication error**.

Expected experiments:

- idealized Black-Scholes/GBM world;
- discrete rebalancing frequency;
- volatility misspecification;
- transaction-cost sensitivity where justified;
- stochastic-volatility misspecification when later model support makes comparison meaningful;
- delta-hedged P&L and terminal replication error.

This milestone introduces risk and P&L evidence locally to the equity-volatility research question. It does **not** justify a generic portfolio/VaR/scenario framework.

---

## M4 — Real option-market evidence

**Question:** What does the observed option market do that constant-volatility Black-Scholes cannot represent?

Expected capabilities:

- provenance-aware option-chain ingestion for research;
- deterministic fixtures/snapshots for CI and reproducibility;
- quote normalization and validation;
- implied-volatility inversion;
- strike/maturity smile/skew/surface analysis;
- data-quality and appropriate static-arbitrage diagnostics.

Scientific purpose:

```text
model assumption
    ↓
empirical contradiction
    ↓
motivation for richer volatility dynamics
```

Do not make core tests depend on live external APIs.

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

## M6 — Calibration

**Question:** Can Heston parameters be inferred from known and observed targets, and how trustworthy is that inference?

Progression:

```text
synthetic parameter recovery
        ↓
calibration objective
        ↓
numerical optimization
        ↓
real volatility-surface calibration
        ↓
residual diagnostics
```

Protect:

```text
calibration problem != numerical optimizer
stochastic law != calibrated parameter values
```

Expected evidence:

- synthetic parameter recovery;
- residual analysis;
- multiple starts / optimization robustness as justified;
- parameter stability;
- identifiability concerns where observed.

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

Narrow spot/volatility/parameter shocks may be used when they answer the model-validation question. Do not generalize them into a universal market-risk engine without additional consumers.

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

Review the then-current literature and select a small number of research models/methods based on a demonstrated limitation of the classical platform.

Rough volatility is a promising first direction, not a pre-committed paper/model.

For a chosen paper/model:

```text
read paper
    ↓
identify problem and assumptions
    ↓
derive/understand mathematics
    ↓
implement within existing architecture
    ↓
reproduce meaningful published result
    ↓
independently validate
    ↓
compare with established baseline
    ↓
measure computational cost
    ↓
analyze limitations/model risk
    ↓
document conclusion
```

### Later specializations

Potential later growth:

```text
Quant Finance Platform
├── Equity Derivatives / Volatility
├── Counterparty Credit Risk / XVA
├── Rates
└── Portfolio Market Risk
```

Do not implement these future specializations prematurely.

## Parallelism guidance

M0A must settle before revised M1 because it defines M1's composition contracts. M1 and the early numerical validation milestones remain intentionally mostly sequential because each supplies evidence and consumers for the next.

Reasonable parallel work once shared contracts stabilize includes:

- documentation/report presentation alongside validated implementation;
- market-data provenance/fixture preparation alongside later Black-Scholes validation studies;
- Heston validation-study preparation alongside stable Heston valuation code.

Do **not** begin a parallel C++ workstream before profiling creates a concrete native-acceleration task.
