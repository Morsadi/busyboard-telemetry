import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase-server';

export async function GET() {
	const supabase = await createClient();

	// Fetch sessions with switch_count and switch_events for the most recent 50 sessions
	const { data, error } = await supabase
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
		.order('started_at', { ascending: false })
		.limit(50);

	if (error) return NextResponse.json({ error: error.message }, { status: 500 });

	const sessions = (data ?? []).map((row) => ({
		...row,
		// count distinct switch names
		switch_count: new Set(row.switch_events.map((e: { switch_name: string }) => e.switch_name)).size,
		switch_events: undefined, // strip from response
	}));

	return NextResponse.json(sessions);
}
