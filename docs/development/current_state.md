# Current State

## Status

**M0 — Engineering Bootstrap is complete.**

**M0A — Mathematical Quant-Finance Architecture Foundation is complete.**

**M1 — European Options & Black-Scholes Reference Vertical is complete.**

**M2 — Independent Valuation and Sensitivity/Greeks is complete.**

**M3 — Dynamic Hedging / Control is complete.**

**M4 — Market Evidence / Inverse Problems is complete.**

**M5 — Heston Model and Independent Valuation is complete.** M5 establishes the first stochastic-volatility pricing specialization with explicit spot/instantaneous-variance state, immutable Heston parameter values, characteristic-function/Fourier valuation, independent full-truncation Euler Monte Carlo valuation, explicit numerical diagnostics, limiting-case evidence, and cross-method validation.

**UI1 — Native Quant Research Workbench Architecture & Black-Scholes Vertical Slice is complete and establishes the current desktop architecture.**

**UI2 — M2 Valuation Comparison, Convergence, Uncertainty & Greeks Workbench is complete.** UI2 extends the existing Black-Scholes Study over the actual merged M2 pricing and sensitivity contracts without adding UI-owned finance semantics or a generic desktop framework.

ADR 0002 remains the platform-wide mathematical architecture authority. M2 pressure-tested the M0A/M1 pricing boundary with independent numerical methods and established the first concrete production sensitivity family. M3 established the first concrete control/dynamic-replication family. M4 established the first production observed-market boundary and the first concrete inverse-problem specialization. M5 now proves that the same pricing architecture can host a materially richer two-factor stochastic law and two independent valuation methods without collapsing state, model parameters, valuation algorithms, or future calibration into one abstraction. ADR 0003 remains the native PySide6 + Qt Quick/QML authority; UI2 deepens that downstream architecture without changing the quantitative contracts.

The next finance-model milestone is **M6 — Heston Calibration / Inverse Problem**. It should consume the validated M5 Heston forward-pricing capability and M4 observation/inference discipline while keeping calibration targets/objectives separate from numerical optimization. The next desktop milestone should still be chosen from actual merged M3/M4/M5 product pressure rather than pre-building generic hedge, market-data, stochastic-volatility, or calibration UI frameworks.

## What exists

The repository now establishes:

- a `src/`-layout Python package with pytest, Ruff, strict Pyright, and GitHub Actions CI;
- the M0A production pricing composition under `qf_platform.pricing`;
- M1 European call/put, Black-Scholes/GBM, ACT/365F, money-market numeraire, and closed-form valuation semantics;
- three valuation methods over the same M1 `PricingProblem`: `BlackScholesClosedForm`, `CoxRossRubinstein`, and `MonteCarloEuropeanOption`;
- method-specific Monte Carlo uncertainty through immutable `MonteCarloValuationResult`;
- the first concrete sensitivity family under `qf_platform.sensitivity` with analytic and finite-difference Black-Scholes Delta, Gamma, Vega, Theta, and Rho;
- the first concrete control/dynamic-replication package under `qf_platform.control`, including exact-transition pricing-measure GBM paths, Delta hedge policy, self-financing accounting, misspecification studies, and transaction-cost evidence;
- the first production observed-market package under `qf_platform.market_data`, with immutable raw observations, provenance, explicit midpoint normalization, and narrow strike-slice diagnostics;
- the first production inverse-problem specialization under `qf_platform.inference`, with a Black-Scholes implied-volatility problem, separate numerical method, immutable result, feasibility checks, and conditioning evidence;
- deterministic synthetic M4 fixtures for CI plus a pinned, provenance-bearing derived SPX evidence artifact showing strike skew and maturity dependence;
- `HestonEquityState`, `HestonStateSpace`, `HestonLaw`, and immutable `HestonParameters` under the existing pricing architecture;
- reuse of the existing `EuropeanOption` contract under Heston rather than a model-specific contract duplicate;
- `HestonFourierEuropeanOption` with explicit integration domain/resolution, stable characteristic-function branch semantics, and immutable quadrature diagnostics;
- `HestonMonteCarloEuropeanOption` with explicit paths, timesteps, integer seed, local RNG ownership, correlated shocks, full-truncation Euler variance dynamics, sampling uncertainty, and negative-variance proposal diagnostics;
- exact deterministic-variance handling at `xi = 0`, validated against the independent Black-Scholes closed form using integrated deterministic variance;
- M5 evidence covering parameter/state domains, Feller-diagnostic semantics, expiry/zero-spot boundaries, put-call parity, Fourier convergence, Feller-violating but numerically supported parameters, seeded Monte Carlo reproducibility, variance-boundary pressure, and Fourier ↔ Monte Carlo agreement;
- the native PySide6 + Qt Quick/QML Quant Research Workbench;
- UI2 method selection and explicit compatibility diagnostics for analytic, CRR, and Monte Carlo valuation over one normalized Black-Scholes pricing problem;
- renderer-neutral payoff, convergence, Monte Carlo uncertainty, and Greek plot inputs;
- UI2 analytic/CRR/Monte Carlo comparison tables, all five M2 Greeks, analytic-vs-finite-difference evidence, finite-difference diagnostics, and numerical/RNG provenance; and
- dedicated desktop validation including QML/offscreen source smoke and one-platform standalone build/launch proof.

## Mathematical architecture

The platform-wide conceptual pattern remains:

```text
Problem + supported Method -> specific immutable Result
```

For Black-Scholes pricing:

```text
same PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
        ↓
ValuationResult or method-specific subtype
```

For Heston pricing:

```text
HestonEquityState(spot, instantaneous variance)
+
HestonLaw + HestonParameters
+
existing EuropeanOption
+
existing money-market numeraire + pricing measure
        ↓
PricingProblem
        ├── HestonFourierEuropeanOption
        └── HestonMonteCarloEuropeanOption
        ↓
method-specific immutable valuation evidence
```

For sensitivity:

```text
BlackScholesSensitivityProblem
        +
supported sensitivity method
        ↓
BlackScholesSensitivityResult
```

For control / dynamic replication:

```text
Black-Scholes pricing problem
        +
model-generated path semantics
        +
rebalance schedule
        +
AnalyticDeltaHedgePolicy
        +
stock/cash financing and cost convention
        ↓
DeltaHedgeResult
        ↓
ReplicationErrorSummary
```

For the first inverse problem:

```text
raw option + underlying observations
        +
provenance
        ↓
explicit normalization
        ↓
NormalizedOptionObservation
        +
BlackScholesImpliedVolatilityProblem
        +
BisectionImpliedVolatility
        ↓
ImpliedVolatilityResult
```

This remains concrete. The repository intentionally has no universal `SensitivityProblem`, `ControlProblem`, `InverseProblem`, `Strategy`, `Portfolio`, `Problem`, `Method`, `Result`, factor-model, Fourier-engine, or stochastic-simulator hierarchy.

Protect:

```text
pricing problem != sensitivity problem != control problem != inverse problem
financial model != numerical method != path simulation
raw observation != normalized observation != modeled state
observed price != model price != implied volatility
inverse financial problem != root-finding method != inverse result
Delta sensitivity != hedge policy != realized hedge action
replication error != model error by definition
implied volatility != directly observed or physical-measure volatility
Heston state != Heston law != Heston parameters
Heston law != Fourier method != Heston Monte Carlo method
Heston forward valuation != future Heston calibration
```

Pricing remains upstream of sensitivity and control. M4 inference consumes pricing and sensitivity behavior but does not move observation semantics into pricing. M5 stays on the forward-pricing side of that boundary; M6 should infer new immutable Heston parameter values rather than mutate model identity.

## M3 dynamic hedging / control

M3 turns Black-Scholes Delta from a static sensitivity into a dynamic policy input while preserving the responsibility boundary:

```text
Delta = dV/dS
        ↓
current-state policy evaluation
        ↓
target stock units
        ↓
explicit rebalance action
        ↓
realized stock/cash hedge trajectory
```

`BlackScholesPathSimulation` / `simulate_black_scholes_path` sample exact adjacent-date GBM transitions under the configured M1 money-market pricing measure. Observation dates are therefore not Euler timesteps and remain distinct from hedge rebalance dates.

The supported first problem is one short European option. Initial hedge wealth equals the hedging-model Black-Scholes present value; stock targets are M2 analytic Delta and residual cash earns through the existing money-market account. The result records stock, cash, financing, trades, costs, terminal payoff/value, and replication error separately.

M3 evidence establishes seeded reproducibility, no-lookahead behavior, self-financing identities, rebalance-frequency effects, volatility misspecification, transaction-cost drag, and replicate-integrity rules. Hedge execution currently requires zero continuous dividend yield until dividend/carry cash-flow accounting is explicit.

See `docs/models/m3_dynamic_delta_hedging.md`.

## M4 observed market evidence / inverse problem

M4 productionizes the observation/model boundary:

```text
real market
    ↓
RawOptionQuote + RawUnderlyingObservation
    + ObservationProvenance
    ↓
normalize_european_option_midpoint
    ↓
NormalizedOptionObservation
    ↓
BlackScholesImpliedVolatilityProblem
    + BisectionImpliedVolatility
    ↓
ImpliedVolatilityResult
```

### Observation and normalization semantics

Raw option quotes retain provider/source identity, market date, retrieval timestamp, optional observation timestamp, optional raw-artifact SHA-256, licensing notes, contract identity, bid/ask/last, volume/open interest, exercise style, and settlement convention where available. Bad finite raw quotes remain evidence; normalization decides whether they are admissible.

The first production normalization policy requires matching underlying/date, European exercise, non-AM settlement under current date-only expiry semantics, present positive bid/ask, a non-crossed market, and positive observed spot. The normalized midpoint keeps references to both raw observations and records its normalization version.

Observed values never silently become modeled state or model-implied quantities.

### Implied-volatility inverse semantics

For fixed model inputs other than volatility, M4 solves

```text
Black-Scholes price(sigma) = normalized observed option price
```

with the financial inverse problem separate from the numerical root finder. European option price bounds are checked before numerical solving. The bisection method owns its volatility bracket, convergence tolerances, and iteration limit. Financial inconsistency, an unbracketed admissible domain, and unresolved numerical convergence have distinct failure semantics.

M4 reuses M2 analytic Vega at the inferred solution to preserve conditioning evidence. The result records Vega, local inverse-price-to-volatility sensitivity, and a first-order half-bid/ask-spread volatility shift so a converged root is not confused with a well-conditioned inference.

### Deterministic and empirical evidence

Core CI uses a deterministic synthetic fixture with deliberate strike and maturity volatility structure. It proves the full observation → normalization → inverse pipeline without representing synthetic data as empirical evidence.

A separate pinned SPX research artifact for January 4, 2023 uses two expiries (approximately 30 and 114 days), explicit flat continuously compounded rate/carry assumptions, midpoint targets, and an OTM put/call selection convention. The derived evidence shows materially higher implied volatility at lower strikes than higher strikes in both expiries and non-identical levels across maturity.

Representative inferred levels under the documented assumptions are approximately:

```text
30-day slice:
K=3720 put   23.03%
K=3850 put   21.45%
K=3900 call  20.65%
K=4020 call  19.08%

~114-day slice:
K=3720 put   23.12%
K=3900 call  21.49%
K=4075 call  19.63%
K=4240 call  18.22%
```

Thus one constant Black-Scholes volatility cannot reconcile the observed option set under the explicit input convention. Same-right midpoint slices were monotone in strike in the inspected data but contained discrete convexity violations, which M4 records as data-quality evidence rather than repairing into an arbitrage-free surface.

See `docs/models/m4_market_evidence_and_implied_volatility.md` and `docs/evidence/m4_spx_implied_volatility_evidence.json`.

## M5 Heston stochastic volatility / independent valuation

M5 responds to M4's observed strike-skew and maturity-dependence pressure by introducing a richer forward model rather than jumping directly to calibration.

Under the existing money-market pricing semantics, the concrete dynamics are:

```text
dS_t = (r - q) S_t dt + sqrt(v_t) S_t dW^S_t

dv_t = kappa (theta - v_t) dt + xi sqrt(v_t) dW^v_t

d<W^S, W^v>_t = rho dt
```

The risk-free accumulation rate remains owned by the numeraire. `HestonEquityState` carries spot and instantaneous annualized variance. `HestonParameters` carries `kappa`, `theta`, `xi`, `rho`, and continuous dividend yield. The Feller discriminant `2*kappa*theta - xi^2` is available as positivity diagnostic evidence, but Feller violation is not treated as automatic model invalidity.

The first deterministic method, `HestonFourierEuropeanOption`, evaluates the Heston characteristic function with a stable square-root branch and explicit finite-frequency composite-Simpson quadrature configuration. Its immutable result records the integration domain/resolution and characteristic-function evaluation count, keeping Fourier truncation/quadrature mechanics outside `HestonLaw`.

The independent stochastic method, `HestonMonteCarloEuropeanOption`, owns explicit path count, timestep count, and integer seed. Each application creates fresh local RNG state, forms correlated Brownian shocks explicitly through `rho`, and uses full-truncation Euler for positive `xi`. Its result retains normal-approximation sampling uncertainty, variance-scheme identity, timestep count, and negative raw variance proposals as boundary-pressure evidence. Those proposals are numerical-discretization diagnostics, not financial-model error counts.

At exactly `xi = 0`, variance is deterministic. M5 evaluates the integrated deterministic variance directly; Fourier pricing reduces to the existing Black-Scholes closed form with the corresponding effective volatility, while Monte Carlo samples the exact terminal log-spot distribution. This boundary provides independent limiting evidence and avoids pretending the singular positive-`xi` characteristic-function formula remains numerically appropriate at zero vol-of-vol.

The validation set includes immutable/domain checks, Feller-violating supported parameters, expiry payoff and zero-spot boundaries, put-call parity, Fourier convergence under finer integration, exact `xi=0` reduction, equal-seed Monte Carlo reproducibility, explicit variance-boundary pressure, and non-degenerate Fourier ↔ Monte Carlo agreement with tolerance tied to MC sampling uncertainty plus discretization allowance.

See `docs/models/m5_heston_stochastic_volatility.md`.

## Native Workbench boundary

The durable desktop dependency direction remains:

```text
Qt Quick / QML
        ↓
curated PySide6 controller / item-model boundary
        ↓
frontend-neutral application + presentation semantics
        ↓
public mathematical-finance APIs
        ↓
production quantitative core
```

QML owns no payoff, pricing, day-count, discounting, compatibility, inference, quote-cleaning, arbitrage-diagnostic, sensitivity, convergence, confidence-interval, Heston-model, or calibration semantics. The Python/application side owns normalization, compatibility, execution, quantitative results, diagnostics, and provenance interpretation.

### UI1

UI1 remains the first M1 analytical vertical: native Home/Study navigation, Guided/Advanced Black-Scholes composition, mathematical inspector, authoritative `ValuationResult.present_value`, terminal payoff presentation, M1 parity/bounds/reference evidence, QML/offscreen smoke, and standalone deployment proof.

### UI2

UI2 extends that same Black-Scholes Study with actual M2 capabilities:

```text
same normalized PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein(steps)
        └── MonteCarloEuropeanOption(paths, seed)
```

The Compose surface exposes method selection and method-specific configuration. RNG seed and finite-difference bump controls live at Advanced disclosure because they are reproducibility/numerical configuration rather than economic inputs.

Analyze exposes renderer-neutral terminal-payoff, CRR-convergence, Monte-Carlo-uncertainty, and selected-Greek curves. Results expose analytic/CRR/Monte Carlo comparison plus a separate all-Greeks analytic-vs-finite-difference table. Validate keeps structural mathematical meaning, implementation availability, selected-method support, validation evidence, and Workbench exposure distinct, and preserves unsupported finite-difference domain-crossing bumps instead of silently changing the method. Present/Export exposes numerical/RNG/sensitivity provenance but does not invent M4 observation-provider provenance.

UI2 uses the existing narrow `QThread` execution pattern for its concrete M2 analysis request. Monte Carlo supplies real asynchronous workload pressure, but UI2 still does not create a universal job/scheduler framework.

UI1's payoff curve plus UI2 convergence/uncertainty/Greek curves earn a deliberately small renderer-neutral plotting value:

```text
PlotData
└── PlotSeries
    └── PlotPoint(x, y, optional lower/upper)
```

Only numeric points, labels, and paired vertical uncertainty bounds are shared. Qt styling, axes layout, pixel mapping, and interaction remain renderer concerns; there is no universal visualization grammar.

See `docs/architecture/native_quant_workbench.md` and ADR 0003.

## Error and evidence taxonomy

The accumulated evidence keeps different mechanisms separate:

```text
financial model / misspecification effect
CRR discretization / approximation error
Fourier truncation / quadrature error
complex characteristic-function numerical stability
Monte Carlo valuation sampling error
Heston time-discretization bias
variance-boundary discretization effect
finite-difference truncation error
finite-difference cancellation / floating-point error
discrete hedge-rebalancing error
stochastic hedge-replicate variation
transaction-cost effect
observed quote width / data-quality effect
inverse-problem conditioning through Vega
root-solver failure
analytical floating-point error
```

A terminal hedging discrepancy is not automatically model error, a Monte Carlo confidence interval is not a deterministic pricing tolerance, Fourier/MC disagreement is not automatically model error, and a numerically converged implied-volatility result is not automatically well conditioned.

## Quality and development cadence

The canonical gate remains:

```text
Ruff lint
Ruff format check
strict Pyright
pytest
```

Use `./scripts/fix` after coherent Python batches, focused behavioral/quantitative validation during the inner loop, `./scripts/check_all` at meaningful checkpoints, and full CI on final candidates. Desktop-only dependencies/checks remain in the dedicated Desktop workflow.

At the first full M5 candidate head, hosted core CI reported Ruff clean, all tracked Python formatted, strict Pyright with zero errors/warnings, and 161 passing tests with the three PySide6-dependent desktop tests skipped in core CI because the optional desktop dependency is not installed there. The final merged M5 head must be reverified after durable documentation reconciliation.

## Deliberately absent

The following remain absent until later milestones create real consumers:

- generic stochastic-control, trading-strategy, execution, trade, or portfolio frameworks;
- physical-measure forecasting/path semantics for M3;
- nonzero-dividend hedge cash-flow accounting;
- generic/live market-data-provider framework;
- generic quote-cleaning or staleness framework;
- generic volatility-surface construction/interpolation/repair framework;
- generic inverse/inference, prediction, risk, or validation frameworks;
- Heston calibration and generic calibration/optimizer infrastructure;
- generic Fourier/quadrature infrastructure;
- generic stochastic-simulator or factor-model infrastructure;
- discount/dividend curve inference from option chains;
- full put-call-parity forward extraction infrastructure;
- native/C++ quantitative backends;
- generic UI schema/form generation, node editors, plugin architecture, universal plotting grammar, or universal background-job infrastructure; and
- UI2 panels for M3 hedging, M4 observations/implied volatility, M5 Heston, or future calibration work.

## Next objectives

### M6 — Heston calibration / inverse problem

M6 should consume M4's observation/provenance discipline and M5's validated Heston forward-pricing contracts to answer whether Heston parameter values can be inferred from known and observed targets, and how trustworthy that inference is.

The required separation is:

```text
observed / synthetic targets
        +
Heston calibration problem
        +
objective / weighting / constraints
        ↓
separate numerical optimization method
        ↓
new immutable HestonParameters
        +
residual / recovery / stability evidence
```

Protect:

```text
HestonLaw != calibrated HestonParameters
calibration problem != numerical optimizer
observations != inferred parameters
forward-pricing numerical error != calibration residual
parameter non-identifiability != optimizer failure
```

Synthetic parameter recovery should precede claims from real-market calibration. M6 should not mutate `HestonLaw`, move market observations into pricing, or create a universal inverse/optimizer framework merely because it has more than one parameter.

### Next native Workbench pressure

UI2 deliberately stops at merged M2 capabilities even though M3, M4, and M5 now exist. A later UI milestone may expose dynamic hedging/control evidence, market-observation/implied-volatility evidence, or Heston forward valuation, but the choice should follow actual merged product/research pressure and stable backend ownership rather than a speculative generic UI framework.
