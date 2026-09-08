# ADR 0001 — Foundational Mathematical Pricing Composition

- **Status:** Accepted
- **Date:** 2026-09-08
- **Supersedes:** Bootstrap two-consumer policy for the foundational pricing-semantic core only
- **Superseded by:** None

## Context

M0 intentionally established an evidence-driven extraction rule:

```text
one consumer
→ keep concrete/local

two real consumers
→ compare semantics

same responsibility
→ consider extracting shared abstraction
```

That policy prevented the repository from inventing a universal finance framework before any finance-domain implementation existed. The initial M1 design therefore planned to introduce concrete European-option and Black-Scholes types first and defer shared pricing abstractions.

Before M1 reached `main`, the project deliberately changed the architecture of the pricing core. The mathematical decomposition of arbitrage-free asset pricing exposes responsibilities that are not accidental similarities between two applications. They are distinct domain semantics of the pricing problem itself:

```math
\mathfrak P = (\mathcal X,\mathcal L_\theta,\mathcal C,N,\mathbb Q^N)
```

with conceptual valuation

```math
\Pi_t = N_t E_t^{\mathbb Q^N}\left[
    \sum_i \frac{C_i(X_{[0,\tau_i]})}{N_{\tau_i}}
\right].
```

A concrete analytic or numerical method is separate:

```math
\mathcal A(\mathfrak P) \approx \Pi_t(\mathfrak P).
```

The active pre-M0A M1 branch was useful evidence that a concrete-first implementation can easily make several of these responsibilities coincide: scalar present value can look like the result type; Black-Scholes dynamics can look like the valuation function; risk-neutral dynamics can make pricing-measure semantics invisible; a terminal payoff can make contract and payoff formula look interchangeable. Those coincidences are properties of the first example, not of asset pricing generally.

## Decision

The repository will represent the **foundational mathematical pricing-semantic core explicitly before two implemented consumers exist**.

The core preserves these distinctions:

```text
financial state / state space
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

### State and path semantics

Modeled state and state-space membership are explicit and generic. The architecture does not require a finite-dimensional state space, a Markov state, or a particular stochastic-process representation. A modeled state value may contain whatever conditioning information a concrete law requires. State-path semantics are point-evaluation semantics and do not prescribe a discrete simulation container.

### Stochastic law and parameters

A stochastic law identifies the state space it governs and whether a model-specific parameter object is compatible with it. The core does **not** prescribe a universal `drift()` / `diffusion()` ontology. Diffusions, jump processes, path-dependent laws, rough/non-Markovian structures, and later specializations may expose their own concrete mathematics.

Parameter values remain separate objects. Calibration may later produce new parameter values; that does not create a new model type.

### Contracts and cash flows

A financial contract maps a modeled path to a realized immutable `CashFlowStream`. The foundational cash-flow value object contains only payment time and finite amount. Contract semantics do not own pricing, calibration, market-data ingestion, trade/portfolio ownership, hedging, plotting, or numerical algorithms.

### Numeraire and pricing-measure semantics

A `Numeraire` supplies a strictly positive finite value at each supported access time. Concrete valuation methods must use the validated numeraire-value boundary rather than silently accepting invalid denomination values.

`PhysicalMeasureSemantics` and `PricingMeasureSemantics` are distinct value/role semantics. A pricing measure is associated with a particular numeraire and carries the mathematical meaning that appropriately modeled traded assets denominated by that numeraire are martingales. The core provides no generic measure-theory engine and no operation that mechanically transforms arbitrary physical-measure dynamics into pricing dynamics.

A `PricingProblem` therefore receives stochastic-law structure and parameter values **under the supplied pricing-measure semantics**. If a later workflow needs both P- and Q-dynamics, that workflow must represent them explicitly instead of hiding a change of measure inside a universal model object.

### Pricing problem, method, and result

`PricingProblem` is an immutable composition of the mathematical valuation question. It owns no valuation algorithm.

A `ValuationMethod` is an algorithmic capability. Structural validity of a financial pricing problem does not imply implementation support by every method. Compatibility is checked explicitly before a method is applied, and unsupported combinations raise a dedicated error.

`ValuationResult` is currently only an immutable finite present value. It is intentionally **not** a universal optional-field container for Greeks, Monte Carlo diagnostics, confidence intervals, calibration, hedging, validation evidence, or benchmarks.

### Scope of the exception

The exception applies only to the foundational asset-pricing semantics above.

The ordinary evidence-driven extraction rule continues to govern, among other things:

- market observations and provenance;
- valuation-ready market-environment construction beyond concrete consumers;
- discount/rates curve hierarchies;
- calibration problems and optimizers;
- Greeks/risk measures;
- validation frameworks;
- hedging and P&L studies;
- trades and portfolios;
- experiment/research orchestration;
- native/C++ backends;
- registries, service locators, and discovery systems.

This ADR does not authorize a universal `FinancialModel` or a general abstraction layer over all of quantitative finance.

## Alternatives considered

### Keep the bootstrap concrete-first rule with no exception

This remained plausible because the rule strongly protects against speculative architecture. It was rejected for the pricing-semantic core because it would intentionally collapse mathematically distinct responsibilities in M1 and then require a predictable architectural rewrite as soon as independent methods or Heston arrive. The distinction between a stochastic law and a valuation method, or between a contract and a cash-flow functional, is not merely an inferred software reuse pattern.

### Build a universal quantitative-finance framework now

This was rejected. The mathematical decomposition justifies a narrow pricing core, not generic rates, XVA, credit, portfolio, risk, calibration, market-data, stochastic-simulation, or backend frameworks.

### Represent all stochastic laws through drift and diffusion

This was rejected because it would make the first GBM use case dictate a process ontology that does not cleanly cover jump, path-dependent, rough, or other non-diffusion models.

### Implement generic change-of-measure machinery

This was rejected because a symbolic or runtime measure transformation for arbitrary models is far broader than current consumers justify and can conceal the concrete dynamics actually used under P or Q.

## Consequences

### Benefits

- M1 can be implemented as a mathematically legible specialization instead of creating an isolated pricing API.
- Black-Scholes, CRR, Monte Carlo, Heston Fourier, and Heston Monte Carlo can remain distinguishable combinations of financial semantics and valuation algorithms.
- Parameter values can evolve through calibration without mutating model identity.
- Contracts remain reusable contingent-cash-flow semantics rather than pricer objects.
- P-vs-Q and numeraire semantics remain explicit enough for model validation.
- Static typing can preserve meaningful relationships without a giant inheritance hierarchy.

### Costs / tradeoffs

- M1 must implement several small foundational interfaces instead of exposing only a concrete pricing function.
- The project must actively resist expanding the foundational exception into unrelated generic architecture.
- Protocol contracts and runtime compatibility checks require care so they remain semantic rather than ceremonial.
- The pre-M0A M1 draft must be reconciled rather than merged unchanged.

### Intentionally deferred

- concrete date/day-count conventions;
- business-day/calendar semantics;
- concrete money-market-account/rate representation;
- discount-curve construction/interpolation;
- dividend/carry conventions;
- volatility conventions;
- Black-Scholes/GBM implementation details;
- generic stochastic simulation;
- calibration/risk/validation/research frameworks;
- portfolio/trade/XVA/rates specializations;
- native execution architecture.

## Validation / evidence

M0A includes focused tests that verify:

- immutable state, cash-flow, pricing-problem, and valuation-result semantics;
- state-space membership and stochastic-law/parameter compatibility;
- contract-to-cash-flow behavior;
- positive finite numeraire values;
- physical-vs-pricing-measure distinction and numeraire association;
- explicit supported/unsupported valuation-method behavior;
- a deterministic one-payment end-to-end composition;
- representative strict-typing relationships;
- dependency direction that keeps valuation downstream of foundational semantics.

The deterministic composition fixture is deliberately not Black-Scholes. M1 remains the first production specialization.

## Compatibility / migration

Current `main` before M0A contains no finance-domain public API, so no merged finance consumer requires migration.

Issue #5 / PR #6 were created under the superseded bootstrap policy and must not be merged unchanged. Their concrete Black-Scholes implementation and validation evidence may be reused when M1 is recomposed on top of M0A.

## References

- Issue #9 — M0A: Mathematical pricing composition foundation
- PR #10 — M0A implementation
- Issue #5 / PR #6 — pre-M0A M1 concrete-first work
- `AGENTS.md`
- `docs/architecture/index.md`
- `docs/quantitative_conventions.md`
