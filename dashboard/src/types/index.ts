// ─── Supabase types ─────
export type DbDevice = {
	device_id: string;
	first_seen_at: string;
	last_seen_at: string;
	status: string;
};

export type DbSession = {
	session_id: string;
	device_id: string;
	started_at: string;
	ended_at: string | null; // null while session is active
	duration_ms: number | null;
	interaction_count: number;
	status: string; // 'active' | 'ended' | 'connection_lost'
};

export type DbEvent = {
	id: number;
	device_id: string;
	session_id: string | null; // null for device-level events outside a session
	event_type: string;
	event_ts: string;
	received_ts: string;
	topic: string; // MQTT topic, e.g. "busyboard/sensor-board-01/session"
	payload_json: Record<string, unknown>;
};

export type DbSwitchEvent = {
	id: number;
	session_id: string;
	device_id: string;
	switch_name: string; // 'SW01'–'SW11'
	value: 0 | 1; // 1 = ON, 0 = OFF
	event_ts: string;
};

// ─── App-level types ─────

export type Device = {
	device_id: string;
	label: string;
	type: 'busyboard' | 'buzzer';
	status: 'online' | 'offline';
	last_seen_at: string;
};

export type Session = {
	session_id: string;
	device_id: string;
	started_at: string;
	ended_at: string | null;
	duration_ms: number | null;
	interaction_count: number;
	status: 'active' | 'ended' | 'connection_lost';
	switch_count: number;
};

// Unified row for EventTable
export type AuditRow = {
	id: number;
	event_ts: string;
	source: string; // 'SW01'–'SW11' for switches | truncated device_id for device events
	source_type: 'switch' | 'device';
	event_type: string;
	value: string;
	payload_json?: Record<string, unknown>;
};
