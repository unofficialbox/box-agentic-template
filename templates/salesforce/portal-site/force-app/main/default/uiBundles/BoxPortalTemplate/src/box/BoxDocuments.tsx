import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import BoxAnnotations from "box-annotations";
import { IntlProvider } from "react-intl";
import { MemoryRouter } from "react-router-dom";
import "box-ui-elements/dist/preview.css";
import { installBoxPreview } from "./boxPreviewRuntime";
import { loadWorkspace, previewToken, type BoxFile, type BoxWorkspace } from "./api";
import { UploadDialog } from "./UploadDialog";
import documentIcon from "../assets/icons/document.png";

// Before ContentPreview mounts, so it finds the bundled renderer and never reaches for the
// Box CDN script that the site's script-src 'self' policy blocks.
installBoxPreview();

const ContentPreview = lazy(() => import("box-ui-elements/es/elements/content-preview").then((m) => ({ default: m.default })));

/** Stateful, so one instance for the page rather than one per render. */
const boxAnnotations = new BoxAnnotations({});

/** The newest preview stylesheet the Box CDN serves; the renderer itself is bundled. */
const PREVIEW_STYLESHEET_VERSION = "3.83.0";

/**
 * The record's Box documents: a list the server filtered to customer-visible files, Box
 * Content Preview for one file at a time, and Box Content Uploader into the upload folder.
 * Content Explorer is not used: embedded here it renders a touch layout whose files never
 * open in preview (observed in unofficialbox/box-agentic-loans).
 */
export function BoxDocuments({ recordId, title }: { recordId: string; title: string }) {
	const [workspace, setWorkspace] = useState<BoxWorkspace | null>(null);
	const [error, setError] = useState("");
	const [open, setOpen] = useState<BoxFile | null>(null);
	const [uploading, setUploading] = useState(false);
	const [previewError, setPreviewError] = useState("");

	const refresh = useCallback(() => {
		loadWorkspace(recordId).then((result) => {
			if (result.ok) {
				setWorkspace(result.value);
				setError("");
			} else {
				setError(result.error);
			}
		});
	}, [recordId]);

	useEffect(refresh, [refresh]);

	// Preview 3.x rejects a string annotator token ("Bad annotatorToken!"), so pass a function.
	const tokenProvider = useCallback(async () => {
		if (!open) throw new Error("Choose a document.");
		const granted = await previewToken(recordId, open.id);
		if (!granted.ok) {
			setPreviewError(granted.error);
			throw new Error(granted.error);
		}
		setPreviewError("");
		return granted.value;
	}, [recordId, open]);

	return (
		<section aria-labelledby="box-documents-title" className="mt-8">
			<div className="flex items-center justify-between gap-4 mb-2">
				<h2 id="box-documents-title" className="text-xl font-medium text-title">{title}</h2>
				{workspace && !open && (
					<button type="button" className="rounded-full bg-primary text-primary-foreground px-4 py-2 text-sm" onClick={() => setUploading(true)}>
						Add documents
					</button>
				)}
			</div>
			{error && <p role="alert" className="text-destructive">{error}</p>}
			{!workspace && !error && <p role="status">Loading documents…</p>}
			{workspace && !open && (
				<ul className="list-none p-0 m-0">
					{workspace.files.length === 0 && <li className="py-3">No documents yet.</li>}
					{workspace.files.map((file) => (
						<li key={file.id} className="border-t border-border">
							<button type="button" className="flex w-full items-center gap-4 py-3 text-left" onClick={() => setOpen(file)}>
								<img src={documentIcon} alt="" className="w-9 h-9" />
								<span className="flex-1">
									<strong className="text-title">{file.name}</strong>
									{file.folder && <span className="block text-sm">{file.folder}</span>}
								</span>
								<span className="text-primary text-sm">Preview</span>
							</button>
						</li>
					))}
				</ul>
			)}
			{open && (
				<div>
					<div className="flex items-center gap-3 py-2">
						<button type="button" className="text-primary" onClick={() => { setOpen(null); setPreviewError(""); }}>← All documents</button>
						<span className="font-medium text-title">{open.name}</span>
					</div>
					{previewError && <p role="alert" className="text-destructive">{previewError}</p>}
					<div className="h-[70vh] rounded-xl border border-border overflow-hidden bg-white">
						<IntlProvider locale="en" messages={{}}>
							<Suspense fallback={<p role="status" className="p-4">Opening preview…</p>}>
								{/* The annotations layer needs router context; memory history keeps the portal URL untouched. */}
								<MemoryRouter>
									<ContentPreview token={tokenProvider} fileId={open.id} boxAnnotations={boxAnnotations}
										previewLibraryVersion={PREVIEW_STYLESHEET_VERSION} hasHeader={false} />
								</MemoryRouter>
							</Suspense>
						</IntlProvider>
					</div>
				</div>
			)}
			{uploading && workspace && (
				<UploadDialog folderId={workspace.uploadFolderId} tokenProvider={() => workspace.accessToken}
					onClose={() => setUploading(false)} onUploaded={() => { setUploading(false); refresh(); }} />
			)}
		</section>
	);
}
