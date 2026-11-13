# Claude, Codex, Cursor, and other agents

Start at the repository root and install `.[mcp,dev]` in its virtual environment. The included server runs locally over stdio with synthetic fixtures; it needs no credentials.

## Skills

| Client | Instructions | Native skills |
|---|---|---|
| Codex | `AGENTS.md` | `.agents/skills/` |
| Claude Code | `CLAUDE.md` → `AGENTS.md` | `.claude/skills/` |
| Cursor | `.cursor/rules/project.mdc` → `AGENTS.md` | `.cursor/skills/` |
| Other agents | Read `AGENTS.md` explicitly | Read the relevant canonical `SKILL.md` explicitly |

Canonical skills live only in `.agents/skills`. Native Claude and Cursor copies are generated, byte-identical files, avoiding symlink portability problems. Edit the canonical source and run `python scripts/sync_skills.py`. They use the shared `name` and `description` frontmatter without client-specific tool grants.

Skill discovery paths follow [Codex skills](https://developers.openai.com/codex/skills/), [Claude Code skills](https://code.claude.com/docs/en/skills), and [Cursor skills](https://cursor.com/docs/skills). Availability can vary by installed client version. The instruction router is an explicit fallback if automatic discovery is unavailable. Repository skills are not automatically uploaded into Claude web or ChatGPT; those clients need their own supported import/configuration path.

## Print a local MCP configuration

With the project virtual environment active:

```bash
python scripts/client_config.py --client claude
python scripts/client_config.py --client codex
python scripts/client_config.py --client cursor
```

Each command prints configuration for **this checkout** using its current Python executable and absolute `--root` path. It does not change your client settings. Reprint after moving the checkout or replacing its virtual environment. These generated absolute paths are local settings and should not be committed.

- **Claude Code:** merge the printed `mcpServers` entry into the project's `.mcp.json`, preserving existing entries. Review any client trust prompt. [Claude MCP documentation](https://code.claude.com/docs/en/mcp).
- **Codex:** merge the printed `mcp_servers.box-agentic-mock` table into your supported Codex configuration scope, preserving existing servers. [Codex MCP documentation](https://developers.openai.com/codex/mcp/).
- **Cursor:** merge the printed `mcpServers` entry into the project's `.cursor/mcp.json`, preserving other entries. [Cursor MCP documentation](https://cursor.com/docs/context/mcp).

The official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) handles protocol transport and initialization. This server does not connect to Box, Salesforce, or an LLM.

## Verify each client

1. Reload the project's skills and MCP connection in the client.
2. Confirm the four project skills are visible or select one by its file path.
3. Confirm `box-agentic-mock` lists the five registry tools with matching argument schemas.
4. Ask: “Use get_record for case-demo-001, then find its term_sheet documents and cite the bank and requested rate.” Expect 6.85% versus 6.50%, with a versioned fixture citation.
5. Ask for a proposal. Verify it returns `applied: false`.
6. Ask whether file-demo-output from job-demo-001 is signature-ready. Expect refusal because the record is Underwriting.
7. Ask to send for signature. Expect an honest missing-capability response; no send tool exists.

Automated stdio tests verify initialization, discovery, schemas, valid calls, and errors. They do not establish that your installed client UI has loaded the server or that an LLM will follow every workflow instruction. Record those acceptance checks separately.
