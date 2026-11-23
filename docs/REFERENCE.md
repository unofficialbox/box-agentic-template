# Reference

This page holds the detail that is not in the README. Start with the [README](../README.md) for the overview and the agent quick start.

## The reference example

The bundled loan example shows the core pattern: document evidence → comparison with the record → proposed update → checks on the generated document. Box and Salesforce are simulated in the offline walkthrough. Bedrock, Databricks, and a frontend are optional. Live accounts are needed only for live integration.

## Verify

Requires Python 3.11+ and Git. No cloud account, API key, Node runtime, or model subscription is needed for the fixture walkthrough.

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

In the unmodified template, the expected result is synthetic evidence at the bank rate of 6.85%, a proposal with `applied: false`, and signature readiness refused because the record is in Underwriting. The demo never calls Box or writes anywhere external. Coverage includes subprocess checks through the committed coverage configuration.

## Create a project

For a tailored project, complete the [guided intake](GUIDED-PROMPT.md) and generate with `--intake-state config/intake.local.json`.

To explore an unchanged reference scaffold, run this from the template root:

```bash
python scripts/new_project.py --slug vendor-onboarding \
  --name "Vendor Onboarding" --system-of-record "Salesforce" --scaffold-only --init-git
cd ../vendor-onboarding
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[mcp,dev]'
python scripts/validate.py
```

- **What it does:** creates a new sibling Git repository, copies only allowlisted source (`config/scaffold.json`), and sets the project identity in `config/project.json`.
- **What it leaves out:** Git history, credentials, local bindings, installed dependencies, and outputs.
- **Content:** the example stays synthetic loans until tailored.
- **Destination:** existing destinations are refused. Use `--destination` for a different location outside the source tree.

## Skills and tools

| Layer | Source | Purpose |
|---|---|---|
| Shared instructions | [AGENTS.md](../AGENTS.md) | Authority, routing, verification |
| Canonical skills | [.agents/skills](../.agents/skills) | Gather, create, connect, deploy, rehearse, verify, brand |
| Brand | [BOX-BRAND.md](brand/BOX-BRAND.md), [config/brand.json](../config/brand.json), [assets/brand/icons](../assets/brand/icons/README.md) | Box brand rules, tokens, and icons for every generated asset |
| Claude entry point | [CLAUDE.md](../CLAUDE.md), `.claude/skills/` | Native Claude discovery |
| Cursor entry point | [.cursor/rules/project.mdc](../.cursor/rules/project.mdc), `.cursor/skills/` | Native Cursor discovery |
| Codex entry point | `AGENTS.md`, `.agents/skills/` | Project instructions and skills |
| Tool registry | [config/tools.json](../config/tools.json) | Input/output schemas and MCP annotations |
| Mock MCP server | [mcp_server.py](../src/box_agentic/mcp_server.py) | Real stdio protocol, synthetic tools |

- **Editing skills:** edit the canonical skills, then run `python scripts/sync_skills.py`. Its `--check` flag detects drift.
- **Clients:** see [client setup](CLIENTS.md) for configurations and discovery checks.
- **Other agents:** they can read `AGENTS.md` and the selected `SKILL.md` directly.

## Live prerequisites

Not needed for offline work or for the Dispatch path, which handles its own sign-in. These are needed for the standalone live path: scratch orgs, metadata deploys, package installs, and anonymous Apex.

**Salesforce CLI.**

```bash
# Requires a current Node.js LTS. Salesforce also publishes native installers.
npm install --global @salesforce/cli
sf --version
```

**Sign in to Salesforce.**

```bash
sf org login web --alias <dev-hub-alias> --set-default-dev-hub   # Dev Hub, needed for scratch orgs
sf org login web --alias <target-alias>                          # or an existing org to deploy into
sf org list
```

- **Dev Hub:** to create scratch orgs, enable Dev Hub in the hub org (Setup → Dev Hub) first.
- **Where aliases go:** record aliases and expiry dates in the ignored `config/runtime.local.json`.
- **No credentials:** never ask for passwords or tokens. The CLI keeps its own session.

**Box.**

- **Connector:** the coding agent needs an authenticated Box connector, such as the Box MCP server. Confirm the user and enterprise with `who_am_i`.
- **Workspace:** get the user's approval for the target folder before creating anything, ideally an isolated new one.
- **Fallback: Box CLI.** Use the CLI when the agent has no Box connector. It also needs a current Node.js LTS.

  ```bash
  npm install --global @box/cli
  box login              # browser OAuth; the CLI stores its own session
  box users:get me       # confirm the user and enterprise
  ```

  The user runs `box login` themselves, for example with `! box login` in Claude Code. The CLI covers the same setup steps: `box folders:create`, `box files:upload`, `box metadata-templates:create`, and `box files:metadata:add`. Run `box <command> --help` for exact flags before using one. The connector rules apply unchanged: approve each write session and never handle tokens or client secrets.

**Box for Salesforce.**

- **Before connecting:** after installing the package, assign `box__Box_Admin_All_Licenses` (Box Admin, All Licenses) to the System Administrator who will connect Box. Do this before asking them to connect in Box Settings.
- **Check:** verify the assignment with a `PermissionSetAssignment` query before the hand-off.

Agents: run `sf --version` and `sf org list` before planning any standalone Salesforce deploy. For Box, call the connector's `who_am_i`. If no connector is available, run `box --version` and `box users:get me`. If any of these checks fail, stop and point the user here instead of guessing.

## Standalone and Dispatch deployment

The project is self-contained: creation, validation, and the demo do not need box-dispatch or Go. It also ships a Dispatch-compatible BCL manifest, Box deployment assets, and Salesforce DX source. See [deployment paths and supported scope](DEPLOYMENT.md).

```bash
python scripts/build_deployment.py
# Optional: test against a separately installed Dispatch source checkout
python scripts/check_dispatch.py --dispatch-root /path/to/box-dispatch
```

## Scope

This is an MIT-licensed local starter with automated generation and protocol tests.

- **Mock only:** the included tool server supports mock mode only.
- **Live acceptance is separate work:** live Box, Salesforce, hosted MCP, Doc Gen, Sign, and client UI acceptance need their own integration work and environment-specific evidence.
- **Not a product:** this is not an underwriting product, and it does not implement either source repo's deployment.

To publish it as a template, enable **Template repository** in the GitHub repository settings.
