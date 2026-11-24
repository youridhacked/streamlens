"""Read-only MyFundedPerps sandbox account-stream manager."""
from __future__ import annotations
import json, random, threading, time, uuid
from collections import deque
from queue import Empty, Full, Queue
from typing import Any
from urllib.parse import urlencode
try:
    import websocket
except ImportError:
    websocket = None

SANDBOX_WS = "wss://account-stream.myfundedperpetuals.com/v1/sandbox/stream"

class StreamManager:
    def __init__(self, api_key: str = "", *, autostart_demo: bool = True):
        self.api_key = api_key.strip()
        self.lock = threading.RLock()
        self.history = deque(maxlen=600)
        self.subscribers = set()
        self.worker = None
        self.stop_event = threading.Event()
        self.ws = None
        self.mode = self.state = "idle"
        self.started_at = None
        self.stream_id = None
        self.last_seq = self.last_time = None
        self.frames_seen = self.data_events = self.seq_gaps = 0
        self.resyncs = self.reconnects = 0
        self.snapshot_accounts = set()
        self.snapshot_end_seen = False
        self.replay_complete = self.upstream_connected = None
        self.last_frame_at = self.last_rtt_ms = None
        self.pending_pings = {}
        self.last_error = None
        self.demo_seq = 0
        self.demo_gap_requested = False
        if autostart_demo:
            self.start_demo()

    def _join_worker(self, worker):
        if worker and worker.is_alive() and worker is not threading.current_thread():
            worker.join(timeout=2)

    def _stop_current(self):
        with self.lock:
            self.stop_event.set()
            worker, ws = self.worker, self.ws
            self.ws = None
        if ws:
            try: ws.close()
            except Exception: pass
        self._join_worker(worker)

    def _reset(self, mode, state):
        with self.lock:
            self.history.clear()
            self.mode, self.state = mode, state
            self.started_at = time.time()
            self.stream_id = self.last_seq = self.last_time = None
            self.frames_seen = self.data_events = self.seq_gaps = 0
            self.resyncs = self.reconnects = 0
            self.snapshot_accounts.clear()
            self.snapshot_end_seen = False
            self.replay_complete = self.upstream_connected = None
            self.last_frame_at = self.last_rtt_ms = None
            self.pending_pings.clear()
            self.last_error = None
            self.demo_seq = 0
            self.demo_gap_requested = False
            self.stop_event = threading.Event()
            return self.stop_event

    def start_demo(self):
        self._stop_current()
        stop = self._reset("demo", "starting")
        self.worker = threading.Thread(target=self._demo_loop, args=(stop,), daemon=True)
        self.worker.start()
        return self.status()

    def start_live(self):
        if not self.api_key:
            raise ValueError("No sandbox key is configured. Set FP_API_KEY to an fp_test_ key on the local server.")
        if not self.api_key.startswith("fp_test_"):
            raise ValueError("StreamLens only accepts fp_test_ sandbox keys. Live keys are intentionally blocked.")
        if websocket is None:
            raise RuntimeError("Live WebSocket mode needs websocket-client. Install requirements.txt, then restart.")
        self._stop_current()
        stop = self._reset("sandbox", "connecting")
        self.worker = threading.Thread(target=self._live_loop, args=(stop,), daemon=True)
        self.worker.start()
        self._publish_local("connecting", "Opening the sandbox account stream.")
        return self.status()

    def disconnect(self):
        self._stop_current()
        with self.lock:
            self.state, self.mode, self.ws = "disconnected", "idle", None
        self._publish_local("disconnected", "StreamLens disconnected. No account changes were made.")
        return self.status()

    def inject_demo_gap(self):
        with self.lock:
            if self.mode != "demo":
                raise ValueError("Gap simulation is available only in demo mode.")
            self.demo_gap_requested = True
        return self.status()

    def subscribe(self):
        q = Queue(maxsize=1200)
        with self.lock:
            self.subscribers.add(q)
            backlog = list(self.history)
        try: q.put_nowait({"kind": "backlog", "items": backlog})
        except Full: pass
        return q

    def unsubscribe(self, q):
        with self.lock: self.subscribers.discard(q)

    def status(self):
        with self.lock:
            return {"mode": self.mode, "state": self.state,
                "connected": self.state == "connected" or (self.mode == "demo" and self.state == "replaying"),
                "read_only": True, "stream_id": self.stream_id, "last_seq": self.last_seq,
                "frames_seen": self.frames_seen, "data_events": self.data_events,
                "seq_gaps": self.seq_gaps, "resyncs": self.resyncs, "reconnects": self.reconnects,
                "snapshot_accounts": len(self.snapshot_accounts), "snapshot_end_seen": self.snapshot_end_seen,
                "replay_complete": self.replay_complete, "upstream_connected": self.upstream_connected,
                "last_frame_at": self.last_frame_at, "last_rtt_ms": self.last_rtt_ms,
                "last_error": self.last_error, "key_configured": self.api_key.startswith("fp_test_")}

    def _publish(self, frame, *, source=None):
        if not isinstance(frame, dict): frame = {"type": "unknown", "payload": str(frame)}
        now, seq = time.time(), frame.get("seq")
        gap = reset = False
        resync = frame.get("type") == "snapshot" and frame.get("reason") == "resync"
        rtt = None
        with self.lock:
            if frame.get("type") == "hello":
                sid = frame.get("stream_id")
                if self.stream_id and sid and sid != self.stream_id and frame.get("resumed") is False:
                    self.last_seq, reset = None, True
                if sid: self.stream_id = str(sid)
            if seq is not None:
                try: n = int(seq)
                except (TypeError, ValueError): n = None
                if n is not None:
                    if self.last_seq is not None and n > self.last_seq + 1:
                        gap = True
                        self.seq_gaps += 1
                    if self.last_seq is not None and n < self.last_seq and frame.get("replay") is not True:
                        reset = True
                    if self.last_seq is None or n > self.last_seq: self.last_seq = n
            if frame.get("time") is not None:
                try: self.last_time = int(frame["time"])
                except (TypeError, ValueError): pass
            if frame.get("type") == "snapshot":
                aid = str(frame.get("account_id", ""))
                if aid: self.snapshot_accounts.add(aid)
                if resync: self.resyncs += 1
            if frame.get("type") == "snapshot_end":
                self.snapshot_end_seen = True
                replay = frame.get("replay")
                if isinstance(replay, dict) and isinstance(replay.get("complete"), bool):
                    self.replay_complete = replay["complete"]
            if frame.get("type") == "heartbeat" and "upstream_connected" in frame:
                self.upstream_connected = bool(frame["upstream_connected"])
            if frame.get("type") == "pong":
                started = self.pending_pings.pop(str(frame.get("id", "")), None)
                if started is not None:
                    rtt = round((time.monotonic()-started)*1000, 1)
                    self.last_rtt_ms = rtt
            self.frames_seen += 1
            if frame.get("type") not in {"hello","heartbeat","pong","snapshot","snapshot_end"}:
                self.data_events += 1
            self.last_frame_at = now
            wrapped = {"kind":"frame","frame":frame,"meta":{"received_at":int(now*1000),
                "source":source or self.mode,"seq_gap":gap,"seq_reset":reset,"resync":resync,"rtt_ms":rtt}}
            self.history.append(wrapped)
            subs = list(self.subscribers)
        for q in subs:
            try: q.put_nowait(wrapped)
            except Full:
                try:
                    q.get_nowait()
                    q.put_nowait({"kind":"local","message":"Browser viewer fell behind; older queued frames were skipped."})
                    q.put_nowait(wrapped)
                except (Empty, Full): pass
        return wrapped

    def _publish_local(self, event, message, *, tone="info", extra=None):
        f = {"type":"streamlens","event":event,"message":message,"tone":tone,"time":int(time.time()*1000)}
        if extra: f.update(extra)
        self._publish(f)

    def _demo_loop(self, stop):
        with self.lock: self.state = "replaying"
        now = int(time.time()*1000)
        self._publish({"type":"hello","stream_id":"demo-"+uuid.uuid4().hex[:8],"environment":"test","resumed":False}, source="demo")
        stop.wait(.25)
        account = {"id":"demo-account-25k","account_number":"DEMO-25000","name":"Sandbox Demo · 25K",
            "stage":"evaluation","status":"active","starting_balance":25000,"balance":25124.80,
            "risk":{"marks_complete":True,"equity":25118.40,"daily_loss_room":368.40,
                    "max_drawdown_room":1118.40,"available_balance":23800.00}}
        self._publish({"type":"snapshot","seq":1,"time":now,"account_id":"demo-account-25k",
            "account":account,"orders":[],"positions":[],"latest_fill":None,"reason":"connect"}, source="demo")
        stop.wait(.25)
        self._publish({"type":"snapshot_end","seq":2,"time":now+1,"replay":{"complete":True,"incomplete_accounts":[]}}, source="demo")
        self.demo_seq = 2
        self._publish_local("ready","Synthetic stream started. Use ‘Test gap detector’ to preview a sequence-gap warning.",tone="good")
        tick = 0
        while not stop.wait(2.2):
            tick += 1
            now = int(time.time()*1000)
            with self.lock:
                inject = self.demo_gap_requested
                self.demo_gap_requested = False
                heartbeat = tick % 4 == 0 and not inject
                if not heartbeat: self.demo_seq += 2 if inject else 1
                seq = self.demo_seq
            if heartbeat:
                self._publish({"type":"heartbeat","upstream_connected":True},source="demo")
            elif inject:
                self._publish({"type":"order","event":"filled","seq":seq,"time":now,"account_id":"demo-account-25k",
                    "synthetic":True,"order":{"id":"demo-gap-order","symbol":"BTC","side":"buy","status":"filled","size":.002}},source="demo")
            elif tick % 3 == 1:
                self._publish({"type":"fill","seq":seq,"time":now,"account_id":"demo-account-25k",
                    "fill":{"id":f"demo-fill-{tick:03d}","symbol":"BTC","side":"buy","size":.002,"price":67920.4}},source="demo")
            elif tick % 3 == 2:
                self._publish({"type":"position","event":"changed","seq":seq,"time":now,"account_id":"demo-account-25k",
                    "position":{"id":"demo-position-btc","symbol":"BTC","side":"long","size":.003,"entry_price":67920.4}},source="demo")
            else:
                self._publish({"type":"account","event":"updated","seq":seq,"time":now,"account_id":"demo-account-25k",
                    "account":{"id":"demo-account-25k","balance":25124.8+tick*1.35,"status":"active"}},source="demo")

    def _live_loop(self, stop):
        backoff, had_connection = 1.0, False
        while not stop.is_set():
            with self.lock:
                self.state = "connecting"
                sid, seq, since = self.stream_id, self.last_seq, self.last_time
            url = SANDBOX_WS
            if sid and seq is not None and since is not None:
                url += "?" + urlencode({"resume":sid,"last_seq":seq,"since":since})
            sock = None
            try:
                sock = websocket.create_connection(url,header=[f"Authorization: Bearer {self.api_key}"],timeout=8,enable_multithread=True)
                sock.settimeout(1)
                with self.lock:
                    self.ws, self.state, self.last_error = sock, "connected", None
                    if had_connection: self.reconnects += 1
                self._publish_local("connected","Sandbox WebSocket connected. Listening to events only.",tone="good")
                had_connection, backoff = True, 1.0
                last_frame, last_ping = time.monotonic(), time.monotonic()
                while not stop.is_set():
                    mono = time.monotonic()
                    if mono-last_frame >= 45: raise TimeoutError("No frame arrived for 45 seconds; reconnecting with resume parameters.")
                    if mono-last_ping >= 30:
                        pid = str(int(time.time()*1000))
                        with self.lock:
                            self.pending_pings[pid] = time.monotonic()
                            if len(self.pending_pings)>20: self.pending_pings.pop(next(iter(self.pending_pings)))
                        sock.send(json.dumps({"op":"ping","id":pid}))
                        last_ping = mono
                    try: message = sock.recv()
                    except websocket.WebSocketTimeoutException: continue
                    if not message:
                        code = getattr(sock,"close_status_code",None)
                        if code == 4001: raise PermissionError("Sandbox key was revoked, expired, or sandbox access lapsed.")
                        raise ConnectionError(f"Account stream closed (code {code or 'unknown'}).")
                    last_frame = time.monotonic()
                    try: frame = json.loads(message)
                    except (json.JSONDecodeError,TypeError):
                        self._publish_local("parse_warning","Received a non-JSON WebSocket message; it was not interpreted.",tone="warning")
                        continue
                    if not isinstance(frame,dict):
                        self._publish_local("parse_warning","Received a non-object WebSocket frame; it was not interpreted.",tone="warning")
                        continue
                    self._publish(frame,source="sandbox")
                    if frame.get("type")=="error" and str(frame.get("code","")) in {"sandbox_access_expired","invalid_api_key","unauthorized"}:
                        raise PermissionError(frame.get("message") or "Sandbox stream authorization failed.")
                break
            except Exception as err:
                if stop.is_set(): break
                if isinstance(err,PermissionError) or getattr(err,"status_code",None) in {401,403}:
                    with self.lock: self.state, self.last_error = "error", str(err)
                    self._publish_local("auth_error",str(err),tone="danger")
                    break
                with self.lock: self.state, self.last_error = "reconnecting", str(err)
                self._publish_local("reconnecting",f"Stream interrupted; retrying with resume/backoff. {err}",tone="warning")
                delay = min(backoff,30.0)+random.uniform(0,min(.35,backoff/4))
                if stop.wait(delay): break
                backoff = min(backoff*2,30.0)
            finally:
                with self.lock:
                    if self.ws is sock: self.ws = None
                if sock:
                    try: sock.close()
                    except Exception: pass
        with self.lock:
            if self.mode=="sandbox" and self.state not in {"error","disconnected"}: self.state="disconnected"

def make_manager(api_key="", *, autostart_demo=True):
    return StreamManager(api_key,autostart_demo=autostart_demo)
