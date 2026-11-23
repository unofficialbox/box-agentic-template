# From one business prompt to a complete demo

Start with the [guided prompt](GUIDED-PROMPT.md). It uses a fixed, resumable question catalog to gather every applicable business, Box, Salesforce, workflow, demo, and deployment decision before implementation. The user reviews and confirms the complete brief, including concrete agent recommendations.

Box and Salesforce, standalone operation, Dispatch compatibility, and the standard output bundle are fixed requirements. The agent gathers domain-specific decisions instead of silently inheriting the loan example.

## Example business request

> Our procurement team needs to onboard suppliers. A specialist reviews insurance certificates, tax forms, and service agreements in Box against the vendor record in Salesforce. Highlight missing or expired documents, draft a review summary, and route exceptions to the procurement manager. We want a ten-minute demo showing a complete supplier and one supplier blocked by expired insurance. Use synthetic data and leave live Box and Salesforce integrations as adapter boundaries.

The resulting code should implement supplier fields and expiration checks; a renamed loan-rate comparison does not meet this request. Its diagram and storyboard should show the two suppliers and the manager's exception decision.

## Agent execution sequence

1. Complete [guided intake](GUIDED-PROMPT.md), receive the user's brief confirmation, and run `python scripts/intake.py check`. Read `config/project.json`. If `kind` is `template`, run `scripts/new_project.py --intake-state config/intake.local.json` with a derived slug and name; Salesforce is the default required system of record. Continue in that sibling directory. The generator creates identity and portable source; the coding agent performs semantic tailoring.
2. Translate the confirmed answers using each question's `maps_to` source list. Preserve the request and record approved assumptions in `config/use-case.json`. Complete the authority and acceptance sections in `docs/USE-CASE.md`.
3. Tailor `src/box_agentic/runtime.py`, `config/tools.json`, fixtures, and `scripts/demo.py`. Replace loan-specific fields and checks, add relevant success and failure cases, and update tests. Keep all mock implementations explicitly labeled.
4. Make each process step actionable: actor, prompt, tool (or human task), visible evidence, expected result, and failure response. Steps may name only registered tools. Use `null` for a human or unimplemented action and state the limitation.
5. Update the canonical skills if domain behavior requires it; regenerate native copies. Keep `docs/CLIENTS.md` accurate for the tools actually implemented.
6. Tailor the Box and Salesforce blueprints and run `python scripts/build_salesforce.py`, `python scripts/build_deployment.py`, then `python scripts/build_deliverables.py`. Commit the resulting `docs/generated/` source and rendered assets together. The renderer uses no model or network; the agent is responsible for turning prose into the correct code and structured definition.
7. Run `python scripts/validate.py` and coverage. Open the HTML storyboard, inspect the SVG, and rehearse the walkthrough. Confirm the artifacts match the implementation, including blocked paths.
8. Hand off the generated repository, the storyboard entry point, actual test evidence, and remaining live integration work.

## Required output bundle

| Output | Source / location |
|---|---|
| Code and tests | `src/`, `scripts/demo.py`, `tests/` |
| Tool and runtime configuration | `config/tools.json`, `config/project.json`, `config/runtime.example.json` |
| Box + Salesforce starters | `config/platforms.json`, `config/box/`, `config/salesforce/`, `salesforce-project/` |
| Standalone / Dispatch deployment | `dispatch.bcl`, `.dispatch/deployment.bcl`, `config/deployment.json`, `config/box/metadata-templates.bcl`, `sample-data/documents/` |
| Synthetic evidence | `fixtures/workflow.json` |
| Guided intake | `config/intake/questions.json`, ignored `config/intake.local.json` |
| Business prompt and narrative | `config/use-case.json`, `docs/USE-CASE.md` |
| Process diagram | `docs/generated/process.mmd`, `process.svg` |
| Demo storyboard | `docs/generated/storyboard.html`, `storyboard.md` |
| Solution brief | `docs/generated/solution-brief.md` |
| Tool matrix and skill routing | `docs/generated/tool-matrix.md`, `AGENTS.md` |
| Presenter runbook | `docs/generated/demo-runbook.md` |
| Acceptance checklist | `docs/generated/acceptance.md` |

All generated materials follow the [Box brand guide](brand/BOX-BRAND.md); the renderer reads `config/brand.json` and refuses text that breaks the checked writing rules. The HTML includes its diagram and styling, so it can be shared as one file. Generated assets are deterministic; `python scripts/build_deliverables.py --check` catches drift. Long SVG labels are summarized; complete text remains in Mermaid and the storyboard.

## Maintainers

The scaffold uses an explicit file list in `config/scaffold.json`. Add intended source files there when extending the template; never add credentials, installed dependencies, runtime bindings, Git metadata, or live receipts. Retest generation after changing the list.
