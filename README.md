# Box + Salesforce Agentic Template

Build your own governed Box + Salesforce workflow with Claude Code, Codex, Cursor, or another coding agent. Provide a business-use-case prompt and have your coding agent create a working demo project, process diagrams, storyboard, solution brief, presenter runbook, and acceptance checks. Start offline, then bind the tools your environment actually exposes.

The loan example demonstrates document evidence → record comparison → proposed update → generated-document checks. Box is the content authority, Salesforce owns structured facts, and a person owns consequential decisions. Box and Salesforce are required parts of every generated solution. Bedrock, Databricks, and a frontend remain optional. Both required platforms are simulated in the offline walkthrough; live accounts are needed only for live integration.

## Start with your business use case

Open the template in your coding agent and paste the [starter prompt](docs/BUILD-YOUR-OWN.md), adding your business request in plain language. The agent creates a sibling project, tailors code/configuration/fixtures, and renders the demo materials from `config/use-case.json`. No technical platform selection is required to begin.

Preview the included reference: [demo storyboard](docs/generated/storyboard.html), [process diagram](docs/generated/process.svg), and [solution brief](docs/generated/solution-brief.md).

## Run locally

Requires Python 3.11+ and Git. No cloud account, API key, Node runtime, or model subscription is required for the fixture walkthrough.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[mcp,dev]'
python scripts/demo.py
python scripts/build_deliverables.py --check
python scripts/validate.py
python -m coverage run scripts/validate.py
python -m coverage combine
python -m coverage report --fail-under=85
```

Expected: synthetic evidence at the bank rate of 6.85%, a proposal with `applied: false`, and signature readiness refused because the record is Underwriting. The demonstration never calls Box or writes externally. Coverage includes subprocess checks through the committed coverage configuration.

## Create your own project

Run from this template's root:

```bash
python scripts/new_project.py --slug vendor-onboarding \
  --name "Vendor Onboarding" --system-of-record "Salesforce" --init-git
cd ../vendor-onboarding
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[mcp,dev]'
python scripts/validate.py
```

This creates a new sibling Git repository, copies only allowlisted source, and sets its identity in `config/project.json`. It does not copy Git history, credentials, local bindings, installed dependencies, or outputs. The example remains synthetic loans until tailored. Existing destinations are refused. Use `--destination` for a different location outside the source tree.

Give your coding agent the [starter prompt](docs/BUILD-YOUR-OWN.md). In a generated project, follow the tailoring steps in that guide.

## Skills and tools

| Layer | Source | Purpose |
|---|---|---|
| Shared instructions | [AGENTS.md](AGENTS.md) | Authority, routing, verification |
| Canonical skills | [.agents/skills](.agents/skills) | Create, connect, deploy, rehearse, verify |
| Claude entry point | [CLAUDE.md](CLAUDE.md), `.claude/skills/` | Native Claude discovery |
| Cursor entry point | [.cursor/rules/project.mdc](.cursor/rules/project.mdc), `.cursor/skills/` | Native Cursor discovery |
| Codex entry point | `AGENTS.md`, `.agents/skills/` | Project instructions and skills |
| Tool registry | [config/tools.json](config/tools.json) | Input/output schemas and MCP annotations |
| Mock MCP server | [mcp_server.py](src/box_agentic/mcp_server.py) | Real stdio protocol, synthetic tools |

Edit canonical skills, then run `python scripts/sync_skills.py`; `--check` detects drift. See [client setup](docs/CLIENTS.md) for configurations and discovery checks. Other agents can read `AGENTS.md` and the selected `SKILL.md` explicitly.

## Standalone and Dispatch deployment

The project is self-contained; ordinary creation, validation, and demo workflows do not require box-dispatch or Go. It also ships a Dispatch-compatible BCL manifest, Box deployment assets, and Salesforce DX source. See [deployment paths and supported scope](docs/DEPLOYMENT.md).

```bash
python scripts/build_deployment.py
# Optional: test against a separately installed Dispatch source checkout
python scripts/check_dispatch.py --dispatch-root /path/to/box-dispatch
```

## Explore

- [Build your own](docs/BUILD-YOUR-OWN.md): prompt and tailoring sequence.
- [Use-case definition](docs/USE-CASE.md): actors, authority, acceptance criteria.
- [Box + Salesforce starter](docs/BOX-SALESFORCE.md): platform configuration, metadata starter, and record-to-folder mapping.
- [Tools and live adapters](docs/TOOLS.md): contracts, mappings, errors, authorization.
- [Architecture](docs/ARCHITECTURE.md): data flow and integration boundaries.
- [Operations](docs/OPERATIONS.md): readiness, recovery, and live acceptance.
- [Source review](docs/SOURCE-REVIEW.md): pinned review of both inspiration repositories.

## Scope

This is an MIT-licensed local starter with automated generation and protocol tests. The included tool server supports mock mode only. Live Box, Salesforce, hosted MCP, Doc Gen, Sign, and client UI acceptance require separate integration work and environment-specific evidence. It is not an underwriting product or an implementation of either source repo's deployment.

To distribute later, create a new GitHub repository from this directory, push it, and enable **Template repository** in its settings. No remote is configured by this starter.
