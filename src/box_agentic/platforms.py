"""Validate required Box/Salesforce authorities and their cross-system mapping."""
import json
import re


def validate_platforms(root):
    config = json.loads((root / "config/platforms.json").read_text())
    project = json.loads((root / "config/project.json").read_text())
    if config.get("required_platforms") != ["box", "salesforce"] or project.get("required_platforms") != ["box", "salesforce"]:
        raise ValueError("Both Box and Salesforce are required")
    if project.get("system_of_record") != "Salesforce":
        raise ValueError("Salesforce must own structured records")
    if config["box"]["role"] != "governed_content" or config["salesforce"]["role"] != "structured_record":
        raise ValueError("Box/Salesforce authority roles disagree")
    sf = config["salesforce"]
    for name in [sf["object_api_name"], sf["external_id_field"], sf["folder_id_field"], sf["status_field"], *sf["field_mapping"].values()]:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*__c", name):
            raise ValueError("Invalid Salesforce custom API name")
    if config["box"]["folder_binding"] != "salesforce." + sf["folder_id_field"]:
        raise ValueError("Box scope must resolve from the Salesforce folder field")
    tools = json.loads((root / "config/tools.json").read_text())["tools"]
    if set(config["tool_authorities"]) != {t["name"] for t in tools}:
        raise ValueError("Every tool needs a platform authority")
    for owners in config["tool_authorities"].values():
        if not owners or len(set(owners)) != len(owners) or set(owners) - {"box", "salesforce"}:
            raise ValueError("Invalid tool platform authority")
    required_owners = {"get_record": {"salesforce"}, "propose_update": {"salesforce"},
                       "search_documents": {"box"}, "analyze_document": {"box"},
                       "verify_generated_document": {"box", "salesforce"}}
    for name, owners in required_owners.items():
        if set(config["tool_authorities"].get(name, [])) != owners:
            raise ValueError("Tool ownership must preserve Box/Salesforce authority boundaries")
    for tool in tools:
        if "changes" in tool["inputSchema"]["properties"]:
            fields = tool["inputSchema"]["properties"]["changes"]["properties"]
            if set(fields) - sf["field_mapping"].keys():
                raise ValueError("Proposed fields need Salesforce field mappings")
    return config
