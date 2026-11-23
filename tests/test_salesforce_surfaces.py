import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_agent  # noqa: E402
import build_portal  # noqa: E402


def project_copy(tmp):
    root = Path(tmp) / "p"
    for part in ("config", "templates"):
        shutil.copytree(ROOT / part, root / part)
    return root


def edit(root, rel, change):
    path = root / rel
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


class PortalTests(unittest.TestCase):
    def test_disabled_portal_renders_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project_copy(tmp)
            edit(root, "config/salesforce/portal.json", lambda p: p.update(enabled=False))
            self.assertEqual(build_portal.render(root), {})

    def test_enabled_portal_renames_tokens_and_applies_config_and_brand(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project_copy(tmp)
            edit(root, "config/salesforce/portal.json", lambda p: p.update(enabled=True, site_name="WealthPortal", url_path_prefix="wealth"))
            out = build_portal.render(root)
            base = "salesforce-project/force-app/main/default/"
            for rel in ("uiBundles/WealthPortal/WealthPortal.uibundle-meta.xml", "networks/WealthPortal.network-meta.xml",
                        "sites/WealthPortal.site-meta.xml", "digitalExperienceConfigs/WealthPortal1.digitalExperienceConfig-meta.xml",
                        "uiBundles/WealthPortal/src/pages/RecordDetail.tsx"):
                self.assertIn(base + rel, out)
            for rel, data in out.items():
                self.assertNotIn("BoxPortalTemplate", rel)
                if not rel.endswith(".png"):
                    text = data.decode()
                    self.assertNotIn("BoxPortalTemplate", text, rel)
                    self.assertNotIn("__PORTAL_TITLE__", text, rel)
            site = json.loads((root / "config/salesforce/portal.json").read_text())["site"]
            config = json.loads(out[base + "uiBundles/WealthPortal/src/portal/portal.config.json"])
            self.assertEqual(config, site)
            css = out[base + "uiBundles/WealthPortal/src/styles/global.css"].decode()
            self.assertIn("--primary: #0061D3", css)
            self.assertIn("Inter Display", css)
            self.assertIn("<urlPathPrefix>wealthvforcesite</urlPathPrefix>", out[base + "sites/WealthPortal.site-meta.xml"].decode())
            self.assertEqual(sorted(build_portal.build(root)), sorted(out))
            self.assertEqual(build_portal.build(root, check=True), [])

    def test_invalid_portal_config_refuses(self):
        cases = [lambda p: p.update(site_name="bad name"), lambda p: p.update(url_path_prefix="Bad_Prefix"),
                 lambda p: p["site"]["record"].update(object="Opportunity; DROP"),
                 lambda p: p["site"].update(status_tone={"Approved": "green"})]
        for change in cases:
            with tempfile.TemporaryDirectory() as tmp:
                root = project_copy(tmp)
                edit(root, "config/salesforce/portal.json", lambda p, c=change: (p.update(enabled=True), c(p)))
                with self.assertRaises(ValueError):
                    build_portal.render(root)

    def test_site_template_keeps_maintained_customizations(self):
        src = ROOT / "templates/salesforce/portal-site/force-app/main/default/uiBundles/BoxPortalTemplate/src"
        routes = (src / "routes.tsx").read_text()
        self.assertIn("records/:recordId", routes)
        self.assertNotIn("TestChatPage", routes)
        self.assertIn("BOX BRAND START", (src / "styles/global.css").read_text())
        self.assertIn("hidden_types", (src / "pages/RecordDetail.tsx").read_text())


class AgentTests(unittest.TestCase):
    def test_agent_script_structure_and_action_bindings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project_copy(tmp)
            generated, seeds = build_agent.render(root)
            agent = json.loads((root / "config/salesforce/agent.json").read_text())
            name = agent["developer_name"]
            script = generated[f"salesforce-project/force-app/main/default/aiAuthoringBundles/{name}/{name}.agent"]
            for block in ("system:", "config:", "start_agent agent_router:", "subagent off_topic:"):
                self.assertIn(block, script)
            self.assertIn(f'developer_name: "{name}"', script)
            self.assertIn('agent_type: "AgentforceEmployeeAgent"', script)
            self.assertNotIn("default_agent_user", script)
            self.assertNotIn("{{", script)
            self.assertIsNone(re.search(r":\s*(true|false)\s*$", script, re.M))
            self.assertNotIn("\t", script)
            for s in agent["subagents"]:
                self.assertIn(f"subagent {s['name']}:", script)
                self.assertIn(f"@utils.transition to @subagent.{s['name']}", script)
            for target in re.findall(r'target: "apex://(\w+)"', script):
                self.assertIn(f"salesforce-project/force-app/main/default/classes/{target}.cls", seeds)
            tools = {t["name"]: t for t in json.loads((root / "config/tools.json").read_text())["tools"]}
            self.assertIn("require_user_confirmation: True", script) if any(
                not tools[t]["annotations"]["readOnlyHint"] for s in agent["subagents"] for t in s["tools"]) else None
            first = agent["subagents"][0]["tools"][0]
            cls = agent["apex_prefix"] + "".join(part.capitalize() for part in first.split("_"))
            stub = seeds[f"salesforce-project/force-app/main/default/classes/{cls}.cls"]
            for key in tools[first]["inputSchema"].get("properties", {}):
                self.assertIn(f" {key};", stub)
            self.assertIn("live_adapter_not_implemented", stub)
            for key in agent.get("record_inputs", ["record_id"]):
                if any(key in tools[t]["inputSchema"].get("properties", {}) for s in agent["subagents"] for t in s["tools"]):
                    self.assertIn(f"with {key} = @variables.record_id", script)

    def test_seeded_apex_is_never_overwritten_but_script_drift_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project_copy(tmp)
            build_agent.build(root)
            stub = next((root / "salesforce-project/force-app/main/default/classes").glob("*.cls"))
            stub.write_text("// implemented by hand")
            self.assertEqual(build_agent.build(root, check=True), [])
            build_agent.build(root)
            self.assertEqual(stub.read_text(), "// implemented by hand")
            script = next((root / "salesforce-project/force-app/main/default/aiAuthoringBundles").rglob("*.agent"))
            script.write_text("stale")
            self.assertEqual(len(build_agent.build(root, check=True)), 1)

    def test_invalid_agent_config_refuses(self):
        cases = [lambda a: a["subagents"][0]["tools"].append("missing_tool"),
                 lambda a: a.update(agent_type="AgentforceServiceAgent"),
                 lambda a: a.update(developer_name="Bad__Name"),
                 lambda a: a["subagents"].append(dict(a["subagents"][0])),
                 lambda a: a.update(agent_type="Other")]
        for change in cases:
            with tempfile.TemporaryDirectory() as tmp:
                root = project_copy(tmp)
                edit(root, "config/salesforce/agent.json", change)
                with self.assertRaises(ValueError):
                    build_agent.render(root)

    def test_disabled_agent_renders_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = project_copy(tmp)
            edit(root, "config/salesforce/agent.json", lambda a: a.update(enabled=False))
            self.assertEqual(build_agent.render(root), ({}, {}))


if __name__ == "__main__":
    unittest.main()
