"""Render the maintained Salesforce Multi-Framework React site template into salesforce-project.

The editable source is templates/salesforce/portal-site (an Experience Cloud site plus a React
UI bundle). This script copies it into salesforce-project/force-app/main/default, renames the
BoxPortalTemplate placeholders, writes the portal configuration, and applies the Box brand
tokens. It runs offline and needs no Node or Salesforce CLI.
"""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path("templates/salesforce/portal-site/force-app/main/default")
TARGET = Path("salesforce-project/force-app/main/default")
TOKEN = "BoxPortalTemplate"
NAME = re.compile(r"[A-Za-z][A-Za-z0-9]{1,38}")
FIELD = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
BRAND = re.compile(r"(/\* BOX BRAND START[^\n]*\*/\n)(.*?)(/\* BOX BRAND END \*/)", re.S)
TEXT = {".ts", ".tsx", ".js", ".mjs", ".json", ".css", ".html", ".xml", ".md", ".yml", ".yaml", ".cls", ".graphql", ".svg", ""}


def load_portal(root=ROOT):
    path = Path(root) / "config/salesforce/portal.json"
    if not path.exists():
        return None
    portal = json.loads(path.read_text())
    if not portal.get("enabled"):
        return None
    if not NAME.fullmatch(portal["site_name"]):
        raise ValueError("Portal site_name must be 2-39 letters or digits and start with a letter")
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,39}", portal["url_path_prefix"]):
        raise ValueError("Portal url_path_prefix must be lowercase letters, digits, or hyphens")
    site = portal["site"]
    record = site["record"]
    names = [record["object"], record["title_field"], record.get("stage_field"), record.get("status_field"),
             *[f["api_name"] for f in record["fields"]]]
    if site.get("documents"):
        d = site["documents"]
        names += [d["relationship"], d["type_field"], d["status_field"], d.get("version_field")]
    if any(n is not None and not FIELD.fullmatch(n) for n in names):
        raise ValueError("Portal config contains an invalid Salesforce API name")
    if any(t not in {"pass", "wait", "fail"} for t in site.get("status_tone", {}).values()):
        raise ValueError("Portal status_tone values must be pass, wait, or fail")
    return portal


def brand_css(brand):
    c, s, font = brand["colors"], brand["status"], brand["typography"]["web_stack"]
    g = brand["gradients"]
    return (":root {\n"
            f"  --primary: {c['box_blue']};\n  --primary-foreground: {c['white']};\n  --ring: {c['box_blue']};\n"
            f"  --foreground: {c['body_dense']};\n  --title: {c['title_start']};\n  --border: {c['container_outline']};\n"
            f"  --pass: {s['pass']};\n  --wait: {s['warn']};\n  --fail: {s['fail']};\n  --destructive: {c['alert']};\n"
            "  --radius: 1rem;\n}\n"
            f"body {{ font-family: {font}; background: linear-gradient({', '.join(g['light_background'])}) fixed; }}\n"
            f".portal-title {{ color: {c['title_start']}; background: linear-gradient(90deg, {', '.join(g['slide_title'])}); "
            "-webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }\n"
            f".portal-card {{ display: block; padding: 1.5rem; border-radius: 1rem; border: 1px solid {c['container_outline']}; "
            f"background: linear-gradient({', '.join(g['container_fill'])}); box-shadow: {brand['shapes']['shadow']}; color: inherit; }}\n")


def render(root=ROOT):
    """Return {relative output path: bytes} for the portal, or {} when the portal option is off."""
    root = Path(root)
    portal = load_portal(root)
    if portal is None:
        return {}
    brand = json.loads((root / "config/brand.json").read_text())
    name, prefix = portal["site_name"], portal["url_path_prefix"]
    replacements = [(TOKEN + "vforcesite", prefix + "vforcesite"), (TOKEN, name), (TOKEN.lower(), prefix),
                    ("__PORTAL_TITLE__", portal["site"]["title"])]
    if portal.get("email_sender"):
        replacements.append(("admin@company.com", portal["email_sender"]))
    source = root / TEMPLATE
    outputs = {}
    for path in sorted(p for p in source.rglob("*") if p.is_file()):
        rel = path.relative_to(source).as_posix().replace(TOKEN, name)
        data = path.read_bytes()
        if path.suffix in TEXT:
            text = data.decode()
            for old, new in replacements:
                text = text.replace(old, new)
            if rel.endswith("src/styles/global.css"):
                text = BRAND.sub(lambda m: m.group(1) + brand_css(brand) + m.group(3), text)
            if rel.endswith("src/portal/portal.config.json"):
                text = json.dumps(portal["site"], indent=2) + "\n"
            data = text.encode()
        outputs[(TARGET / rel).as_posix()] = data
    return outputs


def build(root=ROOT, *, check=False):
    root = Path(root)
    drift = []
    for rel, content in render(root).items():
        path = root / rel
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p.is_relative_to(root)):
            raise ValueError("Portal output must not be a symlink")
        if not path.exists() or path.read_bytes() != content:
            drift.append(rel)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    return drift


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if load_portal(ROOT) is None:
        print("Portal option is off (config/salesforce/portal.json enabled: false)")
        raise SystemExit(0)
    drift = build(check=args.check)
    if args.check and drift:
        raise SystemExit("Stale portal source: " + ", ".join(drift[:10]) + (" …" if len(drift) > 10 else ""))
    print("Portal source matches" if args.check else "Built Salesforce Multi-Framework React site")
