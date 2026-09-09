# Dashboard agent instructions

These instructions apply to `dashboard/`.

Read the local README plus:

- [System architecture](../docs/architecture.md)
- [Data model and session behavior](../docs/data-model.md)
- [Testing and verification](../docs/testing.md)

## Data-access boundary

- Keep the dashboard read-only unless the product model is explicitly changed.
- Preserve the separation between server queries and browser Realtime state.
- Treat session identity and database row shapes as cross-subsystem contracts.
- Treat RLS and Realtime provisioning as deployment-managed and verify it separately when relevant.
- Keep server-only secrets out of client bundles.

## TypeScript and Next.js conventions

- Preserve strict TypeScript and existing `@/` aliases.
- Keep explicit client/server component boundaries.
- Use public framework APIs such as `next/navigation`.
- Follow the existing single-quote, semicolon, named-component-export style.

## Fetching and Realtime

- Check `response.ok` before trusting response bodies.
- Preserve meaningful loading, empty, error, disconnected, and 404 states.
- Protect against stale responses when requests can overlap.
- Clean up subscriptions and async effects.
- Handle duplicate/out-of-order inserts defensively where practical.
- Scope state to the intended device/session rather than assuming one global BusyBoard.

Do not present stale telemetry as definitely current after a fetch or Realtime failure.

## Accessibility

Use semantic HTML, keyboard-operable controls, accessible names, visible focus, and status communication that does not rely only on color or motion. Do not claim automated accessibility coverage unless corresponding tools/tests exist.

## Verification

Use the commands in `dashboard/README.md`. At minimum, run the TypeScript check and production build for dashboard code changes.

For API/data changes, inspect ingestion and schema consumers. For Realtime changes, reason through initial fetch, event-before-fetch, duplicates, device scope, unmount/resubscribe, and disconnect/recovery. Current verification expectations are listed in [testing documentation](../docs/testing.md).

## Current constraints

- The switch grid is one shared set keyed by switch name.
- UI search filters the session pages already loaded in the browser.
- Supabase schema, RLS, and Realtime provisioning are deployment-managed.

Keep changes scoped to the requested task.
