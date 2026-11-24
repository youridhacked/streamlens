# Security policy

StreamLens is an unofficial, local-first, read-only observer for the MyFundedPerps sandbox account stream.

## Credential handling
- Use only a sandbox credential beginning with `fp_test_`.
- Set it through the local `FP_API_KEY` environment variable.
- Never put credentials in browser code, browser storage, source control, screenshots, chat, or issue reports.
- Live credentials beginning with `fp_live_` are intentionally rejected.
- The upstream endpoint is fixed to the sandbox host.

## Network exposure
- The local server binds to `127.0.0.1` by default.
- Do not expose it to a public network or reverse proxy without a separate security review and authentication layer.
- Local control routes enforce loopback and same-origin checks as defense in depth.

## Data sharing
- Raw event payloads may contain account identifiers or private activity.
- JSONL export scrubs common identifiers and credential-like field names, but no automated redactor can guarantee removal of every sensitive value. Review exports manually before sharing.

## Reporting
Do not include credentials or raw account payloads in public issues. Report security concerns with a minimal, redacted reproduction.