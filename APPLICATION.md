# MyFundedPerps Builders — StreamLens application draft

## Recommended tier
Starter — prototype stage. Do not claim production adoption or active users unless that changes and can be evidenced.

## Project
**StreamLens — a sandbox account-stream inspector**

## Short pitch
StreamLens is an independent, read-only developer tool for inspecting the MyFundedPerps sandbox account WebSocket. It turns account snapshots, lifecycle events, heartbeats, and diagnostics into a searchable timeline, and highlights sequence gaps, replay/resync state, reconnects, and ping/pong latency. It includes a synthetic demo and a sandbox-only connection path using a server-side `fp_test_` key. It does not place, amend, or cancel orders.

## Problem
Developers integrating account streams need to know whether their client received the expected sequence of frames and recovered correctly after disconnects. StreamLens aims to make synchronization problems visible before an integration is relied on.

## What to show in a demo
1. Open the local app in synthetic demo mode and point out that all sample account values are fictional.
2. Show the event timeline and select an event to inspect its payload.
3. Filter to fills or positions and use search.
4. Click **Test gap detector** and show the sequence-gap metric and highlighted event.
5. Export the scrubbed JSONL, open it, and manually check it for identifying information before sharing.
6. Optionally show the sandbox connect control only after testing with an approved sandbox key. Never show or record the key.

## Project links
- Repository: https://github.com/youridhacked/streamlens
- Official Builders programme: https://myfundedperpetuals.com/builders
- Account streaming docs: https://docs.myfundedperpetuals.com/account-streaming
- Sandbox docs: https://docs.myfundedperpetuals.com/sandbox

## Honest status and limitations
The repository contains a prototype source tree, local server, dashboard, demo path, unit tests, and CI workflow. The synthetic demo is not live account data. Sandbox authentication, actual server frame compatibility, and real reconnect/resume behavior must not be described as verified until exercised with an approved `fp_test_` key against the official sandbox. Browser verification and CI status should be checked on the exact commit used for submission. Usage/user count must be reported truthfully; do not invent users, metrics, testimonials, or adoption.

## Submission checklist
- [ ] Run unit tests and confirm GitHub Actions is green on the final commit.
- [ ] Complete a browser smoke test of the local app.
- [ ] Record and publish a 60–90 second demo video.
- [ ] Test the real sandbox path with an approved `fp_test_` key, or state clearly that this is not yet verified and ask the Builders team for sandbox access.
- [ ] Enter actual user count and user type.
- [ ] Review all text, links, screenshots, and exports for secrets or personal data.
- [ ] Submit the Starter application only after reviewing the final form and attachments.
