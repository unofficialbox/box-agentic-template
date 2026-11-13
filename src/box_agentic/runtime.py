"""Mock adapters enforce the same contracts served over MCP. No network or writes."""
from copy import deepcopy
import json
from pathlib import Path
from jsonschema import Draft202012Validator


class ToolError(ValueError):
    """A bounded failure safe to return to a tool caller."""


class Runtime:
    def __init__(self, root: Path, *, mode: str = "mock"):
        if mode != "mock":
            raise ToolError("Live adapters are not implemented; use mock mode")
        self.tools = json.loads((root / "config/tools.json").read_text())["tools"]
        self.data = json.loads((root / "fixtures/workflow.json").read_text())
        if self.data.get("synthetic") is not True:
            raise ToolError("Mock runtime requires explicitly synthetic fixtures")
        self._contracts = {t["name"]: t for t in self.tools}
        if len(self._contracts) != len(self.tools) or set(self._contracts) != {
            "get_record", "search_documents", "analyze_document",
            "propose_update", "verify_generated_document",
        }:
            raise ToolError("Tool registry and mock handlers disagree")
        for contract in self.tools:
            for key in ("inputSchema", "outputSchema"):
                Draft202012Validator.check_schema(contract[key])

    def record(self, record_id):
        matches = [r for r in self.data["records"] if r["record_id"] == record_id]
        if len(matches) != 1:
            raise ToolError("Record missing or ambiguous")
        return matches[0]

    def document(self, record, file_id):
        matches = [d for d in self.data["documents"] if d["file_id"] == file_id]
        if len(matches) != 1 or matches[0]["folder_id"] != record["folder_id"]:
            raise ToolError("Document missing, ambiguous, or outside record scope")
        return matches[0]

    def call(self, name, arguments):
        contract = self._contracts.get(name)
        if contract is None:
            raise ToolError("Unknown tool")
        if list(Draft202012Validator(contract["inputSchema"]).iter_errors(arguments)):
            raise ToolError("Arguments do not match the tool input schema")
        result = getattr(self, "_" + name)(**deepcopy(arguments))
        if list(Draft202012Validator(contract["outputSchema"]).iter_errors(result)):
            raise ToolError("Adapter returned an invalid result")
        return deepcopy(result)

    def _get_record(self, record_id):
        return self.record(record_id)

    def _search_documents(self, record_id, document_type):
        record = self.record(record_id)
        return {"documents": [d for d in self.data["documents"]
                if d["folder_id"] == record["folder_id"]
                and d["document_type"] == document_type]}

    def _analyze_document(self, record_id, file_id):
        doc = self.document(self.record(record_id), file_id)
        return {"facts": doc["facts"], "citation": {
            "file_id": file_id, "version": doc["version"], "location": "synthetic fixture, full text"}}

    def _propose_update(self, record_id, expected_version, changes):
        record = self.record(record_id)
        if record["version"] != expected_version:
            raise ToolError("Record changed; re-read before proposing")
        if record["status"] not in {"Underwriting", "Credit Review"}:
            raise ToolError("Record state does not allow term proposals")
        if not changes:
            raise ToolError("A proposal needs at least one changed field")
        return {"record_id": record_id, "expected_version": expected_version,
                "before": {k: record["fields"].get(k) for k in changes}, "changes": changes,
                "requires_human_approval": True, "applied": False}

    def _verify_generated_document(self, record_id, file_id, job_id):
        record = self.record(record_id)
        doc = self.document(record, file_id)
        generation = self.data["generation"]
        reasons = []
        if (generation["file_id"], generation["job_id"], generation["record_id"]) != (file_id, job_id, record_id):
            reasons.append("Output is not bound to this record and generation job")
        if generation["status"] != "completed":
            reasons.append("Generation is not complete")
        if generation["version"] != doc["version"] or generation["record_version"] != record["version"]:
            reasons.append("Document or record version changed")
        if generation["unresolved_tags"] or "{{" in doc["text"] or "}}" in doc["text"]:
            reasons.append("Output contains unresolved tags")
        if generation["terms"] != record["fields"] or doc["facts"] != generation["terms"]:
            reasons.append("Output terms do not match the current record")
        if record["status"] not in {"Approved", "Commitment"}:
            reasons.append("Record is not approved for signature preparation")
        return {"verified": not reasons, "reasons": reasons, "file_id": file_id,
                "version": doc["version"], "job_id": job_id}
