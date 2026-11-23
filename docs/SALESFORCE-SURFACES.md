# Salesforce portal and Agentforce agent

Two optional Salesforce surfaces are part of every project. The intake asks about both: `customer_portal` (`multi_framework_react_site` or `none`) and `agentforce_agent` (`agent_script` or `none`). Each one is a maintained template in this repository plus a build script that renders it into `salesforce-project/`. Edit the template or its config, then rebuild. Never hand-edit the rendered output.

| Surface | Edit | Rebuild | Output |
|---|---|---|---|
| Customer portal: an Experience Cloud site running a React UI bundle (Salesforce Multi-Framework) | `templates/salesforce/portal-site/` for code and layout; `config/salesforce/portal.json` for the site name, record object, fields, stages, and documents | `python scripts/build_portal.py` | `uiBundles/`, `sites/`, `networks/`, `digitalExperience*/`, auth `classes/`, guest `permissionsets/` |
| Agentforce agent in Agent Script | `templates/salesforce/agent/` for the script frame and Apex stub; `config/salesforce/agent.json` for subagents and the tools each may use | `python scripts/build_agent.py` | `aiAuthoringBundles/<Agent>/` plus Apex action stubs in `classes/` |

`python scripts/validate.py` fails when rendered output is stale. Both scripts run offline and need neither Node nor the Salesforce CLI.

## Customer portal (Multi-Framework React site)

The site template began as `sf template generate project --template reactexternalapp` (Salesforce CLI 2.159.7, API 67.0, React 19, Vite 7, Tailwind 4, shadcn/ui, `@salesforce/platform-sdk`). It has been trimmed and customized:

- Removed: the demo chat widget, account sample pages, global search route, and Codey images.
- Added Box: a document list with Box Content Preview, Box Content Uploader, and embedded Box Sign on the record page (see below).
- Added: a record list page (`src/pages/Home.tsx`) and a record detail page (`src/pages/RecordDetail.tsx`) with a stage path and a document list with status pills. The record, fields, stages, and documents come from `src/portal/portal.config.json`, which the build writes from `config/salesforce/portal.json`.
- Branded: `src/styles/global.css` carries a generated `BOX BRAND` block from `config/brand.json`; the header uses Box blue and the cards use the brand container style. See the [Box brand guide](brand/BOX-BRAND.md).
- Kept: login, registration, password reset, profile, session timeout, and the Experience Cloud site metadata.

Placeholders in the template: `BoxPortalTemplate` (API names and paths, replaced with `site_name`), `boxportaltemplate` (URL name, replaced with `url_path_prefix`), and `__PORTAL_TITLE__` (replaced with `site.title`).

**Data and access.** Pages read Salesforce through GraphQL (UI API) with `@salesforce/platform-sdk`, as the signed-in external user. Salesforce sharing decides which records a customer sees; the UI never widens access. `documents.hidden_types` also hides internal document types in the browser, but only as defense in depth: keep internal records unshared in Salesforce.

**Build and deploy** (needs approval for the target org):

1. **Org setup:** use a scratch org or sandbox with Experience Cloud (Communities) and enable "React Development with Salesforce Multi-Framework" in Setup. Check the current release notes for availability.
2. **Install and build:** in `salesforce-project/force-app/main/default/uiBundles/<site_name>/`, run `npx npm@11 install` (npm 10.9 fails with `Cannot read properties of null (reading 'edgesOut')`), then `npm run build`. Node 22 or later is required.
3. **Deploy:** run `sf project deploy start --source-dir force-app --target-org <alias>` from `salesforce-project/`, then publish the site and give external users access to the record object and fields.

### Box documents, preview, upload, and Sign

The record page shows the record's Box documents with Box Content Preview, adds files with Box Content Uploader, and embeds Box Sign when a signing request is open. The pattern is ported from [box-agentic-loans](https://github.com/unofficialbox/box-agentic-loans). All Box access goes through Apex, so the browser never holds the Box client secret or a broad token.

| Piece | Source | What it does |
|---|---|---|
| `PortalBoxTokenService` (`GET /services/apexrest/portal/box-token`) | `classes/` | Checks record access, finds the folder through the Box for Salesforce association, lists customer-visible files on the server, and returns an upload-only token (`base_upload`) for the upload folder. With `fileId`, returns a preview-only token (`base_preview`) for that one file after checking it is visible |
| `PortalBoxFolderService` (`POST .../portal/box-folder`) | `classes/` | Creates the record's folder with Box for Salesforce when none exists. This is a separate request because Apex cannot call out after DML |
| `PortalSignStatus` (`POST .../portal/sign-status`) | `classes/` | Reads the Box Sign status from Box. On a final status, clears the stored iframe URL |
| `PortalBoxSendForSignature` | `classes/` | Invocable action for employees, Flows, and agents. Creates an embedded Box Sign request for a file in the record folder and stores the signer's `iframeable_embed_url` and request ID on the record. Customers cannot call it |
| `PortalBoxAuth`, `PortalBoxAccess`, `PortalBoxDocuments`, `PortalBoxSettings` | `classes/` | Client Credentials Grant through the `Portal_Box` named credential, the record access check (sharing, plus an optional account match), folder listing, and the settings rendered from `site.box` |
| `src/box/BoxDocuments.tsx` | UI bundle | File list and Box Content Preview (`box-ui-elements`). Preview is bundled from npm, not the Box CDN, because the site's `script-src 'self'` blocks it. Content Explorer is not used: embedded, it renders a touch layout whose files never open |
| `src/box/UploadDialog.tsx` | UI bundle | Box Content Uploader in a dialog, limited to the upload folder |
| `src/box/EmbeddedSign.tsx` | UI bundle | Box Sign iframe. Completion is polled from Apex every 5 seconds rather than trusting iframe messages |
| `namedCredentials/`, `externalCredentials/`, `cspTrustedSites/`, `objects/Portal_Box_Config__c`, `permissionsets/<site>_Box_Access` | metadata | Credential, CSP Trusted Sites for Box hosts, the CCG subject setting, and portal user access (Apex classes, the credential principal, read on the portal's custom fields) |

**Customer access in `config/salesforce/portal.json`:**

- `customer_access.profiles`: the external user profiles that become site members and receive a sharing set.
- `customer_access.account_field`: the record's Account lookup (for example `AccountId`). The sharing set grants customers read on records of their own Account.
- `site.documents.object`: the child document object. It adds read on that object and its fields to `<site>_Box_Access`.
- Without these, customers can sign in but see no records.

**`site.box` settings in `config/salesforce/portal.json`:**

- `account_field`: a record field holding the customer's Account. An external user must belong to that Account; leave it null to rely on sharing alone.
- `visible_subfolders`: the record subfolders customers may see. Leave it empty to show files at the folder root.
- `upload_subfolder`: where uploads land.
- `sign_embed_url_field` and `sign_request_id_field`: the record fields that hold the Sign iframe URL and request ID. Set both, or set neither to turn Sign off.

**One-time Box and org setup** (each org write needs approval):

1. **Box app:** create a Box Platform app with Client Credentials Grant, enable it in the enterprise, and add the site origin under CORS domains. Without CORS, previews fail with `cors_origin_not_whitelisted`.
2. **Credentials:** in Setup, open the `Portal_Box` external credential and set `ClientId` and `ClientSecret` on `Portal_Box_Principal`. They stay encrypted in the org and never appear in source.
3. **Subject:** set `Portal Box Config` (a custom setting) with a Box User Id (acts as that user) or an Enterprise Id (service account, which must be collaborated on the record folders).
4. **Packages and access:** install Box for Salesforce, assign `<site>_Box_Access` to portal users, and give them a license that can read the record object. Grant read on any child document object separately.
5. **Sign fields:** to use Sign, add the two Sign fields to the record object.
6. **Build and deploy:** build and deploy as above.

**Org settings the site needs:** Digital Experiences enabled, with ExperienceBundle metadata and standard external profiles allowed. Deploy `CommunitiesSettings` (`enableNetworksEnabled`, `enableOotbProfExtUserOpsEnable`) and `ExperienceBundleSettings` (`enableExperienceBundleMetadata`) before the site. After deploying, assign `<site>_Guest_User_Api_Access` to the site's guest user so sign-in and registration work. The site is served at `https://<org>.my.site.com/<site_name>/`.

**Known build notes:**

- `box-annotations` and `box-content-preview` are pinned to 5.2.1-beta.18 and 3.85.0, the versions proven in box-agentic-loans, and the bundle ships a `package-lock.json`. box-annotations 5.3.0 leaves raw `require("react")` calls in the browser build, which renders a blank page with `ReferenceError: require is not defined`.
- `salesforce-project/.forceignore` keeps `node_modules/` out of deploys.

- `box-ui-elements` needs `.npmrc` `legacy-peer-deps=true`, `define: { global: "globalThis" }`, and a `~@box` alias for its stylesheets. All three are already in the template.
- The main chunk is about 4.9 MB because Preview is bundled.
- The pinned preview stylesheet version (3.83.0) is the newest the Box CDN serves.

## Agentforce agent (Agent Script)

`scripts/build_agent.py` writes one authoring bundle (`<developer_name>.agent` and `.bundle-meta.xml`) from `config/salesforce/agent.json`, `config/tools.json`, and `templates/salesforce/agent/agent.agent`:

- **Structure:** a router (`start_agent agent_router`) transitions to one subagent per entry in `subagents`, plus an `off_topic` guard. Each subagent exposes its tools as reasoning actions.
- **Record binding:** tool inputs named in `record_inputs` (default `record_id`) are bound to the record ID the router captures; the model fills every other input from the conversation.
- **Actions:** each tool becomes an action targeting `apex://<apex_prefix><Tool>`, with inputs taken from the tool's `inputSchema`. Tools that are not read-only get `require_user_confirmation: True`.
- **Guardrails:** the system instructions and every subagent state that documents are data, that proposals are not writes, and that people approve. The agent never approves, signs, or writes on its own.
- **Agent type:** employee agents only (`AgentforceEmployeeAgent`). A service agent also needs `default_agent_user` and messaging setup, so the generator refuses it.

**Apex action stubs** (`classes/<Prefix><Tool>.cls` and `<Prefix>ActionsTest.cls`) are seeded once and never overwritten. Implement the live Box and Salesforce call there. Until you do, each stub returns `live_adapter_not_implemented`, and the agent is told to report that error, so it cannot claim success.

**Validate and publish** (publishing needs approval for the target org):

```bash
cd salesforce-project
sf agent validate authoring-bundle --api-name <developer_name> --target-org <agentforce-org>
sf project deploy start --source-dir force-app --target-org <agentforce-org>
sf agent publish authoring-bundle --api-name <developer_name> --target-org <agentforce-org>
```

Validation compiles the script in an org with Agentforce enabled. A scratch org without Agentforce times out on the compile service. The template's sample agent compiles against an Agentforce Developer Edition org.

## Reporting problems with these templates

If you find a bug or an enhancement in the site template, the agent template, or their build scripts while creating a solution, file an issue on [unofficialbox/box-agentic-template](https://github.com/unofficialbox/box-agentic-template/issues) as described in `AGENTS.md`.
