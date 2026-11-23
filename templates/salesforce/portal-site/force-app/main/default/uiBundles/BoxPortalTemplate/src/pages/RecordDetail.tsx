import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { executeGraphQL } from "../api/graphqlClient";
import { portalConfig } from "../portal/config";
import { childNodes, detailQuery, nodes, tone, value } from "../portal/queries";
import { StagePath, StatusPill } from "../portal/StagePath";
import documentIcon from "../assets/icons/document.png";
import { BoxDocuments } from "../box/BoxDocuments";
import { EmbeddedSign } from "../box/EmbeddedSign";

type Doc = { id: string; type: string; status: string; version: string };
type Detail = { title: string; stage: string; status: string; signUrl: string; fields: { label: string; value: string }[]; docs: Doc[] };

export default function RecordDetail() {
	const { recordId } = useParams();
	const r = portalConfig.record;
	const d = portalConfig.documents;
	const [detail, setDetail] = useState<Detail | null>(null);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		if (!recordId) return;
		executeGraphQL<unknown, { id: string }>(detailQuery(), { id: recordId })
			.then((data) => {
				const node = nodes(data, r.object)[0];
				if (!node) throw new Error(`${r.label} not found or not shared with you`);
				const docs = d
					? childNodes(node, d.relationship)
							.map((n) => ({ id: n.Id, type: value(n, d.type_field), status: value(n, d.status_field), version: value(n, d.version_field) }))
							.filter((doc) => !d.hidden_types.includes(doc.type))
					: [];
				setDetail({
					title: value(node, r.title_field),
					stage: value(node, r.stage_field),
					status: value(node, r.status_field),
					signUrl: value(node, portalConfig.box.sign_embed_url_field),
					fields: r.fields.map((f) => ({ label: f.label, value: value(node, f.api_name) })),
					docs,
				});
			})
			.catch((e: Error) => setError(e.message));
	}, [recordId, r, d]);

	return (
		<main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
			<Link to="/" className="text-primary">← {r.plural_label}</Link>
			{error && <p role="alert" className="text-destructive mt-6">{error}</p>}
			{!detail && !error && <p role="status" className="mt-6">Loading…</p>}
			{detail && (
				<div className="portal-card mt-6">
					<h1 className="portal-title text-3xl font-medium mb-4">{detail.title}</h1>
					<StagePath current={detail.stage} />
					{detail.status && <p className="mt-4">Status: <strong>{detail.status}</strong></p>}
					{detail.fields.length > 0 && (
						<dl className="grid grid-cols-2 gap-x-6 gap-y-1 mt-4">
							{detail.fields.map((f) => (
								<div key={f.label} className="contents">
									<dt className="text-primary text-sm font-semibold uppercase tracking-wide">{f.label}</dt>
									<dd className="m-0">{f.value || "—"}</dd>
								</div>
							))}
						</dl>
					)}
					{detail.signUrl && recordId && (
						<section aria-labelledby="sign-title" className="mt-8">
							<h2 id="sign-title" className="text-xl font-medium text-title mb-2">Sign your document</h2>
							<EmbeddedSign embedUrl={detail.signUrl} recordId={recordId} />
						</section>
					)}
					{recordId && <BoxDocuments recordId={recordId} title={portalConfig.box.documents_label} />}
					{d && (
						<>
							<h2 className="text-xl font-medium text-title mt-8 mb-2">{d.label}</h2>
							<ul className="list-none p-0 m-0">
								{detail.docs.map((doc) => (
									<li key={doc.id} className="flex items-center gap-4 py-3 border-t border-border">
										<img src={documentIcon} alt="" className="w-9 h-9" />
										<div className="flex-1">
											<strong className="text-title">{doc.type}</strong>
											{doc.version && <span className="block text-sm">Version {doc.version}</span>}
										</div>
										<StatusPill status={doc.status} tone={tone(doc.status)} />
									</li>
								))}
							</ul>
						</>
					)}
				</div>
			)}
		</main>
	);
}
