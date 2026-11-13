# Architecture

The user's business prompt drives both the implementation and its demo materials. A coding agent interprets the prompt; deterministic scripts copy portable source and render the agent-authored structured definition. There is no hidden LLM call inside the generator or renderer.

```mermaid
flowchart TD
  prompt[Business use-case prompt] --> agent[Coding agent plus create-use-case skill]
  agent --> project[New local project]
  project --> code[Domain code, contracts, fixtures, tests]
  project --> definition[Structured use-case definition]
  definition --> render[Deterministic material renderer]
  render --> process[Mermaid and rendered process SVG]
  render --> story[HTML and Markdown storyboard]
  render --> brief[Solution brief, runbook, tool matrix, acceptance]
  code --> box[Box governed content]
  code --> salesforce[Salesforce structured records]
  salesforce <-->|Record to Box folder mapping| box
  code --> verify[Behavior and MCP tests]
  definition --> verify
  verify --> handoff[Reviewable offline demo bundle]
```

The business process for the included use case is rendered separately at [process.svg](generated/process.svg), with [Mermaid source](generated/process.mmd).

## Execution boundary

Coding-agent skills describe creation, connection, rehearsal, and verification. The local MCP server exposes the registry's five fixture tools through the official SDK. Runtime handlers validate tool inputs and outputs and enforce record versions, folder scope, allowed proposal fields, and output readiness. All local operations are read-only; proposals and approval checks cannot apply changes.

Every project includes Box for governed content and Salesforce for structured facts, with the contract in `config/platforms.json`. The Salesforce record maps to a Box folder; content lookup cannot broaden that folder scope. See [Box + Salesforce](BOX-SALESFORCE.md) for the configuration and metadata starter. For a live extension, preserve these authorities. A provider adapter must establish identity and authorization server-side. Cloud orchestration, analytics, Salesforce UI, and a portal can be added when the use case requires them; none is silently implied by the starter.

## Narrative and code consistency

`config/use-case.json` holds the original request, actors, authorities, steps, prompts, evidence expectations, failure responses, and acceptance criteria. Its schema and registered tool references are validated before rendering. Code and fixtures still need semantic review: a schema cannot prove a supplier workflow stopped using loan logic. The creation skill and acceptance checklist require this review.

Generated assets are committed alongside their source, and validation compares their contents deterministically. The SVG is a dependency-free process rendering from the same step list as the Mermaid source; long labels are summarized visually while full text remains in the storyboard.


## Deployment interface

The project contains its complete runtime and source assets. Python generation and verification do not import or shell out to Dispatch. Optional `check_dispatch.py` compiles a disposable compatibility probe only when a Dispatch source path is explicitly supplied.

```mermaid
flowchart LR
  source[Self-contained generated project] --> native[Authenticated Box and Salesforce platform tools]
  source --> contract[Portable BCL and Salesforce DX source]
  contract --> dispatch[Optional Box Dispatch package builder]
  dispatch --> provider[Dispatch OAuth and native provider adapters]
  native --> deployed[Verified Box and Salesforce resources]
  provider --> deployed
  deployed --> binding[Bind real records to created Box folder IDs]
  binding --> acceptance[Verify live adapters and workflow]
```

[Deployment scope and operator steps](DEPLOYMENT.md) distinguish infrastructure packaging from live workflow acceptance. Dispatch package normalization and operator settings belong to its assembled copy; developer source regeneration must not overwrite that operator context.
