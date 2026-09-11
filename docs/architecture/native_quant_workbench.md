# Native Quant Research Workbench

## Status

The native Workbench is a PySide6 + Qt Quick/QML desktop application downstream of the quantitative core.

The implemented desktop milestones are:

- **UI1** — Black-Scholes analytical vertical and native desktop architecture;
- **UI2** — independent M2 valuation methods, convergence/uncertainty, and Greeks;
- **UI3** — M3 dynamic hedging/control plus M4 observed-market/implied-volatility workflows;
- **UI4** — M5 Heston forward valuation plus M6 Heston calibration/identifiability workflows.

ADR 0003 remains the authority for the native desktop boundary. UI4 extends that boundary; it does not replace it.

## Dependency direction

```text
Qt Quick / QML
        ↓
curated PySide6 controller / item models
        ↓
frontend-neutral application + presentation semantics
        ↓
public quantitative APIs
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
```

QML does not calculate prices, Greeks, payoff semantics, residuals, objective values, financial bounds, calibration, conditioning, discounting, day count, or method compatibility.

## Product organization

The Workbench starts from the mathematical question rather than from a generic plugin/model browser.

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
```

These are concrete downstream adapters over merged quantitative behavior. They are not instances of a universal workflow framework.

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

The repeated plot responsibility earned through UI1–UI3 remains intentionally small:

```text
PlotData
└── PlotSeries
    └── PlotPoint(x, y, optional lower/upper)
```

UI4 reuses this seam for Heston method comparison, Fourier-resolution stability, calibration parameter error, residuals, multiple-start objectives, and committed M6 SPX derived evidence.

Styling, layout, pixel transforms, legends, and interaction remain renderer-owned. There is still no generic chart DSL or quantitative visualization framework.

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

## Mathematical inspectors

The Heston pricing inspector is concrete:

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

The Heston calibration inspector is separately concrete:

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

No universal metadata hierarchy is introduced merely to render these panels.

## Execution boundary and stale-result safety

UI1–UI3 established a local `QThread` worker boundary. UI4 reuses it for materially heavier Heston Monte Carlo and calibration work.

UI4 adds only the behavior now required by a real interactive consumer:

```text
one active heavy computation
+ concrete job id / workspace ownership
+ input invalidation
        ↓
stale completion cannot become active result
```

If relevant draft inputs change while a UI4 computation is running, execution may finish, but its result is discarded instead of replacing the newer UI state.

This does **not** introduce:

- a scheduler;
- task graph;
- queue;
- cancellation protocol;
- process pool;
- persistence layer;
- generic job registry;
- synthetic progress protocol.

Merged M6 exposes no optimizer progress stream, so UI4 shows busy/completed state only.

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
- application/presentation/controller behavior;
- Qt-free quantitative-core dependency direction;
- isolated QML engine loading;
- source launch smoke;
- standalone `pyside6-deploy` build;
- packaged offscreen launch smoke;
- standalone artifact upload.

## Extension rule / UI5 handoff

Future UI milestones consume only capabilities actually merged on `main`.

M7 is currently an independent in-progress workstream. UI4 does not encode its not-yet-merged Black-Scholes-versus-Heston validation conclusions.

UI5 should begin only from the actual merged M7 validation/model-risk evidence and the concrete M8 performance/release needs that exist at that time. Likely pressure includes comparative validation evidence, model-risk reporting, and performance visibility, but UI5 must not predefine those semantics before the backend work lands.

The growth rule remains:

```text
merged quantitative capability
        ↓
concrete frontend-neutral application/presentation semantics
        ↓
curated controller values/actions
        ↓
QML presentation
```

UI4 still does not justify a universal model registry, inverse-problem framework, optimizer UI, workflow graph editor, chart grammar, or desktop job system.
