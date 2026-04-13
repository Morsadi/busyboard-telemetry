import { formatTimestamp, formatDuration } from '@/lib/utils';
import type { Session } from '@/types';

type Props = {
	session: Session;
	isSelected: boolean;
	onSelect: (id: string) => void;
};

export function SessionItem({ session, isSelected, onSelect }: Props) {
	const isLive = session.status === 'active';

	return (
		<button
			onClick={() => onSelect(session.session_id)}
			className={`
        w-full text-left px-3 py-2.5 border-b border-[#111820]
        border-l-2 transition-colors
        ${isSelected ? 'bg-[#0a1f3a] border-l-blue-600' : 'border-l-transparent hover:bg-[#0e1520]'}
      `}>
			<div className='flex items-center justify-between mb-1'>
				<span className='text-[12px] font-medium text-[#e4eaf0]'>{formatTimestamp(session.started_at, 'session')}</span>
				{isLive && <span className='text-[9px] text-green-600'>● live</span>}
			</div>

			<div className='flex items-center justify-between mb-2'>
				<span className='text-[10px] font-mono text-[#2a4a60]'>{session.session_id}</span>
				<span className='text-[10px] font-mono text-[#2a4a60]'>{formatDuration(session.duration_ms, session.started_at, session.ended_at)}</span>
			</div>

			<div className='flex gap-3'>
				<span className='text-[9px] text-[#2a4a60]'>
					<span className='text-[#3a6080]'>{session.interaction_count}</span> events
				</span>
				<span className='text-[9px] text-[#2a4a60]'>
					<span className='text-[#3a6080]'>{session.switch_count}</span> switches
				</span>
			</div>
		</button>
	);
}
