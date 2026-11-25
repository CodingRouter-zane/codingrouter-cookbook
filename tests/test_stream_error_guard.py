import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples" / "stream-error-guard"))
from parser import parse_sse_stream


class StreamParserTests(unittest.TestCase):
    def test_content_then_done_completes(self):
        result = parse_sse_stream([b'data: {"text":"hello"}\n\ndata: [DONE]\n\n'])
        self.assertEqual((result.completed, result.partial_text, result.status), (True, "hello", "complete"))

    def test_provider_error_preserves_partial_text(self):
        result = parse_sse_stream(['data: {"text":"part"}\n\n',
                                   'data: {"error":{"type":"overloaded","code":"busy"}}\n\n'])
        self.assertFalse(result.completed)
        self.assertEqual(result.partial_text, "part")
        self.assertEqual((result.error_type, result.error_code, result.status),
                         ("overloaded", "busy", "provider_error"))

    def test_error_json_split_across_chunks(self):
        payload = b'data: {"error":{"type":"rate_limit","code":"slow_down"}}\n\n'
        split = payload.index(b'"code"') + 3
        result = parse_sse_stream([b'data: {"text":"kept"}\n\n', payload[:split], payload[split:]])
        self.assertEqual((result.error_type, result.error_code), ("rate_limit", "slow_down"))
        self.assertEqual(result.partial_text, "kept")
        self.assertFalse(result.completed)

    def test_multiple_events_in_one_chunk(self):
        result = parse_sse_stream(['data: {"text":"one"}\n\ndata: {"text":"two"}\n\ndata: [DONE]\n\n'])
        self.assertEqual((result.partial_text, result.status), ("onetwo", "complete"))

    def test_error_before_done_in_same_chunk_stops_as_error(self):
        result = parse_sse_stream(['data: {"error":{"type":"bad","code":"x"}}\n\ndata: [DONE]\n\n'])
        self.assertFalse(result.completed)
        self.assertEqual(result.status, "provider_error")

    def test_multiline_data_and_comments(self):
        result = parse_sse_stream([': ping\n\ndata: {"text":\ndata: "joined"}\n\ndata: [DONE]\n\n'])
        self.assertEqual(result.partial_text, "joined")
        self.assertTrue(result.completed)

    def test_malformed_json_and_missing_done_are_distinct(self):
        malformed = parse_sse_stream(['data: {nope}\n\n'])
        incomplete = parse_sse_stream(['data: {"text":"partial"}\n\n'])
        self.assertEqual(malformed.status, "malformed_event")
        self.assertFalse(malformed.completed)
        self.assertEqual(incomplete.status, "incomplete")
        self.assertEqual(incomplete.partial_text, "partial")

    def test_unterminated_event_at_eof_is_not_dispatched(self):
        result = parse_sse_stream(['data: {"text":"not committed"}'])
        self.assertFalse(result.completed)
        self.assertEqual(result.partial_text, "")
        self.assertEqual(result.status, "incomplete")

    def test_provider_error_does_not_consume_next_chunk(self):
        consumed = []
        def chunks():
            consumed.append("error")
            yield 'data: {"error":{"type":"bad"}}\n\n'
            consumed.append("sentinel")
            yield 'data: [DONE]\n\n'
        result = parse_sse_stream(chunks())
        self.assertEqual(consumed, ["error"])
        self.assertFalse(result.completed)

    def test_utf8_split_inside_chinese_character(self):
        wire = 'data: {"text":"中"}\n\ndata: [DONE]\n\n'.encode()
        index = wire.index("中".encode()) + 1
        result = parse_sse_stream([wire[:index], wire[index:]])
        self.assertEqual(result.partial_text, "中")
        self.assertTrue(result.completed)

    def test_crlf_split_across_chunks(self):
        result = parse_sse_stream([b'data: {"text":"ok"}\r', b'\n\r\ndata: [DONE]\r\n\r\n'])
        self.assertEqual(result.partial_text, "ok")
        self.assertTrue(result.completed)

    def test_invalid_utf8_is_malformed(self):
        result = parse_sse_stream([b'data: {"text":"\xff"}\n\n'])
        self.assertEqual(result.status, "malformed_event")
        self.assertFalse(result.completed)

    def test_offline_python_version_and_compile_evidence(self):
        root = Path(__file__).resolve().parents[1]
        parser = root / "examples" / "stream-error-guard" / "parser.py"
        test_file = Path(__file__).resolve()
        version_cmd = [sys.executable, "--version"]
        version = subprocess.run(version_cmd, capture_output=True, text=True, check=False)
        print("command:", json.dumps(version_cmd), "output:", (version.stdout or version.stderr).strip(),
              "returncode:", version.returncode)
        self.assertEqual(version.returncode, 0)
        compile_cmd = [sys.executable, "-m", "py_compile", str(parser), str(test_file)]
        compiled = subprocess.run(compile_cmd, capture_output=True, text=True, check=False)
        print("command:", json.dumps(compile_cmd), "returncode:", compiled.returncode)
        self.assertEqual(compiled.returncode, 0, compiled.stderr)


if __name__ == "__main__":
    unittest.main()
