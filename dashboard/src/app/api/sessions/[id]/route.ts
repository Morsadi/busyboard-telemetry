import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase-server';
import type { AuditRow } from '@/types';

export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
	const supabase = await createClient();
	const { id } = await params;

	const [switchRes, eventRes] = await Promise.all([
		supabase.from('switch_events').select('id, switch_name, value, event_ts').eq('session_id', id).order('event_ts', { ascending: false }),
		supabase.from('events').select('id, event_type, event_ts, device_id, payload_json').eq('session_id', id).order('event_ts', { ascending: false }),
	]);

	if (switchRes.error) return NextResponse.json({ error: switchRes.error.message }, { status: 500 });
	if (eventRes.error) return NextResponse.json({ error: eventRes.error.message }, { status: 500 });

	const switchRows: AuditRow[] = (switchRes.data ?? []).map((r) => ({
		id: r.id,
		event_ts: r.event_ts,
		source: r.switch_name,
		source_type: 'switch' as const,
		event_type: 'toggle',
		value: r.value === 1 ? 'ON' : 'OFF',
	}));

	const deviceRows: AuditRow[] = (eventRes.data ?? []).map((r) => ({
		id: r.id,
		event_ts: r.event_ts,
		source: r.device_id,
		source_type: 'device' as const,
		event_type: r.event_type,
		value: r.event_type,
		payload_json: r.payload_json,
	}));

	const merged = [...switchRows, ...deviceRows].sort((a, b) => new Date(b.event_ts).getTime() - new Date(a.event_ts).getTime());

	return NextResponse.json(merged);
}
