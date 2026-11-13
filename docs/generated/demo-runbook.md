# Presenter runbook

1. Create a virtual environment and install `.[mcp,dev]` as documented in README.
2. Run `python scripts/validate.py` and `python scripts/build_deliverables.py --check`.
3. Open `docs/generated/storyboard.html` locally; it is self-contained and makes no network requests.
4. Run `python scripts/demo.py` or connect the mock MCP server from docs/CLIENTS.md.
5. Follow each storyboard prompt and verify its expected evidence.
6. Explain each held action and name the human decision owner. Do not describe fixtures as live.
7. Repeat the walkthrough: it has no external side effects and needs no tenant reset.

## Deployment preparation

Read docs/DEPLOYMENT.md. Use included platform assets standalone, or the optional Dispatch BCL interface. Infrastructure deployment does not activate live workflow adapters.

## Live rehearsal

Use docs/OPERATIONS.md after implementing live adapters. Keep live receipts outside the portable bundle.
