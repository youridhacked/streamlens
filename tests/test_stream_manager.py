import unittest

from stream_manager import StreamManager


class StreamManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = StreamManager("", autostart_demo=False)
        self.manager._reset("demo", "replaying")

    def test_sequence_gap_is_flagged(self):
        self.manager._publish({"type": "snapshot", "seq": 1, "time": 1000, "account_id": "demo-1"}, source="demo")
        wrapped = self.manager._publish({"type": "fill", "seq": 3, "time": 2000, "account_id": "demo-1"}, source="demo")
        self.assertTrue(wrapped["meta"]["seq_gap"])
        self.assertEqual(self.manager.status()["seq_gaps"], 1)

    def test_resync_snapshot_is_counted(self):
        self.manager._publish({"type": "snapshot", "seq": 1, "time": 1000, "account_id": "demo-1", "reason": "resync"}, source="demo")
        self.assertEqual(self.manager.status()["resyncs"], 1)

    def test_snapshot_end_reports_replay_completeness(self):
        self.manager._publish({"type": "snapshot_end", "seq": 2, "time": 2000, "replay": {"complete": False, "incomplete_accounts": ["demo-1"]}}, source="demo")
        status = self.manager.status()
        self.assertTrue(status["snapshot_end_seen"])
        self.assertFalse(status["replay_complete"])

    def test_heartbeat_upstream_state_is_recorded(self):
        self.manager._publish({"type": "heartbeat", "upstream_connected": False}, source="sandbox")
        self.assertFalse(self.manager.status()["upstream_connected"])

    def test_live_connect_rejects_missing_or_live_credentials(self):
        with self.assertRaises(ValueError):
            self.manager.start_live()
        live = StreamManager("fp_live_never-use", autostart_demo=False)
        with self.assertRaises(ValueError):
            live.start_live()

    def test_subscriber_receives_backlog_and_new_frames(self):
        self.manager._publish({"type": "hello", "stream_id": "demo-stream", "resumed": False}, source="demo")
        q = self.manager.subscribe()
        backlog = q.get_nowait()
        self.assertEqual(backlog["kind"], "backlog")
        self.assertEqual(len(backlog["items"]), 1)
        self.manager._publish({"type": "heartbeat", "upstream_connected": True}, source="demo")
        event = q.get_nowait()
        self.assertEqual(event["kind"], "frame")
        self.assertEqual(event["frame"]["type"], "heartbeat")
        self.manager.unsubscribe(q)

    def test_reconnecting_is_not_reported_as_connected(self):
        with self.manager.lock:
            self.manager.mode = "sandbox"
            self.manager.state = "reconnecting"
        status = self.manager.status()
        self.assertFalse(status["connected"])
        self.assertEqual(status["state"], "reconnecting")

    def test_connected_state_is_reported_accurately(self):
        with self.manager.lock:
            self.manager.mode = "sandbox"
            self.manager.state = "connected"
        self.assertTrue(self.manager.status()["connected"])


if __name__ == "__main__":
    unittest.main()
