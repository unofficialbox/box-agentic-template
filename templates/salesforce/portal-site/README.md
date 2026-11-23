# Portal site template

This is the maintained source for the customer portal: an Experience Cloud site running a React UI bundle (Salesforce Multi-Framework). `scripts/build_portal.py` renders it into `salesforce-project/` when `config/salesforce/portal.json` has `"enabled": true`. Full guide: [docs/SALESFORCE-SURFACES.md](../../../docs/SALESFORCE-SURFACES.md).

## Modify it

| Change | Where |
|---|---|
| Record object, fields, stages, documents, status colors | `config/salesforce/portal.json` (`site` section), not `src/portal/portal.config.json` |
| Pages and layout | `uiBundles/BoxPortalTemplate/src/pages/`, `src/appLayout.tsx`, `src/routes.tsx` |
| Stage path and status pills | `src/portal/StagePath.tsx` |
| GraphQL queries | `src/portal/queries.ts` |
| Brand colors and fonts | `config/brand.json`; the `BOX BRAND` block in `src/styles/global.css` is regenerated |
| Box documents, preview, upload, Sign | `src/box/`, `classes/PortalBox*.cls`, `classes/PortalSignStatus.cls`; settings in `site.box` of `config/salesforce/portal.json` |
| Box credential, CSP, portal user access | `namedCredentials/`, `externalCredentials/`, `cspTrustedSites/`, `objects/Portal_Box_Config__c/`, `permissionsets/BoxPortalTemplate_Box_Access.permissionset-meta.xml` |
| Site, network, login pages | `networks/`, `sites/`, `digitalExperience*/`, `classes/UIBundle*.cls` |

Keep the placeholders: `BoxPortalTemplate` in names and paths, `boxportaltemplate` for the URL name, and `__PORTAL_TITLE__` for the visible title. After any change, run `python scripts/build_portal.py`, then build the bundle:

```bash
cd salesforce-project/force-app/main/default/uiBundles/<site_name>
npx npm@11 install   # npm 10.9 fails to resolve this dependency tree
npm run build
```

## Origin

Generated with `sf template generate project --template reactexternalapp` (Salesforce CLI 2.159.7, API 67.0), then trimmed and customized. The Box components and Apex are ported from [box-agentic-loans](https://github.com/unofficialbox/box-agentic-loans). To take a newer upstream scaffold, generate it with the name `BoxPortalTemplate`, diff it against this folder, and carry over the portal pages, `src/portal/`, `src/box/`, the Box Apex and metadata, the Vite and `.npmrc` settings, the brand block, and the removals listed in the guide.
