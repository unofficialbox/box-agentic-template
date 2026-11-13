---
name: create-use-case
description: Create a new Box and Salesforce agentic workflow project or tailor its domain, fixtures, authority boundaries, and acceptance criteria.
---

# Create Use Case

Read `config/project.json`, `config/platforms.json`, and `docs/BUILD-YOUR-OWN.md` from the repository root.

Every generated use case must include Box and Salesforce. Keep Box as governed content authority and Salesforce as structured-record authority. Adapt the Salesforce object and field mapping, Box metadata blueprint, and record-to-folder binding to the business domain. Do not make Salesforce optional when tailoring the use case. Read `docs/BOX-SALESFORCE.md` for the integration starter. Keep the generated project standalone and update the supported Dispatch deployment assets per `docs/DEPLOYMENT.md`; neither Dispatch nor a sibling checkout may become a runtime dependency.

If `kind` is `template`, use `scripts/new_project.py` to generate a sibling and continue there. If `kind` is `project`, tailor it in place; the generator remains available for intentionally creating another project.

Preserve the user's full business request in `config/use-case.json.business_prompt`. Read its schema and adapt the structured definition, including actors, process steps, presenter prompts, expected evidence, failure conditions, assumptions, and acceptance criteria. Deliver code AND the demo materials required by `docs/BUILD-YOUR-OWN.md`; a scaffold or renamed loan example alone is incomplete.

Capture the business outcome, actor, record authority, document types, proposed changes, decision owner, and observable success criteria in `docs/USE-CASE.md`. Use reasonable assumptions for optional detail and identify them. Resolve any missing decision that determines authorization or data access before dependent live work.

Replace synthetic fixtures and domain field schemas together; preserve versioned citations, per-record document scope, and distinct requested versus authoritative values. Update mock handlers and tests alongside `config/tools.json`. Do not globally replace text through code or JSON. Generate host skill copies after editing canonical skills.

Tailor `scripts/demo.py` and behavior tests to the new domain. Regenerate Salesforce DX metadata with `python scripts/build_salesforce.py` after changing its blueprints. Tailor `config/deployment.json` and regenerate portable BCL/sample assets with `python scripts/build_deployment.py`. Run `python scripts/build_deliverables.py` to create Mermaid and SVG process diagrams, HTML and Markdown storyboards, a solution brief, tool matrix, presenter runbook, and acceptance checklist. Inspect the rendered diagram and storyboard against the actual code; validate both happy and blocked paths.

Run the offline walkthrough and validator in the generated project. Report whether the domain is tailored, which integrations remain specifications, and the next concrete acceptance check. A generated project still contains the synthetic loan example until you explicitly tailor it.
