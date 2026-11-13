# Operate and report evidence

## Readiness

| Level | Evidence required |
|---|---|
| Specified | Contracts and narrative exist |
| Offline verified | Behavior tests and deterministic walkthrough pass |
| Protocol verified | MCP stdio initialization, discovery, call and error checks pass |
| Client verified | Actual selected client discovers skills/tools and completes the rehearsal |
| Live connected | Authenticated reads from the confirmed tenant and record scope succeed |
| Live action verified | Authorized mutation and exact read-back succeed |
| Presenter ready | Live happy path, failure path, human gate, uncertain completion, and reset rehearsed |

A local test, diagram, or mock receipt does not establish a live deployment. CI files are configuration until a CI run passes. Publication is a separate action.

## Offline walkthrough and reset

Run `python scripts/demo.py`. It returns deterministic synthetic evidence, an unapplied proposal, and a held signature-readiness result. Nothing is saved to a remote service or mutated in the fixture. Rerun to reset. Rebuild docs with `python scripts/build_deliverables.py`; verify them with `--check`.

The self-contained presenter entry point is `docs/generated/storyboard.html`. Open it in a browser without a server. The Markdown storyboard and SVG are separate shareable artifacts. Keep full source evidence and visible failure conditions in the story.

## Live acceptance for future adapters

Use a dedicated disposable scope and confirmed identities. Verify authorized and unauthorized record access, cross-folder refusal, source versions, changed records, field rejection, absent approval, duplicate calls, interrupted jobs, and exact generated output verification. Record request IDs and read-back evidence with secrets redacted. Test the actual client and any portal separately from the connector.

Document reset actions for the exact created resources. Preserve audit records and signed documents according to the environment's policy. Do not turn a demo reset into a broad folder or enterprise delete.

## Dependency and release checks

Use the optional MCP and dev extras for full validation. Run `python -m pip check`, the validator, and coverage. For a release, generate a fresh sibling, create its own virtual environment, install its dependencies, and run validation from there to rule out accidental imports from the template. Version constraints are ranges; record resolved versions in the release evidence, and introduce a lockfile if your deployment workflow needs frozen dependencies.
