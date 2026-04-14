import { SwitchGrid } from '@/components/switches/SwitchGrid';
import { DeviceList } from '@/components/devices/DeviceList';
import { bg, border, text, type as t } from '@/lib/styles';

export function HardwareState() {
	return (
		<div className={`flex gap-6 px-4 py-3 border-b ${border.default} ${bg.base}`}>
			<div className='flex-1'>
				<p className={`${t.label} ${text.muted} mb-2`}>Live switches</p>
				<SwitchGrid />
			</div>
			<div className={`w-px ${bg.surface}`} />
			<div className='w-52 shrink-0'>
				<p className={`${t.label} ${text.muted} mb-2`}>Devices</p>
				<DeviceList />
			</div>
		</div>
	);
}
