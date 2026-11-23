/**
 * The portal's Box endpoints (Apex REST, see classes/PortalBox*.cls). The browser never
 * receives the Box client secret or the parent token: only the customer-visible file list,
 * an upload-only token for the record's upload folder, and preview-only tokens per file.
 */
import { apexFetch } from "./apexRest";

export interface BoxFile {
	id: string;
	name: string;
	size?: number;
	modified_at?: string;
	folder?: string | null;
}

export interface BoxWorkspace {
	folderId: string;
	uploadFolderId: string;
	accessToken: string;
	files: BoxFile[];
}

export type Result<T> = { ok: true; value: T } | { ok: false; error: string };

const MESSAGES: Record<string, string> = {
	not_authenticated: "Sign in to see your documents.",
	record_not_found: "This record is not available to you.",
	no_box_folder_mapping: "No document folder is linked to this record yet.",
	box_not_configured: "Documents are not configured for this portal yet.",
	file_not_allowed: "That document is not available here.",
};

async function readError(response: Response): Promise<string> {
	try {
		const body = (await response.json()) as { error?: string };
		return MESSAGES[body.error ?? ""] ?? "Documents are unavailable right now. Try again shortly.";
	} catch {
		return "Documents are unavailable right now. Try again shortly.";
	}
}

async function tokenRequest(query: string): Promise<Response> {
	return apexFetch(`/services/apexrest/portal/box-token?${query}`, { headers: { Accept: "application/json" } });
}

/** Files and an upload token. Creates the record's Box folder once if it does not exist yet. */
export async function loadWorkspace(recordId: string): Promise<Result<BoxWorkspace>> {
	const query = `recordId=${encodeURIComponent(recordId)}`;
	let response = await tokenRequest(query);
	if (response.status === 404) {
		const body = (await response.clone().json().catch(() => ({}))) as { error?: string };
		if (body.error === "no_box_folder_mapping") {
			// A callout cannot follow DML in one Apex transaction, so provisioning is its own request.
			const created = await apexFetch(`/services/apexrest/portal/box-folder?${query}`, { method: "POST" });
			if (!created.ok) return { ok: false, error: await readError(created) };
			response = await tokenRequest(query);
		}
	}
	if (!response.ok) return { ok: false, error: await readError(response) };
	return { ok: true, value: (await response.json()) as BoxWorkspace };
}

/** A preview-only token for one file the server confirmed is visible. */
export async function previewToken(recordId: string, fileId: string): Promise<Result<string>> {
	const response = await tokenRequest(`recordId=${encodeURIComponent(recordId)}&fileId=${encodeURIComponent(fileId)}`);
	if (!response.ok) return { ok: false, error: await readError(response) };
	return { ok: true, value: ((await response.json()) as { accessToken: string }).accessToken };
}
