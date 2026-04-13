'use client';

import { useRealtime } from '@/context/RealtimeContext';
import { formatTimestamp } from '@/lib/utils';

export function DeviceList() {
	const { devices } = useRealtime();

	if (!devices.length) {
		return <p className='text-[11px] text-slate-700'>No devices found</p>;
	}

	return (
		<div className='flex flex-col gap-1.5'>
			{devices.map((device) => (
				<div
					key={device.device_id}
					className='flex items-center gap-2.5 px-2.5 py-2 rounded bg-[#111820] border border-[#1c2a3a]'>
					{/* Status dot */}
					<div className={`w-1.5 h-1.5 rounded-full shrink-0 ${device.status === 'online' ? 'bg-green-600' : 'bg-slate-600'}`} />

					<div className='flex-1 min-w-0'>
						<p className='text-[11px] text-slate-300 truncate'>{device.label}</p>
						<p className='text-[10px] text-slate-600 font-mono truncate'>{device.device_id}</p>
					</div>

					<span className={`text-[10px] shrink-0 ${device.status === 'online' ? 'text-green-700' : 'text-slate-700'}`}>
						{device.status === 'online' ? 'Online' : `Last seen ${formatTimestamp(device.last_seen_at, 'session')}`}
					</span>
				</div>
			))}
		</div>
	);
}
