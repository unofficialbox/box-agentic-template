# Standalone and Box Dispatch deployment

This is a self-contained source template. All domain code, schemas, synthetic fixtures, skills, Salesforce DX metadata, Box deployment assets, diagrams, and storyboard materials ship in the project. Its generator, validator, fixture demo, and renderers need only the declared Python dependencies and Git for creating repositories. No sibling repository, Go runtime, Dispatch installation, cloud login, or global agent skills are required for those workflows.

Deployment has two supported preparation paths. Both use the same included assets; neither requires copying implementation files from the inspiration repositories.

## Deployment scope

| Included deployment asset | Result |
|---|---|
| `dispatch.bcl` workspace and `config/deployment.json` | Box workspace with three stage folders |
| `config/box/metadata-templates.bcl` | Box document metadata template |
| `sample-data/documents/` and manifest sample list | Three synthetic document files |
| `salesforce-project/` | Salesforce custom object and six reference fields |

The included runtime remains a mock. Deploying these assets does not deploy live workflow adapters, host the MCP server, enable Agentforce, install Box for Salesforce, apply metadata instances, seed business records, or create record-to-folder bindings. Those are explicit implementation/acceptance steps for the generated business use case. Add actual source and supported handlers before expanding advertised deployment scope.

## 1. Prepare independently

```bash
python scripts/build_salesforce.py
python scripts/build_deployment.py
python scripts/build_deliverables.py
python scripts/validate.py
```

The deployment renderer derives package identity from `config/project.json`, the folder tree from `config/deployment.json`, metadata from the Box blueprint, and sample content from the synthetic fixtures. Generated sibling projects refresh the manifest's scenario/template ID. The scaffold includes all referenced files, with no Git history, credentials, installed dependencies, live receipts, or private tenant configuration.

`dispatch.bcl` and Box capability files use the canonical JSON payload form of BCL, which Dispatch's real parser accepts. They carry the proper provider/context/resource envelopes; they are not JSON renamed to bypass the contract. Developer `--check` commands compare rendered source. Dispatch may normalize BCL to its HCL-like form and change deployment settings in its assembled operator package; run source drift checks in the original project, not as a reset of the operator's package.

## 2A. Deploy standalone

No Dispatch installation is needed. Give your coding agent the `deploy-solution` skill and use authenticated Box and Salesforce connectors or platform-native APIs:

1. Review the supported scope and exact tenant identities. Confirm the non-root Box parent folder and Salesforce org.
2. Deploy `salesforce-project/force-app` through the Salesforce Metadata API or your existing Salesforce deployment tool. The included source is Salesforce DX format; use a source-aware converter when the selected tool requires a Metadata API ZIP. Validate against the target org before applying. Salesforce CLI is an optional standalone tool, not a template prerequisite.
3. Read the Box workspace/children and sample source mappings from `dispatch.bcl` → `metadata.manifest.box`. Create or reuse the exact authorized folder tree; reconcile conflicts instead of choosing a similarly named folder.
4. Read `config/box/metadata-templates.bcl` → `resources[0].config.templates`. Translate each template to the connector's discovered schema, using enterprise scope. The local BCL wrapper itself is not a Box API request.
5. Upload only the declared sample files into their mapped stage folders. Record every created resource ID and verify each response.
6. Assign appropriate Salesforce permissions, create the intended business records, and bind each real record's `Box_Folder_ID__c` to the verified Box folder ID. Apply the Box document metadata linking files to those records.
7. Implement/connect live adapters and rehearse the actual use case. Until then, describe the result as deployed infrastructure with an offline workflow example.

The deployment skill orchestrates available tools; the template does not include an autonomous cloud-write command or provision credentials. Missing connector permissions/capabilities are reported explicitly. Keep local bindings in ignored files and tokens in your existing credential store.

## 2B. Deploy through Box Dispatch

Dispatch owns authentication and native provider calls. Do not replace its browser OAuth flow with Salesforce CLI commands or collect client secrets in the template.

1. Commit the intended generated project, or publish it to your own Git repository. Dispatch's package builder clones committed Git content; an uncommitted working tree is not its source.
2. In an isolated Dispatch profile, add a scenario to its runtime `environment.json` with the generated project's slug as the key, a `displayName`, `providers: ["box", "salesforce-agentforce"]`, and `repository` pointing to that committed local Git repository or your Git URL. Preserve other scenarios and provider settings. The browser template catalog is built from these configured scenarios; this project is not automatically registered in Dispatch's bundled catalog.
3. Start Dispatch's browser workspace, select that scenario, and include **both Box and Salesforce**. Dispatch currently requires Box but does not enforce this template's Salesforce requirement globally; a Box-only selection will prune Salesforce source. Treat that selection as unsupported for this template.
4. Connect/select the exact Box and Salesforce identities using Dispatch. Configure a Box parent folder with `BOX_PARENT_FOLDER_ID`, or copy `config/runtime/demo-environment.example.json` to ignored `config/runtime/demo-environment.json` in the operator package and fill `box.parentFolderId`. Root folder 0 requires explicit Dispatch support/authorization and is never a teardown target.
5. Assemble the package, inspect the real validation preview, and resolve provider prerequisites. Deploy only after the exact plan/targets are authorized. The default resource strategy is reuse; configure run-specific create-new naming in Dispatch if needed.
6. Save Dispatch's resource receipts and verify Box and Salesforce results. Complete the same record/folder binding and live-adapter acceptance steps as the standalone lane.

No extra managed package, permission-set assignment, or seed script is declared by the base manifest. If your tailored use case needs Box for Salesforce, Apex, Agentforce, or a portal, add and verify those source artifacts and manifest prerequisites explicitly.

## Optional compatibility check

This is separate from ordinary standalone validation and requires Go plus an explicitly selected Dispatch checkout:

```bash
python scripts/check_dispatch.py --dispatch-root /path/to/box-dispatch
```

The checker creates a disposable generated Git repository, invokes Dispatch's actual `workspace.Build`, loads its BCL manifest, plans both providers, and builds the Salesforce Metadata API ZIP using Dispatch's source converter. It makes zero provider calls and does not alter the selected Dispatch checkout, active profile, connections, or saved plan. Go may download its declared build dependencies.

Reviewed local Dispatch revision: `baf9903428f351fe04c61bac2586909c9725717c`. The compatibility probe passed: five Box plan entries, seven Salesforce metadata components, and a ZIP containing all six custom fields. That is package compatibility evidence, not cloud deployment or live workflow evidence.

## Repeatability and recovery

Before retrying an uncertain cloud write, reconcile its operation ID and provider state. Do not infer idempotency from a filename or tool description. Preserve reusable resources and delete only recorded created IDs when reset is authorized. Keep deployment logs and receipts in ignored local output storage; never ship another tenant's IDs or credentials in a generated template.
