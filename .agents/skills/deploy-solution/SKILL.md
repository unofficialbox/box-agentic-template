---
name: deploy-solution
description: Prepare or deploy the generated Box and Salesforce solution either standalone through platform tools or through Box Dispatch.
---

# Deploy Solution

Read `docs/DEPLOYMENT.md`, `config/deployment.json`, and `dispatch.bcl` from the project root. Both Box and Salesforce are required; deployment readiness is separate from the fixture walkthrough.

Choose the user's requested lane. Standalone operation must not require a Dispatch checkout or Go. Use available authenticated platform connectors or native APIs for Box and Salesforce. For Dispatch, prepare its BCL interface and the Salesforce DX source; let Dispatch own connections, validation previews, provider calls, and resource receipts. Never shell out to Salesforce CLI from the Dispatch lane.

Before preparing a release, regenerate Salesforce metadata, deployment assets, and demo materials with the documented scripts, then run the standalone validator. Run `scripts/check_dispatch.py` only when an explicit Dispatch source checkout and Go are available. This is an optional compatibility test, not a runtime prerequisite.

Inspect actual tool schemas and target identities. Verify the Salesforce org and Box parent folder and preserve authorization already given for the exact action/target. If authorization is missing, complete the local plan before requesting it. Never infer cloud-write authorization from a request to create or review the template.

Deploy only the declared supported scope. The starter provisions a Box folder tree, document metadata template, synthetic sample files, and a Salesforce custom object/fields. It does not deploy the mock MCP server as a live service, enable Agentforce, approve credit, sign documents, or bind live records automatically. For additional components, add real sources and verified deployment contracts before advertising support.

After deployment, use returned resource IDs to bind real Salesforce records to their exact Box folders and apply document metadata. Verify those bindings under the intended user, then test live source reads, allowed and rejected record changes, uncertain completion, and reset. On an ambiguous write response, reconcile the exact operation before retrying. Keep credentials and receipts outside portable source. Reset only recorded created IDs; never delete Box root 0 or name-match resources for deletion.

Report package compatibility, provider validation, actual deployment, record/folder binding, and live workflow acceptance separately. A successful offline Dispatch plan establishes none of the later stages.
