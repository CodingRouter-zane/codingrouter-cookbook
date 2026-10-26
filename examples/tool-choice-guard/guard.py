"""离线工具禁用回归样例（仅使用合成 mock 数据）。

用途：演示 toolChoice='none' 时的本地执行边界和防御性检查。
背景：https://github.com/vercel/ai/releases/tag/ai%405.0.281
      https://github.com/vercel/ai/pull/23846
本实现独立编写，不复刻 Vercel 源码，不判断其他 SDK 版本是否有问题。

环境：Python 3.10+，仅标准库，无第三方依赖，无费用。
启动：python examples/tool-choice-guard/guard.py
测试：python -m unittest discover -s tests -p 'test_*.py' -v
语法检查：python -m py_compile examples/tool-choice-guard/guard.py tests/test_tool_choice_guard.py
预期：演示输出 PolicyViolation 和 mock 执行次数 0；离线测试全部通过。
验证范围：仅本地 mock 策略门；不证明上游模型遵守约束，不证明任何
CodingRouter 接口兼容性，也不验证真实 SDK、供应商或网络流协议。
不读取密钥或环境变量，不联网，不使用客户数据。
流被拒绝前已经转发的普通文本不会撤回；违规片段不会转发给执行层。
"""

TOOL_TYPES = frozenset({
    'tool-input-start', 'tool-input-delta', 'tool-input-end',
    'tool-call', 'tool-result',
})


class PolicyViolation(ValueError):
    """工具策略禁止该事件；不得 repair 或重试。"""


class InputFormatError(ValueError):
    """策略或 mock 输入格式不合法。"""


def _validate(policy, event):
    if policy not in ('none', 'auto'):
        raise InputFormatError('policy must be none or auto')
    if not isinstance(event, dict) or not isinstance(event.get('type'), str):
        raise InputFormatError('event must be a dict with a string type')
    kind = event['type']
    if kind not in TOOL_TYPES and kind != 'text':
        raise InputFormatError('unknown event type')
    if kind == 'text' and not isinstance(event.get('text'), str):
        raise InputFormatError('text event requires string text')
    if kind == 'tool-call':
        if not isinstance(event.get('name'), str) or not event['name']:
            raise InputFormatError('tool-call requires a nonempty name')
        if not isinstance(event.get('arguments'), dict):
            raise InputFormatError('tool-call requires dict arguments')
    if policy == 'none' and kind in TOOL_TYPES:
        raise PolicyViolation('toolChoice=none forbids tool events')


def _deliver(event, execute, forward, repair):
    if event['type'] == 'tool-call':
        try:
            execute(event['name'], event['arguments'])
        except Exception as error:
            if repair is None:
                raise
            repair(error)
    if forward is not None:
        forward(event)


def process_response(policy, response, execute, *, forward=None, repair=None):
    """处理 mock 非流式事件列表。成功返回 True；拒绝抛出明确类型异常。

    整批预检后才执行回调，因此格式错误或策略违规不会产生部分执行。
    execute/forward/repair 仅由调用者提供；此模块没有真实工具实现。
    """
    if not isinstance(response, list):
        raise InputFormatError('response must be a list of mock events')
    if policy not in ('none', 'auto'):
        raise InputFormatError('policy must be none or auto')
    for event in response:
        _validate(policy, event)
    for event in response:
        _deliver(event, execute, forward, repair)
    return True


def process_stream(policy, events, execute, *, forward=None, repair=None):
    """按到达顺序检查 mock 事件，在任何执行层回调前拦截违规事件。

    每次调用处理一个流；遇到错误立即结束，不消费后续事件。
    工具片段仅用于演示转发边界，不实现参数拼装或协议解析。
    """
    if policy not in ('none', 'auto'):
        raise InputFormatError('policy must be none or auto')
    try:
        iterator = iter(events)
    except TypeError as error:
        raise InputFormatError('stream must be iterable') from error
    for event in iterator:
        _validate(policy, event)
        _deliver(event, execute, forward, repair)
    return True


if __name__ == '__main__':
    mock_calls = []
    try:
        process_response('none', [
            {'type': 'tool-call', 'name': 'mock_echo', 'arguments': {'value': 1}},
        ], lambda name, arguments: mock_calls.append((name, arguments)))
    except PolicyViolation as error:
        print(f'{type(error).__name__}: {error}; mock executions={len(mock_calls)}')
