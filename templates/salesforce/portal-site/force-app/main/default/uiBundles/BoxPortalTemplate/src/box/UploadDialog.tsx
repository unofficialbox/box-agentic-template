import { lazy, Suspense, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { IntlProvider } from "react-intl";
import "box-ui-elements/dist/uploader.css";

const ContentUploader = lazy(() => import("box-ui-elements/es/elements/content-uploader").then((m) => ({ default: m.default })));

export interface UploadedFile {
	id: string;
	name: string;
}

/**
 * Box Content Uploader in a dialog over the document list, so the list stays in view. The
 * token can only upload into this one folder. Escape and the backdrop close it, and focus
 * returns to whatever opened it. Ported from unofficialbox/box-agentic-loans.
 */
export function UploadDialog({ folderId, tokenProvider, onClose, onUploaded }: {
	folderId: string;
	tokenProvider: () => string;
	onClose: () => void;
	onUploaded?: (files: UploadedFile[]) => void;
}) {
	const dialog = useRef<HTMLDivElement>(null);
	const opener = useRef<Element | null>(null);

	useEffect(() => {
		opener.current = document.activeElement;
		dialog.current?.focus();
		const onKeyDown = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
		document.addEventListener("keydown", onKeyDown);
		return () => {
			document.removeEventListener("keydown", onKeyDown);
			(opener.current as HTMLElement | null)?.focus?.();
		};
	}, [onClose]);

	return createPortal(
		<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
			onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
			<div ref={dialog} role="dialog" aria-modal="true" aria-labelledby="upload-dialog-title" tabIndex={-1}
				className="portal-card w-full max-w-2xl bg-white">
				<div className="flex items-center justify-between mb-4">
					<h2 id="upload-dialog-title" className="text-xl font-medium text-title">Add documents</h2>
					<button type="button" onClick={onClose} aria-label="Close" className="text-2xl leading-none px-2">×</button>
				</div>
				<div className="h-[420px]">
					<IntlProvider locale="en" messages={{}}>
						<Suspense fallback={<p role="status">Opening uploader…</p>}>
							<ContentUploader token={tokenProvider} rootFolderId={folderId} onClose={onClose}
								onComplete={(items: unknown[]) => onUploaded?.(uploadedFiles(items))} />
						</Suspense>
					</IntlProvider>
				</div>
			</div>
		</div>,
		document.body,
	);
}

/** Only files Box actually created; a failed item has no id. */
function uploadedFiles(items: unknown[]): UploadedFile[] {
	return items.flatMap((item) => {
		const file = item as { id?: unknown; name?: unknown } | null | undefined;
		if (!file || typeof file.id !== "string" || !file.id) return [];
		return [{ id: file.id, name: typeof file.name === "string" ? file.name : file.id }];
	});
}
