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
			<div className={`flex items-center gap-2.5 border-b ${border.default} px-3.5 py-2.5`}>
				<span className={`${t.monoSm} font-medium ${text.primary}`}>{formatTimestamp(session.started_at, 'session')}</span>
				<span className={`rounded-full border px-2 py-0.5 text-[10px] ${STATUS_BADGE[session.status]}`}>{session.status === 'active' ? '● live' : STATUS_LABELS[session.status]}</span>
				<span className={`ml-auto ${t.monoXs} ${text.muted}`}>
					{formatTimestamp(session.started_at, 'table')} → {endDisplay}
				</span>
			</div>

			<div className={`grid grid-cols-4 border-b ${border.default}`}>
				{[
					{ n: session.interaction_count, label: 'Events' },
					{ n: formatDuration(session.duration_ms, session.started_at, session.ended_at), label: 'Duration' },
					{ n: session.switch_count, label: 'Switches used' },
					{ n: STATUS_LABELS[session.status] ?? '—', label: 'End reason' },
				].map(({ n, label }) => (
					<div
						key={label}
						className={`border-r ${border.default} px-3.5 py-2 last:border-r-0`}>
						<div className={`${t.monoSm} font-medium ${text.primary}`}>{n}</div>
						<div className={`${t.tableCol} ${text.muted} mt-0.5`}>{label}</div>
					</div>
				))}
			</div>
		</>
	);
}
