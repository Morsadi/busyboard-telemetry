import type { Metadata } from 'next';
import { createClient } from '@/lib/supabase-server';
import { RealtimeProvider } from '@/context/RealtimeContext';
import { labelDevice } from '@/lib/utils';
import type { Device, DbDevice } from '@/types';
import './globals.css';

export const metadata: Metadata = { title: 'BusyBoard' };

export default async function RootLayout({ children }: { children: React.ReactNode }) {
	const supabase = await createClient();
	const { data } = await supabase.from('devices').select('*');

	const initialDevices: Device[] = (data ?? []).map((row: DbDevice) => {
		const { label, type } = labelDevice(row.device_id);
		return {
			device_id: row.device_id,
			label,
			type,
			status: row.status as Device['status'],
			last_seen_at: row.last_seen_at,
		};
	});

	return (
		<html lang='en'>
			<body className='bg-[#0b0f14] text-[#e4eaf0] antialiased'>
				<RealtimeProvider initialDevices={initialDevices}>{children}</RealtimeProvider>
			</body>
		</html>
	);
}
