import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase-server';

const SESSION_ID_RE = /^\d{14}$/;

export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
	const supabase = await createClient();
	const { id } = await params;

	if (!SESSION_ID_RE.test(id)) {
		return NextResponse.json({ error: 'Invalid session ID' }, { status: 400 });
	}

	const [sessionRes, switchRes, eventRes] = await Promise.all([
		supabase
			.from('sessions')
			.select(
				`
        session_id,
        device_id,
        started_at,
        ended_at,
        duration_ms,
        interaction_count,
        status,
        switch_events ( switch_name )
      `,
			)
			.eq('session_id', id)
			.single(),
		supabase.from('switch_events').select('id, switch_name, value, event_ts').eq('session_id', id).order('event_ts', { ascending: false }),
		supabase
			.from('events')
			.select('id, event_type, event_ts, device_id, payload_json')
			.eq('session_id', id)
			.in('event_type', ['session_started', 'session_ended'])
			.order('event_ts', { ascending: false }),
	]);

	if (sessionRes.error) return NextResponse.json({ error: sessionRes.error.message }, { status: 500 });
	if (switchRes.error) return NextResponse.json({ error: switchRes.error.message }, { status: 500 });
	if (eventRes.error) return NextResponse.json({ error: eventRes.error.message }, { status: 500 });

	const { switch_events, ...sessionData } = sessionRes.data;
	const session = {
		...sessionData,
		switch_count: new Set((switch_events ?? []).map((e: { switch_name: string }) => e.switch_name)).size,
	};

	const switchRows = (switchRes.data ?? []).map((r) => ({
		id: r.id,
		event_ts: r.event_ts,
		source: r.switch_name,
		source_type: 'switch' as const,
		event_type: 'toggle',
		value: r.value === 1 ? 'ON' : 'OFF',
		_ts: Date.parse(r.event_ts),
	}));

	const deviceRows = (eventRes.data ?? []).map((r) => ({
		id: r.id,
		event_ts: r.event_ts,
		source: r.device_id,
		source_type: 'device' as const,
		event_type: r.event_type,
		value: r.event_type,
		payload_json: r.payload_json,
		_ts: Date.parse(r.event_ts),
	}));

	const rows = [...switchRows, ...deviceRows].sort((a, b) => b._ts - a._ts).map(({ _ts, ...row }) => row);

	return NextResponse.json({ session, rows });
}
