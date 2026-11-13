---
name: gather-use-case
description: Gather and confirm all business, Box, Salesforce, workflow, demo, and deployment details before building or substantially retargeting a use case.
---

# Gather Use Case

Read `docs/GUIDED-PROMPT.md` and use `config/intake/questions.json` through `scripts/intake.py`. The catalog defines the question order, conditional live questions, batch limit, and implementation destinations. Do not substitute an improvised questionnaire.

Start or resume the ignored intake state. Preserve the original business request verbatim. Record explicitly supplied facts as `source=brief` or `source=user`; never copy requirements from the reference loan fixtures. Follow `next` and ask every remaining applicable question, at most three related questions per turn. Explain terms and offer concrete choices without assuming a technical background. Do not ask a question again when the user already answered it unless their answer is contradictory or incomplete.

When a user requests a recommendation, record the actual concrete recommendation as `source=agent,status=proposed`, visibly label it in the brief, and include it in the user's final review. Unknown/TBD values stay pending; do not fabricate thresholds, policies, approvals, IDs, connector availability, or entitlements. An explicit none is valid when a feature does not apply. Resolve contradictions with the user before treating an answer as settled.

Keep Box and Salesforce, standalone operation, Dispatch compatibility, and the standard output bundle fixed. Ask conditional live questions only for `live_adapters`. Never request credentials; actual tenant IDs belong in ignored runtime config. Initial brief/state content is local and ignored, not a portable source artifact.

Once `next` returns `confirm_brief`, show the complete grouped brief from `review`, including every answer, all proposed choices, excluded features, deferred live questions, dependencies, and acceptance checks. Ask the user to confirm that exact brief. Run `confirm --fingerprint` only after their confirmation, then `check`. Never confirm on the user's behalf, equate silence with confirmation, or use `--scaffold-only` to bypass an unresolved intake. Editing an answer or changing the catalog requires a fresh review and confirmation.

Hand the confirmed intake to create-use-case. In the template, generate a sibling with `--intake-state`; in a generated project, tailor in place after checking readiness. Translate decisions into each question's `maps_to` sources, and explicitly trace acceptance criteria to tests and storyboard evidence. Intake confirmation does not authorize external deployment, record writes, signature actions, publication, or cleanup.
