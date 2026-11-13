# Tool matrix

All included implementations are mock-only and read-only. Inspect config/tools.json for exact schemas.

| Tool | Purpose | Implementation | External writes |
|---|---|---|---|
| get_record | Read a synthetic structured record and its mapped content folder. | mock | None |
| search_documents | Find synthetic documents by metadata within the record folder. Never searches across records. | mock | None |
| analyze_document | Return curated synthetic facts and a versioned citation. This is a fixture lookup, not an AI model. | mock | None |
| propose_update | Validate a proposed allowlisted field diff against a record version; writes nothing and grants no approval. | mock | None |
| verify_generated_document | Verify the exact synthetic output ID and generation job for signature readiness; no signature action is implemented. | mock | None |
