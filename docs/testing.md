# Testing and verification

This document records the current verification commands and the checks expected when work crosses subsystem boundaries.

## Ingestion

Run from `ingestion/`:

```bash
python -m pytest
```

The suite covers timestamp/JSON/topic helpers, payload validators, routing, SQLite repositories against a temporary database, and local handler/session behavior.

Changes to cloud publication or Postgres repositories require focused verification of those paths in addition to the local suite.

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
