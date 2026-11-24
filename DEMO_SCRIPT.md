# StreamLens — 60–90 second synthetic demo script

## Recording setup
Run `python server.py` locally and open `http://127.0.0.1:8000`. Stay in synthetic demo mode; do not configure or enter credentials. Show no real account data.

## Voiceover and actions

**0–10 seconds — Problem**
“Bot developers need to know not just the current account state, but what their WebSocket client actually received and whether frames were missed.”

**10–25 seconds — Snapshot lifecycle**
Show the `hello`, `snapshot`, and `snapshot_end` frames.
“StreamLens turns the account stream into a searchable event timeline and exposes snapshot/replay lifecycle details.”

**25–40 seconds — Sequence gap**
Click **Test gap detector**. Show the highlighted event and sequence-gap metric.
“This control injects a synthetic sequence skip in demo mode so we can see the gap detector respond. It does not interact with any exchange or account.”

**40–55 seconds — Inspect**
Filter to fills or positions, select a row, and show the JSON payload.
“Filter event types and inspect the payload and local diagnostics.”

**55–70 seconds — Export**
Click **Export JSONL**. Do not share an export without manually checking it.
“Export creates a JSONL file with common sensitive fields redacted. Redaction is best-effort; review the file before sharing.”

**70–90 seconds — Safety and status**
“StreamLens is an independent, read-only prototype. It has no order placement or account-write routes. This recording uses fictional synthetic demo data. Live sandbox compatibility is a separate test and will only be claimed after an approved `fp_test_` credential has been used.”

## Recording checklist
- [ ] Synthetic demo only; no API keys or real account identifiers.
- [ ] Show snapshot lifecycle, event filter, inspector, and **Test gap detector**.
- [ ] State clearly that the sequence gap and all displayed account data are synthetic.
- [ ] Do not imply verified live sandbox behavior or official affiliation.
