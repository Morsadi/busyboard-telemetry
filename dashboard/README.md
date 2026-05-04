# BusyBoard Dashboard

Next.js read-only dashboard for the BusyBoard system. Renders live hardware state, device status, session history, and per-session audit logs sourced from Supabase.

**Live:** [busyboard-telemetry.vercel.app](https://busyboard-telemetry.vercel.app/)

---

## File Structure

```
dashboard/
└── src/
    ├── app/
    │   ├── api/sessions/
    │   │   ├── route.ts             # GET /api/sessions: paginated list
    │   │   └── [id]/route.ts        # GET /api/sessions/:id: session + audit rows
    │   ├── layout.tsx               # Root layout, bootstraps RealtimeProvider
    │   ├── page.tsx                 # Shell, selected-session state, URL sync
    │   └── globals.css
    ├── components/
    │   ├── layout/
    │   │   ├── Topbar.tsx           # Logo and connection status
    │   │   └── HardwareState.tsx    # Switch grid + device list banner
    │   ├── switches/SwitchGrid.tsx  # Live read-only switch state
    │   ├── devices/DeviceList.tsx   # Online/offline device status
    │   ├── sessions/
    │   │   ├── SessionList.tsx      # Searchable, paginated index
    │   │   └── SessionItem.tsx      # Individual session row
    │   └── events/
    │       ├── EventPanel.tsx       # Fetches + renders selected session
    │       ├── EventStats.tsx       # Header and stat strip
    │       └── EventTable.tsx       # Chronological audit table
    ├── context/
    │   └── RealtimeContext.tsx      # Shared Supabase Realtime channel
    ├── lib/
    │   ├── supabase.ts              # Browser client
    │   ├── supabase-server.ts       # Server client for API routes
    │   ├── utils.ts                 # Timestamp formatting, gap calculation
    │   └── styles.ts                # Shared Tailwind design tokens
    ├── types/index.ts               # Shared TypeScript types
    └── middleware.ts                # Upstash rate limiting on /api
```

---

## Stack

| Layer | Detail |
|-------|--------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Data | Supabase (Postgres) |
| Realtime | Supabase Realtime via `postgres_changes` |
| Rate limiting | Upstash Redis sliding window |
| Hosting | Vercel |

---

## Views

| Component | Source | Behavior |
|-----------|--------|----------|
| Switch grid | Latest `switch_events` per switch | Seeded on load, live-updated via Realtime |
| Device list | `devices` table | Online/offline reflects ingestion server status updates |
| Session list | `/api/sessions` | Paginated, searchable by ID/date/time, filters empty sessions, new sessions prepend live |
| Event table | `/api/sessions/:id` | Chronological per-session audit; live rows prepend without refresh |

The event table shows absolute timestamp, relative offset from session start, device, event type, value, and gap since the previous event. Gaps over 60 seconds are highlighted.

---

## Realtime

A single Supabase Realtime channel is created in `RealtimeContext` and shared across the app. Components subscribe to specific tables (`switch_events`, `devices`, `sessions`) without opening their own connections.

---

## Read-Only by Design

The dashboard never writes to the database. The browser uses the Supabase **anon key** with Row Level Security enforcing read-only access at the database level. The service role key stays on the ingestion server.

---

## API Routes

| Route | Returns |
|-------|---------|
| `GET /api/sessions` | Paginated session index with search params |
| `GET /api/sessions/:id` | Session metadata + full audit rows |

Both routes pass through `middleware.ts`, which applies a 60 req/min per-IP limit via Upstash Redis.

---

## Related Components

| Component | Role | Repo |
|-----------|------|------|
| BusyBoard Firmware | Publishes events that populate the dashboard | - |
| Ingestion Server | Writes the data this dashboard reads | - |