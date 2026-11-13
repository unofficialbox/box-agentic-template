"""Validate portable source contracts, skills, generation, and runtime behavior."""
import json
from pathlib import Path
import subprocess
import sys
from box_agentic.runtime import Runtime
from box_agentic.intake import load_catalog, require_ready
from sync_skills import sync
from build_deliverables import build
from build_salesforce import build as build_salesforce
from build_deployment import build as build_deployment

ROOT = Path(__file__).resolve().parents[1]


def main():
    for path in ROOT.rglob("*.json"):
        if not any(p in {".git", ".venv", "output", "build", "dist"} for p in path.relative_to(ROOT).parts):
            json.loads(path.read_text())
    project = json.loads((ROOT / "config/project.json").read_text())
    if project["kind"] not in {"template", "project"} or project["mode"] != "mock":
        raise ValueError("Unsupported project kind or runtime mode")
    load_catalog(ROOT)
    if (ROOT / "config/intake.local.json").exists():
        require_ready(ROOT, ROOT / "config/intake.local.json")
    Runtime(ROOT)
    if build_deployment(check=True):
        raise ValueError("Run python scripts/build_deployment.py to refresh deployment artifacts")
    if build_salesforce(check=True):
        raise ValueError("Run python scripts/build_salesforce.py to refresh Salesforce metadata")
    if build(check=True):
        raise ValueError("Run python scripts/build_deliverables.py to refresh demo materials")
    stale = sync(check=True)
    if stale:
        raise ValueError("Run python scripts/sync_skills.py: " + ", ".join(stale))
    for skill in (ROOT / ".agents/skills").glob("*/SKILL.md"):
        text = skill.read_text()
        if not text.startswith("---\nname: " + skill.parent.name + "\ndescription: "):
            raise ValueError("Invalid skill frontmatter: " + str(skill))
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/demo.py"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    print("Validated contracts, skill parity, scaffold tests, and offline workflow")


if __name__ == "__main__":
    main()
