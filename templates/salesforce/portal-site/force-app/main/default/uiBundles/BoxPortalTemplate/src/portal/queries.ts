/**
 * Builds Salesforce GraphQL (UI API) queries from the portal configuration.
 * Record visibility comes from Salesforce sharing for the signed-in external
 * user; the UI never widens access. Hidden document types are filtered here only
 * as defense in depth: keep internal documents unshared in Salesforce as well.
 */
import { portalConfig, type PortalConfig } from "./config";

const NAME = /^[A-Za-z][A-Za-z0-9_]*$/;

function assertName(name: string): string {
	if (!NAME.test(name)) throw new Error(`Invalid Salesforce API name in portal config: ${name}`);
	return name;
}

function recordFields(config: PortalConfig): string[] {
	const r = config.record;
	return [r.title_field, r.stage_field, r.status_field, config.box.sign_embed_url_field, ...r.fields.map((f) => f.api_name)]
		.filter((f): f is string => Boolean(f))
		.map(assertName);
}

export function listQuery(config: PortalConfig = portalConfig): string {
	const object = assertName(config.record.object);
	const fields = recordFields(config).map((f) => `${f} { value }`).join(" ");
	return `query PortalRecords { uiapi { query { ${object}(first: 50, orderBy: { LastModifiedDate: { order: DESC } }) { edges { node { Id ${fields} } } } } } }`;
}

export function detailQuery(config: PortalConfig = portalConfig): string {
	const object = assertName(config.record.object);
	const fields = recordFields(config).map((f) => `${f} { value }`).join(" ");
	const d = config.documents;
	const docs = d
		? `${assertName(d.relationship)}(first: 100) { edges { node { Id ${[d.type_field, d.status_field, d.version_field]
				.filter((f): f is string => Boolean(f))
				.map((f) => `${assertName(f)} { value }`)
				.join(" ")} } } }`
		: "";
	return `query PortalRecord($id: ID) { uiapi { query { ${object}(where: { Id: { eq: $id } }, first: 1) { edges { node { Id ${fields} ${docs} } } } } } }`;
}

type Node = Record<string, unknown> & { Id: string };

export function value(node: Node, field: string | null | undefined): string {
	if (!field) return "";
	const cell = node[field] as { value?: unknown } | undefined;
	return cell?.value == null ? "" : String(cell.value);
}

export function nodes(data: unknown, object: string): Node[] {
	const root = (data as { uiapi?: { query?: Record<string, { edges?: { node: Node }[] }> } })?.uiapi?.query?.[object];
	return root?.edges?.map((e) => e.node) ?? [];
}

export function childNodes(node: Node, relationship: string): Node[] {
	const rel = node[relationship] as { edges?: { node: Node }[] } | undefined;
	return rel?.edges?.map((e) => e.node) ?? [];
}

export function tone(status: string, config: PortalConfig = portalConfig): "pass" | "wait" | "fail" {
	return config.status_tone[status] ?? "wait";
}
