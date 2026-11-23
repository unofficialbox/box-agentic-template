import { useEffect, useState } from "react";
import { Link } from "react-router";
import { executeGraphQL } from "../api/graphqlClient";
import { portalConfig } from "../portal/config";
import { listQuery, nodes, value } from "../portal/queries";
import { StagePath } from "../portal/StagePath";

type Row = { id: string; title: string; stage: string; status: string };

export default function HomePage() {
	const r = portalConfig.record;
	const [rows, setRows] = useState<Row[] | null>(null);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		executeGraphQL<unknown, Record<string, never>>(listQuery())
			.then((data) =>
				setRows(
					nodes(data, r.object).map((n) => ({
						id: n.Id,
						title: value(n, r.title_field),
						stage: value(n, r.stage_field),
						status: value(n, r.status_field),
					})),
				),
			)
			.catch((e: Error) => setError(e.message));
	}, [r.object, r.title_field, r.stage_field, r.status_field]);

	return (
		<main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
			<title>{`${portalConfig.title}`}</title>
			<h1 className="portal-title text-4xl font-medium text-center mb-2">{r.plural_label}</h1>
			<p className="text-center text-primary mb-10">Track progress and see the status of every document you shared</p>
			{error && <p role="alert" className="text-destructive">{error}</p>}
			{rows === null && !error && <p role="status">Loading…</p>}
			{rows?.length === 0 && <p>Nothing to show yet.</p>}
			<div className="grid gap-6">
				{rows?.map((row) => (
					<Link key={row.id} to={`/records/${row.id}`} className="portal-card block no-underline">
						<h2 className="text-2xl font-medium text-title mb-3">{row.title}</h2>
						<StagePath current={row.stage} />
						{row.status && <p className="mt-3">Status: <strong>{row.status}</strong></p>}
					</Link>
				))}
			</div>
		</main>
	);
}
