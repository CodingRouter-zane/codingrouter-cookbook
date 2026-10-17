import copy
from datetime import datetime, timezone
import json
import unittest
from unittest.mock import patch
import discord_ops as ops

ID = "123456789012345678"
CONFIG = {"processing_approved": True, "review_delivery_approved": True,
    "review_channel_id": "223456789012345678",
    "channels": [{"guild_id": ID, "channel_id": "323456789012345678", "kind": "own"}]}


class DiscordTests(unittest.TestCase):
    def test_configuration_consent(self):
        for field in ("processing_approved", "review_delivery_approved"):
            config = copy.deepcopy(CONFIG)
            config[field] = False
            with self.assertRaises(ValueError):
                ops.load_config(json.dumps(config))

    def test_valid_config_and_no_review_source(self):
        self.assertEqual(ops.load_config(json.dumps(CONFIG)), CONFIG)
        config = copy.deepcopy(CONFIG)
        config["channels"][0]["channel_id"] = config["review_channel_id"]
        with self.assertRaises(ValueError):
            ops.load_config(json.dumps(config))

    def test_external_limit_and_duplicate(self):
        config = copy.deepcopy(CONFIG)
        config["channels"] = [{"guild_id": ID, "channel_id": str(323456789012345678 + i),
            "kind": "external"} for i in range(4)]
        with self.assertRaises(ValueError):
            ops.load_config(json.dumps(config))
        config["channels"] = CONFIG["channels"] * 2
        with self.assertRaises(ValueError):
            ops.load_config(json.dumps(config))

    def test_recent_human_records_and_redaction(self):
        now = datetime(2026, 10, 17, 4, tzinfo=timezone.utc)
        message = {"id": ID, "timestamp": now.isoformat(), "author": {"username": "private"},
            "content": "Hi <@123456789012345678> a@b.com sk-abcdefghijklmnop"}
        old = dict(message, timestamp="2026-10-15T00:00:00+00:00")
        bot = dict(message, author={"bot": True})
        rows = ops.records([message, old, bot], CONFIG["channels"][0], now)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["text"], "Hi [mention] [email] [credential]")
        self.assertNotIn("private", json.dumps(rows))

    def test_content_intent_missing_blocks(self):
        with patch.object(ops, "request", side_effect=[{"guild_id": ID},
                [{"author": {}, "content": ""}]]):
            with self.assertRaises(RuntimeError):
                ops.collect(CONFIG, "fake")

    def test_guild_mismatch_blocks(self):
        with patch.object(ops, "request", return_value={"guild_id": "wrong"}):
            with self.assertRaises(ValueError):
                ops.collect(CONFIG, "fake")

    def test_review_only_no_mentions_and_size(self):
        with patch.object(ops, "request", side_effect=[[], {"id": ID}]) as req:
            self.assertTrue(ops.deliver("draft", CONFIG, "fake", "2026-10-17"))
            args, kwargs = req.call_args
            self.assertIn(CONFIG["review_channel_id"], args[0])
            self.assertEqual(kwargs["payload"]["allowed_mentions"], {"parse": []})
            self.assertTrue(kwargs["payload"]["enforce_nonce"])

    def test_duplicate_review_skips(self):
        with patch.object(ops, "request", return_value=[{
                "content": "[CodingRouter Discord review 2026-10-17]"}]) as req:
            self.assertFalse(ops.deliver("draft", CONFIG, "fake", "2026-10-17"))
            self.assertEqual(req.call_count, 1)

    def test_generation_model_and_privacy_controls(self):
        response = {"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": "x" * 5000}]}]}
        with patch.object(ops, "request", side_effect=[{"data": [{"id": "gpt-6.1-sol"}]}, response]) as req:
            text = ops.generate([], [], "fake")
            self.assertEqual(len(text), 3800)
            payload = req.call_args.args[2]
            self.assertFalse(payload["store"])
            self.assertEqual(payload["model"], "gpt-6.1-sol")

    def test_incomplete_model_response_blocks_delivery(self):
        with patch.object(ops, "request", side_effect=[{"data": [{"id": "gpt-6.1-sol"}]},
                {"status": "incomplete"}]):
            with self.assertRaises(RuntimeError):
                ops.generate([], [], "fake")


if __name__ == "__main__":
    unittest.main()
