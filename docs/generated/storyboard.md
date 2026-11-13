# Commercial Loan Review: demo storyboard

**Platforms: Box + Salesforce. Evidence level: synthetic fixture.**

A source-cited loan review and a checked draft, with human credit approval retained.

## Beat 1: Resolve Salesforce record and Box package

**Actor:** Loan officer

**Say / ask:** Show the Salesforce loan record and the Box folder that owns its documents.

**Show:** Read the Salesforce record and its mapped Box folder.

**Expected evidence:** Record case-demo-001 is Underwriting at version 1.

**Failure path:** Stop if the record is missing or ambiguous.

## Beat 2: Find and analyze the term sheet

**Actor:** Loan officer

**Say / ask:** Compare the bank rate and borrower-requested rate in the term sheet.

**Show:** Find term_sheet documents in the mapped Box folder and cite their versioned facts.

**Expected evidence:** Bank rate 6.85%; borrower requests 6.50%; cite file-demo-terms version 1.

**Failure path:** Reject an unrelated folder or unsupported source claim.

## Beat 3: Propose the bank terms

**Actor:** Loan officer

**Say / ask:** Propose the bank rate for review; keep the record unchanged.

**Show:** Create a reviewable Salesforce rate diff against the current record version.

**Expected evidence:** Proposal requires human approval and applied is false.

**Failure path:** Reject stale versions, unknown fields, and invalid amounts.

## Beat 4: Human credit decision

**Actor:** Credit officer

**Say / ask:** Who owns this decision, and what evidence remains before proceeding?

**Show:** Review the Box evidence and authorize the exact consequential action in Salesforce.

**Expected evidence:** The credit officer owns approval. No approval or write is fabricated.

**Failure path:** Hold the action when authorization or capability is missing.

## Beat 5: Verify the exact generated draft

**Actor:** Loan officer

**Say / ask:** Is this draft ready for signature preparation?

**Show:** Check job-demo-001 and file-demo-output against current terms and lifecycle state.

**Expected evidence:** Not ready: the record is Underwriting. No signature is prepared or sent.

**Failure path:** Hold mismatched jobs, stale versions, unresolved tags, and unapproved records.
