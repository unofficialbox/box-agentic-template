"""Guide a coding agent through a resumable local use-case intake; no cloud calls."""
import argparse
import json
from pathlib import Path
from box_agentic.intake import answer, confirm, load_catalog, new_state, next_batch, require_ready, review

ROOT = Path(__file__).resolve().parents[1]


def save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n")
    path.chmod(0o600)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=ROOT / "config/intake.local.json")
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start")
    start.add_argument("--brief", required=True)
    update = commands.add_parser("answer")
    update.add_argument("--id", required=True)
    update.add_argument("--value", required=True)
    update.add_argument("--status", choices=["answered", "proposed"], default="answered")
    update.add_argument("--source", choices=["user", "brief", "agent"], default="user")
    commands.add_parser("next")
    commands.add_parser("review")
    accept = commands.add_parser("confirm")
    accept.add_argument("--fingerprint", required=True)
    commands.add_parser("check")
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(ROOT)
        if args.command == "start":
            if args.state.exists():
                raise ValueError("Intake already exists; use next, answer, or review to resume")
            state = new_state(args.brief)
            save(args.state, state)
        else:
            state = json.loads(args.state.read_text())
        if args.command == "answer":
            state = answer(catalog, state, args.id, args.value, status=args.status, source=args.source)
            save(args.state, state)
        elif args.command == "confirm":
            state = confirm(catalog, state, args.fingerprint)
            save(args.state, state)
        if args.command == "review":
            result = review(catalog, state)
        elif args.command == "check":
            require_ready(ROOT, args.state)
            result = {"ready_for_implementation": True, "external_writes_authorized": False}
        else:
            result = next_batch(catalog, state)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
