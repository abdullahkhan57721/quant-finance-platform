# Quantitative Conventions

## Purpose

This document is the authoritative register for project quantitative representation conventions.

A convention may be **committed**, **explicitly deferred**, or **local to a specific API/study**. What is not allowed is a consequential convention remaining implicit across a public boundary.

M0A commits the structural mathematics of the platform-wide problem taxonomy and the implemented pricing core. M1 makes the first concrete equity-option conventions explicit. M2 now resolves the first concrete numerical-valuation and sensitivity conventions without promoting Black-Scholes-specific choices into universal solver, risk, portfolio, or market-data policy.

ADR 0002 is the current authority for the mathematical problem architecture. ADR 0001 remains the historical pricing-specific decision record.

## Decision statuses

- **Committed** — project-wide rule; public implementations should follow it unless superseded by a deliberate repository decision.
- **Deferred** — not yet fixed project-wide; the first real consumer should make the decision explicit and update this document if the choice becomes shared.
- **Local** — intentionally specific to one method/study/specialization; encode it in that API/config/result rather than promoting it globally.

## Committed cross-cutting conventions

### Explicit quantitative meaning at public boundaries

Public quantitative inputs must make their semantic meaning clear through type, field name, documentation, or configuration.

Avoid APIs where an anonymous numeric value could ambiguously mean one of several conventions, for example:

```text
0.05
→ 5% simple annual rate?
→ 5% continuously compounded rate?
→ 5 percentage points?
→ a discount-factor-related quantity?
```

This rule does not require a wrapper type for every number. It requires ambiguity to be removed where it affects correctness.

### Mathematical problem-family distinction

ADR 0002 commits the following conceptual organization:

```text
foundations
    ↓
problem family
    ↓
supported solution method
    ↓
specific immutable result / evidence
```

The recognized problem families are:

```text
forward / pricing
inverse / inference
sensitivity
prediction
control / optimization
risk
validation
```

This is a structural convention, not a requirement for universal runtime base classes.

Protect:

```text
problem != solution method
pricing problem != valuation method
inverse problem != optimizer / root finder
sensitivity problem != differentiation method
prediction problem != pricing problem
control problem != optimizer
risk problem != risk-measure implementation
validation problem != validation method
request/configuration != immutable result
```

### Foundational asset-pricing semantics

The implemented pricing core commits these project-wide conceptual distinctions:

```text
modeled state / state space
!= stochastic law
!= model parameter values
!= financial contract
!= realized cash-flow stream
!= numeraire
!= physical-measure semantics
!= numeraire-associated pricing-measure semantics
!= pricing problem
!= valuation method
!= completed valuation result
```

The theoretical pricing problem is composed from those semantics; an analytic/numerical valuation method is a separate capability.

A pricing problem supplies stochastic-law structure and parameter values under the relevant pricing-measure semantics. The project does not assume that a generic measure object can mechanically transform arbitrary physical-measure dynamics into pricing dynamics.

This is a **structural convention**, not permission to create generic inference/calibration, sensitivity, prediction, control, risk, market-data, rates, portfolio, validation, or research frameworks before consumers justify them.

### Observation, normalization, and model separation

Observed information must remain distinguishable from modeled and model-implied quantities.

Conceptually:

```text
real world
    ↓
observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready information
```

separately from:

```text
modeled state
+
stochastic law
+
parameter values
+
probability semantics
```

Do not silently overwrite or reinterpret historical observations as model outputs. Raw observation, normalized input, inferred/calibrated quantity, and model-implied quantity are distinct semantics even when they share the same numerical type.

### Probability semantics are part of the quantitative question

Do not silently reuse one probability interpretation across problem families.

Protect:

```text
physical measure P != pricing measure Q^N
prediction under P != pricing under Q^N
```

A future prediction, risk, or inference API must make the relevant probability/scenario semantics explicit enough that a user cannot accidentally interpret a pricing-measure output as a physical-world forecast, or vice versa.

M0A does not define one universal probability-measure API.

### Numeraire positivity

At every supported access used by pricing code, a numeraire value must be finite and strictly positive:

```math
N_t > 0.
```

Concrete rates/discounting representations remain consumer-specific. The foundational pricing API must not silently spread naked scalar-rate assumptions where numeraire semantics are the relevant mathematical boundary.

### Physical vs pricing measure

Physical-measure semantics `P` and numeraire-associated pricing-measure semantics `Q^N` are distinct.

`Q^N` carries the martingale interpretation that appropriately modeled traded assets denominated by `N` are martingales under that pricing measure. M0A does not provide generic change-of-measure machinery.

### Cash-flow amount semantics

A foundational `CashFlow` currently consists only of payment time and a finite real amount. Positive and negative amounts are allowed. Currency, collateral, counterparty, settlement, and XVA semantics are intentionally absent until real consumers justify them.

### Result specificity and present-value terminology

Completed results should be narrow and truthful to the problem/method execution that produced them. Do not create giant optional-field result containers merely to anticipate future workflows.

The foundational completed pricing result uses **present value** terminology. `ValuationResult.present_value` is a finite scalar.

M2 proves one small extension of that result boundary: a concrete valuation method may return a specific immutable subtype when the method genuinely produces additional evidence. `MonteCarloValuationResult` therefore retains `present_value` while adding Monte Carlo sampling uncertainty, path count, and seed. Those fields do not become optional members of every `ValuationResult`.

Greeks/sensitivities, inference/calibration outputs, control policies, risk outputs, hedging evidence, validation evidence, and benchmark metadata remain separate specific result/evidence structures rather than optional fields on generic valuation output.

### Volatility values use explicit decimal/annualization semantics

When a public API names a quantity **annualized volatility**, it is represented as a decimal annualized standard deviation unless that API explicitly documents a different quantity. For example:

```text
annualized_volatility = 0.20
```

means 20% annualized volatility, not 0.20% and not 20 percentage points. Variance, instantaneous variance, volatility-of-volatility, and model-specific variance-state quantities remain distinct concepts and should be named accordingly.

### No hidden project-wide numerical tolerance

There is no universal magic tolerance for finance/numerical tests.

Every meaningful tolerance should be justified by the evidence type involved, such as:

- analytical floating-point error;
- discretization error;
- Monte Carlo standard error;
- optimizer/root-finder convergence;
- statistical decision error;
- market quote precision;
- backend parity.

Prefer tolerances derived from the expected error mechanism rather than copied globally.

### Explicit stochastic ownership

Production stochastic APIs must not depend on ambient global RNG state.

Use explicitly owned/configured RNG state. Record seed/RNG information in reproducible studies when applicable.

M2's Monte Carlo valuation method exercises this rule concretely: the method owns an explicit integer seed and creates a fresh local `random.Random(seed)` for each application. The seed is retained in the immutable Monte Carlo result. This gives repeatability within the committed Python implementation without promising identical random streams across future backends.

Equal integer seeds across Python/C++ are **not** a contract for identical random streams. Use shared pre-generated random inputs when strict kernel parity is required.

### Reproducible core tests do not depend on live market services

Live data can support research and manual workflows, but core CI tests should use deterministic fixtures, synthetic data, or curated snapshots whose provenance/licensing permits repository use.

## M1 local equity-option / Black-Scholes conventions

M1 resolves the conventions needed by the first concrete pricing specialization. These are **local to the M1 Black-Scholes/European-option family unless explicitly identified above as committed cross-cutting rules**.

| Convention | M1 decision | Scope / non-claim |
| --- | --- | --- |
| Contract expiry representation | `datetime.date` calendar date | No time-of-day or universal contract-time hierarchy. |
| Valuation date representation | `PricingProblem.valuation_time` is a `datetime.date` for this specialization | Other future problem families may use other time representations. |
| Year-fraction API | `actual_365_fixed_year_fraction(start, end)` | Concrete helper, not a generic day-count framework. |
| Day-count convention | Actual/365 Fixed: actual calendar days divided by exactly 365 | Leap days count as days; denominator remains 365. |
| Business-day/calendar handling | No business-day adjustment in M1 | General calendar handling remains deferred until a real consumer such as M4 requires it. |
| Interest-rate representation | `FlatMoneyMarketNumeraire(reference_date, continuously_compounded_rate)` | The pricing core still depends on numeraire semantics, not a universal scalar-rate field. |
| Compounding convention | Continuously compounded annualized decimal rate | Negative finite rates are allowed. |
| Discounting representation | Risk-free discount from valuation to expiry is the numeraire ratio `N_V / N_E` | No general discount-curve/yield-curve hierarchy. |
| Dividend/carry representation | Finite continuously compounded proportional annualized yield `q` in `BlackScholesParameters` | No discrete cash-dividend schedule. |
| Spot vs forward | `EquityState.spot` is modeled spot | M1 closed form is a spot-input specialization; future market-data workflows may also observe forwards. |
| Volatility | `BlackScholesParameters.annualized_volatility` follows the committed decimal annualized-volatility rule | Non-negative finite values; zero is an admitted deterministic boundary. |
| Option right | `OptionRight.CALL` / `OptionRight.PUT` | No general instrument taxonomy. |
| Spot domain | Finite, non-negative; zero admitted as a degenerate boundary | Negative equity spot is invalid. |
| Strike domain | Finite, non-negative; zero admitted as a degenerate boundary | No strike schedule/quote convention. |
| Present-value output | Existing `ValuationResult.present_value` | Method-specific evidence uses specific results rather than giant optional-field output. |
| Analytical tolerance | `2e-13` absolute for the ~100-unit deterministic benchmark/parity checks | Local to the floating-point analytical evidence; not a project-wide tolerance. |

The detailed formula, notation mapping, pricing-measure assumptions, limits, and evidence map are in `docs/models/black_scholes.md`.

## M2 local numerical-valuation and sensitivity conventions

M2 resolves the conventions needed by the first independent numerical valuation methods and the first production sensitivity specialization. These decisions are **local to the M1/M2 Black-Scholes European-option family unless explicitly identified above as cross-cutting**.

| Convention | M2 decision | Scope / non-claim |
| --- | --- | --- |
| CRR configuration | `steps` is an explicit positive integer | No universal tree/grid configuration abstraction. |
| CRR finite-model support | For non-degenerate steps, require `d < exp((r-q)dt) < u`, equivalently `0 < p < 1` | A valid Black-Scholes problem may be unsupported by a particular coarse CRR configuration. |
| CRR interpretation | Fixed `steps` is a discrete-time complete-market model; increasing `steps` is also studied as convergence toward Black-Scholes | Do not silently identify the finite tree with the continuous model. |
| Monte Carlo path count | Explicit integer `paths >= 2` | Minimum supports sample-variance / standard-error estimation; no global default path budget. |
| Monte Carlo RNG | Explicit integer seed; fresh local Python `random.Random(seed)` on each method application | Reproducible in the committed Python implementation; no cross-language stream-identity promise. |
| Monte Carlo state simulation | Exact terminal GBM sampling for the supported European terminal-payoff problem | No generic path simulator or time-discretized SDE engine is introduced. |
| Monte Carlo uncertainty | Sample standard error of discounted payoff mean | Sampling uncertainty, not deterministic valuation error. |
| Monte Carlo confidence interval | Normal-approximation 95% interval `estimate ± 1.959963984540054 * SE` | Local reporting convention for this result, not a project-wide confidence-level default. |
| Delta | `dV/dS` | First order; PV units per spot unit. |
| Gamma | `d²V/dS²` | Second order; PV units per spot-unit squared. |
| Vega | `dV/dsigma` for annualized decimal volatility | Reported per `1.00` volatility decimal, not per 1 percentage point. |
| Theta | `dV/dt` as valuation time advances with expiry and other differentiation inputs fixed | Reported per ACT/365F model year; standard passage-of-time sign convention, not per day. |
| Rho | `dV/dr` for the continuously compounded annualized decimal money-market rate | Reported per `1.00` rate decimal, not per 1 percentage point. |
| Analytic Greek support | Positive differentiable interior `T>0`, `S>0`, `K>0`, `sigma>0` | Boundary prices remain valid without promising smooth finite Greeks. |
| Finite-difference scheme | Central first differences for Delta/Vega/Theta/Rho; central second difference for Gamma | Concrete Black-Scholes bump-and-revalue method, not a universal differentiation engine. |
| Finite-difference bump units | Spot, volatility, and rate bumps use their native core units; Theta uses an explicit positive integer calendar-day bump | No project-wide epsilon; method support rejects domain-crossing central bumps. |
| Bump selection | Evidence studies multiple bump sizes and distinguishes truncation from cancellation/floating-point error | No single bump is canonically correct for all problems/scales. |

Detailed numerical formulas, error taxonomy, and executable evidence are in `docs/models/m2_numerical_methods_and_sensitivities.md`.

## Explicitly deferred finance conventions

These decisions should be settled by the first milestones that create real consumers. Until then, do not spread a local choice across the codebase as if it were canonical.

| Convention | Status | First expected pressure | Guidance until settled |
| --- | --- | --- | --- |
| General business-day/calendar framework | Deferred | M4 | M1 intentionally performs no business-day adjustment; do not generalize that into a universal calendar policy. |
| General discount-factor/curve representation | Deferred | M4/M5 | M1 uses a flat money-market numeraire; M0A commits numeraire semantics, not a curve hierarchy. |
| Discrete dividend/corporate-action representation | Deferred | M4/future instrument consumer | M1's continuous yield is local; do not reinterpret it as a discrete dividend schedule. |
| Forward-market observation semantics | Deferred | M4 | M1 prices from modeled spot; observed spot/forward quote provenance belongs to market-data work. |
| Array axis/order conventions for numerical kernels | Deferred | M5 | Define only when vectorized/compiled kernels create a shared boundary. |
| Hedging/control objective and admissible-action semantics | Deferred | M3 | The first control-like workflow must state objective, actions, constraints, and timing explicitly. |
| Market timestamp timezone convention | Deferred | M4 | Must become explicit before real-market ingestion. |
| Missing/bad quote policy | Deferred | M4 | Preserve raw observations/provenance; normalization/cleaning policy must be explicit and testable. |
| Inference/calibration loss/objective convention | Deferred | M4/M6 | Must belong to the concrete inverse problem; do not hide it inside a generic optimizer. |
| Inference weighting convention | Deferred | M6 | State how observations/targets are weighted and why. |
| Parameter bounds/transforms | Deferred | M6 | Keep model-domain constraints distinct from optimizer mechanics. |
| Prediction probability semantics | Deferred | future prediction consumer | State conditioning information, horizon, target, and probability semantics explicitly. |
| Risk horizon | Deferred | first risk consumer | Must be explicit; no project-wide default. |
| Risk probability/scenario semantics | Deferred | first risk consumer | Distinguish historical/physical/model/stress/scenario interpretations. |
| Risk loss/exposure definition | Deferred | first risk consumer | Must be explicit before a risk measure is meaningful. |
| Validation criterion/tolerance semantics | Deferred | each validation consumer | State what is being validated, reference evidence, and error/statistical rationale. |

## Decision rules for later milestones

When a milestone encounters a deferred convention:

1. Identify the concrete consumer and why the choice matters.
2. Compare realistic alternatives and failure modes.
3. Decide whether the convention is local or project-wide.
4. Encode the convention in types/configuration/documentation so it cannot be silently reinterpreted.
5. Add tests that distinguish the chosen semantics from plausible wrong interpretations.
6. Update this register if the choice becomes project-wide or a durable local convention.
7. Use an ADR only when the decision is durable, consequential, and not obvious from code plus this document.

Do not force a global convention merely to make this register complete.

## Formula traceability convention

Important mathematical implementations should document or link enough information to recover:

- the source/reference or project derivation;
- notation mapping from the source into code;
- assumptions and parameter domain;
- units/conventions involved;
- probability/measure semantics where relevant;
- limiting cases or identities used for validation;
- tests that provide independent evidence.

M1 is the first production valuation implementation to exercise this convention fully; `docs/models/black_scholes.md` maps the Black-Scholes-Merton references and notation to the M0A composition, formulas, assumptions, limits, benchmark, tolerance rationale, and tests.

M2 extends the same discipline to independent numerical valuation and sensitivities in `docs/models/m2_numerical_methods_and_sensitivities.md`, including method interpretation, stochastic ownership, uncertainty, derivative variables/units/sign conventions, numerical error mechanisms, and the executable evidence map.

## Market-data provenance convention

When real market data arrives, preserve as applicable and legally permitted:

- provider/source;
- as-of timestamp;
- retrieval timestamp;
- raw artifact or content hash;
- normalization/transformation version;
- licensing/redistribution notes.

If raw data cannot be redistributed, prefer a reproducible retrieval/processing recipe plus deterministic synthetic or curated fixtures over committing restricted data.

## Changing a committed convention

A committed convention can change when evidence justifies it.

A change should normally include:

- the motivation and affected public contracts;
- migration/compatibility consequences;
- tests distinguishing old and new semantics where executable behavior changes;
- documentation updates in the same PR;
- an ADR when the decision is durable and consequential enough to require historical rationale.

Repository truth should evolve rather than preserving a bad convention for historical consistency.
