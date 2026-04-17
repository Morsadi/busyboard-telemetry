'use client';

import { useRealtime } from '@/context/RealtimeContext';
import { formatTimestamp } from '@/lib/utils';
import { bg, border, text, type as t } from '@/lib/styles';

export function DeviceList() {
	const { devices } = useRealtime();

	if (!devices.length) {
		return <p className={`text-[11px] ${text.dim}`}>No devices found</p>;
	}

	return (
		<div className='flex flex-col gap-1.5'>
			{devices.map((device) => {
				const online = device.status === 'online';
				return (
					<div
						key={device.device_id}
						className={`flex items-center gap-2.5 px-2.5 py-2 rounded ${bg.surfaceDeep} border ${border.default}`}>
						<div className={`w-1.5 h-1.5 rounded-full shrink-0 ${online ? 'bg-green-600' : 'bg-slate-600'}`} />
						<div className='flex-1 min-w-0'>
							<p className={`text-[11px] md:text-[13px] ${text.primary} truncate`}>{device.label}</p>
							<p className={`text-[10px] ${text.dim} ${t.mono} truncate`}>{device.device_id}</p>
						</div>
						<span className={`text-[10px] shrink-0 ${online ? 'text-green-700' : text.dim}`}>
							{online ? (
								'Online'
							) : (
								<div className={`flex flex-col`}>
									<p>Last seen</p>
									<p className={`text-[10px] ${text.dim}`}>{formatTimestamp(device.last_seen_at, 'session')}</p>
								</div>
							)}
						</span>
					</div>
				);
			})}
		</div>
	);
}
