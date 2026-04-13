import { formatDuration, formatTimestamp } from '@/lib/utils';
import type { Session } from '@/types';

const STATUS_LABELS: Record<string, string> = {
	active: 'Live',
	ended: 'Clean',
	connection_lost: 'Lost',
};

export function EventStats({ session }: { session: Session }) {
	const endDisplay = session.ended_at ? formatTimestamp(session.ended_at, 'table') : 'live';

	return (
		<>
			{/* Session header */}
			<div className='flex items-center gap-2.5 border-b border-[#1c2a3a] px-3.5 py-2.5'>
				<span className='font-mono text-[12px] font-medium text-[#e4eaf0]'>{session.session_id}</span>
				<span
					className={`rounded-full border px-2 py-0.5 text-[10px]
            ${
				session.status === 'active'
					? 'border-[#1a3a1a] bg-[#071a07] text-[#639922]'
					: session.status === 'connection_lost'
						? 'border-[#2a1a0a] bg-[#1a0e0a] text-[#854f0b]'
						: 'border-[#1c2a3a] bg-[#0a1520] text-[#2a4a60]'
			}`}>
					{session.status === 'active' ? '● live' : STATUS_LABELS[session.status]}
				</span>
				<span className='ml-auto font-mono text-[11px] text-[#3a6080]'>
					{formatTimestamp(session.started_at, 'table')} → {endDisplay}
				</span>
			</div>

			{/* Stat strip */}
			<div className='grid grid-cols-4 border-b border-[#1c2a3a]'>
				{[
					{ n: session.interaction_count, label: 'Events' },
					{ n: formatDuration(session.duration_ms, session.started_at, session.ended_at), label: 'Duration' },
					{ n: session.switch_count, label: 'Switches used' },
					{ n: STATUS_LABELS[session.status] ?? '—', label: 'End reason' },
				].map(({ n, label }) => (
					<div
						key={label}
						className='border-r border-[#1c2a3a] px-3.5 py-2 last:border-r-0'>
						<div className='font-mono text-[15px] font-medium text-[#e4eaf0]'>{n}</div>
						<div className='text-[9px] uppercase tracking-[1px] text-[#3a6080]'>{label}</div>
					</div>
				))}
			</div>
		</>
	);
}
