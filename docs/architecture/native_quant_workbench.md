# Native Quant Research Workbench

## Status

The native Workbench is a PySide6 + Qt Quick/QML desktop application downstream of the quantitative core.

The implemented desktop milestones are:

- **UI1** — Black-Scholes analytical vertical and native desktop architecture;
- **UI2** — independent M2 valuation methods, convergence/uncertainty, and Greeks;
- **UI3** — M3 dynamic hedging/control plus M4 observed-market/implied-volatility workflows;
- **UI4** — M5 Heston forward valuation plus M6 Heston calibration/identifiability workflows; and
- **UI5** — M7 validation/model-risk evidence, M8 measured performance evidence, and product hardening.

ADR 0003 remains the authority for the native desktop boundary. UI5 extends that boundary; it does not replace it.

## Dependency direction

```text
Qt Quick / QML
        ↓
curated PySide6 controller / item models
        ↓
frontend-neutral application + presentation semantics
        ↓
public quantitative APIs / committed derived evidence
        ↓
production quantitative core
```

The finance core remains Qt-independent. PySide6 remains an optional desktop dependency.

QML receives only curated scalar properties, signals/slots, item models, and serialized renderer-neutral plot values. Production finance-domain graphs remain private to Python.

Protect:

```text
QML presentation != quantitative authority
UI draft state != committed finance state
Qt object != immutable quantitative result
training fit != held-out evaluation
measured runtime != model quality
measured optimization != justification for a native backend
```

QML does not calculate prices, Greeks, payoff semantics, residuals, objective values, financial bounds, calibration, conditioning, validation metrics, performance measurements, discounting, day count, or method compatibility.

## Product organization through UI5

The Workbench starts from the mathematical/research question rather than from a generic plugin/model browser.

Current concrete workflows are:

```text
Forward valuation / sensitivity
    ├── Black-Scholes valuation & Greeks
    └── Heston forward valuation

Control / replication
    └── Black-Scholes dynamic Delta hedging

Observed-market inverse inference
    └── Black-Scholes implied volatility / market evidence

Multi-parameter inverse inference
    └── Heston calibration / identifiability

Validation / model risk
    └── fair Black-Scholes vs Heston train/held-out comparison

Performance engineering evidence
    └── revision-pinned M7 baseline vs M8 optimized workloads
```

These are concrete downstream adapters over merged quantitative behavior and committed derived evidence. They are not instances of a universal workflow framework.

## Draft state and normalization

Interactive editing remains transient until Python normalization succeeds.

Black-Scholes follows:

```text
text-valued financial draft
        ↓
BlackScholesStudyDraft
        ↓
M1 typed composition / PricingProblem
```

Heston follows:

```text
text-valued Heston draft
        ↓
HestonPricingDraft
        ↓
HestonEquityState + HestonLaw + HestonParameters
+ EuropeanOption + numeraire + pricing measure
        ↓
PricingProblem
```

Numerical configuration remains separate from financial/model coordinates. For Heston in particular:

```text
v0, kappa, theta, xi, rho, q
!=
Fourier integration bounds / intervals
!=
Monte Carlo paths / timesteps / seed
```

`v0` remains current state-like instantaneous variance. It is not moved into `HestonParameters` for UI convenience.

## Renderer-neutral presentation seam

The repeated plot responsibility remains intentionally small:

```text
PlotData
└── PlotSeries
    └── PlotPoint(x, y, optional lower/upper)
```

UI4 reuses this seam for Heston method comparison, Fourier-resolution stability, calibration parameter error, residuals, multiple-start objectives, and committed M6 SPX derived evidence.

UI5 reuses the same seam for M7 residual/held-out/stability views and M8 revision-pinned baseline-versus-optimized workload timing evidence. Styling, layout, pixel transforms, legends, and interaction remain renderer-owned. There is still no generic chart DSL or quantitative visualization framework.

## UI4 — Heston forward valuation

UI4 makes the model distinction visible while preserving the shared forward-pricing question and contract:

```text
Black-Scholes
    state: S_t
    constant annualized volatility

Heston
    state: (S_t, v_t)
    stochastic variance
    correlated spot/variance shocks
```

The Heston workspace normalizes draft inputs into actual merged M5 objects:

- `HestonEquityState`;
- `HestonLaw`;
- `HestonParameters`;
- existing `EuropeanOption`;
- existing flat money-market numeraire and pricing-measure semantics;
- `PricingProblem`.

The same Heston pricing problem is evaluated by both authoritative M5 methods:

```text
same Heston PricingProblem
        ├── HestonFourierEuropeanOption
        └── HestonMonteCarloEuropeanOption
```

Method-specific result evidence remains specific.

Fourier exposes:

- present value;
- integration bounds;
- Simpson interval count;
- characteristic-function evaluation count;
- same-problem resolution-stability evidence.

Monte Carlo exposes:

- present value;
- standard error and 95% sampling interval;
- paths, timesteps, and seed;
- variance scheme;
- negative-variance proposal count.

The Workbench interprets disagreement according to actual error mechanisms:

```text
Monte Carlo sampling uncertainty
!= Heston time-discretization bias
!= Fourier truncation/quadrature error
!= financial-model error
```

The Feller discriminant/status is shown as diagnostic evidence only. It is not rendered as a universal valid/invalid model badge.

### No fabricated paths

Merged M5 valuation results do not retain authoritative Heston spot/variance trajectories. UI4 therefore does not synthesize decorative paths. A future path view requires a merged backend capability that owns those trajectories.

## UI4 — Heston calibration as a separate inverse workflow

Calibration is a separate workspace rather than a button embedded into the model-parameter editor.

The authoritative M6 composition remains visible:

```text
HestonPriceCalibrationTarget(s)
+ fixed spot / rate / q
+ HestonCalibrationBounds
+ price-space residual / weighting semantics
+ Heston Fourier forward method
        ↓
HestonCalibrationProblem
        +
ScipyLeastSquaresHestonCalibration
        ↓
HestonCalibrationResult
```

Protect:

```text
Heston model != calibrated parameter estimate
calibration problem != optimizer
observed target != model price != residual
objective / weighting != optimizer configuration
optimizer convergence != parameter identification != model validity
```

M6 implements option-price-space calibration only. UI4 does not invent implied-volatility-space Heston calibration.

The inferred direct financial coordinates are:

```text
(v0, kappa, theta, xi, rho)
```

Spot, risk-free accumulation, and `q` remain fixed problem inputs in this first consumer. There are no hidden transformed optimizer coordinates. The Feller condition remains diagnostic rather than an optimizer constraint.

## Synthetic recovery and identifiability laboratory

UI4 includes two deterministic M6-backed experiments.

### Truth-known recovery

```text
known Heston truth
        ↓
M5-generated option-price targets
        ↓
M6 calibration from explicit non-truth starts
        ↓
recovered coordinates + residuals + conditioning
```

The UI shows truth versus recovered coordinates, target/model prices, residuals, objectives, optimizer termination, and local conditioning evidence.

### Thin non-identifiability counterexample

A deliberately underdetermined three-target/five-coordinate calibration is first-class evidence. Multiple starts can achieve tiny loss while producing materially different parameter estimates and rank-deficient local Jacobians.

The Workbench therefore teaches directly:

```text
small objective
!= unique parameter estimate
!= trustworthy parameter estimate
```

Local singular values/rank/condition evidence are not presented as posterior uncertainty or proof of global uniqueness.

## Real-market M6 reference evidence

UI4 exposes the committed derived M6 SPX calibration reference without redistributing raw source rows.

The standalone package carries a reviewed value mirror of `docs/evidence/m6_spx_heston_calibration_reference.json`; tests compare that mirror against the committed artifact so the packaged display cannot silently drift. The repository evidence artifact and `scripts/m6_heston_calibration.py` remain authoritative for raw-artifact replay.

The UI exposes:

- market snapshot/source lineage and non-redistribution note;
- target count and expiries;
- half-spread price weighting;
- three recorded starts and estimates;
- best calibrated coordinates and objective;
- standardized residuals;
- Feller diagnostic;
- optimizer termination;
- Jacobian rank, singular values, and condition number;
- explicit non-claims about identification/model validity.

It does not fabricate a raw quote table, continuous surface, or observations absent from the committed evidence.

## UI5 — validation and model-risk workspace

UI5 consumes the merged M7 validation specialization rather than re-implementing model comparison in QML.

The authoritative composition remains:

```text
NormalizedOptionObservation(s)
+ predeclared TRAINING / EVALUATION partition
+ fixed financial inputs
+ Black-Scholes benchmark fit domain
+ Heston calibration domain / Fourier forward map
        ↓
BlackScholesHestonValidationProblem
        +
CrossSectionalBlackScholesHestonValidation
        ↓
BlackScholesHestonValidationEvidence
```

The native validation workspace preserves the M7 distinctions directly:

```text
training fit != held-out evaluation
same-date cross-sectional holdout != temporal forecasting
better held-out pricing != universal model validity
optimizer convergence != parameter identification
conditioning != posterior uncertainty
Heston pricing advantage != demonstrated Heston hedging advantage
```

The Workbench displays training and evaluation metrics separately, contract-level residuals, Heston training/full-sample stability, local Jacobian diagnostics, the bounded M7 conclusion, and explicit non-claims.

The M7 validation run executes off the GUI thread. Because the production method exposes no progress stream or cancellation contract, UI5 shows truthful busy/completed/error state only—no invented percentage or cancel button.

## UI5 — committed M8 performance evidence

M8 is merged and the Workbench presents its measured result directly. The standalone package carries a reviewed value mirror of `docs/evidence/m8_performance_reference.json`; regression tests compare the mirror with the committed artifact so the packaged display cannot silently drift.

The performance surface exposes all six representative workloads, including:

```text
Heston MC, 20k x 252                 3.3673 s -> 0.1230 s   27.38x
10-target / 3-start calibration      2.2919 s -> 0.4971 s    4.61x
14-target / 3-start calibration      3.2752 s -> 0.5454 s    6.01x
complete M7 validation study         5.4136 s -> 1.0819 s    5.00x
```

The two scalar reference workloads remain explicitly marked as non-speedup claims. Hosted-runner timings are revision/environment-pinned descriptive evidence, not CI thresholds or universal latency guarantees.

Parity remains first-class evidence:

- deterministic financial comparison checks pass;
- Heston Monte Carlo parity is statistical because M8 intentionally changed RNG implementation;
- equal integer seed does not imply identical old/new random streams.

Most importantly, UI5 preserves M8's measured negative native decision:

```text
profile representative workloads
        ↓
remove scalar Python/RNG and repeated Fourier work
        ↓
4.61x–27.38x heavy-workload reference improvement
        ↓
parity retained
        ↓
C++ not justified for the current representative workload scale
```

There is therefore no native-backend selector, generic backend registry, or fictitious C++ execution path in UI5.

## Mathematical inspectors and reporting

The Heston pricing inspector remains concrete:

```text
State
Stochastic law
Parameters
Pricing measure
Contract
Pricing problem
Valuation methods
Numerical assumptions
```

The Heston calibration inspector remains separately concrete:

```text
Targets
Unknown coordinates
Forward operator
Objective
Weights
Financial bounds
Inverse method / optimizer
Completed result
Conditioning / identifiability evidence
```

UI5 adds a validation inspector over observed quantities, predeclared partition, validation problem/method, training fits, immutable evidence, and stability/conditioning. It also provides a concrete copy/select evidence report over already-owned M7/M8 values.

No universal metadata hierarchy, report-generation framework, persisted-study model, or arbitrary file-export system is introduced merely to render these panels.

## Execution boundary and worker lifetime

UI1–UI4 established a local one-active-`QThread` worker boundary for materially expensive computations. UI5 reuses it for the M7 validation study.

The desktop gate now executes native controller tests in separate Python processes. This isolates Qt/PySide object lifetimes between test nodes and prevents one test's native runtime teardown from contaminating another.

UI5 also hardens the inherited worker cleanup path after process isolation exposed a PySide wrapper-lifetime race around `QThread.finished`/`deleteLater`. Product semantics remain unchanged: one active heavy computation, explicit status, and completed immutable evidence installation.

UI4 stale-result protection remains:

```text
one active heavy computation
+ concrete job id / workspace ownership
+ input invalidation
        ↓
stale completion cannot become active result
```

This does **not** introduce:

- a scheduler;
- task graph;
- queue;
- generic cancellation protocol;
- process pool;
- persistence layer;
- generic job registry;
- synthetic progress protocol.

## Product hardening and deliberate limits

UI5 adds concrete accessibility/product improvements without creating a generic desktop framework:

- keyboard launch/workspace shortcuts;
- accessible names for primary controls;
- explicit focus flow for principal controls;
- responsive layouts;
- empty/running/result/warning/error states;
- bounded unsupported-claim warnings;
- copy/select evidence reporting;
- continued standalone package proof.

The project still deliberately does not claim:

- temporal out-of-sample validation;
- authoritative Heston hedge superiority;
- posterior parameter uncertainty;
- generic saved-study/fork/project persistence;
- arbitrary report/document infrastructure;
- Windows/macOS installer certification;
- code signing/notarization; or
- a C++ quantitative backend for the current representative workload scale.

## Packaging and validation

Source launch:

```text
python -m pip install -e ".[dev,desktop]"
python -m qf_platform.desktop.main
```

Headless source smoke:

```text
QT_QPA_PLATFORM=offscreen python -m qf_platform.desktop.main --smoke-test
```

Dedicated Desktop CI verifies:

- pinned PySide6 runtime;
- desktop Ruff and strict Pyright;
- process-isolated native controller behavior;
- frontend-neutral application/presentation behavior;
- Qt-free quantitative-core dependency direction;
- isolated QML engine loading;
- source launch smoke;
- standalone `pyside6-deploy` build;
- packaged offscreen launch smoke; and
- standalone artifact upload.

## Multi-surface extension rule / F-series handoff

Future clients consume only capabilities and evidence actually merged on main.

The current F-series broadens downstream access without changing the quantitative authority:

~~~text
production quantitative core / committed evidence
                 ↓
frontend-neutral application + presentation/research semantics
          ┌──────┼──────┬──────────┐
          ↓      ↓      ↓          ↓
       Jupyter  exports  Dash     Qt/QML
          ↑
        Python
~~~

The native Workbench remains a first-class client, but not the universal interface layer.

F1 must audit the existing application/presentation seams before extracting anything new. F2 notebooks, F3 exports, and F4 Dash then consume the merged F1 contracts. F5 integrates the sibling surfaces.

The growth rule remains consumer-driven. Multiple clients do **not** by themselves justify a universal model registry, workflow graph, chart grammar, job system, report engine, persistence layer, or numerical-backend registry.

Historical M9 packaging/release work remains history and does not block continued development or require a GitHub Release/tag before the F-series proceeds.

## F1 research interface audit

The [implemented multi-surface boundary](research_interfaces.md) records the F1
audit, public API decision and dependency checks. The existing application and
domain packages serve Python consumers directly; no separate research façade
is introduced. See the [Python research guide](../research/python_api.md) for
public workflow contracts and runnable examples.
