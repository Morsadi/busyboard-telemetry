'use client';

import { useState } from 'react';
import { HardwareState } from '@/components/layout/HardwareState';
import { Topbar } from '@/components/layout/Topbar';

export default function DashboardPage() {
	const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

	return (
		<div className='flex flex-col h-screen bg-[#0b0f14] text-white overflow-hidden'>
			<Topbar />
			<HardwareState />
		</div>
	);
}
