# UI5 — Validation, Model Risk & Product Hardening

## Status

UI5 consumes the merged M7 validation/model-risk specialization and the merged M8 performance-engineering evidence.

The product story is deliberately evidence-ordered:

```text
financial/model question
        ↓
M7 fair model comparison
        ↓
held-out validation + model-risk limits
        ↓
M8 representative workload profiling
        ↓
measured Python/algorithmic optimization
        ↓
measured negative C++ decision for v0.1
```

The Workbench presents those layers without turning validation, benchmarking, reporting, persistence, or native execution into speculative universal frameworks.

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
public M7 validation APIs + committed M8 derived evidence
        ↓
production quantitative core
```

QML does not calculate fits, residuals, objectives, metrics, conditioning, partitions, speedups, parity, or model-risk conclusions.

## Validation and model-risk surfaces

UI5 makes the following questions first-class where M7 actually supports them:

- training fit versus held-out evaluation;
- aggregate Black-Scholes versus Heston pricing metrics;
- contract-level residual structure by log-forward moneyness;
- held-out absolute pricing error;
- Heston multiple-start stability and local conditioning;
- train-to-full-sample Heston coordinate movement;
- bounded M7 conclusions and explicit non-claims.

Protect:

```text
training fit != held-out evaluation
same-date cross-sectional holdout != temporal forecasting
better held-out pricing != universal model validity
optimizer convergence != parameter identification
Heston pricing advantage != Heston hedging advantage
conditioning != posterior uncertainty
measured runtime != model quality
faster implementation != different financial semantics
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

## M8 performance evidence

M8 profiles the six representative workloads predeclared by M7:

1. one Black-Scholes closed-form valuation;
2. one Heston Fourier valuation;
3. one seeded Heston Monte Carlo valuation;
4. the 10-target / 3-start Heston training calibration;
5. the 14-target / 3-start Heston stability calibration; and
6. the complete M7 validation study.

UI5 uses a package-safe frontend-neutral mirror of the committed derived artifact at `docs/evidence/m8_performance_reference.json`. Tests cross-check the mirror against the repository artifact so the installed Workbench cannot silently diverge from the durable evidence.

The pinned same-run reference reports:

| Workload | Frozen M7 baseline | M8 optimized | Interpretation |
| --- | ---: | ---: | --- |
| Black-Scholes scalar | 0.000002083 s | 0.000002272 s | scalar reference; no speedup claim |
| Heston Fourier scalar | 0.000749 s | 0.000818 s | scalar reference; no speedup claim |
| Heston MC, 20k × 252 | 3.367340 s | 0.122980 s | **27.38×** measured speedup |
| 10-target / 3-start calibration | 2.291878 s | 0.497131 s | **4.61×** measured speedup |
| 14-target / 3-start calibration | 3.275181 s | 0.545352 s | **6.01×** measured speedup |
| complete M7 validation | 5.413631 s | 1.081868 s | **5.00×** measured speedup |

Hosted wall-clock timings are descriptive evidence, not CI thresholds. The two scalar references were intentionally not optimization targets, so their microsecond/sub-millisecond differences are not presented as regressions or speedup claims.

### Correctness / parity

M8 retains deterministic parity for Black-Scholes scalar value, scalar Heston Fourier value, calibration objectives, and M7 held-out RMSE evidence.

Heston Monte Carlo changed from scalar Python RNG/path work to a local NumPy `PCG64(seed)` generator and vectorized path propagation. Old and new random streams are therefore not expected to match sample-for-sample. The committed comparison is statistical:

```text
old/new present-value difference
≈ 0.853 combined standard errors
< explicit 4-SE comparison bound
```

UI5 states this distinction explicitly. Equal integer seeds do not imply identical pre-M8/post-M8 random streams.

### Measured native decision

M8 did **not** add C++.

This is a measured negative decision, not a missing implementation. Python/NumPy changes removed enough of the actual measured cost that a compiler/binding/toolchain surface, cross-platform native packaging, additional parity obligations, and reduced audit simplicity are not justified for the current v0.1 representative workloads.

UI5 therefore exposes no fake backend selector and no disabled C++ option for visual symmetry.

Future materially larger path, surface, portfolio, calibration, or scenario workloads may reopen the question only after fresh profiling.

## Long-running operations

The M7 validation method exposes no progress stream and no cancellation protocol.

UI5 therefore uses the existing one-active-QThread ownership model and exposes a truthful busy state only:

```text
running
!= known percent complete
!= cancellable
```

No pseudo progress, estimated completion percentage, task graph, scheduler, or cancellation framework is introduced.

The M8 improvements reduce the representative M7 study's runtime, but they do not retroactively create progress/cancellation semantics.

## Product hardening

UI5 adds concrete product improvements without creating a generic desktop framework:

- keyboard launch shortcuts and workspace shortcuts;
- explicit accessibility names for primary actions and evidence/report surfaces;
- deterministic focus navigation on principal launch/run controls;
- resizable layouts that collapse comparison grids at narrower widths;
- explicit empty, running, result, warning and existing execution-error states;
- clear visual distinction between validation evidence, unsupported scientific claims, and computational evidence;
- a validation-first shell while preserving UI1–UI4 as the research-workbench library;
- a concrete copy/select evidence report combining already-owned M7 and M8 evidence;
- process-isolated Qt controller tests to avoid native QObject/QThread lifetime contamination across unrelated test cases;
- continued `pyside6-deploy` standalone packaging, packaged-launch smoke, and artifact-upload verification in Desktop CI.

## Persistence, comparison, fork and export boundaries

UI5 deliberately does not invent a generic saved-project model merely to satisfy product vocabulary.

The concrete M7 workflow itself is already a controlled study comparison: Black-Scholes and Heston are fit on the same training partition, frozen, and evaluated on the same held-out contracts. The Workbench exposes that comparison directly.

The repository still has no authoritative persisted `Study`/workspace/document identity with serialization/versioning semantics. Therefore generic save/open/fork infrastructure would be premature and could freeze the wrong product model. The same applies to a generic report-document framework and arbitrary file-export subsystem.

UI5 provides the concrete export that is already earned: a selectable/copyable evidence report over immutable M7/M8 values.

## Packaging and platform boundary

UI5 continues the repository's real packaging proof:

```text
source launch
→ pyside6-deploy standalone build
→ packaged offscreen launch smoke
→ uploaded executable artifact
```

That proves the maintained CI platform can produce and launch the native Workbench. It does **not** claim macOS/Windows release certification, signing, notarization, installers, update channels, or end-user distribution guarantees.

Those are M9 release-target questions and should be implemented only after M9 chooses concrete supported platforms and distribution requirements.

## UI5 completion gate

UI5 is complete only when:

1. the M7 validation/model-risk workspace runs the authoritative M7 contracts;
2. the merged M8 reference is presented with revision/environment provenance, before/after measurements, parity semantics, and the no-C++ decision;
3. unsupported Heston hedging, temporal forecasting, posterior uncertainty, backend-selection, and runtime-threshold claims remain explicit non-claims;
4. Core and Desktop quality gates pass on the exact final head;
5. QML load, source launch, standalone deployment, packaged launch and artifact upload pass;
6. the branch is reconciled to current `main` with no unresolved review threads; and
7. the squash-merged `main` result is reverified before M9 begins.
