'use client';

import { useEffect, useState } from 'react';
import { useRealtime } from '@/context/RealtimeContext';
import { EventStats } from './EventStats';
import { EventTable } from './EventTable';
import { text } from '@/lib/styles';
import type { Session, AuditRow } from '@/types';

type Props = { sessionId: string | null };

export function EventPanel({ sessionId }: Props) {
	const [session, setSession] = useState<Session | null>(null);
	const [rows, setRows] = useState<AuditRow[]>([]);
	const [loading, setLoading] = useState(false);
	const { latestSwitchEvent, latestEvent } = useRealtime();

	useEffect(() => {
		if (!sessionId) {
			setSession(null);
			setRows([]);
			return;
		}
		setLoading(true);
		Promise.all([fetch('/api/sessions').then((r) => r.json()), fetch(`/api/sessions/${sessionId}`).then((r) => r.json())])
			.then(([sessions, auditRows]) => {
				setSession(sessions.find((s: Session) => s.session_id === sessionId) ?? null);
				setRows(auditRows);
			})
			.finally(() => setLoading(false));
	}, [sessionId]);

	// Prepend live switch events for active session
	useEffect(() => {
		if (!latestSwitchEvent || !session) return;
		if (latestSwitchEvent.session_id !== session.session_id) return;
		if (session.status !== 'active') return;
		const newRow: AuditRow = {
			id: latestSwitchEvent.id,
			event_ts: latestSwitchEvent.event_ts,
			source: latestSwitchEvent.switch_name,
			source_type: 'switch',
			event_type: 'toggle',
			value: latestSwitchEvent.value === 1 ? 'ON' : 'OFF',
		};
		setRows((prev) => [newRow, ...prev]);
		setSession((prev) => (prev ? { ...prev, interaction_count: prev.interaction_count + 1 } : prev));
	}, [latestSwitchEvent]);

	// Mark session ended without full refetch
	useEffect(() => {
		if (!latestEvent || !session) return;
		if (latestEvent.session_id !== session.session_id) return;
		if (latestEvent.event_type === 'session_ended') {
			setSession((prev) => (prev ? { ...prev, status: 'ended' } : prev));
		}
	}, [latestEvent]);

	const centered = `flex flex-1 items-center justify-center text-[12px] ${text.dim}`;

	if (!sessionId) return <main className={centered}>Select a session to view its log</main>;
	if (loading) return <main className={centered}>Loading…</main>;
	if (!session) return null;

	return (
		<main className='flex min-h-0 flex-1 flex-col'>
			<EventStats session={session} />
			<EventTable
				rows={rows}
				session={session}
			/>
		</main>
	);
}
