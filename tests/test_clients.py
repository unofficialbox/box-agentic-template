import json
from pathlib import Path
import sys
import tomllib
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from client_config import config


class ClientTests(unittest.TestCase):
    def test_client_configs_preserve_paths_with_spaces(self):
        root = Path("/tmp/example project")
        for client in ("claude", "cursor", "codex"):
            text = config(client, root)
            parsed = tomllib.loads(text) if client == "codex" else json.loads(text)
            key = "mcp_servers" if client == "codex" else "mcpServers"
            spec = parsed[key]["box-agentic-mock"]
            self.assertEqual(spec["args"][-1], str(root.resolve()))
            self.assertEqual(spec["command"], sys.executable)

    def test_cli_prints_parseable_config(self):
        for client in ('claude', 'cursor', 'codex'):
            result = subprocess.run([sys.executable, 'scripts/client_config.py', '--client', client],
                                    cwd=ROOT, capture_output=True, text=True, check=True)
            parsed = tomllib.loads(result.stdout) if client == 'codex' else json.loads(result.stdout)
            self.assertTrue(parsed)
