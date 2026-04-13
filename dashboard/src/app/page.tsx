'use client';

import { useState } from 'react';
import { HardwareState } from '@/components/layout/HardwareState';
import { Topbar } from '@/components/layout/Topbar';
import { SessionList } from '@/components/sessions/SessionList';

export default function DashboardPage() {
	const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

	return (
		<div className='flex flex-col h-screen bg-[#0b0f14] text-white overflow-hidden'>
			<Topbar />
			<HardwareState />

			<div className='flex flex-1 overflow-hidden'>
				<SessionList
					selectedId={selectedSessionId}
					onSelect={setSelectedSessionId}
				/>
			</div>
		</div>
	);
}
