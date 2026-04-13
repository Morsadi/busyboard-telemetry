// ─── Timestamp helpers ────────────────────────────────────────────────────────

/**
 * 'session' → "Apr 7 · 2:33 PM"
 * 'table'   → "2:33:51 PM"
 */
export function formatTimestamp(iso: string, style: 'session' | 'table'): string {
	const d = new Date(iso);
	if (style === 'session') {
		const date = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
		const time = d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
		return `${date} · ${time}`;
	}
	return d.toLocaleTimeString('en-US', {
		hour: 'numeric',
		minute: '2-digit',
		second: '2-digit',
		hour12: true,
	});
}

/**
 * "+0:29" — time elapsed from session start to event
 */
export function formatRelative(eventTs: string, sessionStart: string): string {
	const diffMs = new Date(eventTs).getTime() - new Date(sessionStart).getTime();
	const totalSec = Math.floor(Math.abs(diffMs) / 1000);
	const m = Math.floor(totalSec / 60);
	const s = totalSec % 60;
	return `+${m}:${String(s).padStart(2, '0')}`;
}

/**
 * Gap between two consecutive events.
 * Returns display string + whether it's notable (> 60s).
 */
export function calcGap(laterTs: string, earlierTs: string): { display: string; notable: boolean } {
	const diffMs = new Date(laterTs).getTime() - new Date(earlierTs).getTime();
	const totalSec = Math.floor(diffMs / 1000);
	if (totalSec < 0) return { display: '—', notable: false };
	const display = totalSec >= 60 ? `${Math.floor(totalSec / 60)}m ${totalSec % 60}s` : `${totalSec}s`;
	return { display, notable: totalSec > 60 };
}

/**
 * "12:43" — human duration from ms or start/end pair
 */
export function formatDuration(startOrMs: string | number, end?: string | null): string {
	const ms = typeof startOrMs === 'number' ? startOrMs : end ? new Date(end).getTime() - new Date(startOrMs).getTime() : Date.now() - new Date(startOrMs).getTime();

	const totalSec = Math.floor(ms / 1000);
	const m = Math.floor(totalSec / 60);
	const s = totalSec % 60;
	return `${m}:${String(s).padStart(2, '0')}`;
}

// ─── Device helpers ───────────────────────────────────────────────────────────

/**
 * Derives a human label and type from device_id.
 * TO EXTEND.
 */
export function labelDevice(device_id: string): { label: string; type: 'busyboard' | 'buzzer' } {
	if (device_id.startsWith('buzzer')) return { label: 'Alarm', type: 'buzzer' };
	return { label: 'Control Panel', type: 'busyboard' };
}
