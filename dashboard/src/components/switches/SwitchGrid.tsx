'use client';

import { useRealtime } from '@/context/RealtimeContext';
import { bg, border, text, type as t } from '@/lib/styles';

const SWITCH_NAMES = ['SW1', 'SW2', 'SW3', 'SW4', 'SW5', 'SW6', 'SW7', 'SW8', 'SW9', 'SW10', 'SW11'];

export function SwitchGrid() {
	const { switchStates, devices } = useRealtime();

	return (
		<div className='flex flex-wrap gap-1'>
			{SWITCH_NAMES.map((name) => {
				const isOn = devices.some((device) => device.type === 'busyboard' && device.status === 'online' && switchStates[name] === 1);
				return (
					<div
						key={name}
						className={`h-9 w-9 md:h-13 md:w-12 rounded flex flex-col items-center justify-center gap-0.5 border
              ${isOn ? `${bg.activeSession} border-blue-800` : `${bg.surfaceDeep} ${border.default}`}`}>
						<div className={`w-2 h-2 rounded-full ${isOn ? 'bg-blue-500' : 'bg-[#1c2a3a]'}`} />
						<span className={`text-[10px] md:text-[12px] font-bold ${t.mono} ${isOn ? text.sw : text.dim}`}>{name.replace('SW', '')}</span>
					</div>
				);
			})}
		</div>
	);
}
