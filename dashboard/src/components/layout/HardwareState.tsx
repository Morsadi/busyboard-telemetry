import { SwitchGrid } from '@/components/switches/SwitchGrid';
import { DeviceList } from '@/components/devices/DeviceList';
import { bg, border, text, type as t } from '@/lib/styles';

export function HardwareState() {
	return (
		<div className={`grid gap-2 grid-cols-[0.5fr_auto_1fr] px-4 py-3 border-b ${border.default} ${bg.base}`}>
			<div>
				<p className={`${t.sectionLabel} mb-2`}>Devices</p>
				<DeviceList />
			</div>
			<div className={`w-px ${bg.surface}`} />
			<div>
				<p className={`${t.sectionLabel} mb-2`}>Live switches</p>
				<SwitchGrid />
			</div>
		</div>
	);
}
