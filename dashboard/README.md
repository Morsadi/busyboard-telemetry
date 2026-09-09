# BusyBoard dashboard

The dashboard is a Next.js/React application that renders BusyBoard device status, switch state, session history, and per-session event rows from Supabase.

**Live:** [busyboard-telemetry.vercel.app](https://busyboard-telemetry.vercel.app/)

The application does not read SQLite. See [the architecture documentation](../docs/architecture.md) and [data model](../docs/data-model.md) for cross-system behavior.

## Requirements and environment

Install dependencies from the lockfile:

```bash
npm ci
```

Create a local gitignored `.env.local` containing:

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL used by browser and server clients |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Anonymous Supabase key used by browser and server clients |
| `UPSTASH_REDIS_REST_URL` | Upstash Redis REST endpoint for API rate limiting |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash Redis REST token |

Do not put a Supabase service-role key in `NEXT_PUBLIC_*` variables.

## Commands

Run from `dashboard/`:

```bash
npm run dev
npx tsc --noEmit --incremental false
npm run build
npm start
```

There is currently no repository-defined dashboard test or lint script.

## Structure

```text
src/
├── app/
│   ├── api/sessions/       session list/detail API routes
│   ├── layout.tsx          device seed and Realtime provider
│   └── page.tsx            dashboard shell and selected-session URL state
├── components/
│   ├── devices/            device presence
│   ├── events/             selected-session stats and rows
│   ├── layout/             top bar and hardware state
│   ├── sessions/           session list and items
│   └── switches/           live switch grid
├── context/                shared Supabase Realtime channel
├── lib/                    Supabase clients, styles, and formatting helpers
├── types/                  hand-written database and app types
└── middleware.ts           Upstash-backed API rate limiting
```

## Data flow and views

| View | Current source and behavior |
|---|---|
| Device list | Server-seeded from `devices`, then updated by device Realtime inserts/updates |
| Switch grid | Seeded from newest `switch_events` per switch name, then updated by switch inserts |
| Session list | Paginated `/api/sessions` results; UI search filters only sessions already loaded |
| Event table | `/api/sessions/{id}` combines switch rows with session start/end events |

A single browser Realtime channel listens to `devices`, `switch_events`, and `events`. It does not directly subscribe to the `sessions` table. The current switch grid is one shared set keyed by switch name.

## API routes

| Route | Response |
|---|---|
| `GET /api/sessions` | Paginated session summaries; optional server-side session-ID search |
| `GET /api/sessions/{id}` | Session summary and selected session audit rows |

The detail route currently accepts only 14-digit session IDs. API middleware applies an Upstash sliding-window rate limit.

## Data-access assumptions

The dashboard is intended to be read-only and uses the Supabase anonymous key. Deployments must configure Row Level Security for anonymous reads, protection against anonymous writes, and Realtime publication. Supabase provisioning is managed outside this repository.

## Verification

```bash
npx tsc --noEmit --incremental false
npm run build
```

See [testing and verification](../docs/testing.md) for current checks and cross-system verification.
