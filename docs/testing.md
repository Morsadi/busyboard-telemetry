# Testing and verification

This document records the current verification commands and the checks expected when work crosses subsystem boundaries.

## Ingestion

Run from `ingestion/`:

```bash
python -m pytest -ra
```

The default suite covers helpers, validators, routing, SQLite repositories, local/cloud handler boundaries, and the cloud publisher using fake connections. Postgres tests are marked `postgres` and skipped unless explicitly enabled. A skip does not verify cloud SQL.

Test collection imports application configuration with dotenv loading disabled and empty application credentials. Each test uses temporary SQLite storage, resets publisher state, and blocks ordinary Postgres connections. Only the explicit integration fixture can connect to the disposable database below. No broker, application environment file, or local telemetry database is needed.

### Focused regression checks

From `ingestion/`:

```bash
python -m pytest tests/test_cloud_publisher.py tests/test_cloud_handlers.py -v
```

These tests characterize current behavior, including its limitations: disabled startup publication, failed writes being dropped, local commit before enqueue, local rollback, reconnection on the next queued job, and repeated receipts producing distinct writes. Worker tests drain a finite queue synchronously; they do not leave background threads running or sleep. They do not implement or verify durable replay.

### Disposable Postgres integration checks

Start Docker Desktop's Linux engine, then launch a dedicated disposable instance (the command works in PowerShell and POSIX shells):

```bash
docker run --detach --rm --name busyboard-test-postgres --publish 127.0.0.1:55432:5432 --env POSTGRES_USER=busyboard_test --env POSTGRES_DB=busyboard_test --env POSTGRES_HOST_AUTH_METHOD=trust postgres:16
docker exec busyboard-test-postgres pg_isready -U busyboard_test -d busyboard_test
```

Run the readiness command again if necessary, until it reports accepting connections. This instance deliberately uses passwordless authentication for disposable test data and exposes its port only on the host loopback interface. Do not reuse it for real telemetry or deploy this configuration. No persistent volume is attached. An existing container with this name should be inspected before reuse, not automatically replaced.

From `ingestion/`, run the SQL checks and then the complete suite:

```bash
python -m pytest tests/test_supabase_repositories.py --postgres -v
python -m pytest --postgres -ra
```

The fixture connects only to `127.0.0.1`, database/user `busyboard_test`, default port `55432`. For a port conflict, change the published host port and pass the same value with `--postgres-port`. It ignores libpq environment defaults and password files and never falls back to the application cloud connection. With `--postgres`, an unavailable database is a test failure, not a skip.

Each integration test creates a uniquely named schema, sets its connections' search path to that schema, and closes its connections and removes only that schema on teardown. The schema fixture is test-only evidence for repository SQL, not a production migration or verification of deployed Supabase provisioning.

Checks exercise real Postgres transactions, foreign keys, JSONB, timestamp conversion, lifecycle/count guards, handler-to-cloud delivery, lost-parent rollback, repeated delivery, and representative dashboard query fields. They do not exercise PostgREST relationship expansion, browser behavior, RLS, Supabase Realtime, deployment triggers, or hardware.

After the test run, stop the dedicated container; `--rm` removes the container and its disposable data:

```bash
docker stop busyboard-test-postgres
```

### Windows notes

If Python is not activated in this checkout, invoke the existing root environment from `ingestion/` as `..\.venv\Scripts\python.exe -m pytest` with the same options. If the default pytest temporary location is inaccessible, use a fresh throwaway path with `--basetemp` and optionally disable cache writes with `-p no:cacheprovider`. Pytest deletes an existing base-temp directory; never select a directory containing user data.

## Dashboard

Run from `dashboard/`:

```bash
npx tsc --noEmit --incremental false
npm run build
```

The repository does not currently define a dashboard unit-test or lint script. UI changes should also be exercised in a browser when a local runtime and required services are available.

## Firmware

The repository does not currently pin an Arduino/ESP32 toolchain or board target. Firmware verification should name the actual FQBN, ESP32 core, libraries, and toolchain used.

Compile the affected sketch and exercise the relevant serial, broker, and physical-device behavior. Compile both sketches when changing their shared MQTT contract.

## Verification by change type

| Change area | Verification |
|---|---|
| Ingestion parsing/validation | Focused test module, then full pytest suite |
| Session lifecycle or persistence | Handler/repository tests, full pytest suite, and data-model review |
| MQTT topic or payload | Both firmware sketches, ingestion router/validators, tests, MQTT contract, and downstream consumers |
| Postgres/cloud publication | Both repository paths and relevant failure handling |
| Dashboard types/API/UI | TypeScript check, production build, and relevant browser workflow |
| Realtime behavior | Initial fetch, inserts, subscription cleanup, connection state, and device/session scope |
| Firmware behavior | Compile affected sketches and record applicable physical checks |
| Cross-system contract | All affected producers/consumers plus documentation consistency review |

## Documentation verification

For documentation changes:

1. Validate relative Markdown links.
2. Check behavioral statements against source, schemas, and tests.
3. Keep the MQTT contract and data-model descriptions consistent with their consumers.
4. Run documented commands when changing setup or verification guidance.
5. Review the Git diff for secrets, generated files, local databases, and unrelated changes.
