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
            self.assertTrue(ops.deliver("draft", CONFIG, "fake", "2026-10-17", ID))
            args, kwargs = req.call_args
            self.assertIn(CONFIG["review_channel_id"], args[0])
            self.assertEqual(kwargs["payload"]["allowed_mentions"], {"parse": []})
            self.assertTrue(kwargs["payload"]["enforce_nonce"])

    def test_duplicate_review_skips(self):
        with patch.object(ops, "request", return_value=[{
                "content": "[CodingRouter Discord review 2026-10-17]", "author": {"id": ID}}]) as req:
            self.assertFalse(ops.deliver("draft", CONFIG, "fake", "2026-10-17", ID))
            self.assertEqual(req.call_count, 1)

    def sample(self):
        url = "https://discord.com/channels/123456789012345678/323456789012345678/423456789012345678"
        items = [{"kind": "own", "url": url, "text": "How can I debug streaming errors?"}]
        brief = {"summary_zh": "一个接入问题", "replies": [{"source_url": url,
            "evidence": "debug streaming errors", "category": "coding",
            "reply_en": "Which version are you using?", "meaning_zh": "询问版本",
            "technical_check_zh": "核对具体客户端的版本与错误"}], "api_needs": []}
        return items, brief

    def test_generation_model_and_privacy_controls(self):
        items, brief = self.sample()
        response = {"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": json.dumps(brief)}]}]}
        with patch.object(ops, "request", side_effect=[{"data": [{"id": "gpt-6.1-sol"}]}, response]) as req:
            text = ops.generate(items, [], "fake")
            self.assertIn(items[0]["url"], text)
            self.assertIn("待处理", text)
            payload = req.call_args.args[2]
            self.assertFalse(payload["store"])
            self.assertEqual(payload["model"], "gpt-6.1-sol")

    def test_incomplete_model_response_blocks_delivery(self):
        with patch.object(ops, "request", side_effect=[{"data": [{"id": "gpt-6.1-sol"}]},
                {"status": "incomplete"}]):
            with self.assertRaises(RuntimeError):
                ops.generate(self.sample()[0], [], "fake")

    def test_invalid_model_draft_regenerates_once(self):
        items, brief = self.sample()
        def response(text):
            return {"status": "completed", "output": [{"type": "message", "content": [
                {"type": "output_text", "text": text}]}]}
        with patch.object(ops, "request", side_effect=[{"data": [{"id": "gpt-6.1-sol"}]},
                response("not json"), response(json.dumps(brief))]) as req:
            self.assertIn(items[0]["url"], ops.generate(items, [], "fake"))
            self.assertEqual(req.call_count, 3)

    def test_bad_evidence_still_blocks_after_repair(self):
        items, brief = self.sample()
        brief["replies"][0]["evidence"] = "invented"
        response = {"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": json.dumps(brief)}]}]}
        with patch.object(ops, "request", side_effect=[{"data": [{"id": "gpt-6.1-sol"}]},
                response, response]) as req:
            with self.assertRaises(ops.BriefError):
                ops.generate(items, [], "fake")
            self.assertEqual(req.call_count, 3)

    def test_empty_source_does_not_call_model(self):
        with patch.object(ops, "request") as req:
            self.assertIn("未调用模型", ops.generate([], [], None))
            req.assert_not_called()

    def test_invented_evidence_or_url_blocks(self):
        for field, value in (("evidence", "invented statement"), ("source_url", "https://evil.example")):
            items, brief = self.sample()
            brief["replies"][0][field] = value
            with self.assertRaises(ValueError):
                ops.validate_brief(brief, items)

    def test_external_requires_separate_approvals(self):
        config = copy.deepcopy(CONFIG)
        channel = config["channels"][0]
        channel["kind"] = "external"
        approvals = ("rules_reviewed", "admin_bot_approved", "source_processing_approved",
                     "channel_scope_approved")
        for flag in approvals:
            with self.assertRaises(ValueError):
                ops.load_config(json.dumps(config))
            channel[flag] = True
        self.assertEqual(ops.load_config(json.dumps(config)), config)

    def test_other_author_cannot_spoof_review_marker(self):
        with patch.object(ops, "request", return_value=[{
                "content": "[CodingRouter Discord review 2026-10-17]", "author": {"id": "wrong"}}]):
            self.assertFalse(ops.review_exists(CONFIG, "fake", "2026-10-17", ID))

    def test_long_review_is_split_without_truncation(self):
        text = "a" * 5000
        with patch.object(ops, "request", side_effect=[[], {"id": ID}]) as req:
            ops.deliver(text, CONFIG, "fake", "2026-10-17", ID)
            embeds = req.call_args.kwargs["payload"]["embeds"]
            self.assertEqual("".join(x["description"] for x in embeds), text)
            self.assertTrue(all(len(x["description"]) <= 3800 for x in embeds))

    def test_more_credential_and_private_link_redaction(self):
        raw = ("github_pat_abcdef012345 api_key=secret123 https://host.example/?token=abc "
               "https://user:pass@host.example/ " + "A" * 24 + "." + "B" * 6 + "." + "C" * 30)
        filtered = ops.redact(raw)
        for secret in ("abcdef012345", "secret123", "token=abc", "user:pass", "C" * 30):
            self.assertNotIn(secret, filtered)

    def test_duplicate_main_skips_source_and_model(self):
        from types import SimpleNamespace
        env = {"DISCORD_CHANNEL_CONFIG": json.dumps(CONFIG), "DISCORD_BOT_TOKEN": "fake"}
        with patch.dict(ops.os.environ, env, clear=True), \
                patch.object(ops.argparse.ArgumentParser, "parse_args", return_value=SimpleNamespace(check=False)), \
                patch.object(ops, "request", side_effect=[{"id": ID}, {"guild_id": ID}]), \
                patch.object(ops, "review_exists", return_value=True), \
                patch.object(ops, "collect") as collect, patch.object(ops, "generate") as generate:
            ops.main()
            collect.assert_not_called()
            generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
