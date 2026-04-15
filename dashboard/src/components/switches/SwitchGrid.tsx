'use client';

import { useRealtime } from '@/context/RealtimeContext';
import { bg, border, text, type as t } from '@/lib/styles';

const SWITCH_NAMES = ['SW1', 'SW2', 'SW3', 'SW4', 'SW5', 'SW6', 'SW7', 'SW8', 'SW9', 'SW10', 'SW11'];

export function SwitchGrid() {
	const { switchStates } = useRealtime();

	return (
		<div className='flex flex-wrap gap-1'>
			{SWITCH_NAMES.map((name) => {
				const isOn = switchStates[name] === 1;
				return (
					<div
						key={name}
						className={`h-8 w-8 rounded flex flex-col items-center justify-center gap-0.5 border
              ${isOn ? `${bg.activeSession} border-blue-800` : `${bg.surfaceDeep} ${border.default}`}`}>
						<div className={`w-1.5 h-1.5 rounded-full ${isOn ? 'bg-blue-500' : 'bg-[#1c2a3a]'}`} />
						<span className={`text-[9px] ${t.mono} ${isOn ? text.sw : text.dim}`}>{name.replace('SW', '')}</span>
					</div>
				);
			})}
		</div>
	);
}
