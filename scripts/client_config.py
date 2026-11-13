"""Print local mock MCP config for the current checkout; never edit client settings."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def config(client, root=ROOT):
    spec = {"command": sys.executable, "args": ["-m", "box_agentic.mcp_server", "--root", str(root.resolve())]}
    if client == "codex":
        return "[mcp_servers.box-agentic-mock]\ncommand = " + json.dumps(spec["command"]) + "\nargs = " + json.dumps(spec["args"]) + "\n"
    if client not in {"claude", "cursor"}:
        raise ValueError("Unknown client")
    return json.dumps({"mcpServers": {"box-agentic-mock": spec}}, indent=2) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=["claude", "codex", "cursor"], required=True)
    args = parser.parse_args()
    print(config(args.client), end="")
