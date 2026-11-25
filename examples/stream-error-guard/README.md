# SSE stream error guard

An offline, provider-neutral demonstration of parsing a small subset of Server-Sent Events and preserving partial output when a provider error arrives. It accepts synthetic `bytes` or `str` chunks and makes no network calls.

Python 3.10 or newer is required. The example uses only the Python standard library and synthetic inputs; it reads no credentials, environment variables, or customer data.

Run from the repository root:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected result includes `Ran 13 tests` and `OK`. The evidence test prints the actual interpreter version, compile command, and return codes when run verbosely. Example parser result:

```python
from parser import parse_sse_stream

result = parse_sse_stream([
    'data: {"text":"hello"}\n\n',
    'data: [DONE]\n\n',
])
print(result)
```

Expected output:

```text
StreamResult(completed=True, partial_text='hello', error_type=None, error_code=None, status='complete')
```

Acceptance evidence maps directly to tests in `tests/test_stream_error_guard.py`: complete DONE event: `test_content_then_done_completes`; provider error and preserved partial output: `test_provider_error_preserves_partial_text`; split error JSON including bytes chunks: `test_error_json_split_across_chunks`; multiple events and error-before-DONE in one chunk: `test_multiple_events_in_one_chunk` and `test_error_before_done_in_same_chunk_stops_as_error`; multiline data and ignored comments: `test_multiline_data_and_comments`; malformed JSON, absent DONE, and unterminated EOF event: `test_malformed_json_and_missing_done_are_distinct` and `test_unterminated_event_at_eof_is_not_dispatched`; stop consuming after provider error: `test_provider_error_does_not_consume_next_chunk`; multibyte UTF-8 split, CRLF split, and invalid UTF-8: `test_utf8_split_inside_chinese_character`, `test_crlf_split_across_chunks`, and `test_invalid_utf8_is_malformed`; offline interpreter and compilation evidence: `test_offline_python_version_and_compile_evidence`.

This parser implements only `data:` fields, comments, blank-line event dispatch, and `[DONE]`. It does not implement connection management, reconnection, `id`, or `retry`. Incomplete events at EOF are not dispatched; provider errors and malformed events never count as completion. These tests validate local parser behavior only and are not live API tests or proof of isolated validation by a credential-free publisher job.
