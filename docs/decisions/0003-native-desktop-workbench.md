# ADR 0003: Native Desktop Workbench with PySide6 and Qt Quick/QML

## Status

Accepted

## Context

The platform now has a complete first pricing specialization on merged M1. A desktop product can therefore be proven against real mathematical-finance APIs rather than invented around placeholders.

The product goal is an interactive, compositional Quant Research Workbench that remains downstream of the quantitative core. The UI must support transient editing, inspectable mathematical semantics, responsive execution, and eventual standalone distribution without allowing frontend technology to redefine financial meaning.

A separate Evolution Simulation Engine project independently demonstrated a PySide6 + Qt Quick/QML architecture with a curated Python/QML boundary, optional desktop dependency, offscreen QML smoke tests, narrow worker-thread execution, and standalone deployment. Those software lessons are transferable; its domain abstractions are not.

## Decision

Use PySide6 with Qt Quick/QML for the native Quant Research Workbench.

The dependency direction is:

```text
Qt Quick / QML
        ↓
curated PySide6 controller
        ↓
frontend-neutral application / presentation semantics
        ↓
public quantitative APIs
        ↓
production quantitative core
```

The finance core must remain Qt-independent.

Only deliberately curated values cross the QML boundary. Production finance-domain graphs remain private to Python. Interactive draft values are normalized in Python into authoritative typed production objects before execution.

PySide6 is an optional desktop dependency. Desktop-specific typing, QML loading, startup smoke, and packaging are validated in a dedicated CI surface rather than making Qt part of the canonical core environment.

Execution crosses a small worker/thread boundary. UI1 uses a single `QThread` adapter around the authoritative pricing call. This establishes non-GUI-thread ownership without creating a generic job framework.

Renderer-neutral presentation values may be introduced when a real frontend consumer needs them, but quantitative results and evidence remain owned by production/application semantics rather than Qt chart objects or QML calculations.

## Consequences

Positive consequences:

- the project gains a real downloadable/native product direction rather than a dashboard-only interface;
- QML can focus on interaction and visual composition while Python owns mathematical normalization and execution;
- the production library remains reusable from scripts, research studies, tests, and future frontends;
- Qt-specific dependencies and validation remain isolated;
- future longer-running methods can reuse the already-established asynchronous ownership boundary without inheriting GUI-thread coupling.

Costs and constraints:

- the repository now has a second validation environment for optional desktop dependencies;
- PySide6/QML boundary code requires deliberate typing and lifecycle management;
- packaging is platform-sensitive and must be validated explicitly;
- the frontend cannot rely on arbitrary Python-object introspection and therefore needs curated presentation contracts.

## Rejected alternatives

### Web/dashboard frontend as the primary product architecture

Rejected for this milestone because the target product is a downloadable native research workbench, not a browser dashboard. A web frontend may be considered later only for a demonstrated product need.

### Qt Widgets as the primary UI layer

Rejected because Qt Quick/QML better matches the intended compositional, visually rich workbench direction while retaining a narrow Python boundary.

### Expose production domain objects directly to QML

Rejected because it would couple frontend rendering to quantitative object structure, encourage QML-side business logic, and make future API evolution harder to control.

### Generic job framework in UI1

Rejected because one analytic pricing vertical does not justify scheduler, registry, cancellation, persistence, or task-graph abstractions. The QThread adapter is intentionally local and replaceable.

### Reflection-driven UI / generic form generation

Rejected because one Black-Scholes composition does not justify a universal schema or capability registry, and reflection would make implementation structure rather than mathematical product semantics the user-facing vocabulary.

## Guardrails

- QML does not own financial formulas, payoff logic, day count, discounting, compatibility, or validation decisions.
- `qf_platform.pricing` and lower quantitative packages do not import PySide6, Qt, QML, or `qf_platform.desktop`.
- UI-facing draft/configuration state is not an authoritative quantitative result.
- Qt objects are never the authoritative representation of valuation results or validation evidence.
- Future Workbench extensions consume only capabilities already merged on `main`.
- No generic UI framework should be extracted until repeated concrete consumers prove a shared responsibility.
