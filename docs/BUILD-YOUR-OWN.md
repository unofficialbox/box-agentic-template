# From one business prompt to a complete demo

Open this repository in your coding agent and paste the following with your own business request. Technical platform choices are optional; the agent should infer a minimal offline implementation and state assumptions.

```text
Use this template to build a complete demo for this business use case:

[Describe the business problem, people, documents, decisions, and desired outcome in plain language.]

Read AGENTS.md and use the create-use-case skill. If this is the template,
create a new sibling Git project; continue in that generated project.
Make reasonable assumptions for optional details and record them.
Ask only when a missing decision prevents correct or authorized work.

Deliver working code, tool contracts, configuration, synthetic fixtures,
a process diagram (Mermaid and rendered SVG), a self-contained HTML and
Markdown demo storyboard, a solution brief, a tool/skill map, a presenter
runbook, and acceptance checks. Tailor all of them to my use case.

Use config/use-case.json as the shared narrative source. Preserve my
original request in business_prompt. Adapt runtime handlers, schemas,
fixtures, tests, and scripts/demo.py to the domain; do not stop after
renaming the loan example. Run scripts/build_deliverables.py, then the
validator and coverage. Keep live integration gaps explicit. Do not
deploy, publish, or modify cloud data merely to generate the project.
```

## Example business request

> Our procurement team needs to onboard suppliers. A specialist reviews insurance certificates, tax forms, and service agreements in Box against the vendor record in our CRM. Highlight missing or expired documents, draft a review summary, and route exceptions to the procurement manager. We want a ten-minute demo showing a complete supplier and one supplier blocked by expired insurance. Use synthetic data and leave the CRM integration as an adapter boundary.

The resulting code should implement supplier fields and expiration checks; a renamed loan-rate comparison does not meet this request. Its diagram and storyboard should show the two suppliers and the manager's exception decision.

## Agent execution sequence

1. Read `config/project.json`. If `kind` is `template`, run `scripts/new_project.py` with a derived slug, name, and system of record. Continue in that sibling directory. The generator creates identity and portable source; the coding agent performs semantic tailoring.
2. Preserve the request and record assumptions in `config/use-case.json`. Complete the authority and acceptance sections in `docs/USE-CASE.md`.
3. Tailor `src/box_agentic/runtime.py`, `config/tools.json`, fixtures, and `scripts/demo.py`. Replace loan-specific fields and checks, add relevant success and failure cases, and update tests. Keep all mock implementations explicitly labeled.
4. Make each process step actionable: actor, prompt, tool (or human task), visible evidence, expected result, and failure response. Steps may name only registered tools. Use `null` for a human or unimplemented action and state the limitation.
5. Update the canonical skills if domain behavior requires it; regenerate native copies. Keep `docs/CLIENTS.md` accurate for the tools actually implemented.
6. Run `python scripts/build_deliverables.py`. Commit the resulting `docs/generated/` source and rendered assets together. The renderer uses no model or network; the agent is responsible for turning prose into the correct code and structured definition.
7. Run `python scripts/validate.py` and coverage. Open the HTML storyboard, inspect the SVG, and rehearse the walkthrough. Confirm the artifacts match the implementation, including blocked paths.
8. Hand off the generated repository, the storyboard entry point, actual test evidence, and remaining live integration work.

## Required output bundle

| Output | Source / location |
|---|---|
| Code and tests | `src/`, `scripts/demo.py`, `tests/` |
| Tool and runtime configuration | `config/tools.json`, `config/project.json`, `config/runtime.example.json` |
| Synthetic evidence | `fixtures/workflow.json` |
| Business prompt and narrative | `config/use-case.json`, `docs/USE-CASE.md` |
| Process diagram | `docs/generated/process.mmd`, `process.svg` |
| Demo storyboard | `docs/generated/storyboard.html`, `storyboard.md` |
| Solution brief | `docs/generated/solution-brief.md` |
| Tool matrix and skill routing | `docs/generated/tool-matrix.md`, `AGENTS.md` |
| Presenter runbook | `docs/generated/demo-runbook.md` |
| Acceptance checklist | `docs/generated/acceptance.md` |

The HTML includes its diagram and styling, so it can be shared as one file. Generated assets are deterministic; `python scripts/build_deliverables.py --check` catches drift. Long SVG labels are summarized; complete text remains in Mermaid and the storyboard.

## Maintainers

The scaffold uses an explicit file list in `config/scaffold.json`. Add intended source files there when extending the template; never add credentials, installed dependencies, runtime bindings, Git metadata, or live receipts. Retest generation after changing the list.
