"""纯离线 mock 测试；不是 live API 测试。"""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock


MODULE = Path(__file__).resolve().parents[1] / 'examples/tool-choice-guard/guard.py'
SPEC = importlib.util.spec_from_file_location('tool_choice_guard', MODULE)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


def tool_call():
    return {'type': 'tool-call', 'name': 'mock_echo', 'arguments': {'value': 7}}


class ToolChoiceGuardTests(unittest.TestCase):
    def setUp(self):
        self.execute = Mock()
        self.forward = Mock()
        self.repair = Mock()

    def invoke(self, processor, policy, events):
        return processor(policy, events, self.execute,
                         forward=self.forward, repair=self.repair)

    def test_none_nonstream_rejects_before_execution_or_repair(self):
        with self.assertRaisesRegex(guard.PolicyViolation, 'toolChoice=none'):
            self.invoke(guard.process_response, 'none', [tool_call()])
        self.execute.assert_not_called()
        self.forward.assert_not_called()
        self.repair.assert_not_called()

    def test_none_stream_blocks_each_tool_fragment_before_delivery(self):
        for kind in sorted(guard.TOOL_TYPES):
            with self.subTest(kind=kind):
                event = tool_call() if kind == 'tool-call' else {'type': kind}
                with self.assertRaises(guard.PolicyViolation):
                    self.invoke(guard.process_stream, 'none', iter([event]))
                self.execute.assert_not_called()
                self.forward.assert_not_called()
                self.repair.assert_not_called()

    def test_none_text_passes_in_both_modes(self):
        text = {'type': 'text', 'text': 'synthetic hello'}
        for processor in (guard.process_response, guard.process_stream):
            self.assertTrue(self.invoke(processor, 'none', [text]))
        self.assertEqual(self.forward.call_count, 2)
        self.forward.assert_called_with(text)
        self.execute.assert_not_called()

    def test_auto_executes_only_mock_callback_once_per_call(self):
        for processor in (guard.process_response, guard.process_stream):
            self.execute.reset_mock()
            self.assertTrue(self.invoke(processor, 'auto', [tool_call()]))
            self.execute.assert_called_once_with('mock_echo', {'value': 7})
        self.repair.assert_not_called()

    def test_format_errors_are_distinct_and_do_not_repair(self):
        for processor in (guard.process_response, guard.process_stream):
            for event in (None, {'type': 'unknown'}, {'type': 'text'},
                          {'type': 'tool-call', 'name': 'mock_echo'}):
                with self.subTest(processor=processor.__name__, event=event):
                    with self.assertRaises(guard.InputFormatError) as caught:
                        self.invoke(processor, 'none', [event])
                    self.assertNotIsInstance(caught.exception, guard.PolicyViolation)
        self.execute.assert_not_called()
        self.repair.assert_not_called()

    def test_invalid_policy_and_container(self):
        for processor in (guard.process_response, guard.process_stream):
            with self.assertRaises(guard.InputFormatError):
                self.invoke(processor, 'required', [])
            with self.assertRaises(guard.InputFormatError):
                self.invoke(processor, 'none', None)

    def test_stream_stops_at_violation_without_consuming_later_events(self):
        text = {'type': 'text', 'text': 'synthetic prefix'}
        def events():
            yield text
            yield tool_call()
            self.fail('stream consumed past policy violation')
        with self.assertRaises(guard.PolicyViolation):
            self.invoke(guard.process_stream, 'none', events())
        self.forward.assert_called_once_with(text)
        self.execute.assert_not_called()
        self.repair.assert_not_called()

    def test_batch_preflight_prevents_partial_execution(self):
        with self.assertRaises(guard.InputFormatError):
            self.invoke(guard.process_response, 'auto', [tool_call(), None])
        self.execute.assert_not_called()

    def test_repair_is_only_used_for_mock_execution_failure(self):
        self.execute.side_effect = RuntimeError('synthetic tool failure')
        self.invoke(guard.process_response, 'auto', [tool_call()])
        self.assertEqual(self.execute.call_count, 1)
        self.repair.assert_called_once_with(self.execute.side_effect)


if __name__ == '__main__':
    unittest.main()
