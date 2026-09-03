# Architecture Decision Records

## Purpose

Architecture Decision Records (ADRs) preserve the rationale for durable, consequential decisions that would otherwise be difficult to reconstruct from code, tests, `AGENTS.md`, the architecture index, or the quantitative-convention register.

ADRs are historical decision records, not a second roadmap and not a place for routine implementation notes.

## When to create an ADR

Create one when a decision is:

- architecturally or quantitatively consequential;
- expected to constrain multiple future implementations;
- based on meaningful alternatives/tradeoffs;
- difficult to infer later from the resulting code alone;
- expensive or risky to reverse without understanding the original rationale.

Examples that may justify future ADRs:

- a durable market-environment/discounting boundary after real consumers establish it;
- a project-wide date/year-fraction convention with important tradeoffs;
- a stable calibration ownership boundary;
- a native Python/C++ execution boundary once a real second implementation exists.

## When not to create an ADR

Do not create one for:

- ordinary refactors;
- naming choices obvious from local code;
- temporary implementation details;
- speculative future architecture;
- every dependency or library choice;
- ticket-level status or roadmap sequencing;
- quantitative choices that are intentionally local to one study/method.

## Lifecycle

ADRs should use a simple status such as:

```text
Proposed
Accepted
Superseded
Rejected
```

Once accepted, preserve the historical record. If the project changes direction, create a new ADR that supersedes the old one rather than rewriting history to make the old decision appear different.

## Naming

Use sequential files once the first real ADR is needed:

```text
0001-short-decision-name.md
0002-next-decision.md
```

The repository intentionally contains only a template today; M0 did not create enough concrete finance consumers to justify historical ADRs yet.

## Template

Copy [`_template.md`](_template.md) and remove sections that genuinely do not apply. Keep enough context that a future contributor can understand the decision without the original chat.
