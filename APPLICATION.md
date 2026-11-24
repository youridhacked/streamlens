# MyFundedPerps Builders — StreamLens application draft

## Project
**StreamLens — a sandbox account-stream inspector**

## Short pitch
StreamLens is a read-only developer tool for the MyFundedPerps account WebSocket. It turns the stream's `hello`, account snapshots, `snapshot_end`, heartbeats, and order/fill/position/account updates into a searchable event timeline. It surfaces sequence gaps, resync snapshots, incomplete replay, upstream-degraded heartbeats, reconnects, and ping/pong latency. The prototype includes a synthetic demo and a sandbox-only connection path using an `fp_test_` key held on the local server. It has no order or position write calls.

## Why build it
The account-stream documentation describes resume, sequence numbers, replay, and resync behavior. A visual inspector can help a trader or bot developer verify what the stream delivered, debug reconnect handling, and produce a scrubbed event log before shipping an automation. It complements the trading terminal rather than replacing its calculators or dashboard.

## Evidence to include
- Public source repository: https://github.com/youridhacked/streamlens
- A 60–90 second demo showing the synthetic snapshot/event flow, the **Test gap detector** button, the gap warning, a fills filter, and scrubbed JSONL export. Manually review exports before sharing.
- A separate sandbox recording only after testing with an approved key. Never show the key.
- Link the official account-stream docs and label StreamLens as independent, not official.

## Honest current status
The synthetic demo has been exercised locally; Python compilation and 8 unit tests pass. A headless-browser smoke test could not be completed because local browser navigation was blocked in the development environment. Sandbox authentication, real frame shapes, and reconnect/resume behavior remain unverified because no approved `fp_test_` key has been provided.

## Submission plan
Apply under Starter with the repository and demo link. If sandbox access is unavailable, ask the Builders team for temporary sandbox access. Do not claim live integration is verified until the approved-key tests have actually passed.