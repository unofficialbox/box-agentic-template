# Tools, skills, and adapter boundaries

A **skill** tells a coding agent how to work. A **tool** exposes an executable capability. A **binding** maps a local capability to a provider's authenticated tool. Installing a skill does not install a connector or authorize an action.

`config/tools.json` is the authoritative local tool registry. The runtime validates arguments and results with JSON Schema Draft 2020-12. The MCP server serves the same schemas and annotations through the official Python SDK. Tool names below belong to this template; they are not Box API names.

| Tool | Required input | Output | Boundary |
|---|---|---|---|
| `get_record` | `record_id` | Versioned record, folder, fields | Missing or ambiguous records refuse |
| `search_documents` | `record_id`, `document_type` | Matching synthetic documents | Exact mapped folder only |
| `analyze_document` | `record_id`, `file_id` | Curated facts and versioned citation | Fixture lookup, no model inference |
| `propose_update` | `record_id`, `expected_version`, `changes` | Before/after diff, approval required, applied false | Amount, rate, term only; writes nothing |
| `verify_generated_document` | `record_id`, `file_id`, `job_id` | Verified flag and refusal reasons | Exact job/file/record versions, terms, tags, lifecycle |

All tools are read-only, idempotent, closed-world mock implementations. Required fields, types, allowed properties, and complete outputs are in the registry. Unknown tools and schema-invalid arguments return errors. Unknown documents, cross-folder documents, stale proposals, and invalid adapter outputs also refuse. Errors do not echo submitted payloads or credentials.

`search_documents` returns synthetic document text for demonstration. A live Box adapter should return scoped references and metadata and use authorized content/AI tools when content is needed. The mock's folder check is an invariant test, not production identity authorization.

## Bind a live capability

Start with a read-only operation in a disposable folder. Discover the actual connected inventory and input/output schemas; never copy a tool name from the inspiration repositories without checking your connector.

Record a binding in ignored `config/runtime.local.json` and use this worksheet in the integration change:

| Capability | Provider tool and schema/version | Identity and target scope | Required permission | Output and verification evidence |
|---|---|---|---|---|
| Record lookup | Fill from discovery | Named record system and principal | Record read | Version and mapped folder |
| Scoped document lookup | Fill from discovery | Confirmed Box tenant/folder | Scoped content read | File IDs and versions |
| Analysis / policy | Fill from discovery | Authorized files or policy Hub | Content or AI permission | Source-cited findings |
| Record write (new capability) | Implement explicitly | Exact record and field allowlist | Current identity + action authorization | Versioned read-back |
| Generation (new capability) | Implement explicitly | Confirmed template/destination | Create document | Job ID, terminal status, exact output |
| Signature preparation (new capability) | Implement explicitly | Checked output and confirmed signer | Signature preparation | Actual request ID and preparation state |

Prefer an existing purpose-built connector where it provides the required capability. The template does not ship live adapter code or hosted MCP credentials. Runtime `mode=live` refuses; do not remove this guard to imply connectivity.

## Write contracts for a live extension

Enforce identity, record/folder ownership, current version, lifecycle state, field allowlists, exact payload authorization, and provider-supported idempotency at the server. A prompt or `confirmed: true` field by itself cannot establish authorization. Keep a proposal separate from apply and preparation separate from sending/signing.

If a write times out, reconcile the exact operation and record state before retrying. Never choose generated outputs by name or latest timestamp. Job acceptance is not completion. Verify the job's output ID and version, resolved tags, matching terms, and current approval state before any signature action. Do not reuse a prior request after generating a new draft.

Persist live receipts with operation IDs, timestamps, before/after versions, verification, and redacted authorization provenance in ignored output storage. Stop retries when completion cannot be determined; report an uncertain outcome rather than asserting nothing changed.
