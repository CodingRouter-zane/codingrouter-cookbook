# 离线 SSE 中途错误解析器

本示例用明确标注的 synthetic/mock SSE 数据展示：HTTP 200 后仍可能在流中收到错误。解析结果包含 `completed`、错误前的 `partial_text`、`error_type`、`error_code` 和 `status`，便于审计；不会把半截答案标记为成功，也不会自行推断是否应该重试。

需要 Python 3.9+，仅使用标准库，第三方依赖为 0，费用为 0。运行示例：

```bash
python -c 'import sys; sys.path.insert(0, "examples/stream-error-guard"); from parser import parse_sse_stream; print(parse_sse_stream(["data: {\\"text\\":\\"synthetic\\"}\\n\\n", "data: [DONE]\\n\\n"]))'
```

测试命令：`python -m unittest discover -s tests -p "test_*.py"`。预期 4 个测试通过、退出状态 0。编译检查：`python -m py_compile examples/stream-error-guard/parser.py tests/test_stream_error_guard.py`，退出状态 0。

验证状态：已用 synthetic/mock 数据覆盖完成、provider error、跨块 JSON、单块多事件、多 `data:` 行、keepalive、malformed JSON、缺少 `[DONE]` 及错误后停止消费。验证不联网、不读取密钥、提示词、客户数据或环境变量，不代表 CodingRouter 或任何上游接口兼容性；真实传输层、重试策略和业务持久化仍由调用方负责。
