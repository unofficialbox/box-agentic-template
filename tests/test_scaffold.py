import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from new_project import generate
from sync_skills import sync
from demo import run


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.dest = self.base / "new-case"

    def generate(self, **kwargs):
        return generate("new-case", 'New "Case"', "Salesforce", self.dest, **kwargs)

    def test_clean_generated_project_and_git(self):
        self.generate(init_git=True)
        project = json.loads((self.dest / "config/project.json").read_text())
        self.assertEqual(project["kind"], "project")
        self.assertEqual(project["name"], 'New "Case"')
        self.assertEqual(project["system_of_record"], "Salesforce")
        self.assertTrue((self.dest / ".git").is_dir())
        self.assertFalse((self.dest / ".venv").exists())
        self.assertFalse((self.dest / "config/runtime.local.json").exists())
        self.assertEqual(run(self.dest)["external_writes"], 0)
        self.assertEqual(sync(self.dest, check=True), [])
        result = subprocess.run([sys.executable, "scripts/demo.py"], cwd=self.dest, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_existing_destination_is_preserved(self):
        self.dest.mkdir()
        marker = self.dest / "keep"
        marker.write_text("keep")
        with self.assertRaises(ValueError):
            self.generate()
        self.assertEqual(marker.read_text(), "keep")

    def test_invalid_inputs_and_nested_destination_refuse(self):
        for slug in ("../oops", "Upper", "bad/slash", "", "-bad"):
            with self.assertRaises(ValueError):
                generate(slug, "name", "Salesforce", self.dest)
        with self.assertRaises(ValueError):
            generate("valid", " ", "Salesforce", self.dest)
        with self.assertRaises(ValueError):
            generate("valid", "Name", " ", self.dest)
        with self.assertRaises(ValueError):
            generate("valid", "Name", "Salesforce", ROOT / "nested-output")

    def test_manifest_rejects_traversal_private_missing_and_symlinks(self):
        source = self.base / "source"
        (source / "config").mkdir(parents=True)
        (source / "ok").write_text("ok")
        (source / "alias").symlink_to(source / "ok")
        (source / ".env").write_text("not-a-real-secret")
        (source / "aliasdir").symlink_to(source / "config", target_is_directory=True)
        for entries in (["../escape"], ["/absolute"], ["missing"], ["alias"], [".env"], ["ok", "ok"], ["aliasdir/scaffold.json"]):
            (source / "config/scaffold.json").write_text(json.dumps({"files": entries}))
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                self.generate(source=source)
            self.assertFalse(self.dest.exists())

    def test_skill_drift_detects_and_repairs(self):
        self.generate()
        skill = next((self.dest / ".claude/skills").glob("*/SKILL.md"))
        skill.write_text("stale")
        self.assertIn(str(skill.relative_to(self.dest)), sync(self.dest, check=True))
        sync(self.dest)
        self.assertEqual(sync(self.dest, check=True), [])

    def test_walkthrough_is_deterministic_and_stops_before_signature(self):
        first = run()
        self.assertEqual(first, run())
        self.assertFalse(first["signature_readiness"]["verified"])
        self.assertFalse(first["proposal"]["applied"])

    def test_generator_cli_success_and_refusal(self):
        args = [sys.executable, 'scripts/new_project.py', '--slug', 'new-case', '--name', 'New Case',
                '--system-of-record', 'Salesforce', '--destination', str(self.dest)]
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        refused = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn('already exists', refused.stderr)

    def test_sync_cli_checks_and_repairs_real_drift(self):
        self.generate()
        args = [sys.executable, 'scripts/sync_skills.py']
        target = next((self.dest / '.claude/skills').glob('*/SKILL.md'))
        target.write_text('stale')
        result = subprocess.run(args + ['--check'], cwd=self.dest, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        subprocess.run(args, cwd=self.dest, capture_output=True, check=True)
        subprocess.run(args + ['--check'], cwd=self.dest, capture_output=True, check=True)
