import { useEffect, useRef, useState } from "react";
import { apexFetch } from "./apexRest";

/**
 * Box Sign embedded signing in an iframe. Completion is read from Box through Apex
 * (classes/PortalSignStatus.cls) every 5 seconds: cross-origin iframe messages cannot prove
 * a signature. Ported from unofficialbox/box-agentic-loans.
 */
export function EmbeddedSign({ embedUrl, recordId, onDone }: {
	embedUrl: string;
	recordId: string;
	onDone?: (status: "signed" | "declined" | "closed") => void;
}) {
	const [checked, setChecked] = useState(false);
	const [loading, setLoading] = useState(true);
	const [statusError, setStatusError] = useState(false);
	const [final, setFinal] = useState<string | null>(null);
	const done = useRef(onDone);
	useEffect(() => { done.current = onDone; }, [onDone]);

	useEffect(() => {
		let disposed = false;
		let timer: ReturnType<typeof setTimeout>;
		const controller = new AbortController();
		async function check() {
			try {
				const response = await apexFetch(`/services/apexrest/portal/sign-status?recordId=${encodeURIComponent(recordId)}`, {
					method: "POST", headers: { Accept: "application/json" }, signal: controller.signal,
				});
				if (!response.ok) throw new Error("Status unavailable");
				const { status } = (await response.json()) as { status?: string };
				if (disposed || !status) return;
				setStatusError(false);
				if (status === "signed" || status === "declined") {
					setFinal(status);
					done.current?.(status);
					return;
				}
				if (["cancelled", "expired", "none"].includes(status)) {
					setFinal("closed");
					done.current?.("closed");
					return;
				}
				setChecked(true);
			} catch {
				if (disposed) return;
				setStatusError(true);
			}
			if (!disposed) timer = setTimeout(check, 5000);
		}
		void check();
		return () => { disposed = true; controller.abort(); clearTimeout(timer); };
	}, [embedUrl, recordId]);

	if (final === "signed") return <p role="status" className="py-3">Signed. Your signed copy will appear in your documents shortly.</p>;
	if (final === "declined") return <p role="status" className="py-3">You declined to sign. Your relationship manager will follow up.</p>;
	if (final === "closed") return <p role="status" className="py-3">This signing request is no longer open.</p>;
	return (
		<div>
			{statusError && <p role="status">Unable to check signing status. Retrying automatically.</p>}
			{(loading || !checked) && !statusError && <p role="status">Loading your signing request…</p>}
			{checked && (
				<iframe src={embedUrl} title="Box Sign document" className="w-full h-[75vh] rounded-xl border border-border bg-white"
					onLoad={() => setLoading(false)} allow="clipboard-write"
					sandbox="allow-scripts allow-same-origin allow-forms allow-popups" />
			)}
		</div>
	);
}
