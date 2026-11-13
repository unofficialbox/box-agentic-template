# Guided use-case prompt

Paste this into Claude Code, Codex, Cursor, or another coding agent opened at this repository. Start with a plain-language business request; the agent gathers the rest in a fixed sequence.

```text
Help me define and build a complete Box + Salesforce use-case demo.

My initial business request:
[Describe the business problem and desired outcome. A short paragraph is enough to start.]

Read AGENTS.md and use the gather-use-case skill first. Follow the question
catalog at config/intake/questions.json using scripts/intake.py. This is
a guided intake: do not begin domain implementation from my short prompt.

Record details I already explicitly provided, retaining their provenance.
Do not treat the template's loan example as my requirements. Ask every
remaining applicable question in catalog order, no more than three related
questions per turn. Keep stable question IDs so we can resume or revise.
Explain technical terms and give concrete choices when I need help.

If I say "recommend", propose a concrete answer and mark it proposed;
do not silently turn it into my decision. Leave unanswered or unknown
design decisions pending until resolved. "None" is a valid explicit answer
where a feature or constraint does not apply. Resolve contradictions with
me; do not select an answer based on whichever source was read last.

Box, Salesforce, standalone operation, Dispatch compatibility, and the
standard demo artifact bundle are fixed requirements. Ask about the
business, actors/access, workflow/approvals, Salesforce objects and fields,
Box documents/folders/metadata/policies, rules/calculations, document
creation/signatures, tools/clients, demo story, tests, and deployment/reset.
Ask live-environment questions only if we choose implemented live adapters.
Do not ask for passwords, access tokens, client secrets, or private keys.

When all applicable answers are concrete, show the complete build brief
with every answer, proposed choice, assumption, excluded feature, deferred
live item, acceptance criterion, and intended output. Ask me to confirm
that exact brief. Do not confirm it on my behalf. Save its current review
fingerprint only after my confirmation. If any answer changes, review and
confirm again before implementation.

Then use create-use-case to generate a sibling Git project with the
confirmed intake, or tailor the current generated project. Build domain
code, configuration, fixtures, shared agent skills/tools, process diagrams,
HTML/Markdown storyboard, solution brief, presenter runbook, tool matrix,
acceptance checks, and standalone/Dispatch deployment assets. Run the
validator, coverage, render checks, and available browser checks.

Keep the project standalone and explicitly distinguish offline evidence,
Dispatch package compatibility, live deployment, and live workflow tests.
My confirmation of a build brief is not authorization for cloud writes,
deployment, publishing, sharing, sending signatures, or deleting resources.
```

## Fixed question order

| Stage | Required details |
|---|---|
| 1. Business purpose | Project name/slug, problem/outcome, process boundaries |
| 2. Implementation scope | Offline versus live adapters, technical/performance/cost constraints, agents/clients/tools |
| 3. People and access | Roles, user surfaces, data/record/document boundaries |
| 4. Workflow and decisions | Trigger and ordered steps, approval ownership, exceptions/recovery |
| 5. Salesforce | Objects/relationships/fields/external IDs, lifecycle, allowed writes/concurrency |
| 6. Box | Documents/extraction, folders/metadata/record mapping, policy/citations/governance |
| 7. Rules and documents | Validations/calculations, document generation, signature behavior |
| 8. Demo | Audience/duration, success and blocked scenarios, artifact preferences |
| 9. Acceptance and operations | Observable checks, deployment/reset/audit, dependencies/entitlements |
| 10. Live preparation, conditional | Target aliases/scope, authenticated capabilities, disposable acceptance data |

There are 27 core questions, plus three live-preparation questions when `implementation_depth` is `live_adapters`. Known answers are not asked again. The state machine determines question order and coverage; the coding agent is still responsible for interpreting prose, detecting contradictions, and verifying technical claims. Presence checks cannot prove a business answer is correct.

## Local commands

With the project's virtual environment active:

```bash
python scripts/intake.py start --brief "Our procurement team needs supplier onboarding in Box and Salesforce."
python scripts/intake.py next
python scripts/intake.py answer --id project_identity --value "Supplier Onboarding; slug supplier-onboarding"
python scripts/intake.py answer --id implementation_depth --value offline
python scripts/intake.py answer --id technical_constraints --value "Use the existing Python starter and no hosted services" --source agent --status proposed
python scripts/intake.py review
```

`next` prints only the next unresolved group, capped at three questions. The agent presents those questions conversationally and records each answer. It may use `--source brief` only for facts explicitly stated in the original request. Recommendations use `--source agent --status proposed` and remain visibly proposed in the review.

After reviewing the complete output and receiving the user's confirmation of that exact brief:

```bash
python scripts/intake.py confirm --fingerprint <fingerprint-from-current-review>
python scripts/intake.py check
python scripts/new_project.py --slug supplier-onboarding --name "Supplier Onboarding" \
  --intake-state config/intake.local.json --init-git
```

`confirm` rejects missing answers and stale fingerprints. Editing an answer invalidates confirmation. A changed question catalog also invalidates the prior fingerprint. `check` succeeds only for a complete, confirmed intake. The CLI records freshness/completeness; it cannot authenticate who spoke in a chat. The skill requires actual user confirmation and forbids agent self-confirmation.

State defaults to ignored `config/intake.local.json` with owner-only file permissions. Use `--state output/intake/another-session.json` before the command for a separate intake. `start` refuses to overwrite an existing session. Do not put secrets in answers. Keep actual tenant IDs in ignored runtime bindings, not the portable business definition.

## Build gate and handoff

Normal project generation requires `--intake-state`; incomplete/unconfirmed intake fails before a destination is created. The confirmed state is copied into the generated project's ignored intake file so it can resume. The original request, approved business decisions, and clearly labeled assumptions should then be translated into `config/use-case.json`, `docs/USE-CASE.md`, platform blueprints, code, and tests using each question's `maps_to` list.

For an existing generated project, complete/confirm its intake before tailoring it in place. When a local intake exists, renderers and the validator refuse incomplete/unconfirmed state. An unstarted reference scaffold can still run the included demo without inventing user answers.

`--scaffold-only` explicitly copies the reference example for exploration or compatibility testing. It does not gather requirements or produce a tailored use case. The standard guided prompt does not use that bypass.

Confirming the brief authorizes the agreed local implementation scope only. Offline selection defers the three live-preparation questions and leaves live adapters/targets as explicit follow-up work. Choosing live adapters activates those questions; it still does not authorize a live write or deployment.
