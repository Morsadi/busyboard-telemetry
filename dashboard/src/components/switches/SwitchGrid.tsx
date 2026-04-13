'use client';

import { useRealtime } from '@/context/RealtimeContext';

// Switch names in board order
const SWITCH_NAMES = ['SW01', 'SW02', 'SW03', 'SW04', 'SW05', 'SW06', 'SW07', 'SW08', 'SW09', 'SW10', 'SW11'];

export function SwitchGrid() {
	const { latestSwitchEvent } = useRealtime();

	// Build a name→value map from the latest event.
	// For a full live state map you'd maintain state in context;
	// this component intentionally stays read-only and stateless.
	// The latest toggle is highlighted; all others show as neutral.
	return (
		<div className='grid grid-cols-11 gap-1'>
			{SWITCH_NAMES.map((name) => {
				const isLatest = latestSwitchEvent?.switch_name === name;
				const isOn = isLatest && latestSwitchEvent?.value === 1;

				return (
					<div
						key={name}
						className={`
              h-9 rounded flex flex-col items-center justify-center gap-0.5
              border border-[#1c2a3a]
              ${isOn ? 'bg-[#0a1f3a] border-blue-800' : 'bg-[#111820]'}
            `}>
						<div className={`w-1.5 h-1.5 rounded-full ${isOn ? 'bg-blue-500' : 'bg-[#1c2a3a]'}`} />
						<span className={`text-[9px] font-mono ${isOn ? 'text-blue-400' : 'text-[#2a4a60]'}`}>{name.replace('SW', '')}</span>
					</div>
				);
			})}
		</div>
	);
}
