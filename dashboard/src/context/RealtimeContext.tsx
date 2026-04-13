'use client';

import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { createClient } from '@/lib/supabase';
import { labelDevice } from '@/lib/utils';
import type { Device, DbDevice, DbEvent, DbSwitchEvent } from '@/types';

type RealtimeContextValue = {
	devices: Device[];
	latestSwitchEvent: DbSwitchEvent | null;
	latestEvent: DbEvent | null;
};

const RealtimeContext = createContext<RealtimeContextValue>({
	devices: [],
	latestSwitchEvent: null,
	latestEvent: null,
});

export function RealtimeProvider({ children, initialDevices }: { children: React.ReactNode; initialDevices: Device[] }) {
	const supabase = useRef(createClient());
	const [devices, setDevices] = useState<Device[]>(initialDevices);
	const [latestSwitchEvent, setLatestSwitchEvent] = useState<DbSwitchEvent | null>(null);
	const [latestEvent, setLatestEvent] = useState<DbEvent | null>(null);

	// Initial device fetch
	useEffect(() => {
		supabase.current
			.from('devices')
			.select('*')
			.then(({ data }) => {
				if (data) setDevices(data.map(toDevice));
			});
	}, []);

	// Single channel — all realtime subscriptions
	useEffect(() => {
		const channel = supabase.current
			.channel('busyboard-realtime')
			.on<DbDevice>('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'devices' }, ({ new: row }) =>
				setDevices((prev) => prev.map((d) => (d.device_id === row.device_id ? toDevice(row) : d))),
			)
			.on<DbSwitchEvent>('postgres_changes', { event: 'INSERT', schema: 'public', table: 'switch_events' }, ({ new: row }) => setLatestSwitchEvent(row))
			.on<DbEvent>('postgres_changes', { event: 'INSERT', schema: 'public', table: 'events' }, ({ new: row }) => setLatestEvent(row))
			.subscribe();

		return () => {
			supabase.current.removeChannel(channel);
		};
	}, []);
	console.log('RealtimeContext render', { devices, latestSwitchEvent, latestEvent });
	return <RealtimeContext.Provider value={{ devices, latestSwitchEvent, latestEvent }}>{children}</RealtimeContext.Provider>;
}

export function useRealtime() {
	return useContext(RealtimeContext);
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function toDevice(row: DbDevice): Device {
	const { label, type } = labelDevice(row.device_id);
	return {
		device_id: row.device_id,
		label,
		type,
		status: row.status === 'online' ? 'online' : 'offline',
		last_seen_at: row.last_seen_at,
	};
}
