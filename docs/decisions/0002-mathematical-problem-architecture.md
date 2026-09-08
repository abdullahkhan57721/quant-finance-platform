# ADR 0002 — Mathematical Problem Architecture

- **Status:** Accepted
- **Date:** 2026-09-08
- **Supersedes:** ADR 0001 as the current authority for foundational mathematical architecture
- **Superseded by:** None

## Context

ADR 0001 established a narrow but important exception to the repository's ordinary evidence-driven extraction rule. It allowed the stable mathematical responsibilities of asset pricing to be represented explicitly before multiple concrete software consumers existed:

```text
state / state space / path
stochastic law
model parameter values
financial contract
cash-flow stream
numeraire
physical- and pricing-measure semantics
pricing problem
valuation method
completed valuation result
```

That pricing decomposition is correct and remains implemented production truth.

M0A's broader architectural goal, however, is not only to make pricing compositional. Quantitative finance repeatedly asks several mathematically different kinds of questions over related financial states, stochastic laws, parameters, observations, contracts, positions, controls, and evidence. If those problem families are allowed to collapse into feature-specific APIs, the platform will eventually accumulate unrelated `price(...)`, `calibrate(...)`, `risk(...)`, `forecast(...)`, and `validate(...)` interfaces whose mathematical responsibilities are difficult to recover.

The opposite failure mode would be to create universal `Problem`, `Method`, `Result`, `FinancialModel`, optimizer, simulator, risk, or validation frameworks before concrete behavior exists.

The architecture therefore needs a doctrine that distinguishes **mathematical generality** from **operational software generality**.

## Decision

Foundational mathematical domain distinctions may be represented explicitly from the outset when their distinctness follows from the mathematics of quantitative finance rather than from speculative software reuse.

Problem-specific operational frameworks remain narrow and evidence-driven. A mathematical taxonomy is not permission to manufacture universal APIs.

The platform adopts the following conceptual organization:

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

analytic
lattice / tree
Monte Carlo
Fourier
finite difference / PDE
root finding
optimization
regression / filtering
scenario generation
statistical tests
and other problem-appropriate algorithms

        ↓

SPECIFIC IMMUTABLE RESULTS / EVIDENCE
```

This taxonomy describes mathematical responsibility and dependency direction. It does **not** require a single inheritance hierarchy or shared runtime interface across all problem families.

## Platform-wide Problem → Method → Result pattern

The conceptual pattern is:

```text
Problem
   +
supported Method
   ↓
specific immutable Result
```

A problem states the quantitative question and the semantics needed to make that question well-defined.

A method states how a supported instance of that problem will be solved or approximated.

A result records the committed output/evidence of that execution.

The repository does **not** introduce universal `Problem`, `Method`, or `Result` base classes merely because this conceptual pattern is shared. Common software behavior must still be earned by real consumers.

Request/configuration/orchestration state remains distinct from immutable completed results.

## Problem-family responsibilities

### Forward / pricing problem

A pricing problem asks for financial value under specified contract/model/numeraire/pricing-measure semantics.

The foundational specialization remains

```math
\mathfrak P_{\mathrm{price}}
=
(\mathcal X,\mathcal L_\theta,\mathcal C,N,\mathbb Q^N)
```

with theoretical value

```math
\Pi_t
=
N_t E_t^{\mathbb Q^N}\left[
\sum_i \frac{C_i}{N_{\tau_i}}
\right].
```

A valuation algorithm remains separate:

```math
\mathcal A(\mathfrak P_{\mathrm{price}})
\approx
\Pi_t.
```

The production `PricingProblem`, `ValuationMethod`, and `ValuationResult` contracts implement this family today.

### Inverse / inference problem

An inverse problem asks which latent quantities make a model consistent, in a specified sense, with observations or target quantities.

Conceptually:

```text
observations / targets
+
model structure
+
parameter domain / constraints
+
comparison / error semantics
        ↓
inference question
```

Examples include implied-volatility inversion, parameter calibration, filtering, and state estimation.

Protect:

```text
inverse problem != numerical optimizer
observations != inferred parameters
model structure != fitted parameter values
```

An optimizer/root finder is a possible solution method, not the financial inference problem itself.

No generic production `InverseProblem` framework is created by this ADR.

### Sensitivity problem

A sensitivity problem asks how a specified quantitative output changes when selected inputs, states, parameters, or conventions are perturbed.

Conceptually:

```math
\text{sensitivity}
=
\frac{\partial\,\text{output}}{\partial\,\text{specified input}}
```

or an explicitly defined finite/functional perturbation when derivatives are not appropriate.

Protect:

```text
sensitivity question != differentiation method
analytic Greek != finite-difference algorithm
sensitivity != risk by definition
```

Risk workflows may consume sensitivities, but a derivative/local-response question and a loss/exposure question are not the same responsibility.

No generic production `SensitivityProblem` framework is created by this ADR.

### Prediction problem

A prediction problem asks for a future quantity or distribution conditional on specified information under explicit probability semantics.

Conceptually:

```text
conditioning information
+
stochastic law / parameters
+
probability semantics
+
horizon / target
        ↓
predictive distribution or forecast
```

Prediction is not automatically pricing. Physical-measure forecasting and pricing-measure valuation answer different questions even when they use related state variables or stochastic structures.

Protect:

```text
prediction problem != pricing problem
physical measure P != pricing measure Q^N
forecast target != financial contract
```

No generic production `PredictionProblem` framework is created by this ADR.

### Control / optimization problem

A control problem asks which admissible action, policy, hedge, allocation, or stopping rule best achieves a stated objective subject to dynamics and constraints.

Conceptually:

```text
state / dynamics
+
admissible controls
+
objective functional
+
constraints
        ↓
optimal-control question
```

Protect:

```text
control problem != optimizer
objective/constraints != search algorithm
policy/result != mutable solver state
```

Dynamic programming, stochastic control, mathematical programming, or other optimizers may be methods for particular control problems.

No generic production `ControlProblem` framework is created by this ADR.

### Risk problem

A risk problem asks for a specified characterization of loss, exposure, uncertainty, or adverse outcomes for a defined financial object, horizon, scenario/probability semantics, and conditioning information.

Conceptually:

```text
position / quantity being exposed
+
state / market information
+
horizon
+
probability or scenario semantics
+
loss/exposure definition
        ↓
risk question
```

Protect:

```text
risk problem != risk-measure implementation
risk measure != stochastic law
risk result != portfolio/trade by default
```

VaR, expected shortfall, stress loss, exposure profiles, and sensitivity-based approximations may eventually be different concrete questions/methods; this ADR does not force them into one engine.

No generic production `RiskProblem` framework is created by this ADR.

### Validation problem

A validation problem asks whether a specified model, implementation, method, result, calibration, or empirical claim satisfies explicit criteria and what evidence supports that conclusion.

Conceptually:

```text
object/claim under review
+
validation criteria
+
reference / independent evidence
+
tolerances / statistical decision semantics
        ↓
validation question
```

Protect:

```text
validation problem != validation method
validation evidence != model output itself
one implementation agreeing with itself != independent validation
```

Validation may invoke pricing, inference, sensitivity, prediction, control, or risk capabilities to gather evidence. That orchestration does not make those responsibilities one framework.

No generic production `ValidationProblem` framework is created by this ADR.

## Observations and model boundary

Observed data and modeled quantities remain distinct even when they use similar numeric representations.

The conceptual real-world flow is:

```text
real world
    ↓
observations + provenance
    ↓
normalization / cleaning / construction
    ↓
problem-ready information
```

Separately, the model side is:

```text
modeled state
+
stochastic law
+
parameter values
+
probability semantics
```

Problem construction may combine problem-ready observed information with modeled semantics when the specific problem requires both.

Protect:

```text
market observation != modeled state
observed quote != model-implied quantity
raw observation != normalized input
normalization != calibration
```

Historical observations must not be silently overwritten by model-generated values or by derived quantities used for convenience.

## Dependency direction

The platform should generally read from foundations toward questions, methods, and committed evidence:

```text
observations/provenance ──→ normalization / problem-ready information

modeled state / stochastic law / parameters / probability semantics
financial contracts / cash flows / numeraires / conventions
                         ↓
                 specific Problem
                         ↓
                  supported Method
                         ↓
              specific immutable Result
                         ↓
          validation / research / presentation
```

This is conceptual dependency guidance, not a mandated package tree.

Numerical utilities may be used by methods but must not own finance-domain policy.

Validation may consume results and may invoke other problem/method pairs to gather independent evidence. That higher-level evidence flow does not reverse low-level ownership boundaries.

## Software realization policy

The pricing family is implemented now because M0A and M1 provide immediate consumers.

The other problem families remain architectural concepts until milestones create real behavior. Their first implementations should be concrete and narrow. Only repeated consumers may justify shared production abstractions within or across families.

Accordingly:

```text
foundational mathematical distinction
→ may be documented/typed explicitly from the outset when mathematically stable

problem-family runtime framework
→ wait for concrete behavior

cross-family universal base class
→ wait for demonstrated shared software responsibility
```

Mathematical generality does not imply universal operational APIs.

## Protected distinctions

The repository must preserve at least these distinctions:

```text
financial state != market observation
model structure != parameter values
physical measure P != pricing measure Q^N
contract != pricing model
contract != trade != portfolio
problem != solution method
pricing problem != valuation method
inverse problem != optimizer
sensitivity problem != differentiation method
prediction problem != pricing problem
control problem != optimizer
risk problem != risk-measure implementation
validation problem != validation method
request/configuration != immutable result
production library != research study != presentation
```

## Anti-goals

This decision does not authorize:

- one universal `FinancialModel`;
- a god object that prices, calibrates, predicts, hedges, validates, and measures risk;
- universal `Problem`, `Method`, or `Result` inheritance trees;
- a universal stochastic simulator;
- generic rates/XVA/credit/portfolio infrastructure;
- generic prediction infrastructure;
- generic risk engines;
- generic experiment frameworks;
- giant optional-field result containers;
- registries merely for extensibility;
- speculative C++ backend architecture;
- a generic measure-theory or arbitrary change-of-measure engine.

## Consequences

### Benefits

- Later milestones can be organized around the mathematical question being asked rather than around incidental feature names.
- Pricing, calibration/inference, sensitivity, prediction, control, risk, and validation can compose without collapsing into one model API.
- Observed data and model-generated quantities have an explicit conceptual boundary from the start.
- Algorithms such as Monte Carlo, root finding, optimization, Fourier methods, and finite differences remain methods that can serve different problem families without owning their domain semantics.
- Result structures can stay narrow and truthful to the evidence they contain.

### Costs / tradeoffs

- Architecture documentation must remain disciplined enough that conceptual names do not become pressure to create empty packages/classes.
- Future milestones must decide concretely what information each problem/result needs instead of inheriting a universal schema.
- Some similar-looking workflows may remain separate until evidence proves a shared software responsibility.

## Compatibility and migration

ADR 0001 remains the historical record explaining why the pricing-semantic core was implemented before multiple consumers. Its pricing decomposition and production contracts remain valid.

ADR 0002 supersedes ADR 0001 only as the **current architectural doctrine**: the foundational exception is no longer phrased as pricing-only. Stable mathematical domain distinctions across quantitative finance may be explicit from the outset, while operational frameworks remain evidence-driven.

No production migration is required by this ADR. The current `qf_platform.pricing` implementation remains unchanged.

The pre-M0A M1 Issue/PR must be reconciled so M1 specializes the existing pricing foundation instead of creating a parallel concrete-first API.

## M1 consequence

M1 remains the first concrete specialization:

```text
Equity state / path
+
GBM / Black-Scholes law
+
Black-Scholes parameters under Q
+
European call/put contract
+
money-market numeraire
        ↓
PricingProblem
        +
Black-Scholes closed-form ValuationMethod
        ↓
ValuationResult
        ↓
theoretical validation evidence
```

M1 must not create inference, sensitivity, prediction, control, risk, or validation frameworks merely because those families are now part of the architectural taxonomy.

## References

- ADR 0001 — Foundational Mathematical Pricing Composition
- Issue #11 — M0A completion: platform-wide mathematical problem architecture
- PR #10 — merged M0A pricing foundation
- `AGENTS.md`
- `docs/architecture/index.md`
- `docs/development/current_state.md`
- `docs/development/roadmap.md`
- `docs/quantitative_conventions.md`
