# StreamLens

**See every frame. Understand the stream.**

StreamLens is an independent, read-only inspector for the MyFundedPerps sandbox account WebSocket. It turns account-stream frames into a searchable event timeline and surfaces sequence gaps, resync snapshots, replay completeness, heartbeats, reconnects, and ping/pong latency.

> Unofficial community prototype. Not MyFundedPerps software and not affiliated with the firm.

## Download the complete source

The complete Python server, browser UI, stream manager, tests, GitHub Actions workflow, security policy, and application notes are in [`downloads/streamlens-hardened.zip`](downloads/streamlens-hardened.zip). Extract the archive; it contains the project under `streamlens/`.

## What it does

- Runs a synthetic account-stream demo without credentials.
- Can connect to the documented sandbox stream using an `fp_test_` key stored only in the local server environment.
- Displays `hello`, snapshots, `snapshot_end`, orders, fills, positions, account events, heartbeats, and diagnostics.
- Detects sequence gaps and shows resync/replay state.
- Exports a scrubbed JSONL log; manually inspect every export before sharing.

## Safety

- Fixed to the MyFundedPerps sandbox WebSocket endpoint.
- Refuses `fp_live_` keys.
- No order/position write routes or trading actions.
- Server binds to `127.0.0.1` by default.
- Demo account data is fictional.

## Verification status

The synthetic demo and local server were exercised in development. Python compilation passes and all 8 unit tests pass. Live sandbox authentication and real reconnect/resume behavior have **not** been verified with an approved `fp_test_` key. A browser smoke test could not be completed because local browser navigation was blocked in the development environment. We will update this status only after those checks are actually performed.

## Run

```bash
cd streamlens
python3 server.py
```

Open `http://127.0.0.1:8000` and click **Test gap detector** to see the synthetic sequence-gap demonstration.

For sandbox mode, install `requirements.txt`, set `FP_API_KEY` to an approved `fp_test_` key in the local environment, and run `python3 server.py`. Never put credentials in source control, chat, screenshots, or the browser.

## Official references

- [MyFundedPerps Builders](https://myfundedperpetuals.com/builders)
- [Account streaming documentation](https://docs.myfundedperpetuals.com/account-streaming)
- [Sandbox documentation](https://docs.myfundedperpetuals.com/sandbox)

See [`APPLICATION.md`](APPLICATION.md) and [`SECURITY.md`](SECURITY.md) inside the source archive for submission notes and security guidance.