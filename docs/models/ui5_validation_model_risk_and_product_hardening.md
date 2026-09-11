# UI5 — Validation, Model Risk & Product Hardening

## Status

UI5 is intentionally staged across M7 and M8.

- **Phase A** consumes merged M7 validation/model-risk evidence and hardens the native product around scientific comparison, accessibility, keyboard use, resizable layouts, explicit empty/running/error/result states, and a concrete copyable evidence report.
- **Phase B** may add measured performance/native-backend presentation only after M8 produces authoritative profiling/parity evidence.

UI5 must finish before M9, but it must not invent M8 or M9 conclusions merely to fill a product surface.

## Central scientific story

```text
BLACK-SCHOLES              HESTON
      │                       │
      └──────────┬────────────┘
                 ▼
            VALIDATION
```

The native validation workspace runs the actual production M7 composition:

```text
NormalizedOptionObservation(s)
+ predeclared TRAINING / EVALUATION partition
+ fixed financial inputs
+ Black-Scholes fit domain
+ Heston calibration domain / Fourier forward map
        ↓
BlackScholesHestonValidationProblem
        +
CrossSectionalBlackScholesHestonValidation
        ↓
BlackScholesHestonValidationEvidence
```

The desktop remains downstream:

```text
Qt Quick / QML
        ↓
curated PySide6 controller / item models
        ↓
frontend-neutral UI5 application + presentation adapters
        ↓
public M7 validation API
        ↓
production quantitative core
```

QML does not calculate fits, residuals, objectives, metrics, conditioning, partitions, or model-risk conclusions.

## Phase-A evidence surfaces

UI5 makes the following questions first-class where M7 actually supports them:

- training fit versus held-out evaluation;
- aggregate Black-Scholes versus Heston pricing metrics;
- contract-level residual structure by log-forward moneyness;
- held-out absolute pricing error;
- Heston multiple-start stability and local conditioning;
- train-to-full-sample Heston coordinate movement;
- bounded M7 conclusions and explicit non-claims;
- the representative M8 workload definitions and structural work counts.

Protect:

```text
training fit != held-out evaluation
same-date cross-sectional holdout != temporal forecasting
better held-out pricing != universal model validity
optimizer convergence != parameter identification
Heston pricing advantage != Heston hedging advantage
conditioning != posterior uncertainty
structural workload evidence != measured runtime
measured runtime != model quality
```

## Hedging boundary

UI5 does not manufacture a Black-Scholes-versus-Heston hedge comparison.

M3 owns a real Black-Scholes/GBM dynamic-Delta hedge experiment. M7 explicitly records that the production backend does not yet own the Heston path + Heston Delta + hedge-accounting composition needed for a fair Heston hedge comparison.

The validation workspace therefore states:

```text
Heston held-out pricing advantage
!= demonstrated Heston hedging advantage
```

The established M3 hedging workspace remains available through the UI1–UI4 research-workbench library as contextual evidence only.

## M8 handoff

M7 defines six representative profiling workloads:

1. one Black-Scholes closed-form valuation;
2. one Heston Fourier valuation;
3. one seeded Heston Monte Carlo valuation;
4. the 10-target / 3-start Heston training calibration;
5. the 14-target / 3-start Heston stability calibration; and
6. the complete M7 validation study.

UI5 Phase A may display those workload definitions and structural evaluation counts. It must not display runtime bars, speedups, memory comparisons, a C++ backend selector, or native-backend superiority until M8 measures and validates them.

If M8 concludes that no native acceleration is warranted, UI5 should present that outcome honestly rather than invent a C++ path for product symmetry.

## Long-running operations

The M7 validation method exposes no progress stream and no cancellation protocol.

UI5 therefore uses the existing one-active-QThread ownership model and exposes a truthful busy state only:

```text
running
!= known percent complete
!= cancellable
```

No pseudo progress, estimated completion percentage, task graph, scheduler, or cancellation framework is introduced.

## Product hardening earned in Phase A

The validation-first shell adds concrete improvements without creating a generic desktop framework:

- keyboard launch shortcuts and workspace shortcuts;
- explicit accessibility names for primary actions;
- deterministic focus navigation on the principal launch/run controls;
- resizable layouts that collapse comparison grids at narrower window widths;
- explicit empty and running states;
- bounded warning states for unsupported scientific claims;
- the existing status/error boundary for execution failures;
- a copy/select report surface generated from already-owned immutable evidence values;
- continued standalone `pyside6-deploy` packaging verification through Desktop CI.

The existing UI1–UI4 workflows remain available unchanged as the research-workbench library.

## Deliberately deferred product work

UI5 Phase A does **not** claim completion of features for which the platform still lacks an owned product/data contract:

- generic project/workspace persistence;
- generic saved-study/fork semantics;
- a generic report generator or document model;
- arbitrary file export infrastructure;
- cross-platform installer/signing/notarization guarantees;
- Windows/macOS release certification;
- native-backend controls or measured runtime presentation;
- progress/cancellation without a backend contract.

Those concerns should be implemented only when M8/M9 or a concrete study/document persistence model creates real consumer pressure.

## Completion gate

UI5 is not fully complete until:

1. the M7-backed Phase-A workspace and product hardening pass Core/Desktop exact-head and merged-main verification;
2. M8 is merged;
3. UI5 is reconciled against M8's measured performance/parity evidence;
4. only the performance/release presentation genuinely earned by M8 is added; and
5. the final UI5 head again passes Core/Desktop, standalone deployment, packaged launch, and artifact upload before M9.
