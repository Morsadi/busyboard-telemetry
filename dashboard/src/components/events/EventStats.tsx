import { formatDuration, formatTimestamp } from '@/lib/utils';
import { bg, border, text, type as t } from '@/lib/styles';
import type { Session } from '@/types';

const STATUS_LABELS: Record<string, string> = {
	active: 'Live',
	ended: 'Clean',
	connection_lost: 'Lost',
};

const STATUS_BADGE: Record<string, string> = {
	active: 'border-green-900 bg-[#071a07] text-green-600',
	connection_lost: 'border-amber-900 bg-[#1a0e0a] text-amber-600',
	ended: `${border.default} bg-[#0a1520] ${text.dim}`,
};

export function EventStats({ session }: { session: Session }) {
	const endDisplay = session.ended_at ? formatTimestamp(session.ended_at, 'table') : 'live';

	return (
		<>
			<div className={`grid grid-cols-1 md:grid-cols-3 gap-3 border-b ${border.default} px-3.5 py-2.5 md:grid-cols-[auto_auto_1fr]`}>
				<time className={`${t.monoSm} font-medium ${text.primary}`}>{formatTimestamp(session.started_at, 'session')}</time>

				<span className={`w-max rounded-full border px-2 py-0.5 ${t.monoSm} ${STATUS_BADGE[session.status]}`}>{session.status === 'active' ? '● live' : STATUS_LABELS[session.status]}</span>

				<p className={`${t.monoSm} ${text.muted} md:ml-auto`}>
					<time>{formatTimestamp(session.started_at, 'table')}</time> → <time>{endDisplay}</time>
				</p>
			</div>

			<div className={`grid grid-cols-1 md:grid-cols-4 border-b ${border.default}`}>
				{[
					{ n: session.interaction_count, label: 'Events' },
					{ n: formatDuration(session.started_at, session.ended_at), label: 'Duration' },
					{ n: session.switch_count, label: 'Switches used' },
					{ n: STATUS_LABELS[session.status] ?? '—', label: 'End reason' },
				].map(({ n, label }) => (
					<div
						key={label}
						className={`border-r ${border.default} px-3.5 py-2 last:border-r-0`}>
						<p className={`${t.monoSm} font-medium ${text.primary}`}>{n}</p>
						<p className={`${t.tableCol} ${text.muted} mt-0.5`}>{label}</p>
					</div>
				))}
			</div>
		</>
	);
}
