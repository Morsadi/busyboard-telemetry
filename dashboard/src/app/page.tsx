'use client';

import { useState, Suspense } from 'react';
import { HardwareState } from '@/components/layout/HardwareState';
import { Topbar } from '@/components/layout/Topbar';
import { SessionList } from '@/components/sessions/SessionList';
import { EventPanel } from '@/components/events/EventPanel';
import { useRouter, useSearchParams } from 'next/dist/client/components/navigation';

export default function Page() {
	return (
		<Suspense>
			<DashboardPage />
		</Suspense>
	);
}

function DashboardPage() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const [selectedSessionId, setSelectedSessionId] = useState<string | null>(searchParams.get('session') ?? null);

	function handleSelectSession(id: string) {
		setSelectedSessionId(id);
		router.push(`/?session=${id}`, { scroll: false });
	}

	return (
		<div className='flex flex-col h-screen bg-[#0b0f14] overflow-hidden'>
			<Topbar />
			<HardwareState />

			<div className='flex flex-1 overflow-x-auto'>
				<SessionList
					selectedId={selectedSessionId}
					onSelect={handleSelectSession}
				/>
				<EventPanel sessionId={selectedSessionId} />
			</div>
		</div>
	);
}
