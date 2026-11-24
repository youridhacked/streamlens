# StreamLens

**See every frame. Understand the stream.**

StreamLens is an independent, read-only inspector concept and prototype for the MyFundedPerps sandbox account WebSocket. It is designed to turn account-stream frames into a searchable event timeline and surface sequence gaps, resync snapshots, replay completeness, heartbeats, reconnects, and ping/pong latency.

> Unofficial community project. Not MyFundedPerps software and not affiliated with the firm.

## What it is for

A developer building a bot, trade copier, or account-monitoring tool needs to know whether their integration received the account stream correctly. StreamLens is intended to make the raw event lifecycle visible so developers can debug synchronization problems before shipping an automation.

## Intended capabilities

- Synthetic demo with fictional account data.
- Sandbox-only account-stream observer using a server-side `fp_test_` key.
- Timeline for snapshots, orders, fills, positions, account events, heartbeats, and diagnostics.
- Sequence-gap, resync, replay, upstream-health, and reconnect diagnostics.
- Scrubbed JSONL export with manual review required.

## Safety boundaries

- Read-only: no order, cancel, close-position, or other trading-write routes.
- Sandbox endpoint only; `fp_live_` credentials are refused.
- Credentials stay in the local server environment, never browser code or source control.
- Demo balances, fills, positions, and account IDs are fictional.

## Verification status

The local prototype has been exercised in demo mode; Python compilation and 8 unit tests pass. A headless-browser smoke test could not be completed because local browser navigation was blocked in the development environment. Live sandbox authentication and real reconnect/resume behavior have **not** been verified with an approved `fp_test_` key.

**Repository status:** this public repository currently contains the project overview, application draft, security policy, and license. The complete source tree still needs to be mirrored into the repository before this URL is used as a code-submission link. Do not submit this landing-page repository as if it already contains the full source.

## Official references

- [MyFundedPerps Builders](https://myfundedperpetuals.com/builders)
- [Account streaming documentation](https://docs.myfundedperpetuals.com/account-streaming)
- [Sandbox documentation](https://docs.myfundedperpetuals.com/sandbox)

See [APPLICATION.md](APPLICATION.md), [SECURITY.md](SECURITY.md), and [DEMO_SCRIPT.md](DEMO_SCRIPT.md).