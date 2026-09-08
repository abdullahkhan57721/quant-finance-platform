# Native Quant Research Workbench

## Status

UI1 establishes the first native desktop product architecture for the Quantitative Finance Research & Validation Platform.

The implemented proof is intentionally narrow: a European option / Black-Scholes study using the already-merged M1 quantitative semantics. It proves the desktop boundary without turning the UI into a second quantitative authority.

## Dependency direction

The durable direction is:

```text
Qt Quick / QML
        ↓
curated PySide6 controller
        ↓
frontend-neutral application + presentation semantics
        ↓
M0A/M1 public mathematical-finance APIs
        ↓
production quantitative core
```

The reverse dependency is forbidden. The pricing core does not import PySide6, Qt, QML, or `qf_platform.desktop`.

## Boundary rule

Values cross the QML boundary; finance-domain object graphs do not.

QML receives only deliberately exposed:

- scalar properties;
- signals;
- slots/actions;
- Qt item models containing renderer-neutral rows;
- serialized renderer-neutral payoff samples.

The Python controller may privately retain committed `PricingProblem` and `ValuationResult` objects. QML never receives arbitrary contracts, stochastic laws, parameters, numeraires, pricing-measure objects, or valuation-result graphs.

## Draft state and committed financial state

Interactive editing requires temporarily incomplete or invalid values. Therefore:

```text
QML/transient text inputs
        ↓
BlackScholesStudyDraft
        ↓
Python normalization + M1 domain validation
        ↓
BlackScholesStudyComposition
        ↓
immutable M1 PricingProblem + selected method
```

`BlackScholesStudyDraft` is deliberately text-valued. It is not financial state. A successful composition creates fresh M1 objects using the same date, spot, strike, volatility, money-market rate, continuous carry, option-right, numeraire, pricing-measure, and method semantics used by the production library.

Guided and Advanced disclosure are two views of the same composition. They do not normalize into different quantitative models.

## UI1 product slice

The native shell exposes the product concepts:

```text
HOME
├── New Study
├── Open Study
└── Examples

STUDY
├── Compose
├── Analyze
├── Results
├── Validate
└── Present / Export

Run / Price = action
```

UI1 does not create a Python class hierarchy matching these labels. Only the Black-Scholes vertical is deeply implemented; inactive product concepts remain shell/navigation affordances rather than speculative frameworks.

## Mathematical inspector

The frontend-neutral presentation layer exposes read-only rows for:

- State;
- Stochastic law;
- Parameters;
- Contract / payoff;
- Numeraire;
- Pricing-measure semantics;
- Pricing problem;
- Valuation method;
- assumptions / conventions;
- validation status.

These values are derived in Python from the normalized M1 composition. QML performs no Black-Scholes formula, payoff, discounting, day-count, compatibility, parity, or no-arbitrage calculation.

## Compatibility semantics

UI1 keeps five product questions separate:

```text
mathematically meaningful
!= implemented
!= supported by selected method
!= validated
!= Workbench-exposed
```

For UI1 only one deep valuation method is exposed: `BlackScholesClosedForm`. Method support is obtained from the production method's support boundary in Python. QML renders the resulting status; it is not a capability registry.

Future methods should extend application semantics only after they exist on merged `main`. UI1 contains no speculative CRR, Monte Carlo, sensitivity, calibration, or Heston adapters.

## Presentation semantics

`qf_platform.presentation` contains concrete renderer-neutral values required by this slice:

- labeled inspector/evidence rows;
- terminal payoff sample points;
- compact M1 validation evidence.

The payoff curve uses the production `EuropeanOption.cash_flows(...)` contract semantics rather than duplicating payoff formulas in QML.

The result surface displays the immutable `ValuationResult.present_value` produced by the public M1 evaluation path. Additional UI1 evidence includes method-support status, put-call parity evidence, and discounted no-arbitrage bounds derived in Python from the same committed M1 semantics.

These contracts are concrete to the Black-Scholes vertical. They are not a universal visualization grammar.

## Execution boundary

Pricing is submitted through a deliberately small `QThread` worker adapter:

```text
immutable BlackScholesStudyComposition
        ↓
_PricingWorker.run()
        ↓
evaluate(problem, method)
        ↓
ValuationResult signal
        ↓
controller-owned committed result/presentation
```

The M1 analytic call is cheap, but this boundary prevents GUI-thread ownership from becoming architectural precedent for later Monte Carlo or calibration work.

This is not a generic scheduler, job registry, cancellation framework, or task system. A broader execution abstraction must be earned by later concrete workloads.

## Packaging and validation

PySide6 is an optional desktop dependency, pinned independently of the core development environment.

Source launch after installing the desktop extra:

```text
python -m pip install -e ".[dev,desktop]"
python -m qf_platform.desktop.main
```

Headless source smoke:

```text
QT_QPA_PLATFORM=offscreen python -m qf_platform.desktop.main --smoke-test
```

The dedicated Desktop CI surface verifies:

- the pinned PySide6 runtime;
- desktop Ruff and strict Pyright checks;
- application/presentation/controller tests;
- dependency direction;
- QML load and offscreen source startup;
- a `pyside6-deploy` standalone build on Ubuntu;
- offscreen launch smoke of the packaged executable.

The canonical core `./scripts/check_all` remains Qt-independent.

UI1 deliberately does not include signing, notarization, installers, or a cross-platform release matrix.

## Extension rule

When a later quantitative milestone is merged, extend the Workbench from actual public contracts on `main`.

Do not pre-build empty panels, fake result types, reflection-driven forms, universal study schemas, generic compatibility registries, or generalized worker frameworks in anticipation of future methods.

The intended evolution is:

```text
merged quantitative capability
        ↓
concrete frontend-neutral composition/result semantics
        ↓
curated controller values/actions
        ↓
QML presentation
```

Repository truth remains authoritative for every extension.
