# Research and multi-surface interfaces

## F1 audit and decision

The production packages already expose typed mathematical problems, methods,
results and domain errors. `qf_platform.application.__init__` already exports
concrete comparison/research workflows covering M1–M8. Those workflows contain
no Qt import and preserve the quantitative core as the calculation authority.
`qf_platform.presentation` separately builds renderer-neutral rows/plots.

| Audited surface | Existing responsibility | F1 decision |
| --- | --- | --- |
| `pricing`, `sensitivity`, `control`, `market_data`, `inference`, `validation` | Typed custom problems, methods, normalization and immutable results | Retain public package exports as the custom-research API |
| `application.black_scholes_study` | Optional text-to-domain composition | Document direct numeric composition alongside draft normalization |
| `application.m2_workbench` | Valuation/Greek comparison and convergence studies | Re-export six nested evidence types through `application`; preserve identities |
| `application.ui3_hedging`, `ui3_market` | Paired replication studies and raw-to-inferred market outcomes | Document existing public requests/configuration/results |
| `application.ui4_heston` | Heston method comparison and fixed synthetic calibration experiments | Keep concrete; distinguish these studies from arbitrary domain calibration |
| `application.ui5_validation` | Packaged derived-reference M7 validation plus workload lineage | Keep replay provenance explicit; custom validation remains domain composition |
| `application.ui5_performance` | Package-safe mirror of committed M8 timings | Expose recorded evidence, never present as a new measurement |
| `presentation` | Rows, labels and renderer-neutral plots | Optional downstream view; preserve raw numerical evidence separately |
| `desktop` | Qt controller, worker lifetime, QML interaction/rendering | Remains a sibling consumer; no migration needed |

A new `qf_platform.research` package would merely duplicate these imports or add
another orchestration layer with no distinct responsibility. F1 therefore adds
no façade, generic runner, registry, parameter dictionary or renaming migration.
The M2 exports close an actual annotation/discovery gap for evidence consumers.
Historical UI-prefixed names remain supported and Qt-independent.

## Dependency and ownership contract

```text
public quantitative core / immutable evidence
                    ↓
frontend-neutral application orchestration
                    ↓
Python studies / Jupyter / exports / Dash / Qt
```

`presentation` is an optional downstream adapter over quantitative/application
values. Neither the core nor application imports it. Clients may use domain
APIs directly for custom questions, application studies for existing comparisons,
and presentation builders for rendering. They must not use Qt controllers as
research services or feed rounded labels back into numerical calculations.

- Problems own financial meaning; methods own numerical settings.
- Application requests select concrete studies and retain inspectable typed
  inputs. Drafts represent transient text, not financial state.
- Completed domain/application results remain frozen value objects. F1 exports
  reference the same classes that existing Qt code already consumes.
- Scripts and future notebooks own research composition and narrative; domain
  formulas stay in the production library.
- Exporters own schemas/formatting; Dash and Qt own interaction, rendering and
  their execution lifecycle. They consume full-precision evidence and explicit
  failures rather than reconstructing metrics from displayed strings.
- Seeds, financial inputs, method settings and provenance remain explicit at
  their existing boundaries. F1 adds no cache, mutable singleton or global RNG.

Application request dataclasses are not a new generic validation framework.
For untrusted text, use the existing normalization helpers; typed custom callers
must satisfy the documented domain and study preconditions. Individual methods
retain their own capability checks. Curated studies have fixed research designs
and may do more work than a single domain evaluation.

## Independent follow-on seams

| Milestone | Shared inputs | Client-owned work | Must not depend on |
| --- | --- | --- | --- |
| F2 | Public domain/application APIs and F1 guide/examples | Notebook narrative, explicit study configuration, reproducible execution | Dash sessions, Qt controller, F3 formatting |
| F3 | Typed requests/results and provenance | Numeric export schema and file formatting | Notebook cells or Qt presentation strings as numerical authority |
| F4 | Public domain/application APIs; optional presentation values | Dash layout, session state, concrete execution adapter | Qt worker objects, notebook execution or new finance formulas |

These boundaries permit evaluating parallel work after F1's verified merge;
they do not override live overlap checks or authorize starting blocked work.

## Validation evidence

F1 adds executable Python consumers for every required workflow family.
Tests compare representative results to production evaluators and committed
reference scales, preserve result immutability and check meaningful provenance
and model-risk distinctions. Existing numerical/convergence/financial tests
remain authoritative; wrapper agreement alone is not independent validation.

Fresh subprocesses run every example from an unrelated working directory with
an import hook that rejects attempted Qt/desktop and other optional frontend
imports. A negative control proves the guard actually rejects imports. Public
`__all__` names are resolved in the same guarded process. Static checks restrict
example imports to public package surfaces and protect the application →
presentation/client boundary. Existing desktop dependency tests remain in place.

The canonical gate type-checks the examples as well as the production code and
tests. A clean, non-editable base-package install is additionally used for F1
handoff evidence, so source-path import accidents do not establish readiness.
Exact commands, head SHA and CI results belong in the PR checkpoint.

## Navigation

- [Python API and runnable examples](../research/python_api.md)
- [Native Workbench](native_quant_workbench.md)
- [Architecture index](index.md)
- [Quantitative conventions](../quantitative_conventions.md)


## F2 notebook execution boundary

F2 makes Jupyter a concrete sibling client of the F1 boundary:

```text
committed output-free notebook
        ↓
public qf_platform application/domain APIs
        ↓
immutable quantitative result/evidence
        ↓
notebook-owned Markdown tables and Matplotlib figures
```

The notebooks own research composition and narrative only. They do not own
finance formulas, calibration/validation algorithms, persistent quantitative
state, or hidden data acquisition. The default studies use explicit seeds and
package-safe committed/derived evidence, so automated execution requires no
network or Qt runtime.

Committed `.ipynb` files deliberately retain no execution counts or outputs.
`scripts/check_notebooks.py` executes them in memory under the optional
`research` dependency set, while core tests statically protect the flagship set,
public-import direction, output-free contract, and important model-risk
non-claims. This keeps notebook diffs stable without weakening executable
verification.


## F3 structured reporting boundary

F3 adds another concrete sibling client downstream of the F1 application/domain
contracts:

```text
typed quantitative result/evidence
            ↓
concrete workflow report adapter
            ↓
limited tabular report values
            ↓
XLSX / CSV / JSON
```

The shared `ReportField` / `ReportColumn` / `ReportTable` / `TabularReport`
values exist only because the M2, M3, M4, M6, and M7/M8 exporters share the same
small rectangular-export responsibility. They are not an arbitrary-object
serializer, dataframe layer, formula language, workflow engine, or quantitative
result hierarchy.

Concrete adapters read existing immutable evidence and copy source values into
explicit schemas. They do not import or invoke pricing, sensitivity, hedge,
inference, calibration, or validation execution functions. Units, assumptions,
provenance, partitions, conditioning, and non-claims travel with the exported
evidence rather than being inferred from spreadsheet formatting.

CSV and JSON are supported by the base reporting package with standard-library
dependencies. XLSX rendering lazily imports the optional `reporting` dependency,
so OpenPyXL does not become a quantitative-core dependency. Workbooks contain
values rather than financial formulas, and generated binaries are temporary
artifacts rather than committed authorities.

The flagship validation report intentionally keeps training evidence, held-out
evidence, residuals, calibration starts, parameter stability, conditioning,
provenance, model-risk limitations, and revision-pinned M8 performance evidence
in separate tables/sheets.
