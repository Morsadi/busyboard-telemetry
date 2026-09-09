# BusyBoard repository instructions

BusyBoard is an IoT telemetry monorepo with three independently deployed areas:

- `firmware/`: BusyBoard publisher and Buzzer subscriber firmware;
- `ingestion/`: Python MQTT processing and local/cloud persistence;
- `dashboard/`: Next.js UI backed by Supabase.

Before editing a subsystem, read its nearest `AGENTS.md` and README. More specific instructions override this file within their directory.

## Authoritative documentation

- [System architecture](docs/architecture.md)
- [Current MQTT contract](docs/contracts/mqtt.md)
- [Data model and session behavior](docs/data-model.md)
- [Testing and verification](docs/testing.md)

Do not redefine complete MQTT or data-model contracts in local documentation or code comments. Update the authoritative document and link to it.

## Safety

- Never expose, print, commit, or rewrite `.env*`, `secrets.h`, credentials, connection strings, local databases, or generated output.
- Preserve unrelated worktree changes.
- Treat tracked schemas and configuration as repository state; verify deployment-managed services separately.
- Cloud publication is asynchronous and uses a separate transaction path; persistence changes must verify both local and cloud behavior.
- Do not change topics, payload fields, switch identity, session identity, timestamps, or database row shapes as a local-only refactor.
- Do not document proposed or deployment-specific behavior as current repository behavior.

## Cross-boundary changes

Before changing an interface shared across subsystems:

1. identify every producer and consumer;
2. inspect schemas, repository operations, dashboard queries, and tests;
3. define compatibility and migration behavior;
4. update all affected implementations and authoritative docs together;
5. verify each runnable subsystem and state the hardware/cloud verification boundaries.

## Working approach

1. Inspect the affected implementation, README, nearest AGENTS file, and existing tests.
2. Make the smallest coherent change that addresses the request.
3. Add focused regression coverage where the subsystem supports it.
4. Run the verification documented for that scope.
5. Review the complete diff for unrelated edits and contract drift.
6. Report exactly what passed and what could not be verified.

Avoid unrelated cleanup, silent data coercion, broad dependency additions, and schema changes that have not been traced through every reader and writer.

## Definition of done

A task is complete only when requested behavior is implemented, relevant checks pass, cross-system consumers have been considered, unrelated behavior was not intentionally changed, and remaining risk is explicit. Do not claim success from inspection alone when a runnable verification path exists.
