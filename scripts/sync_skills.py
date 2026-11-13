"""Generate native client skill copies from .agents/skills; check drift in CI."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sync(root=ROOT, *, check=False):
    root = root.resolve()
    sources = sorted((root / ".agents/skills").glob("*/SKILL.md"))
    if not sources:
        raise ValueError("No canonical skills found")
    stale = []
    for client in (".claude", ".cursor"):
        for source in sources:
            target = root / client / "skills" / source.parent.name / "SKILL.md"
            if target.is_symlink() or any(p.is_symlink() for p in target.parents if p.is_relative_to(root)):
                raise ValueError("Skill destinations must not be symlinks")
            if not target.exists() or target.read_bytes() != source.read_bytes():
                stale.append(str(target.relative_to(root)))
                if not check:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.read_bytes())
    return stale


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = sync(check=args.check)
    if args.check and stale:
        raise SystemExit("Skill drift: " + ", ".join(stale))
    print("Skills synchronized" if not args.check else "Skill copies match")
