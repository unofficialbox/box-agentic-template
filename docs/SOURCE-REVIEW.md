# Inspiration review and design decisions

Reviewed source on 2026-11-13. This is a source review of pinned snapshots; no live Box, Salesforce, Bedrock, or source-repository deployment was tested.

| Repository | Reviewed commit | Role |
|---|---|---|
| [box-agentic-loans](https://github.com/unofficialbox/box-agentic-loans/tree/d691ad35ecd34d5368dddca5319c7d3851f68a4f) | `d691ad35ecd34d5368dddca5319c7d3851f68a4f` | Concrete governed document/record workflow |
| [box-bedrock-template](https://github.com/unofficialbox/box-bedrock-template/tree/98ea8c82338560fd4ee31a32737f0bc155a6ee0a) | `98ea8c82338560fd4ee31a32737f0bc155a6ee0a` | Portable scaffold and cross-platform creator workflow |

## Retained patterns

- **Loans:** Box content authority versus Salesforce structured authority; metadata-first scoped lookup; requested versus bank terms; human decision owner; exact Doc Gen output verification; signature preparation distinguished from sending.
- **Bedrock:** sibling project generation through an allowlist; optional platform starters; task-based skills; explicit readiness levels; deterministic fixture and presenter-material workflows.
- **Both:** portable tenant-neutral configuration, source evidence, failure recovery, and separation of coding instructions from environment operation.

## Findings addressed in this starter

| Finding | Source evidence | Consequence and response |
|---|---|---|
| Tool naming drifts between architecture and presenter contract | Loans `docs/ARCHITECTURE.md` names `query_metadata`, `box_ai_ask`, `create_document_from_template`; `CLAUDE.md` and presenter skill use other names including `search_files_metadata`, `ai_qa_single_file`, `create_docgen_batch` | A new user could invoke unavailable or wrong tools. This template serves one registry through both runtime validation and MCP discovery; live names require discovery and mapping. |
| Presentation field policy is narrower than backend capability | Loans presenter allows amount/rate/term only; `LosApplyLoanTerms.cls` also accepts collateral value, LTV, DSCR, maturity with confirmation | The presenter restriction is not the same as the backend allowlist. Here proposal fields are schema-constrained and tested; a future apply adapter must enforce its own authorization and allowlist. This is a contract distinction, not proof of an exploit. |
| Signature preparation is not sending | Loans `LosSendForSignature.cls` returns `prepared` and a preparation URL | New demos must not narrate signing completion from preparation. This starter exposes verification only and documents the missing signature capability. |
| Generic orchestration contracts are specifications | Bedrock `config/agentcore/tool-contracts.json` uses shorthand input/output types; `run_agentcore_mock.py` emits a synthetic trace | Configuration and traces do not establish live agents. This starter includes executable fixture tools, full JSON Schemas, and protocol tests, and still labels them mock. |
| Source domain and platform assumptions can leak into new demos | Loans includes Acme/Harborview data, Salesforce metadata and a tenant portal link; Bedrock includes Life Sciences and several platform contracts | Generator copies only this new neutral starter. The agent must tailor code, fixtures, narrative, and tests to the user's prompt. No source tenant IDs, portal links, or deployed metadata are imported. |
| Cross-client copies can diverge | Loans has separate presenter skills with consistency tests; Bedrock routes through shared workflow skills | Canonical skills generate byte-identical native copies and validation catches drift. |

## New work

The implementation here was authored as a fresh starter, rather than copied from either repository. It keeps the loan workflow as an explicitly synthetic example, makes external platforms optional, and adds a prompt-to-demo output bundle: process source and image, storyboard, solution brief, runbook, tool matrix, and acceptance checks from one narrative definition.

The loans snapshot includes an MIT license. No root license was found in the Bedrock snapshot; its implementation and assets were not copied. This project has its own MIT license. This note records provenance, not a legal opinion about the source repositories.

## Review limits

Source entry points, relevant instructions/personas/skills, the scaffold manifest and generator, mock orchestration, core tool contracts, loan apply/signature classes, and selected consistency tests were inspected. Source-repository test suites, Salesforce Apex deployment, hosted connectors, and cloud services were not executed. The template's own checks are documented separately in its validation evidence.
