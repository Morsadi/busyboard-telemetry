'use client';

import { useRealtime } from '@/context/RealtimeContext';
import { bg, border, text, type } from '@/lib/styles';

export function Topbar() {
	const { devices } = useRealtime();
	const anyOnline = devices.some((d) => d.status === 'online');

	return (
		<header className={`flex items-center gap-3 px-4 py-2.5 ${bg.surface} border-b ${border.default}`}>
			<div className='w-2 h-2 rounded-full bg-blue-600 shrink-0' />
			<span className='text-xs font-medium tracking-[0.2em] uppercase text-white'>BusyBoard</span>
			<div className='ml-auto flex items-center gap-2'>
				<div className={`w-1.5 h-1.5 rounded-full ${anyOnline ? 'bg-green-600' : 'bg-slate-600'}`} />
				<span className={`text-[11px] ${text.muted}`}>{anyOnline ? 'Device connected' : 'No devices online'}</span>
			</div>
		</header>
	);
}
