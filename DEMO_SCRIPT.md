# StreamLens — 60–90 second demo script

## Recording setup

Run the local prototype in synthetic demo mode. Do not enter credentials. Keep the dashboard and browser address bar visible enough to establish that this is a local demo. Avoid showing any real account data.

## Voiceover and actions

**0–10 seconds — The problem**

“Trading bots depend on account events arriving in the right order. A normal trading dashboard shows the current state, but it does not always show what the bot's WebSocket integration actually received.”

**10–25 seconds — The stream lifecycle**

Show the initial `hello`, account snapshot, and `snapshot_end` events.

“StreamLens makes the account stream visible as a searchable timeline, including snapshots and subsequent account events.”

**25–40 seconds — Sequence-gap demonstration**

Click **Test gap detector**. Show the sequence-gap counter and highlighted event.

“This demo-only action intentionally skips a synthetic sequence number, so developers can see how StreamLens surfaces a possible missed event.”

**40–55 seconds — Inspect events**

Filter to fills or positions. Select a row and show its JSON payload and diagnostic metadata.

“You can filter the event types and inspect the exact JSON frame received by the local app.”

**55–70 seconds — Export**

Click **Export scrubbed**. Do not open or share a real account export.

“StreamLens can export a scrubbed JSONL log. Redaction is a safeguard, not a guarantee, so exports still need manual review before sharing.”

**70–90 seconds — Safety and status**

Show the demo/sandbox distinction and close with:

“StreamLens is read-only. It does not place, edit, or cancel orders. The live connection is sandbox-only and uses a server-side test key. This recording demonstrates synthetic data; live sandbox behavior will only be claimed after testing with an approved test key.”

## Recording checklist

- [ ] Use synthetic demo data only.
- [ ] Show the initial snapshot lifecycle.
- [ ] Click **Test gap detector**.
- [ ] Filter and inspect a fill or position.
- [ ] Show the export control without sharing private data.
- [ ] State clearly that this is demo mode.
- [ ] Do not show API keys, account identifiers, or real activity.
- [ ] Do not claim a verified live sandbox connection.