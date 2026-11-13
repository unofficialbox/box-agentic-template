# Use-case definition

The included reference is a **synthetic commercial loan review**, not a live deployment. The machine-readable narrative and original request are in `config/use-case.json`; generated materials live in `docs/generated/`.

| Decision | Reference choice |
|---|---|
| Business outcome | Source-cited review, proposed bank terms, checked draft |
| Primary actor | Loan officer |
| Content authority | Box; simulated by synthetic documents locally |
| Record authority | Example CRM; simulated by a versioned fixture |
| Consequential decision owner | Credit officer |
| Document classes | Term sheet, policy, generated draft |
| Proposed fields | Amount, rate, term in months |
| Fixture boundary | No production records, policy advice, or live AI inference |
| Completion | Review evidence and proposal are available; unapproved signature action is held |

## Acceptance

- The bank rate (6.85%) and borrower-requested rate (6.50%) remain distinct.
- File findings include a file ID, version, and evidence location.
- A proposal has `applied: false` and cannot update a record.
- Document lookup cannot cross record-folder boundaries.
- Wrong generation jobs, stale versions, unresolved tags, inconsistent terms, and unapproved record states fail signature readiness.
- Both narrative and code identify the missing live adapters.

For a new domain, replace these decisions, the structured narrative, fixtures, schemas, handlers, and acceptance tests together. Capture assumptions and intended success and blocked paths; avoid retaining loan-specific labels or logic accidentally.
