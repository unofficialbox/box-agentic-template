# Box + Salesforce are included

Every generated project contains both platform blueprints and a Salesforce metadata starter. A business prompt selects the domain; it does not remove either platform. The offline runtime simulates their responsibilities without requiring accounts.

| Platform | Authority | Included starter |
|---|---|---|
| Box | Governed files, document metadata, source versions, policy evidence, generated documents | `config/box/content-model.json`, scoped document/analysis mock tools |
| Salesforce | Business records, structured fields, workflow state, authorization of record changes | `config/salesforce/object.json`, generated `salesforce-project/`, record/proposal mock tools |
| Cross-system | Salesforce record → authorized Box folder → cited documents → proposed Salesforce changes | `config/platforms.json`, generated-output verification, fixtures, storyboard |

## Portable configuration

`config/platforms.json` defines required platforms, authority roles, tool ownership, and the Salesforce field mapping. The starter uses `Agentic_Work_Item__c`:

- `External_Key__c`: stable business reference for duplicate-safe lookup/upsert in a future adapter.
- `Box_Folder_ID__c`: exact Box folder mapped to this Salesforce record.
- `Status__c`: lifecycle state; tailor its domain values and server-side transition rules.
- `Amount__c`, `Rate__c`, `Term_Months__c`: reference loan fields; replace for another business use case.
- `SystemModstamp`: Salesforce's standard record version source; a live adapter must use the platform's supported concurrency mechanism, not the fixture's numeric version.

The Box document metadata blueprint includes `salesforceRecordId`, `documentType`, and `versionStatus`. It is a portable specification, not a ready-to-submit Box API request. A live adapter must verify the authenticated user's access to the Salesforce record and the mapped Box folder. Never trust a caller-supplied folder or a document's record ID as authorization. Keep employee-only notes and findings out of any object that inherits a customer-visible record's sharing; use the internal notes pattern in [SALESFORCE-SURFACES.md](SALESFORCE-SURFACES.md#employee-only-notes-internal-notes-pattern).

Copy `config/runtime.example.json` to ignored `config/runtime.local.json` for tenant-specific non-secret Box and Salesforce bindings. Use existing authenticated connectors or a credential store; do not put tokens or client secrets in these files.

## Salesforce metadata starter

Edit `config/salesforce/object.json` and `config/platforms.json` together, then run:

```bash
python scripts/build_salesforce.py
python scripts/build_salesforce.py --check
```

The renderer creates Salesforce DX object/field metadata and project configuration under `salesforce-project/`. Object sharing defaults to Private. The version starts at 67.0, matching the reviewed loans reference; confirm compatibility with your target org before validation or deployment. `deploymentStatus=Deployed` is a Salesforce metadata property, not a claim that this project has been deployed.

This starter does not provision a Box folder, deploy Apex, grant permissions, register a hosted MCP server, enable Agentforce, or install Box for Salesforce. Choose authenticated connectors and implement the integration surface appropriate to the business prompt. Keep deployment sources, user permissions, server-side access checks, and live tests in the generated project's implementation scope.

## Tool routing

- Salesforce: `get_record` and `propose_update` model record reads and an unapplied diff.
- Box: `search_documents` and `analyze_document` model scoped content lookup and versioned evidence.
- Box + Salesforce: `verify_generated_document` reconciles exact output/job identity with record terms, version, and lifecycle state.

These are local contract names, not assumed provider MCP names. The connect-tools skill must discover both providers' actual schemas and map them explicitly. A missing connector stays a reported live integration gap.

## Business prompt requirements

Keep both systems visible in the process diagram, storyboard, code/configuration, and acceptance checks. For supplier onboarding, for example, Box stores certificates and contracts; Salesforce stores supplier onboarding status and the mapped folder; a procurement manager approves exceptions. Tailor fields and tests rather than retaining loan math.

## Deployment lanes

Both platform source sets ship in every generated project. See [standalone and Box Dispatch deployment](DEPLOYMENT.md) for native platform deployment, the BCL package interface, declared deployable scope, and explicit post-deployment record/folder binding. Dispatch support does not create a runtime dependency on Dispatch.
