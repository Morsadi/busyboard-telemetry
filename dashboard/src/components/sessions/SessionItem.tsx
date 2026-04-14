import { formatTimestamp, formatDuration } from '@/lib/utils';
import { bg, border, text, type as t } from '@/lib/styles';
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
			className={`w-full text-left px-3 py-2.5 border-b ${border.subtle} border-l-2 transition-colors
        ${isSelected ? `${bg.activeSession} ${border.active}` : `border-l-transparent hover:${bg.surface}`}`}>
			<div className='flex items-center justify-between mb-1'>
				<span className={`text-[12px] font-medium ${text.primary}`}>{formatTimestamp(session.started_at, 'session')}</span>
				{isLive && <span className={`text-[9px] ${text.live}`}>● live</span>}
			</div>

			<div className='flex items-center justify-between mb-2'>
				<span className={`${t.monoXs} ${text.dim}`}>{session.session_id}</span>
				<span className={`${t.monoXs} ${text.dim}`}>{formatDuration(session.duration_ms, session.started_at, session.ended_at)}</span>
			</div>

			<div className='flex gap-3'>
				<span className={`text-[9px] ${text.dim}`}>
					<span className={text.muted}>{session.interaction_count}</span> events
				</span>
				<span className={`text-[9px] ${text.dim}`}>
					<span className={text.muted}>{session.switch_count}</span> switches
				</span>
			</div>
		</button>
	);
}
