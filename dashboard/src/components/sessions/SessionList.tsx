'use client';

import { useEffect, useState } from 'react';
import { useRealtime } from '@/context/RealtimeContext';
import { SessionItem } from './SessionItem';
import { bg, border, text, type as t } from '@/lib/styles';
import type { Session } from '@/types';

type Props = {
	selectedId: string | null;
	onSelect: (id: string) => void;
};

async function fetchSessions(page: number): Promise<{
	sessions: Session[];
	hasMore: boolean;
}> {
	const r = await fetch(`/api/sessions?page=${page}`);
	return r.json();
}

export function SessionList({ selectedId, onSelect }: Props) {
	const [sessions, setSessions] = useState<Session[]>([]);
	const [loading, setLoading] = useState(true);
	const [loadingMore, setLoadingMore] = useState(false);
	const [page, setPage] = useState(0);
	const [hasMore, setHasMore] = useState(false);
	const [input, setInput] = useState('');
	const [query, setQuery] = useState('');
	const [hideEmpty, setHideEmpty] = useState(false);
	const { latestSwitchEvent, latestEvent } = useRealtime();

	useEffect(() => {
		setLoading(true);
		fetchSessions(0)
			.then(({ sessions: data, hasMore: more }) => {
				setSessions(data);
				setHasMore(more);
				setPage(0);
			})
			.finally(() => setLoading(false));
	}, []);

	useEffect(() => {
		const timer = setTimeout(() => setQuery(input), 400);
		return () => clearTimeout(timer);
	}, [input]);

	function loadMore() {
		const nextPage = page + 1;
		setLoadingMore(true);
		fetchSessions(nextPage)
			.then(({ sessions: data, hasMore: more }) => {
				setSessions((prev) => [...prev, ...data]);
				setPage(nextPage);
				setHasMore(more);
			})
			.finally(() => setLoadingMore(false));
	}

	useEffect(() => {
		if (!latestSwitchEvent) return;
		setSessions((prev) => prev.map((s) => (s.session_id === latestSwitchEvent.session_id ? { ...s, interaction_count: s.interaction_count + 1 } : s)));
	}, [latestSwitchEvent]);

	useEffect(() => {
		if (!latestEvent) return;
		if (latestEvent.event_type === 'session_started' || latestEvent.event_type === 'session_ended') {
			fetchSessions(0).then(({ sessions: data, hasMore: more }) => {
				setSessions(data);
				setHasMore(more);
				setPage(0);
			});
		}
	}, [latestEvent]);

	// Client-side filter across ID, date label, and time
	const visible = sessions.filter((s) => {
		const matchesHide = hideEmpty ? s.interaction_count > 0 : true;
		if (!query) return matchesHide;

		const q = query.toLowerCase();
		const label = new Date(s.started_at).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
		});
		const time = new Date(s.started_at).toLocaleTimeString('en-US', {
			hour: 'numeric',
			minute: '2-digit',
			hour12: true,
		});

		const matchesSearch = s.session_id.toLowerCase().includes(q) || label.toLowerCase().includes(q) || time.toLowerCase().includes(q);

		return matchesHide && matchesSearch;
	});

	const groups = Object.groupBy(visible, (s) =>
		new Date(s.started_at).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
		}),
	);

	const grouped = Object.entries(groups).map(([label, items]) => ({
		label,
		items: items ?? [],
	}));

	return (
		<aside className={`w-[160px] md:w-[220px] lg:w-[300px] flex flex-col border-r ${border.default}`}>
			<div className={`border-b ${border.default} px-3 py-2.5 flex-shrink-0`}>
				<p className={`${t.sectionLabel} ${text.muted} mb-2`}>Sessions</p>

				<input
					type='text'
					placeholder='ID, Apr 14, 4:53 PM...'
					value={input}
					onChange={(e) => setInput(e.target.value)}
					className={`
            w-full px-2.5 py-1.5 rounded text-[11px] ${t.mono}
            ${bg.surfaceDeep} border ${border.default}
            ${text.primary} placeholder:${text.faint}
            outline-none focus:border-blue-800 mb-2
          `}
				/>

				<button
					onClick={() => setHideEmpty((v) => !v)}
					className={`flex items-center gap-1.5 text-[10px] ${t.mono} transition-colors
            ${hideEmpty ? text.sw : text.dim}`}>
					<span
						className={`w-3 h-3 rounded-sm border flex items-center justify-center
            ${hideEmpty ? 'border-blue-700 bg-[#0a1f3a]' : border.default}`}>
						{hideEmpty && <span className='w-1.5 h-1.5 rounded-sm bg-blue-500' />}
					</span>
					Has Activity
				</button>
			</div>

			<div className='min-h-0 flex-1 overflow-y-auto'>
				{loading && <p className={`px-3 py-4 text-[0.75rem] md:text-[1rem] ${text.dim}`}>Loading…</p>}
				{!loading && visible.length === 0 && <p className={`px-3 py-4 text-[0.75rem] md:text-[1rem] ${text.dim}`}>No sessions found.</p>}

				{grouped.map(({ label, items }) => (
					<div key={label}>
						<div className={`sticky top-0 z-10 ${bg.base} px-3 py-1.5 text-[0.75rem] md:text-[1rem] uppercase tracking-[1.5px] ${text.faint}`}>{label}</div>
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

				{hasMore && !loading && (
					<button
						onClick={loadMore}
						disabled={loadingMore}
						className={`w-full py-3 text-[11px] border-t ${border.subtle} transition-colors
              ${loadingMore ? text.dim : `${text.dim} hover:${text.muted}`}`}>
						{loadingMore ? 'Load more' : 'Load more'}
					</button>
				)}
			</div>
		</aside>
	);
}
