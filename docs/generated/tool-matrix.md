# Tool matrix

All included implementations are mock-only and read-only. Inspect config/tools.json for exact schemas.

| Tool | Purpose | Platform authority | Implementation | External writes |
|---|---|---|---|---|
| get_record | Read a synthetic structured record and its mapped content folder. | Salesforce | mock | None |
| search_documents | Find synthetic documents by metadata within the record folder. Never searches across records. | Box | mock | None |
| analyze_document | Return curated synthetic facts and a versioned citation. This is a fixture lookup, not an AI model. | Box | mock | None |
| propose_update | Validate a proposed allowlisted field diff against a record version; writes nothing and grants no approval. | Salesforce | mock | None |
| verify_generated_document | Verify the exact synthetic output ID and generation job for signature readiness; no signature action is implemented. | Box + Salesforce | mock | None |
