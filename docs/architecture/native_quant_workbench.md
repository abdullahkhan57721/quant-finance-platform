# Native Quant Research Workbench

## Status

UI1 established the native PySide6 + Qt Quick/QML desktop architecture over the M1 Black-Scholes analytical vertical. UI2 extends that same architecture over the actual merged M2 valuation and sensitivity capabilities. UI3 extends the same boundary over the merged M3 dynamic-control and M4 observed-market/inverse-problem capabilities while preserving them as different mathematical workflows.

The durable dependency direction remains:

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

The finance core remains Qt-independent.

## Boundary rule

Values cross the QML boundary; finance-domain object graphs do not.

QML receives only deliberately exposed:

- scalar properties;
- signals and slots/actions;
- Qt item models containing renderer-neutral rows;
- serialized renderer-neutral plot data.

The Python controller may privately retain immutable `PricingProblem`, valuation result, sensitivity result, application request, and presentation objects. QML never receives arbitrary contracts, stochastic laws, model parameters, numeraires, pricing-measure objects, method objects, or production result graphs.

QML owns interaction and pixel rendering. It does not calculate prices, Greeks, confidence intervals, convergence errors, finite-difference diagnostics, payoff semantics, day count, discounting, compatibility, parity, or no-arbitrage evidence.

## Draft state and committed state

Interactive text remains transient until Python normalization succeeds:

```text
financial draft text
        ↓
BlackScholesStudyDraft
        ↓
M1 typed financial composition
        ↓
immutable PricingProblem
```

UI2 adds separate numerical/reproducibility configuration:

```text
method / RNG / sensitivity draft text
        ↓
M2WorkbenchDraft
        ↓
M2WorkbenchConfig
```

These are deliberately distinct responsibilities:

```text
spot / strike / volatility / rate / carry
!=
CRR steps / Monte Carlo paths / RNG seed / finite-difference bumps
```

The RNG seed is reproducibility configuration, not an economic or stochastic-law parameter. Guided and Advanced disclosure are product views over one normalization path, not different financial models.

## Product surface

The native shell keeps the UI1 product model:

```text
HOME
└── New Study

STUDY
├── Compose
├── Analyze
├── Results
├── Validate
└── Present / Export

Run Study = action
```

UI2 deepens the existing Black-Scholes Study rather than creating a generic study framework.

### Compose

Guided financial inputs remain:

- Spot;
- Strike;
- Expiry;
- Volatility;
- Interest rate;
- Dividend/carry;
- Option type.

UI2 adds a valuation-method selector for:

- `BlackScholesClosedForm`;
- `CoxRossRubinstein(steps)`;
- `MonteCarloEuropeanOption(paths, seed)`.

Method-specific configuration is conditional. CRR exposes steps. Monte Carlo exposes paths, while the seed sits in Advanced disclosure because it is reproducibility provenance rather than a financial input.

Advanced disclosure also exposes valuation date, ACT/365F and continuous-rate/carry semantics, finite-difference bump configuration, model/measure identity, and RNG semantics.

### Analyze

UI2 exposes renderer-neutral plots for:

- terminal payoff;
- CRR convergence against the analytic reference;
- Monte Carlo valuation across path counts with 95% uncertainty bounds;
- one selected Greek against spot, comparing analytic and finite-difference methods where supported.

### Results

The result surface preserves method specificity. Common valuation rows may display `present_value`, but Monte Carlo uncertainty remains owned by `MonteCarloValuationResult` and is surfaced only when that concrete result exists.

The comparison table therefore keeps separate:

```text
analytic reference
CRR approximation/discretization evidence
Monte Carlo sampling evidence
```

The sensitivity table is a separate workflow over `BlackScholesSensitivityProblem` and compares analytic versus finite-difference Delta, Gamma, Vega, Theta, and Rho. Greeks are not fields on `ValuationResult`.

### Validate

The Workbench keeps these questions distinct:

```text
mathematically meaningful
!= implemented
!= supported by selected method/configuration
!= validated
!= Workbench-exposed
```

Compatibility authority remains in Python and ultimately delegates to the production method support boundary. In particular, a structurally valid Black-Scholes pricing problem can be unsupported by a coarse CRR configuration when the finite-tree risk-neutral probability condition fails.

Finite-difference diagnostics retain unsupported domain-crossing bumps explicitly. The UI does not silently clip a bump or switch to a different differentiation scheme.

### Present / Export

UI2 records numerical provenance needed to interpret its evidence:

- normalized pricing inputs;
- selected valuation method and method configuration;
- Monte Carlo path count and seed;
- finite-difference bump configuration;
- sensitivity method identity;
- explicit evidence/error semantics.

Market-observation/provider provenance is intentionally absent from UI2 and belongs to M4. General file/report export remains future product work.

## Renderer-neutral plotting values

UI1 had one payoff-series consumer. UI2 adds multiple real plot consumers, so a small shared renderer-neutral plotting contract is now earned:

```text
PlotData
└── PlotSeries
    └── PlotPoint(x, y, optional lower/upper)
```

The abstraction intentionally contains only responsibilities shared by the concrete payoff, convergence, uncertainty, and Greek plots:

- labels;
- numeric x/y points;
- optional paired vertical uncertainty bounds.

Styling, pixel transforms, legends, themes, interaction, and Qt objects remain renderer-owned. This is not a universal visualization grammar, plugin system, or chart schema.

## Execution boundary

UI1 established a local `QThread` worker. UI2 reuses that ownership pattern for a concrete M2 analysis request:

```text
immutable M2WorkbenchRequest
        ↓
_M2Worker.run()
        ↓
run_m2_workbench(...)
        ↓
immutable M2WorkbenchAnalysis
        ↓
controller-owned presentation
```

Monte Carlo supplies real longer-running pressure for this boundary, but UI2 still does not justify a universal scheduler, job registry, task graph, persistence system, cancellation framework, or progress protocol.

## Quantitative ownership

The application layer orchestrates already-merged public M2 APIs. It does not reimplement their mathematics.

Valuation plurality is:

```text
same M1 PricingProblem
        ├── BlackScholesClosedForm
        ├── CoxRossRubinstein
        └── MonteCarloEuropeanOption
```

Sensitivity remains separate:

```text
BlackScholesSensitivityProblem
        ├── AnalyticBlackScholesSensitivity
        └── FiniteDifferenceBlackScholesSensitivity
        ↓
BlackScholesSensitivityResult
```

UI2 generates convergence and curve evidence by constructing fresh immutable requests/problems. It does not mutate a committed pricing problem in place.

## Error and evidence semantics

The desktop presentation must preserve the M2 distinctions:

```text
financial-model limitation
!= CRR approximation/discretization error
!= Monte Carlo sampling uncertainty
!= finite-difference truncation error
!= finite-difference cancellation / floating-point error
```

A generic `error` field would erase quantitative meaning and is intentionally absent.

## UI3 — dynamic hedging and observed-market inference

UI3 adds a workflow home that asks the mathematical question before choosing a screen:

```text
Valuation & Sensitivity
Dynamic Hedging / Control
Market Evidence / Implied Volatility
```

The existing UI2 valuation workspace remains intact. The two new workspaces are concrete downstream adapters over M3 and M4 rather than a universal workflow schema.

### Dynamic hedging

The application layer constructs an immutable hedge request from the existing Black-Scholes financial composition plus explicit generating volatility, hedge-assumed volatility, rebalance cadence, seed, replicate count, and proportional transaction-cost rate. It preserves M3's zero-continuous-dividend execution boundary.

One selected trajectory remains distinct from replicate evidence. Rebalance-frequency, volatility-misspecification, and transaction-cost comparisons reuse the same generated seeded paths across conditions, so displayed differences are controlled comparisons rather than unrelated Monte Carlo draws. QML receives only prepared path rows, aggregate rows, inspector values, and renderer-neutral plots; it never recomputes Delta, financing, trades, costs, payoff, or replication error.

The hedging mathematical inspector remains concrete:

```text
State
Generating law
Sensitivity source
Control policy
Rebalance schedule
Financing / transaction-cost convention
Replication objective / error
```

### Market evidence and implied volatility

The market workspace keeps the M4 lifecycle visible:

```text
raw observation + provenance
        ↓
explicit normalization
        ↓
normalized observed target
        ↓
Black-Scholes implied-volatility problem
        +
bracketed bisection method
        ↓
immutable inverse result + conditioning evidence
```

Synthetic deterministic M4 observations support the runnable raw-to-normalized-to-inferred laboratory. Invalid normalization remains explicit. Financial inconsistency, failure to bracket the admissible volatility domain, numerical convergence evidence, and poor inverse conditioning remain different concepts. Vega, local inverse price-to-volatility sensitivity, and first-order half-spread volatility shift come from authoritative M4 results.

The historical SPX panel is deliberately **derived empirical evidence only**. UI3 renders the pinned M4 strike/maturity implied-volatility and conditioning evidence plus source/non-redistribution provenance; it does not fabricate or redistribute upstream raw SPX rows that M4 intentionally did not retain. Static monotonicity/convexity findings remain diagnostics, not surface repair.

The inverse-problem mathematical inspector is likewise concrete:

```text
Observed target
Forward model
Unknown parameter
Admissible domain
Inverse method
Conditioning evidence
```

### UI3 execution and presentation boundary

UI3 reuses the narrow QThread ownership pattern for one immutable M3 hedge request and one bundled M4 evidence request. It does not add cancellation, queues, progress protocols, a scheduler, or a generic job registry.

The existing `PlotData -> PlotSeries -> PlotPoint` value seam is sufficient for hedge time series, replicate/frequency evidence, discrete implied-volatility slices, and conditioning plots. Synchronized row selection remains a concrete controller/presentation responsibility. No universal visualization grammar is introduced.

M5 Heston pricing is merged but intentionally not surfaced by UI3. The next desktop milestone must consume actual merged M5/M6 contracts rather than retrofitting Heston or calibration semantics into UI3.

## Packaging and validation

PySide6 remains an optional desktop dependency. The canonical core gate stays Qt-independent.

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

- pinned PySide6;
- desktop Ruff and strict Pyright;
- application/presentation/controller behavior;
- dependency direction;
- QML load and offscreen startup;
- standalone `pyside6-deploy` build;
- packaged offscreen launch smoke.

## Extension rule

Future UI milestones consume only capabilities actually merged on `main`.

Do not infer a generic framework from the Workbench vocabulary. In particular UI2 does not create:

- a valuation-method registry/plugin architecture;
- a universal Problem/Method/Result UI schema;
- reflection-driven forms;
- a generic sensitivity framework;
- a generic job system;
- a universal plot grammar;
- M3 control panels;
- M4 market-data/implied-volatility panels;
- Heston/calibration panels.

The intended growth rule remains:

```text
merged quantitative capability
        ↓
concrete frontend-neutral application/presentation semantics
        ↓
curated controller values/actions
        ↓
QML presentation
```
