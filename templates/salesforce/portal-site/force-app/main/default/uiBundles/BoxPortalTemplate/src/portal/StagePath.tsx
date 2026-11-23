import { portalConfig } from "./config";

/** Stage path: completed stages in green, the current stage in Box blue, upcoming stages outlined. */
export function StagePath({ current }: { current: string }) {
	const stages = portalConfig.stages;
	if (!stages.length) return null;
	const index = stages.indexOf(current);
	return (
		<ol aria-label={`${portalConfig.record.label} stages`} className="flex flex-wrap gap-2 p-0 list-none">
			{stages.map((stage, i) => {
				const state = index < 0 ? "upcoming" : i < index ? "complete" : i === index ? "current" : "upcoming";
				const style =
					state === "current"
						? "bg-primary text-primary-foreground border-primary"
						: state === "complete"
							? "bg-pass/25 border-pass text-foreground"
							: "bg-card border-border text-foreground";
				return (
					<li key={stage} aria-current={state === "current" ? "step" : undefined} className={`rounded-full border px-3 py-1 text-sm ${style}`}>
						{stage}
					</li>
				);
			})}
		</ol>
	);
}

export function StatusPill({ status, tone }: { status: string; tone: "pass" | "wait" | "fail" }) {
	const style = tone === "pass" ? "bg-pass/25" : tone === "fail" ? "bg-fail/25" : "bg-wait/25";
	return <span className={`inline-block whitespace-nowrap rounded-full px-3 py-1 text-sm text-foreground ${style}`}>{status}</span>;
}
