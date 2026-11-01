import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "examples" / "stream-error-guard"))
from parser import parse_sse_stream


class StreamErrorGuardTests(unittest.TestCase):
    def test_done_after_content(self):
        r = parse_sse_stream([b'data: {"text":"hi"}\n\n', b'data: [DONE]\n\n'])
        self.assertTrue(r.completed); self.assertEqual(r.partial_text, "hi")

    def test_provider_error_stops_generator(self):
        consumed = []
        def stream():
            for x in ['data: {"text":"a"}\n\n', 'data: {"error":{"type":"rate_limit","code":"E1"}}\n\n', 'data: {"text":"late"}\n\n']:
                consumed.append(x); yield x
        r = parse_sse_stream(stream())
        self.assertFalse(r.completed); self.assertEqual(r.partial_text, "a")
        self.assertEqual(r.error_type, "rate_limit"); self.assertEqual(r.error_code, "E1")
        self.assertEqual(len(consumed), 2)

    def test_split_json_multiple_events_and_multiline_data(self):
        r = parse_sse_stream([': keepalive\n\n', 'data: {"te', 'xt":"a"}\n', 'data: \n', '\n', 'data: [DONE]\n\n'])
        self.assertTrue(r.completed); self.assertEqual(r.partial_text, "a")
        r = parse_sse_stream(['data: {"text":"a"', '}\n\n'])
        self.assertEqual(r.partial_text, "a")

    def test_malformed_and_incomplete_are_distinct(self):
        malformed = parse_sse_stream(['data: {bad}\n\n'])
        self.assertEqual(malformed.error_type, "malformed_event")
        incomplete = parse_sse_stream(['data: {"text":"x"}\n\n'])
        self.assertFalse(incomplete.completed); self.assertIsNone(incomplete.error_type)
        self.assertEqual(incomplete.status, "incomplete")


if __name__ == "__main__":
    unittest.main()
