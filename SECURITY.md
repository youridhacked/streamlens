# Security policy

StreamLens is an unofficial, local-first, read-only observer prototype for the MyFundedPerps sandbox account stream.

## Credential handling
- Use only an approved sandbox credential with the `fp_test_` prefix.
- Set it in the environment of the local Python server as `FP_API_KEY`.
- Never place credentials in frontend code, source control, browser storage, screenshots, logs, recordings, or issue reports.
- Do not use `fp_live_` credentials. The application intentionally refuses credentials without the sandbox prefix.

## Network and permissions
- The server defaults to binding to `127.0.0.1`; do not expose it publicly without a security review.
- Local POST control routes accept loopback clients and same-origin requests only.
- The only upstream WebSocket endpoint in the application is the sandbox account-stream endpoint.
- StreamLens has no trading-write routes and must not be extended with trading actions under this project's read-only scope.

## Export handling
- JSONL export redacts common credential fields and selected account identifiers.
- Redaction is best-effort, not a privacy guarantee. Inspect exports manually before sharing.
- Treat logs, screenshots, browser downloads, and crash reports as potentially sensitive.

## Reporting
Please do not publish credentials or private account data in an issue. Report suspected vulnerabilities privately to the repository maintainer.
