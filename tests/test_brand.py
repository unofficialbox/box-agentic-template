import json
from pathlib import Path
import re
import shutil
import tempfile
import sys
import unittest

from box_agentic.brand import lint, load_brand, visible_text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_deliverables  # noqa: E402


class BrandTests(unittest.TestCase):
    def test_tokens_load_and_colors_are_normalized(self):
        brand = load_brand(ROOT)
        self.assertEqual(brand["colors"]["box_blue"], "#0061D3")
        self.assertIn("Inter Display", brand["typography"]["web_stack"])
        for gradient in brand["gradients"].values():
            self.assertTrue(all(re.fullmatch(r"#[0-9A-F]{6}", c) for c in gradient))
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "config").mkdir()
            bad = dict(brand, colors=dict(brand["colors"], box_blue="#0061d3"))
            (Path(tmp) / "config/brand.json").write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                load_brand(tmp)

    def test_writing_rules_flag_violations_and_pass_clean_copy(self):
        self.assertEqual(lint("Automate and secure workflows, our strategies, and operations, legal, and sales"), [])
        findings = lint("Automate & secure\nThank you!!!\nBox's strategies")
        self.assertEqual(len(findings), 3)
        self.assertIn("line 1", findings[0])

    def test_visible_text_ignores_markup_styles_and_quoted_user_input(self):
        self.assertNotIn("&", visible_text("a.html", "<style>a{b:c}</style><p>Fish &amp; chips</p>").replace("Fish & chips", ""))
        self.assertEqual(visible_text("a.html", "<style>x & y</style><p>ok</p>").strip(), "ok")
        self.assertEqual(visible_text("a.md", "> R&D request\nPlain"), "\nPlain")
        self.assertEqual(lint(visible_text("a.md", "Run `a && b`\n```\nx && y\n```\nQ&A")), [])
        self.assertEqual(visible_text("a.mmd", 'a["R&amp;D &#91;x&#93;"]'), "R&D [x]")

    def test_generated_materials_use_brand_tokens_and_pass_writing_rules(self):
        brand = load_brand(ROOT)
        outputs = build_deliverables.render(ROOT)
        for name, content in outputs.items():
            self.assertEqual(lint(visible_text(name, content), brand), [], name)
        for token in (brand["colors"]["box_blue"], brand["colors"]["container_outline"], *brand["gradients"]["slide_title"]):
            self.assertIn(token, outputs["storyboard.html"])
            self.assertIn(token, outputs["process.svg"])
        self.assertIn("Inter Display", outputs["storyboard.html"])
        self.assertIn("'theme': 'base'", outputs["process.mmd"])
        self.assertNotIn("http", outputs["storyboard.html"].replace("http://www.w3.org/2000/svg", ""))

    def test_renderer_refuses_off_brand_copy_but_quotes_the_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "p"
            for part in ("config", "fixtures", "src", "docs"):
                shutil.copytree(ROOT / part, root / part)
            usecase = json.loads((root / "config/use-case.json").read_text())
            usecase["business_prompt"] = "Our R&D team wants this!!"
            (root / "config/use-case.json").write_text(json.dumps(usecase))
            brief = build_deliverables.render(root)["solution-brief.md"]
            self.assertIn("> Our R&D team wants this!!", brief)
            usecase["outcome"] = "Faster & safer reviews"
            (root / "config/use-case.json").write_text(json.dumps(usecase))
            with self.assertRaisesRegex(ValueError, "Box writing rules"):
                build_deliverables.render(root)

    def test_icon_index_matches_files_and_catalog(self):
        index = json.loads((ROOT / "assets/brand/icons/index.json").read_text())["icons"]
        paths = [i["path"] for i in index]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertGreater(len(paths), 300)
        for entry in index:
            self.assertTrue((ROOT / "assets/brand/icons" / entry["path"]).is_file(), entry["path"])
            self.assertTrue(re.fullmatch(r"[a-z0-9-]+", entry["name"]), entry["name"])
            self.assertTrue((ROOT / "assets/brand/icons/catalog" / (entry["group"].replace("/", "--") + ".png")).is_file())
        on_disk = {str(p.relative_to(ROOT / "assets/brand/icons")) for p in (ROOT / "assets/brand/icons").rglob("*")
                   if p.is_file() and p.parent.name != "catalog" and p.name not in {"index.json", "README.md"}}
        self.assertEqual(on_disk, set(paths))

    def test_scaffold_ships_brand_assets(self):
        files = set(json.loads((ROOT / "config/scaffold.json").read_text())["files"])
        for required in ("config/brand.json", "docs/brand/BOX-BRAND.md", ".agents/skills/box-brand/SKILL.md", "assets/brand/icons/index.json"):
            self.assertIn(required, files)
        self.assertTrue(all(("assets/brand/icons/" + i["path"]) in files
                            for i in json.loads((ROOT / "assets/brand/icons/index.json").read_text())["icons"]))


if __name__ == "__main__":
    unittest.main()
