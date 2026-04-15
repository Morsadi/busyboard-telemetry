'use client';

import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { createClient } from '@/lib/supabase';
import { labelDevice } from '@/lib/utils';
import type { Device, DbDevice, DbEvent, DbSwitchEvent } from '@/types';

const SWITCH_NAMES = ['SW1', 'SW2', 'SW3', 'SW4', 'SW5', 'SW6', 'SW7', 'SW8', 'SW9', 'SW10', 'SW11'];

type SwitchStates = Record<string, number>;

type RealtimeContextValue = {
	devices: Device[];
	switchStates: SwitchStates;
	latestSwitchEvent: DbSwitchEvent | null;
	latestEvent: DbEvent | null;
};

const RealtimeContext = createContext<RealtimeContextValue>({
	devices: [],
	switchStates: Object.fromEntries(SWITCH_NAMES.map((n) => [n, 0])),
	latestSwitchEvent: null,
	latestEvent: null,
});

export function RealtimeProvider({ children, initialDevices }: { children: React.ReactNode; initialDevices: Device[] }) {
	const supabase = useRef(createClient());
	const [devices, setDevices] = useState<Device[]>(initialDevices);
	const [switchStates, setSwitchStates] = useState<SwitchStates>(Object.fromEntries(SWITCH_NAMES.map((n) => [n, 0])));
	const [latestSwitchEvent, setLatestSwitchEvent] = useState<DbSwitchEvent | null>(null);
	const [latestEvent, setLatestEvent] = useState<DbEvent | null>(null);

	// Fetch real switch state on mount — latest value per switch_name
	useEffect(() => {
		supabase.current
			.from('switch_events')
			.select('switch_name, value, event_ts')
			.order('event_ts', { ascending: false })
			.then(({ data }) => {
				if (!data) return;
				// Take the first (most recent) row per switch_name
				const seen = new Set<string>();
				const initial: SwitchStates = Object.fromEntries(SWITCH_NAMES.map((n) => [n, 0]));
				for (const row of data) {
					if (!seen.has(row.switch_name)) {
						seen.add(row.switch_name);
						initial[row.switch_name] = Number(row.value);
					}
				}
				setSwitchStates(initial);
			});
	}, []);

	// Realtime channel
	useEffect(() => {
		const channel = supabase.current
			.channel('busyboard-realtime')
			.on<DbDevice>('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'devices' }, ({ new: row }) =>
				setDevices((prev) => prev.map((d) => (d.device_id === row.device_id ? toDevice(row) : d))),
			)
			.on<DbDevice>('postgres_changes', { event: 'INSERT', schema: 'public', table: 'devices' }, ({ new: row }) => setDevices((prev) => [...prev, toDevice(row)]))
			.on<DbSwitchEvent>('postgres_changes', { event: 'INSERT', schema: 'public', table: 'switch_events' }, ({ new: row }) => {
				setSwitchStates((prev) => ({
					...prev,
					[row.switch_name]: Number(row.value),
				}));
				setLatestSwitchEvent(row);
			})
			.on<DbEvent>('postgres_changes', { event: 'INSERT', schema: 'public', table: 'events' }, ({ new: row }) => setLatestEvent(row))
			.subscribe((status) => {
				console.log('[realtime] status:', status);
			});

		return () => {
			supabase.current.removeChannel(channel);
		};
	}, []);

	return <RealtimeContext.Provider value={{ devices, switchStates, latestSwitchEvent, latestEvent }}>{children}</RealtimeContext.Provider>;
}

export function useRealtime() {
	return useContext(RealtimeContext);
}

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
