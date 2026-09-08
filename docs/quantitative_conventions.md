# Quantitative Conventions

## Purpose

This document is the authoritative register for project quantitative representation conventions.

A convention may be **committed**, **explicitly deferred**, or **local to a specific API/study**. What is not allowed is a consequential convention remaining implicit across a public boundary.

M0A commits the structural mathematics of the platform-wide problem taxonomy and the implemented pricing core. M1 makes the first concrete equity-option conventions explicit. M2 resolves the first concrete numerical-valuation and sensitivity conventions. M3 resolves the first concrete dynamic-hedging/control conventions without promoting Black-Scholes-specific choices into universal solver, risk, portfolio, simulation, or execution policy. M4 resolves the first concrete observed-market normalization and implied-volatility inverse-problem conventions without creating generic market-data, surface, or inverse-problem frameworks. M5 resolves the first stochastic-volatility state/parameter and independent Fourier/Monte Carlo valuation conventions without creating generic factor-model, Fourier, quadrature, or stochastic-simulator frameworks.

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

M4 is the first production consumer of this rule: raw option/underlying observations retain provenance, normalized midpoint observations retain references to their raw evidence, and implied volatility remains a separate model-dependent result.

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

M5 adds two further specific valuation-result subtypes without widening the common result. `HestonFourierValuationResult` retains explicit finite integration bounds, interval count, and characteristic-function evaluation count. `HestonMonteCarloValuationResult` extends Monte Carlo sampling evidence with Heston timestep and variance-discretization evidence. Those fields remain method-specific.

Greeks/sensitivities, inference/calibration outputs, control policies, risk outputs, hedging evidence, validation evidence, and benchmark metadata remain separate specific result/evidence structures rather than optional fields on generic valuation output.

### Volatility values use explicit decimal/annualization semantics

When a public API names a quantity **annualized volatility**, it is represented as a decimal annualized standard deviation unless that API explicitly documents a different quantity. For example:

```text
annualized_volatility = 0.20
```

means 20% annualized volatility, not 0.20% and not 20 percentage points. Variance, instantaneous variance, volatility-of-volatility, and model-specific variance-state quantities remain distinct concepts and should be named accordingly.

M4 implied volatility follows the same unit convention, but the semantic role differs: it is the Black-Scholes parameter value inferred from an observed option target under explicit model inputs, not an observed or physical-measure volatility.

M5 makes the variance distinction concrete: `HestonEquityState.instantaneous_variance = 0.04` means an instantaneous variance level whose square root is `0.20` annualized volatility under the model-year convention. It is not itself a 4% volatility input.

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

M3 follows the same ownership rule for path simulation: `BlackScholesPathSimulation` owns an explicit integer seed, `simulate_black_scholes_path` creates fresh local RNG state, and the immutable realized path retains the generating configuration and seed.

M5 follows the rule independently: `HestonMonteCarloEuropeanOption` owns explicit path count, timestep count, and integer seed and constructs fresh local `random.Random(seed)` state for each application. Its correlated Gaussian construction is local to method execution.

Equal integer seeds across Python/C++ are **not** a contract for identical random streams. Use shared pre-generated random inputs when strict kernel parity is required.

### Reproducible core tests do not depend on live market services

Live data can support research and manual workflows, but core CI tests should use deterministic fixtures, synthetic data, or curated snapshots whose provenance/licensing permits repository use.

M4 follows this rule by testing market-observation, normalization, inversion, conditioning, and strike-slice diagnostics against deterministic synthetic fixtures. Real SPX evidence is a separately pinned research artifact and is not required for CI.

## M1 local equity-option / Black-Scholes conventions

M1 resolves the conventions needed by the first concrete pricing specialization. These are **local to the M1 Black-Scholes/European-option family unless explicitly identified above as committed cross-cutting rules**.

| Convention | M1 decision | Scope / non-claim |
| --- | --- | --- |
| Contract expiry representation | `datetime.date` calendar date | No time-of-day or universal contract-time hierarchy. |
| Valuation date representation | `PricingProblem.valuation_time` is a `datetime.date` for this specialization | Other future problem families may use other time representations. |
| Year-fraction API | `actual_365_fixed_year_fraction(start, end)` | Concrete helper, not a generic day-count framework. |
| Day-count convention | Actual/365 Fixed: actual calendar days divided by exactly 365 | Leap days count as days; denominator remains 365. |
| Business-day/calendar handling | No business-day adjustment in M1 | General calendar handling remains deferred until a real consumer justifies it. |
| Interest-rate representation | `FlatMoneyMarketNumeraire(reference_date, continuously_compounded_rate)` | The pricing core still depends on numeraire semantics, not a universal scalar-rate field. |
| Compounding convention | Continuously compounded annualized decimal rate | Negative finite rates are allowed. |
| Discounting representation | Risk-free discount from valuation to expiry is the numeraire ratio `N_V / N_E` | No general discount-curve/yield-curve hierarchy. |
| Dividend/carry representation | Finite continuously compounded proportional annualized yield `q` in `BlackScholesParameters` | No discrete cash-dividend schedule. |
| Spot vs forward | `EquityState.spot` is modeled spot | M1 closed form is a spot-input specialization; market-data workflows keep observed spot separate. |
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
| CRR interpretation | Fixed `steps` is a discrete-time complete-market model; increasing steps are also studied as convergence toward Black-Scholes | Do not silently identify the finite tree with the continuous model. |
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

## M3 local dynamic-hedging/control conventions

M3 resolves the deferred control choices for the first concrete Black-Scholes replication consumer. These decisions are **local to this dynamic Delta-hedging specialization**; they are not universal trading, portfolio, execution, or control policy.

| Convention | M3 decision | Scope / non-claim |
| --- | --- | --- |
| Liability / objective | One short European option; terminal replication error is `hedge value - option payoff` | Positive means surplus after settlement; this is not a universal P&L convention. |
| Initial funding | Initial hedge cash/stock wealth equals the hedging-model Black-Scholes present value | No trade premium, margin, collateral, or balance-sheet layer. |
| Hedge action | Target stock units equal M2 analytic Delta at the current modeled state | Delta is consumed by a policy; sensitivity does not own dynamic hedge state. |
| Hedge timing | First rebalance equals valuation date; all later rebalance dates are explicit and strictly before expiry | No intraday timing or event-driven execution model. |
| Path probability semantics | Exact-transition GBM under the configured M1 money-market pricing measure | A replication experiment, not a physical-world forecast. |
| Path dates | Explicit observation/output grid; adjacent GBM transitions are exact | Observation dates are not Euler timesteps and are distinct from hedge rebalance dates. |
| Financing | Cash compounds between hedge dates by the existing money-market numeraire ratio | No funding spread, collateral rate, or multiple cash accounts. |
| Frictionless rebalance | Stock purchase/sale is offset exactly by cash, preserving wealth at the trade time | Local self-financing stock/cash convention. |
| Proportional transaction cost | `kappa * abs(stock trade notional)` deducted from cash at each rebalance | Symmetric stock-trade cost only; no bid/ask, impact, option-trading, or terminal liquidation cost. |
| Terminal hedge value | Final stock holding is marked at terminal spot plus financed cash | Stock is not automatically liquidated at expiry. |
| Dividend/carry execution support | Hedge execution requires `continuous_dividend_yield == 0` | Nonzero carry remains unsupported until dividend/carry cash-flow accounting is explicit. |
| Volatility misspecification | Generating volatility and hedging/pricing volatility are separately represented | Current misspecification study varies volatility only. |
| Stochastic replicate summary | At least two results with distinct seeds and one identical study condition, including identical observation grid | Duplicate seeds are not treated as independent replicates; mixed conditions are rejected. |
| Aggregate error evidence | Mean/median error, standard deviation, MAE, and RMSE | Experiment summaries, not additions to pricing or sensitivity result types. |

Detailed equations, accounting identities, path semantics, limitations, and executable evidence are in `docs/models/m3_dynamic_delta_hedging.md`.

## M4 local market-observation and implied-volatility conventions

M4 resolves only the conventions needed by its first observed option-market consumer and Black-Scholes inverse problem. These are **local to the M4 European-option evidence path unless explicitly identified as cross-cutting**.

| Convention | M4 decision | Scope / non-claim |
| --- | --- | --- |
| Raw vs normalized data | Preserve immutable raw option/underlying observations and construct separate normalized observations | Normalization never overwrites raw evidence. |
| Market date | Required `datetime.date` because the supported M1 pricing vertical is date-valued | No general exchange-calendar or intraday valuation-time framework. |
| Retrieval/observation timestamps | Retrieval timestamp must be timezone-aware; contract observation timestamp is optional but timezone-aware when present | Missing quote timestamps do not imply freshness. |
| Provenance | Provider/source, market date, retrieval time, optional observation time, optional raw SHA-256, and license notes | Concrete evidence fields, not a universal provider adapter framework. |
| Quote target | Positive, non-crossed bid/ask midpoint | `last` is retained raw where available but is not the first inference target. |
| Missing/bad quote policy | Missing bid/ask, nonpositive bid/ask, crossed markets, mismatched underlying/date, unsupported exercise/settlement fail normalization | Bad raw observations may still exist as evidence. |
| Exercise support | European only for the first inference consumer | No American-option inversion. |
| Settlement support | Explicit PM settlement required under current date-only M1 expiry semantics | AM or unknown settlement is not silently normalized. |
| Staleness | No staleness inference without source evidence sufficient to support it | Absence of a timestamp is preserved, not guessed. |
| Implied-volatility problem | Solve the existing Black-Scholes forward map for annualized decimal `sigma` against one normalized observed target | Implied volatility is model-dependent inference, not observed/physical volatility. |
| Volatility domain | Default `[0.0, 5.0]` annualized volatility decimals | Method/problem-local admissible interval, not an economic universal bound. |
| Financial feasibility | Check discounted European price bounds before root search | A materially inconsistent quote does not receive a plausible-looking IV. |
| Price-bound roundoff | Scale-aware `1e-12` relative tolerance for comparing an observed target to theoretical bounds | Local floating-point guard only; distinct from quote precision and root tolerance. |
| Numerical inverse method | Deterministic bracketed bisection | No universal inverse-method hierarchy or optimizer framework. |
| Bisection defaults | Price tolerance `1e-10`, volatility-bracket tolerance `1e-10`, max iterations `200` | Method-local convergence configuration. |
| Numerical failures | Unbracketed admissible target and exhausted convergence budget are distinct failures | Financial inconsistency, domain choice, and numerical nonconvergence remain distinguishable. |
| Conditioning | Reuse M2 analytic Vega at the inferred solution; retain `1/Vega` and half-spread first-order IV displacement | Conditioning evidence, not a solver-failure label. |
| Moneyness coordinate | `log(K/F)` with `F = S exp((r-q)T)` using the same explicit rate/carry inputs as pricing | Rate/carry are not silently inferred from observations. |
| Static quote diagnostics | Same-right strike monotonicity and discrete convexity only | Reports violations; does not repair/interpolate an arbitrage-free surface. |
| Real SPX research inputs | Pinned raw public artifact plus explicit flat `r=0.045`, `q=0.017` assumptions for the committed study | These rates/carry are research assumptions, not observed or calibrated values. |
| SPXW contract enrichment | Selected non-third-Friday expiries use separately sourced European/PM SPXW semantics because the raw CSV omits them | Enrichment is recorded explicitly rather than presented as a raw field. |

Detailed formulas, failure semantics, conditioning, deterministic fixtures, and real-market evidence are in `docs/models/m4_market_evidence_and_implied_volatility.md`.

## M5 local Heston stochastic-volatility and valuation conventions

M5 resolves only the conventions needed by the first stochastic-volatility law and its two independent European-option valuation methods. These are **local to the Heston pricing specialization unless explicitly identified above as cross-cutting**.

| Convention | M5 decision | Scope / non-claim |
| --- | --- | --- |
| Current state | `HestonEquityState` refines `EquityState` with non-negative finite `instantaneous_variance` | Same European-option contract is reused; no generic factor/state-component framework. |
| Instantaneous variance | Annualized variance under ACT/365F model-year units; `v=0.04` corresponds to instantaneous volatility `sqrt(v)=0.20` | Variance is not volatility and is not an implied-volatility quote. |
| Mean reversion | `mean_reversion_speed = kappa > 0`, in inverse model-year units | Model parameter, not optimizer speed or a global time constant. |
| Long-run level | `long_run_variance = theta >= 0` | Variance level, not long-run volatility. |
| Volatility of variance | `volatility_of_variance = xi >= 0`, the CIR/Heston variance diffusion coefficient under model-year units | Do not reinterpret `xi` as an annualized spot-volatility decimal. |
| Correlation | `rho` finite in `[-1, 1]` | Instantaneous Brownian correlation between spot and variance shocks. |
| Dividend/carry | Finite continuous annualized yield `q` in `HestonParameters` | Same economic convention as M1 pricing; no discrete dividends. |
| Risk-free rate | Existing flat money-market numeraire owns `r` | Heston parameters do not duplicate the risk-free rate. |
| Feller condition | Expose `2*kappa*theta - xi^2` and whether it is non-negative as diagnostics | Feller inequality is not a universal constructor-validity requirement. |
| Fourier method | Heston characteristic-function `P1/P2` valuation with explicit finite Simpson integration | No generic Fourier/quadrature framework. |
| Fourier frequency domain | Default `[1e-8, 100]` with lower endpoint strictly positive | Local frequency truncation choice; not a universal transform domain. |
| Fourier resolution | Default `2048` even Simpson intervals | Explicit method configuration; convergence evidence varies range/resolution. |
| Complex branch | Square root chosen with non-negative real part, then non-negative imaginary part when the real part is zero | Heston implementation branch convention, documented for reproducibility. |
| `xi=0` Fourier boundary | Exact deterministic variance integral mapped to independently implemented Black-Scholes with `sigma_eff=sqrt(I_T/T)` | Exact model boundary, not a small-`xi` approximation. |
| Heston Monte Carlo path count | Explicit integer `paths >= 2` | No global Heston simulation budget. |
| Heston Monte Carlo time grid | Explicit positive integer `time_steps`; uniform spacing in ACT/365F model time `T/time_steps` | Numerical SDE grid, not calendar observation dates and not M3 hedge rebalance dates. |
| Heston Monte Carlo RNG | Explicit integer seed; fresh local Python `random.Random(seed)` on every application | Reproducible current Python execution; no cross-language stream-identity promise. |
| Correlated shocks | `Z_S = rho Z_v + sqrt(1-rho^2) Z_perp` from independent standard normals | Method-local shock construction implementing Heston correlation. |
| Variance discretization | Full-truncation Euler for `xi>0`: use positive part of raw variance in variance drift/diffusion and log-spot coefficients | Numerical scheme, not Heston-law semantics. |
| Variance-boundary evidence | Record count of negative raw next-variance proposals | Discretization-pressure diagnostic, not continuous-model negative variance and not model error. |
| `xi=0` Monte Carlo boundary | Sample terminal log spot exactly from deterministic integrated variance | Sampling error remains; Heston timestep-discretization bias does not. |
| Heston Monte Carlo uncertainty | Reuse M2 sample standard error and normal-approximation 95% interval for discounted payoff mean | Sampling uncertainty only; does not cover timestep bias or model error. |
| Cross-method comparison | Compare deterministic Fourier value with seeded MC using a tolerance that separately admits sampling uncertainty plus explicit timestep-bias allowance | Agreement is evidence, not proof by itself. |

Detailed equations, characteristic-function notation, scheme definitions, references, limiting cases, and executable evidence are in `docs/models/m5_heston_stochastic_volatility.md`.

## Explicitly deferred finance conventions

These decisions should be settled by the first milestones that create real consumers. Until then, do not spread a local choice across the codebase as if it were canonical.

| Convention | Status | First expected pressure | Guidance until settled |
| --- | --- | --- | --- |
| General business-day/calendar framework | Deferred | future calendar-sensitive consumer | M1/M4/M5 intentionally use date-valued ACT/365F semantics; do not generalize this into a universal calendar policy. |
| General discount-factor/curve representation | Deferred | future curve/rates consumer | M1/M4/M5 use a flat money-market numeraire for supported evidence; M0A commits numeraire semantics, not a curve hierarchy. |
| Discrete dividend/corporate-action representation | Deferred | future instrument/market-data consumer | M1/M5 continuous yield is local; do not reinterpret it as a discrete dividend schedule. M3 explicitly rejects nonzero continuous yield for hedge execution until cash-flow accounting is settled. |
| General forward-market observation semantics | Deferred | future forward/curve consumer | M4 observes spot and constructs a model forward from explicit `r/q`; that is not an observed forward quote. |
| Array axis/order conventions for numerical kernels | Deferred | future vectorized/native kernel consumer | M5's scalar Python Fourier/Monte Carlo implementations do not create a shared array boundary. |
| Generic market timestamp/calendar convention | Deferred | future intraday/multi-market consumer | M4 requires timezone-aware retrieval/optional observation timestamps locally but does not define exchange-session semantics. |
| Generic quote cleaning policy | Deferred | second materially different market-data consumer | M4 commits only its European midpoint normalization; do not assume it fits every instrument/provider. |
| Inference/calibration loss/objective convention | Deferred | M6 | M4 solves a scalar equality; calibration objectives must belong to the future concrete calibration problem. |
| Inference weighting convention | Deferred | M6 | State how observations/targets are weighted and why. |
| Parameter bounds/transforms | Deferred | M6 | Keep model-domain constraints distinct from optimizer mechanics. |
| Arbitrage-free surface repair/interpolation | Deferred | future surface/calibration consumer | M4 reports narrow static violations only; it does not repair or interpolate a surface. |
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

M3 extends it to dynamic replication in `docs/models/m3_dynamic_delta_hedging.md`, including exact-transition GBM path semantics, the Delta-to-policy boundary, stock/cash self-financing identities, terminal error sign convention, transaction costs, misspecification, and distributional validation evidence.

M4 extends it to observed-data normalization and Black-Scholes inversion in `docs/models/m4_market_evidence_and_implied_volatility.md`, including price bounds, numerical method/failure semantics, M2-Vega conditioning, strike/maturity coordinates, static quote diagnostics, the pinned real-market source, explicit study assumptions, and the empirical evidence artifact.

M5 extends it to stochastic volatility in `docs/models/m5_heston_stochastic_volatility.md`, including Heston state/parameter notation, Feller semantics, the characteristic-function branch and `P1/P2` integrals, deterministic `xi=0` reduction, full-truncation Euler, stochastic ownership, and independent Fourier/Monte Carlo validation evidence.

## Market-data provenance convention

M4 establishes the first concrete production market-data provenance representation. Preserve as applicable and legally permitted:

- provider/source;
- market/as-of date;
- retrieval timestamp;
- optional observation timestamp when the source preserves one;
- raw artifact or content hash;
- normalization/transformation version; and
- licensing/redistribution notes.

If raw data cannot be redistributed or licensing is unclear, prefer a reproducible acquisition/processing recipe plus a pinned hash and derived evidence. Core CI should use deterministic synthetic or legally distributable curated fixtures rather than depending on live services.

## Changing a committed convention

A committed convention can change when evidence justifies it.

A change should normally include:

- the motivation and affected public contracts;
- migration/compatibility consequences;
- tests distinguishing old and new semantics where executable behavior changes;
- documentation updates in the same PR;
- an ADR when the decision is durable and consequential enough to require historical rationale.

Repository truth should evolve rather than preserving a bad convention for historical consistency.