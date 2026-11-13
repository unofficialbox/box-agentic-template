"""Generate a clean sibling project from an explicit file allowlist."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
from build_deployment import build as build_deployment

ROOT = Path(__file__).resolve().parents[1]


def generate(slug, name, system_of_record, destination, *, init_git=False, source=ROOT):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("slug must be lowercase kebab-case")
    if system_of_record != "Salesforce":
        raise ValueError("This template requires Salesforce as the system of record")
    if not name.strip() or not system_of_record.strip():
        raise ValueError("name and system of record must not be empty")
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination already exists; choose a new directory")
    source = source.resolve()
    if destination.resolve().is_relative_to(source):
        raise ValueError("Create a sibling outside the source repository")
    manifest = json.loads((source / "config/scaffold.json").read_text())
    entries = manifest["files"]
    if len(set(entries)) != len(entries):
        raise ValueError("Duplicate scaffold entries")
    for entry in entries:
        path = PurePosixPath(entry)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise ValueError("Unsafe scaffold path")
        candidate = source / entry
        if any((source / Path(*path.parts[:i])).is_symlink() for i in range(1, len(path.parts) + 1)):
            raise ValueError("Scaffold symlinks are not allowed")
        if not candidate.is_file():
            raise ValueError("Missing scaffold file: " + entry)
        if set(path.parts) & {".git", ".venv", "output", "__pycache__"} or candidate.name.startswith(".env") or candidate.name == "runtime.local.json":
            raise ValueError("Private or generated file in scaffold")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".agentic-scaffold-", dir=destination.parent))
    try:
        for entry in entries:
            target = staging / entry
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / entry, target)
        project = {"kind": "project", "slug": slug, "name": name,
                   "system_of_record": "Salesforce", "required_platforms": ["box", "salesforce"], "mode": "mock"}
        (staging / "config/project.json").write_text(json.dumps(project, indent=2) + "\n")
        build_deployment(staging)
        if init_git:
            subprocess.run(["git", "init", "-b", "main", str(staging)], check=True, capture_output=True)
        # mkdir reserves the destination without overwriting a concurrent creator.
        destination.mkdir()
        try:
            for child in staging.iterdir():
                child.rename(destination / child.name)
        except BaseException:
            shutil.rmtree(destination)
            raise
    finally:
        shutil.rmtree(staging)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--system-of-record", choices=["Salesforce"], default="Salesforce",
                        help="Salesforce is required and selected by default")
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--init-git", action="store_true")
    args = parser.parse_args()
    try:
        result = generate(args.slug, args.name, args.system_of_record,
                          args.destination or ROOT.parent / args.slug, init_git=args.init_git)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + "\n")
    print(result)


if __name__ == "__main__":
    main()
