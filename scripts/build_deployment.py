"""Build a portable deployment contract; no Dispatch checkout, Go, or cloud needed."""
import argparse
import json
from pathlib import Path
import re
from box_agentic.platforms import validate_platforms
from box_agentic.intake import require_ready

ROOT = Path(__file__).resolve().parents[1]


def encoded(value):
    return json.dumps(value, indent=2) + "\n"


def document(scenario, provider, context, *, metadata=None, resources=None):
    return {"version": "1.0", "scenario": scenario, "provider": provider, "context": context,
            "generatedAt": "", "metadata": metadata or {}, "resources": resources or []}


def render(root=ROOT):
    if (root / "config/intake.local.json").exists():
        require_ready(root, root / "config/intake.local.json")
    validate_platforms(root)
    project = json.loads((root / "config/project.json").read_text())
    config = json.loads((root / "config/deployment.json").read_text())
    content = json.loads((root / "config/box/content-model.json").read_text())
    fixture = json.loads((root / "fixtures/workflow.json").read_text())
    if fixture.get("synthetic") is not True:
        raise ValueError("Only explicitly synthetic fixtures may be packaged")
    scenario = project["slug"]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", scenario):
        raise ValueError("Deployment scenario must be a safe project slug")
    workspace = config["workspace"]
    if config["box_strategy"] != "reuse":
        raise ValueError("Portable defaults use reuse; choose a run-specific strategy in Dispatch")
    samples, outputs = [], {}
    for doc in fixture["documents"]:
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", doc["file_id"]):
            raise ValueError("Unsafe fixture file name")
        folder = config["document_folders"][doc["document_type"]]
        if folder not in workspace["children"]:
            raise ValueError("Sample content must target a declared workspace child")
        path = "sample-data/documents/" + doc["file_id"] + ".md"
        if path in outputs:
            raise ValueError("Duplicate sample file name")
        outputs[path] = doc["text"] + "\n"
        samples.append({"source": path, "target_folder": folder})
    defaults = {"global_strategy": "reuse", "naming": {"pattern": "{name} - {suffix}"},
                "rollback": {"enabled": True, "directory": ".dispatch/deployments", "retain": 10},
                "component_strategies": {}, "components": {"mode": "defaults", "selections": {}}}
    manifest = {"schema_version": "1.0", "template_id": scenario, "deployment_config": ".dispatch/deployment.bcl",
                "salesforce": {"required_packages": [], "required_permission_sets": [], "seed_scripts": []},
                "box": {"deployment_defaults": defaults, "component_order": ["Folder Structure", "Metadata Template", "Sample Content"],
                        "workspace": {"component_type": "Folder Structure", "display_name": workspace["name"],
                                      "name": workspace["name"], "children": workspace["children"]},
                        "sample_content": samples, "capabilities": [
                            {"id": "folder_structure", "component_type": "Folder Structure", "enabled_by_default": True,
                             "api": "public", "handler": "box.folder-tree", "operations": ["validate", "deploy"]},
                            {"id": "metadata_template", "component_type": "Metadata Template", "enabled_by_default": True,
                             "api": "public", "handler": "box.metadata-template", "operations": ["validate", "deploy"]},
                            {"id": "sample_content", "component_type": "Sample Content", "enabled_by_default": True,
                             "api": "public", "handler": "box.file-upload", "operations": ["validate", "deploy"]}]}}
    outputs["dispatch.bcl"] = encoded(document(scenario, "box-dispatch", "solution-manifest", metadata={"manifest": manifest}))
    outputs[".dispatch/deployment.bcl"] = encoded(document("", "box-dispatch", "deployment-settings",
        metadata={"settings": {"schema_version": "1.0", "box": defaults}}))
    templates = [{"templateKey": content["template_key"], "displayName": "Agentic Document",
                  "fields": [{"key": f["key"], "type": f["type"], "displayName": f["key"]} for f in content["fields"]]}]
    outputs["config/box/metadata-templates.bcl"] = encoded(document(scenario, "generic", "box-metadata-templates", resources=[{
        "name": "agentic_document_template", "type": "config_file", "provider": "generic",
        "config": {"templates": templates}}]))
    return outputs


def build(root=ROOT, *, check=False):
    drift = []
    for name, content in render(root).items():
        path = root / name
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p.is_relative_to(root)):
            raise ValueError("Deployment output must not be a symlink")
        if not path.exists() or path.read_text() != content:
            drift.append(name)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
    return drift


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    drift = build(check=args.check)
    if args.check and drift:
        raise SystemExit("Stale deployment artifacts: " + ", ".join(drift))
    print("Deployment artifacts match" if args.check else "Built standalone deployment assets and Dispatch BCL interface")
