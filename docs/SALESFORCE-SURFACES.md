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
- Added: a record list page (`src/pages/Home.tsx`) and a record detail page (`src/pages/RecordDetail.tsx`) with a stage path and a document list with status pills. The record, fields, stages, and documents come from `src/portal/portal.config.json`, which the build writes from `config/salesforce/portal.json`.
- Branded: `src/styles/global.css` carries a generated `BOX BRAND` block from `config/brand.json`; the header uses Box blue and the cards use the brand container style. See the [Box brand guide](brand/BOX-BRAND.md).
- Kept: login, registration, password reset, profile, session timeout, and the Experience Cloud site metadata.

Placeholders in the template: `BoxPortalTemplate` (API names and paths, replaced with `site_name`), `boxportaltemplate` (URL name, replaced with `url_path_prefix`), and `__PORTAL_TITLE__` (replaced with `site.title`).

**Data and access.** Pages read Salesforce through GraphQL (UI API) with `@salesforce/platform-sdk`, as the signed-in external user. Salesforce sharing decides which records a customer sees; the UI never widens access. `documents.hidden_types` also hides internal document types in the browser, but only as defense in depth: keep internal records unshared in Salesforce.

**Build and deploy** (needs approval for the target org):

1. **Org setup:** use a scratch org or sandbox with Experience Cloud (Communities) and enable "React Development with Salesforce Multi-Framework" in Setup. Check the current release notes for availability.
2. **Install and build:** in `salesforce-project/force-app/main/default/uiBundles/<site_name>/`, run `npx npm@11 install` (npm 10.9 fails with `Cannot read properties of null (reading 'edgesOut')`), then `npm run build`. Node 22 or later is required.
3. **Deploy:** run `sf project deploy start --source-dir force-app --target-org <alias>` from `salesforce-project/`, then publish the site and give external users access to the record object and fields.

### Box content in the portal

To show Box files in the portal, follow the pattern already proven in [box-agentic-loans](https://github.com/unofficialbox/box-agentic-loans) (`los-salesforce-project/.../uiBundles/losreactapp`). It is not in this template yet:

- **Preview and Uploader:** `box-ui-elements` React components loaded lazily inside `IntlProvider` and `MemoryRouter`. Bundle `box-content-preview` locally and set `globalThis.Box.Preview`, because Experience Cloud's `script-src 'self'` blocks the Box CDN. Pass `token` as a function.
- **Content Explorer:** not used there. In this embedding it renders a touch layout where files do not open in preview, so list the folder through the API and draw your own table.
- **Box Sign:** a plain `<iframe>` of the signer's `iframeable_embed_url`, created by an Apex action with `embed_url_external_user_id`. Detect completion by polling `GET /sign_requests/{id}` from Apex, not by trusting iframe messages.
- **Tokens:** an Apex REST endpoint checks record access, resolves the folder with the Box for Salesforce Toolkit (`getFolderIdByRecordId`), and returns a downscoped token. Internal users get `base_explorer item_preview base_upload`; customers get `base_upload` plus per-file `base_preview`. The parent token comes from a Client Credentials Grant through a named credential, so Apex never holds the secret.
- **Site settings:** add CSP Trusted Sites for `api.box.com`, `upload.box.com`, `*.boxcloud.com`, `public.boxcloud.com`, `cdn01.boxcdn.net`, and `*.app.box.com` (frame, for Sign). Add the site origin to the Box app's CORS domains.

## Agentforce agent (Agent Script)

`scripts/build_agent.py` writes one authoring bundle (`<developer_name>.agent` and `.bundle-meta.xml`) from `config/salesforce/agent.json`, `config/tools.json`, and `templates/salesforce/agent/agent.agent`:

- **Structure:** a router (`start_agent agent_router`) transitions to one subagent per entry in `subagents`, plus an `off_topic` guard. Each subagent exposes its tools as reasoning actions.
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
