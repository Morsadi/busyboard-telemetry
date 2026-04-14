'use client';

import { useRealtime } from '@/context/RealtimeContext';
import { bg, border, text, type as t } from '@/lib/styles';

const SWITCH_NAMES = ['SW01', 'SW02', 'SW03', 'SW04', 'SW05', 'SW06', 'SW07', 'SW08', 'SW09', 'SW10', 'SW11'];

export function SwitchGrid() {
	const { latestSwitchEvent } = useRealtime();

	return (
		<div className='grid grid-cols-11 gap-1'>
			{SWITCH_NAMES.map((name) => {
				const isLatest = latestSwitchEvent?.switch_name === name;
				const isOn = isLatest && latestSwitchEvent?.value === 1;

				return (
					<div
						key={name}
						className={`h-9 rounded flex flex-col items-center justify-center gap-0.5 border
              ${isOn ? `${bg.activeSession} border-blue-800` : `${bg.surfaceDeep} ${border.default}`}`}>
						<div className={`w-1.5 h-1.5 rounded-full ${isOn ? 'bg-blue-500' : 'bg-[#1c2a3a]'}`} />
						<span className={`text-[9px] ${t.mono} ${isOn ? text.sw : text.dim}`}>{name.replace('SW', '')}</span>
					</div>
				);
			})}
		</div>
	);
}
