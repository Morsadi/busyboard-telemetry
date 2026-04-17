import { NextRequest, NextResponse } from 'next/server';
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
	redis: Redis.fromEnv(),
	limiter: Ratelimit.slidingWindow(60, '1 m'),
	analytics: true,
});

export async function middleware(req: NextRequest) {
	if (!req.nextUrl.pathname.startsWith('/api')) {
		return NextResponse.next();
	}

	const ip = req.headers.get('x-forwarded-for') ?? '127.0.0.1';
	const { success } = await ratelimit.limit(ip);

	if (!success) {
		return NextResponse.json({ error: 'Too many requests' }, { status: 429 });
	}

	return NextResponse.next();
}

export const config = {
	matcher: '/api/:path*',
};
