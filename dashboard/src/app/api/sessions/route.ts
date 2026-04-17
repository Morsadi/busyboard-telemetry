import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase-server';

const PAGE_SIZE = 50;

export async function GET(req: Request) {
	const supabase = await createClient();
	const { searchParams } = new URL(req.url);

	const page = Math.max(0, parseInt(searchParams.get('page') ?? '0'));
	const search = searchParams.get('search')?.trim() ?? '';
	const from = page * PAGE_SIZE;
	const to = from + PAGE_SIZE - 1;

	let query = supabase
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
		.range(from, to);

	if (search) {
		query = query.ilike('session_id', `%${search}%`);
	}

	const { data, error } = await query;
	if (error) return NextResponse.json({ error: error.message }, { status: 500 });

	const sessions = (data ?? []).map((row) => {
		const { switch_events, ...session } = row;
		return {
			...session,
			switch_count: new Set((switch_events ?? []).map((e: { switch_name: string }) => e.switch_name)).size,
		};
	});

	return NextResponse.json({
		sessions,
		page,
		hasMore: sessions.length === PAGE_SIZE,
	});
}
