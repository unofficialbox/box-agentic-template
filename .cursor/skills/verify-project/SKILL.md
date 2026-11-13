---
name: verify-project
description: Validate changes to this template or a generated project, including tool contracts, native skill parity, project generation, and MCP behavior.
---

# Verify Project

Read the verification commands in `README.md` and the readiness definitions in `docs/OPERATIONS.md`.

Run the narrow changed-behavior test first. Then run `python scripts/validate.py` and the coverage command from README. Install the MCP extra for stdio protocol checks; a skipped MCP test must be reported as a gap. Test generated projects in temporary sibling directories, including paths with spaces, refusal to overwrite, and exclusion of private files. Do not write generated fixtures into the source repository.

After changing `.agents/skills`, run `python scripts/sync_skills.py` and its `--check` mode. Run `python scripts/build_deliverables.py --check` and inspect the generated storyboard and process SVG. Verify the business request appears in the brief and domain-specific acceptance checks cover the code.

Keep the scaffold file allowlist in `config/scaffold.json` in sync with intended portable source. Review new entries for credentials, local config, dependencies, outputs, and Git history.

Use actual evidence in the handoff: passed tests and coverage, protocol discovery/calls, client UI verification if performed, and live connectivity or mutation only if observed. CI configuration is not a CI run. A local Git repository is not a published GitHub template. Name any skipped checks and the specific next acceptance action.
