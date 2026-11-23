"""离线、供应商无关的 SSE 中途错误解析示例。"""

from dataclasses import dataclass
import codecs
import json
from typing import Iterable, Optional, Union


@dataclass
class StreamResult:
    completed: bool = False
    partial_text: str = ""
    error_type: Optional[str] = None
    error_code: Optional[str] = None
    status: str = "incomplete"


def _text_from_payload(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    if isinstance(payload.get("text"), str):
        return payload["text"]
    error = payload.get("error")
    if isinstance(error, dict):
        return ""
    choices = payload.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        choice = choices[0]
        delta = choice.get("delta")
        if isinstance(delta, dict) and isinstance(delta.get("content"), str):
            return delta["content"]
        if isinstance(choice.get("text"), str):
            return choice["text"]
    return ""


def parse_sse_stream(chunks: Iterable[Union[bytes, str]]) -> StreamResult:
    """解析 synthetic SSE 数据块，并在 provider error 后停止消费。"""
    result = StreamResult()
    decoder = codecs.getincrementaldecoder("utf-8")()
    line_buffer = ""
    data_lines = []
    stopped = False

    def dispatch() -> bool:
        nonlocal data_lines
        if not data_lines:
            return False
        raw = "\n".join(data_lines)
        data_lines = []
        if raw == "[DONE]":
            result.completed = True
            result.status = "complete"
            return True
        try:
            payload = json.loads(raw)
        except (TypeError, ValueError):
            result.error_type = "malformed_event"
            result.status = "malformed_event"
            return True
        if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
            error = payload["error"]
            result.error_type = str(error.get("type", "provider_error"))
            result.error_code = (str(error["code"]) if error.get("code") is not None else None)
            result.status = "provider_error"
            return True
        result.partial_text += _text_from_payload(payload)
        return False

    def consume_line(line: str) -> bool:
        nonlocal data_lines
        if line == "":
            return dispatch()
        if line.startswith(":"):
            return False
        if line.startswith("data:"):
            value = line[5:]
            data_lines.append(value[1:] if value.startswith(" ") else value)
        return False

    iterator = iter(chunks)
    while not stopped:
        try:
            chunk = next(iterator)
        except StopIteration:
            break
        if isinstance(chunk, bytes):
            try:
                line_buffer += decoder.decode(chunk, final=False)
            except UnicodeDecodeError:
                result.error_type = "malformed_event"
                result.status = "malformed_event"
                break
        elif isinstance(chunk, str):
            line_buffer += chunk
        else:
            result.error_type = "malformed_event"
            result.status = "malformed_event"
            break
        while "\n" in line_buffer:
            line, line_buffer = line_buffer.split("\n", 1)
            if line.endswith("\r"):
                line = line[:-1]
            stopped = consume_line(line)
            if stopped:
                break
    if not stopped:
        try:
            line_buffer += decoder.decode(b"", final=True)
        except UnicodeDecodeError:
            result.error_type = "malformed_event"
            result.status = "malformed_event"
        else:
            if line_buffer:
                consume_line(line_buffer.rstrip("\r"))
            if data_lines and result.error_type is None and not result.completed:
                dispatch()
    return result

