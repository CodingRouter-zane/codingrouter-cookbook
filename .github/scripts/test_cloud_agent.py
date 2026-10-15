import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("agent", Path(__file__).with_name("cloud_agent.py"))
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


class ControllerTests(unittest.TestCase):
    def test_model_name_normalization_does_not_choose_another_model(self):
        self.assertEqual(agent.model_name_key("6.1-Sol"), agent.model_name_key("gpt-6.1-sol"))
        self.assertNotEqual(agent.model_name_key("6.1-Sol"), agent.model_name_key("gpt-6.1-sol-mini"))
    def check_selection(self, dry_run, key_configured, custom=False, endpoint="", model=""):
        issue = {"number": 1, "title": "[技术任务] calculator", "state": "open",
                 "user": {"login": "CodingRouter-zane"},
                 "html_url": "https://github.com/CodingRouter-zane/codingrouter-cookbook/issues/1",
                 "body": "Use synthetic data only."}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {"GITHUB_OUTPUT": str(root / "outputs"),
                   "GITHUB_STEP_SUMMARY": str(root / "summary"),
                   "KEY_CONFIGURED": str(key_configured).lower(),
                   "CUSTOM_PROVIDER": str(custom).lower(),
                   "RESPONSES_ENDPOINT": endpoint, "CODEX_MODEL": model}
            with patch.dict(os.environ, env), patch.object(agent, "api", side_effect=[[], [issue]]), \
                    patch.object(agent, "git", return_value=b"abc123\n"):
                agent.select_task(root / "task", 0, dry_run)
            return (root / "outputs").read_text(), json.loads((root / "task/task.json").read_text())

    def test_missing_key_disables_model_job(self):
        output, task = self.check_selection(False, False)
        self.assertIn("ready=false", output)
        self.assertEqual(task["issue"], 1)

    def test_dry_run_disables_model_even_with_key(self):
        output, _ = self.check_selection(True, True)
        self.assertIn("ready=false", output)

    def test_configured_real_run_is_ready(self):
        output, _ = self.check_selection(False, True)
        self.assertIn("ready=true", output)

    def test_custom_provider_requires_endpoint_and_model(self):
        for endpoint, model in [("", "model"), ("http://example.com/v1/responses", "model"),
                                ("https://example.com/v1/chat/completions", "model"),
                                ("https://example.com/v1/responses", "")]:
            output, _ = self.check_selection(False, True, True, endpoint, model)
            self.assertIn("ready=false", output)

    def test_custom_responses_provider_ready(self):
        output, _ = self.check_selection(False, True, True, "https://example.com/v1/responses", "model")
        self.assertIn("ready=true", output)

    def test_allow_examples_and_tests(self):
        for path in ["examples/cost/main.py", "tests/test_cost.py", "examples/cost/README.md"]:
            self.assertTrue(agent.allowed(path))

    def test_reject_control_files_and_paths(self):
        for path in [".github/workflows/x.yml", "docs/content-index.json", "README.md",
                     "examples/../README.md", "/tests/a.py", "examples/.env",
                     "examples/x/.git/config", "examples/x.exe", "examples\\x.py"]:
            self.assertFalse(agent.allowed(path), path)

    def test_owner_issue_allowed(self):
        issue = {"number": 1, "title": "[技术任务] calculator", "state": "open",
                 "user": {"login": "CodingRouter-zane"}}
        self.assertTrue(agent.eligible(issue, []))
        for field, value in [("state", "closed"), ("title", "untrusted"),
                             ("user", {"login": "someone-else"}), ("pull_request", {})]:
            self.assertFalse(agent.eligible({**issue, field: value}, []))

    def test_existing_pr_skips_issue(self):
        issue = {"number": 1, "title": "[技术任务] calculator", "state": "open",
                 "user": {"login": "CodingRouter-zane"}}
        self.assertFalse(agent.eligible(issue, [{"head": {"ref": "codex/cloud-issue-1-123"}}]))
        self.assertTrue(agent.eligible(issue, [{"head": {"ref": "codex/cloud-issue-12-123"}}]))
        self.assertFalse(agent.eligible(issue, [{"head": {"ref": "codex/issue-1-cost"}}]))
        self.assertFalse(agent.eligible(issue, [{"user": {"login": "CodingRouter-zane"}, "body": "Refs #1"}]))


if __name__ == "__main__":
    unittest.main()
