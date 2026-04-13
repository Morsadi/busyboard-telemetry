import { SwitchGrid } from '@/components/switches/SwitchGrid';
import { DeviceList } from '@/components/devices/DeviceList';

export function HardwareState() {
	return (
		<div className='flex gap-6 px-4 py-3 border-b border-[#1c2a3a] bg-[#0b0f14]'>
			<div className='flex-1'>
				<p className='text-[10px] uppercase tracking-[0.15em] text-slate-600 mb-2'>Live switches</p>
				<SwitchGrid />
			</div>

			<div className='w-px bg-[#1c2a3a]' />

			<div className='w-52 shrink-0'>
				<p className='text-[10px] uppercase tracking-[0.15em] text-slate-600 mb-2'>Devices</p>
				<DeviceList />
			</div>
		</div>
	);
}
