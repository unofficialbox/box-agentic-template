import copy
import unittest
from pathlib import Path
from box_agentic.runtime import Runtime, ToolError

ROOT = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = Runtime(ROOT)
        self.record_id = "case-demo-001"

    def call(self, name, **kwargs):
        return self.runtime.call(name, {"record_id": self.record_id, **kwargs})

    def test_lookup_and_citations(self):
        record = self.call("get_record")
        docs = self.call("search_documents", document_type="term_sheet")["documents"]
        evidence = self.call("analyze_document", file_id=docs[0]["file_id"])
        self.assertEqual(evidence["facts"]["bank_rate"], 6.85)
        self.assertEqual(evidence["facts"]["requested_rate"], 6.5)
        self.assertEqual(evidence["citation"]["version"], docs[0]["version"])
        self.assertEqual(record["folder_id"], docs[0]["folder_id"])
        self.assertEqual(self.call("search_documents", document_type="absent"), {"documents": []})

    def test_proposals_never_mutate_and_return_independent_copies(self):
        original = copy.deepcopy(self.runtime.data)
        proposal = self.call("propose_update", expected_version="1", changes={"rate": 6.85})
        self.assertFalse(proposal["applied"])
        self.assertTrue(proposal["requires_human_approval"])
        proposal["changes"]["rate"] = 99
        result = self.call("get_record")
        result["fields"]["rate"] = 0
        self.assertEqual(self.runtime.data, original)

    def test_unknown_tool_and_live_mode_refuse(self):
        with self.assertRaises(ToolError):
            self.runtime.call("send_signature", {})
        with self.assertRaises(ToolError):
            Runtime(ROOT, mode="live")

    def test_invalid_arguments(self):
        for changes in ({"ltv": 85}, {"rate": -1}, {"term_months": 1.5}, {"amount": True}, {}):
            with self.subTest(changes=changes), self.assertRaises(ToolError):
                self.call("propose_update", expected_version="1", changes=changes)
        with self.assertRaises(ToolError):
            self.call("get_record", injected=True)
        with self.assertRaises(ToolError):
            self.runtime.call("get_record", {})

    def test_record_resolution_refuses_missing_and_ambiguous(self):
        with self.assertRaises(ToolError):
            self.runtime.call("get_record", {"record_id": "absent"})
        self.runtime.data["records"].append(copy.deepcopy(self.runtime.data["records"][0]))
        with self.assertRaises(ToolError):
            self.call("get_record")

    def test_document_scope_and_ambiguity(self):
        self.runtime.data["documents"][0]["folder_id"] = "other-folder"
        with self.assertRaises(ToolError):
            self.call("analyze_document", file_id="file-demo-terms")
        with self.assertRaises(ToolError):
            self.call("analyze_document", file_id="missing")
        self.runtime.data["documents"].append(copy.deepcopy(self.runtime.data["documents"][1]))
        with self.assertRaises(ToolError):
            self.call("analyze_document", file_id="file-demo-policy")

    def test_stale_and_closed_proposals_refuse(self):
        with self.assertRaises(ToolError):
            self.call("propose_update", expected_version="0", changes={"rate": 7})
        self.runtime.data["records"][0]["status"] = "Closed"
        with self.assertRaises(ToolError):
            self.call("propose_update", expected_version="1", changes={"rate": 7})

    def verify(self, **kwargs):
        return self.call("verify_generated_document", file_id="file-demo-output", job_id=kwargs.get("job_id", "job-demo-001"))

    def test_unapproved_output_is_not_signature_ready(self):
        result = self.verify()
        self.assertFalse(result["verified"])
        self.assertEqual(len(result["reasons"]), 1)

    def test_only_exact_completed_current_output_verifies(self):
        self.runtime.data["records"][0]["status"] = "Approved"
        self.assertTrue(self.verify()["verified"])
        for field, value in (("file_id", "wrong"), ("job_id", "wrong"), ("record_id", "wrong"),
                             ("status", "running"), ("version", "0"), ("record_version", "0"),
                             ("unresolved_tags", ["amount"]), ("terms", {"rate": 99})):
            original = copy.deepcopy(self.runtime.data["generation"])
            self.runtime.data["generation"][field] = value
            self.assertFalse(self.verify()["verified"], field)
            self.runtime.data["generation"] = original
        self.assertFalse(self.verify(job_id="different")["verified"])
        self.runtime.data["documents"][2]["text"] = "Draft {{amount}}"
        self.assertFalse(self.verify()["verified"])
        self.runtime.data["documents"][2]["text"] = "Draft"
        self.runtime.data["documents"][2]["facts"]["rate"] = 99
        self.assertFalse(self.verify()["verified"])

    def test_bad_adapter_output_fails_contract_validation(self):
        self.runtime.data["records"][0]["unexpected"] = "field"
        with self.assertRaises(ToolError):
            self.call("get_record")
