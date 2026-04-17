'use client';

import { useState } from 'react';
import { HardwareState } from '@/components/layout/HardwareState';
import { Topbar } from '@/components/layout/Topbar';
import { SessionList } from '@/components/sessions/SessionList';
import { EventPanel } from '@/components/events/EventPanel';

export default function DashboardPage() {
	const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

	return (
		<div className='flex flex-col h-screen bg-[#0b0f14] overflow-hidden'>
			<Topbar />
			<HardwareState />

			<div className='flex flex-1 overflow-x-auto'>
				<SessionList
					selectedId={selectedSessionId}
					onSelect={setSelectedSessionId}
				/>
				<EventPanel sessionId={selectedSessionId} />
			</div>
		</div>
	);
}
