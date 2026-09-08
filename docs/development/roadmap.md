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
independent valuation methods + sensitivity              ← M2 next
        ↓
delta-hedging / control experiments
        ↓
real option-market observations
        ↓
implied-volatility inference + smile/skew evidence
        ↓
Heston
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

**Historical non-goal:** M0 itself added no Black-Scholes or finance-domain code.

---

## M0A — Mathematical Quant-Finance Architecture Foundation

**Status: complete.**

**Question:** Can the platform encode the stable mathematical distinctions of quantitative finance directly enough that later workflows compose around well-defined questions, without turning those distinctions into universal software frameworks?

### Mathematical taxonomy

```text
FINANCIAL / MATHEMATICAL FOUNDATIONS

state / state space
stochastic law
model parameters
probability semantics
physical measure P
pricing measure Q^N
numeraire N
market observations + provenance
financial contracts
cash flows
quantitative conventions

        ↓

PROBLEM FAMILIES

forward / pricing
inverse / inference
sensitivity
prediction
control / optimization
risk
validation

        ↓

SOLUTION METHODS

analytic / tree / Monte Carlo / Fourier / finite difference
root finding / optimization / filtering / regression / scenario methods / tests

        ↓

SPECIFIC IMMUTABLE RESULTS / EVIDENCE
```

Platform-wide conceptual pattern:

```text
Problem + supported Method -> specific immutable Result
```

This pattern is architectural. M0A does **not** introduce universal `Problem`, `Method`, or `Result` base classes.

### Implemented pricing foundation

The first production problem family is:

```text
state space / modeled state / state path
+
stochastic law + separate parameter values
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

Implemented pricing capabilities include:

- generic state-space, modeled-state, and path semantics that do not require finite-dimensional or Markov structure;
- stochastic-law responsibility without a universal drift/diffusion ontology;
- model-specific immutable/value-like parameter objects kept separate from law structure;
- immutable cash flows and cash-flow streams;
- contract semantics that map paths to cash flows and own no valuation/inference/market-data/portfolio behavior;
- strictly-positive numeraire access;
- distinct physical- and pricing-measure semantics, with Q associated to its numeraire and no generic change-of-measure engine;
- immutable compositional `PricingProblem`;
- valuation-method compatibility separate from structural validity;
- narrow immutable present-value result; and
- one tiny deterministic composition fixture proving the architecture without implementing M1 inside the foundation itself.

### Observation/model boundary

M0A establishes:

```text
real world
    ↓
observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready information

separately:

modeled state + stochastic law + parameters + probability semantics
```

Observed information must remain distinguishable from modeled or model-implied quantities.

### Scope rule

ADR 0002 is the current authority:

```text
Foundational mathematical domain distinctions
may be represented explicitly from the outset.

Problem-specific software frameworks
should remain narrow and evidence-driven.

Mathematical generality
does not imply
universal operational APIs.
```

The inverse, sensitivity, prediction, control, risk, and validation families are therefore documented but receive production abstractions only when their milestones create real behavior.

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
        ↓
theoretical validation evidence
```

Implemented capabilities:

- European call/put terminal cash-flow semantics;
- valuation-ready modeled equity spot state;
- explicit calendar valuation/expiry dates and Actual/365 Fixed year fractions;
- concrete flat money-market numeraire with continuously compounded annualized decimal rates, including negative rates;
- explicit continuous proportional dividend/carry yield;
- GBM / Black-Scholes stochastic-law identity separated from immutable parameter values;
- annualized decimal volatility semantics;
- analytic Black-Scholes closed-form valuation as a compatible M0A valuation method;
- put-call parity;
- discounted no-arbitrage bounds;
- expiry, zero-volatility, zero-spot, and zero-strike limiting cases;
- independently published benchmark values;
- convention-discriminating tests for Actual/365 Fixed and continuous compounding; and
- formula traceability in `docs/models/black_scholes.md`.

Architecturally, M1 keeps:

```text
state
!= stochastic law
!= parameters
!= contract
!= cash flows
!= numeraire
!= pricing measure
!= valuation method
!= valuation result
```

The risk-free rate is not duplicated in `BlackScholesParameters`; risk-free discounting is obtained from the pricing problem's numeraire. M1 does not create a competing Black-Scholes API, universal `FinancialModel`, general rates framework, market-data container, sensitivity framework, or trade/portfolio layer.

---

## M2 — Independent valuation and sensitivity/Greeks

**Status: next.**

**Question:** Can independent methods reproduce the analytical reference and can local sensitivities be established independently for the right reasons?

Expected capabilities:

- CRR/binomial valuation as another valuation method over the supported Black-Scholes problem family;
- Monte Carlo valuation with explicit RNG ownership;
- estimator variance/standard error and appropriate uncertainty reporting;
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

M2 is the first production pressure for the **sensitivity** family. Start concrete: do not create a universal `SensitivityProblem` or giant Greek/result framework unless the actual consumers establish shared behavior.

M2 should also let the second and third real valuation methods pressure-test the M0A pricing method/problem boundaries.

Keep distinct:

```text
financial model error
numerical discretization error
Monte Carlo sampling error
finite-difference truncation/cancellation error
floating-point error
```

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

M3 creates local pressure for **control/optimization** semantics because a hedge policy is an action rule, and for **validation** because replication error is evidence about a model claim. Keep those responsibilities concrete to the hedging study unless repeated consumers justify shared frameworks.

This milestone may also introduce narrow risk/P&L evidence. It does **not** justify a generic portfolio/VaR/scenario engine.

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

M4 is the first major production pressure for the **observation/provenance boundary** and for a narrow **inverse/inference** problem through implied-volatility inversion.

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

M6 is the first substantial consumer that may earn concrete `InverseProblem`-like production semantics. Do not assume the eventual boundary before synthetic and real calibration workflows reveal what information the problem and result actually need.

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

M7 creates direct pressure for concrete **validation** and potentially **risk** problem semantics. Keep them scoped to the model-comparison evidence unless multiple workflows demonstrate a reusable operational boundary.

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

The mathematical taxonomy can organize these later domains, but it does not justify implementing their operational infrastructure prematurely.

## Parallelism guidance

M0A must settle before revised M1 because it defines M1's composition contracts and architectural doctrine. M0A and M1 are now complete.

M2 is intentionally next because its independent valuation methods and first sensitivity consumers pressure-test the shared contracts established by M0A/M1.

M3 may run in parallel with M4 only after M2 has stabilized the pricing/sensitivity contracts and the branches have explicit ownership boundaries.

Reasonable parallel work once shared contracts stabilize includes:

- documentation/report presentation alongside validated implementation;
- market-data provenance/fixture preparation alongside later Black-Scholes validation studies;
- Heston validation-study preparation alongside stable Heston valuation code.

Do **not** begin a parallel C++ workstream before profiling creates a concrete native-acceleration task.
