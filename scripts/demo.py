"""Deterministic fixture walkthrough; never invokes remote services."""
import json
from pathlib import Path
from box_agentic.runtime import Runtime

ROOT = Path(__file__).resolve().parents[1]


def run(root=ROOT):
    runtime = Runtime(root)
    record = runtime.call("get_record", {"record_id": "case-demo-001"})
    documents = runtime.call("search_documents", {"record_id": record["record_id"], "document_type": "term_sheet"})
    evidence = runtime.call("analyze_document", {"record_id": record["record_id"], "file_id": documents["documents"][0]["file_id"]})
    proposal = runtime.call("propose_update", {"record_id": record["record_id"], "expected_version": record["version"],
                                             "changes": {"rate": evidence["facts"]["bank_rate"]}})
    verification = runtime.call("verify_generated_document", {"record_id": record["record_id"],
                                                              "file_id": "file-demo-output", "job_id": "job-demo-001"})
    return {"readiness": "offline-verified", "synthetic": True, "evidence": evidence,
            "proposal": proposal, "signature_readiness": verification, "external_writes": 0}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
