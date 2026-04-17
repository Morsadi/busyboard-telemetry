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
	const hasInteractions = session.interaction_count > 0;

	return (
		<button
			onClick={() => onSelect(session.session_id)}
			className={`relative w-full text-left px-3 py-2.5 border-b transition-colors
        ${border.subtle}
        ${isSelected ? bg.activeSession : `hover:${bg.surface}`}`}>
			<div className={`absolute left-0 top-0 h-full w-[3px] ${hasInteractions ? bg.sw : bg.mutedBar}`} />

			<div className='flex items-center justify-between mb-1'>
				<time className={`text-[0.8rem] md:text-[1rem] font-medium ${text.primary}`}>{formatTimestamp(session.started_at, 'session')}</time>

				{isLive && <span className={`text-[9px] ${text.live}`}>● live</span>}
			</div>

			<div className='flex items-center justify-between mb-2'>
				<code className={`${t.monoXs} ${text.dim}`}>{session.session_id}</code>

				<time className={`${t.monoSm} ${text.dim}`}>{formatDuration(session.started_at, session.ended_at)}</time>
			</div>

			<div className='flex gap-3'>
				<span className={`text-[9px] ${text.dim}`}>
					<span className={`${t.monoXs} ${text.muted}`}>{session.interaction_count}</span> events
				</span>

				<span className={`text-[9px] ${text.dim}`}>
					<span className={`${t.monoXs} ${text.muted}`}>{session.switch_count}</span> switches
				</span>
			</div>
		</button>
	);
}
