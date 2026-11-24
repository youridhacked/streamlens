# StreamLens

**See every frame. Understand the stream.**

StreamLens is an independent, read-only inspector prototype for the MyFundedPerps sandbox account WebSocket. It presents account-stream frames in a searchable timeline and reports sequence gaps, snapshot/resync state, replay completeness, heartbeat health, reconnects, and measured ping/pong round-trip time.

> Unofficial community project. Not MyFundedPerps software and not affiliated with the firm.

## What is included

- Local Python HTTP server and server-sent-event (SSE) event delivery.
- Synthetic demo stream with fictional account data.
- Sandbox-only WebSocket connection path using a server-side `fp_test_` credential.
- Event timeline, filtering, search, payload inspector, and JSONL export with common sensitive fields redacted.
- Unit tests and a GitHub Actions workflow.

## Safety boundaries

- Read-only observer: there are no order, cancel, close-position, or other trading-write API routes.
- Only the documented sandbox WebSocket URL is used; credentials without the `fp_test_` prefix are rejected.
- Credentials are read by the local server from `FP_API_KEY`; never put a key in browser code, source control, screenshots, logs, or issue reports.
- Demo balances, fills, positions, and identifiers are fictional. Demo activity is not a trading result.
- JSONL redaction is best-effort. Review exports manually before sharing them.

## Run locally

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python server.py
```

Open http://127.0.0.1:8000. The app starts in synthetic demo mode.

For sandbox mode, set `FP_API_KEY` in the server process environment to an approved `fp_test_` key before starting the server. Do not use or paste a live credential. The key remains server-side. To return to demo mode, use the dashboard's demo control.

## Tests

```bash
python -m py_compile server.py stream_manager.py
python -m unittest discover -s tests -v
```

The CI workflow runs compilation and unit tests on pushes and pull requests.

## Local API

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/status` | Current local stream state and diagnostics |
| GET | `/api/events` | Server-sent event stream for the dashboard |
| POST | `/api/connect` | Connect to the sandbox account stream |
| POST | `/api/demo` | Start synthetic demo mode |
| POST | `/api/disconnect` | Disconnect the observer |
| POST | `/api/demo-gap` | Inject a synthetic sequence gap in demo mode |

The POST routes are loopback-only and reject cross-origin requests from non-local origins. StreamLens has no trading-write routes.

## Verification status

The repository contains the application source, tests, and CI workflow. Unit tests and a browser smoke test must pass on the current committed revision before describing the release as verified. Sandbox authentication and real frame/reconnect semantics must be tested with an approved sandbox credential before claiming live sandbox operation is verified. No such credential is included in this repository.

## Project links

- Source: https://github.com/youridhacked/streamlens
- Builders programme: https://myfundedperpetuals.com/builders
- Account streaming documentation: https://docs.myfundedperpetuals.com/account-streaming
- Sandbox documentation: https://docs.myfundedperpetuals.com/sandbox

See [APPLICATION.md](APPLICATION.md), [SECURITY.md](SECURITY.md), and [DEMO_SCRIPT.md](DEMO_SCRIPT.md).
