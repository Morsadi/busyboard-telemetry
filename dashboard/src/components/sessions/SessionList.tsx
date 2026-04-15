'use client';

import { useEffect, useState } from 'react';
import { useRealtime } from '@/context/RealtimeContext';
import { SessionItem } from './SessionItem';
import type { Session } from '@/types';

type Props = {
	selectedId: string | null;
	onSelect: (id: string) => void;
};

export function SessionList({ selectedId, onSelect }: Props) {
	const [sessions, setSessions] = useState<Session[]>([]);
	const [loading, setLoading] = useState(true);
	const { latestSwitchEvent, latestEvent } = useRealtime();

	useEffect(() => {
		fetch('/api/sessions')
			.then((r) => r.json())
			.then((data) => setSessions(data))
			.finally(() => setLoading(false));
	}, []);

	// Increment interaction_count on the active session when a new switch event arrives
	useEffect(() => {
		if (!latestSwitchEvent) return;
		setSessions((prev) => prev.map((s) => (s.session_id === latestSwitchEvent.session_id ? { ...s, interaction_count: s.interaction_count + 1 } : s)));
	}, [latestSwitchEvent]);

	// Handle session_start — prepend new session
	useEffect(() => {
		if (!latestEvent) return;
		if (latestEvent.event_type === 'session_started' || latestEvent.event_type === 'session_ended') {
			fetch('/api/sessions')
				.then((r) => r.json())
				.then((data) => setSessions(data));
		}
	}, [latestEvent]);

	// Group sessions by date label
	const grouped = sessions.reduce<{ label: string; items: Session[] }[]>((acc, session) => {
		const label = new Date(session.started_at).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
		});
		const existing = acc.find((g) => g.label === label);
		if (existing) existing.items.push(session);
		else acc.push({ label, items: [session] });
		return acc;
	}, []);

	return (
		<aside className='flex flex-col border-r border-[#1c2a3a]'>
			<div className='border-b border-[#1c2a3a] px-3 py-2.5'>
				<p className='text-[10px] uppercase tracking-[1.5px] text-[#3a6080]'>Sessions</p>
			</div>

			<div className='min-h-0 flex-1 overflow-y-auto'>
				{loading && <p className='px-3 py-4 text-[11px] text-[#2a4a60]'>Loading…</p>}
				{!loading && sessions.length === 0 && <p className='px-3 py-4 text-[11px] text-[#2a4a60]'>No sessions yet.</p>}
				{grouped.map(({ label, items }) => (
					<div key={label}>
						<div className='sticky top-0 z-10 bg-[#0b0f14] px-3 py-1.5 text-[9px] uppercase tracking-[1.5px] text-[#1c2a3a]'>{label}</div>
						{items.map((session) => (
							<SessionItem
								key={session.session_id}
								session={session}
								isSelected={selectedId === session.session_id}
								onSelect={onSelect}
							/>
						))}
					</div>
				))}
			</div>
		</aside>
	);
}
