# Cloud technical automation

The technical worker runs on GitHub-hosted Ubuntu runners. Your computer and phone do not need to stay on. ChatGPT continues to handle editorial selection, documentation and X drafts.

## Setup

1. In repository **Settings → Secrets and variables → Actions**, add repository secret `CODINGROUTER_API_KEY`. The user-confirmed endpoint defaults to `https://api.codingrouter.ai/v1/responses`; optional variable `CODEX_RESPONSES_API_URL` overrides it. The requested model defaults to `6.1-Sol`; the worker queries `/v1/models` and resolves an exact or uniquely matching `gpt-`/case-normalized API ID. It never substitutes a different model. Optional `CODEX_MODEL` sets an exact ID if required. The endpoint must implement Responses API semantics compatible with Codex; Chat Completions support alone is insufficient. Alternatively, an OpenAI configuration uses repository secret `OPENAI_API_KEY`. CodingRouter takes precedence when its key is present. Never put a key in an Issue, commit or chat.
2. In **Settings → Actions → General**, allow GitHub Actions to create pull requests. Keep the workflow permissions as declared; do not grant administration access.
3. In **Actions → CodingRouter cloud technical agent → Run workflow**, first keep `dry_run=true`. This checks the task queue and controller without calling a model.
4. After that succeeds, run once with `dry_run=false` and `issue_number=1` (or another owner-created technical Issue). This makes billable model calls. An optional Actions variable `CODEX_MODEL` selects an available model; when unset the official action uses its default.
5. Read the run logs and draft PR. Only after the first real run works should the old desktop technical worker be paused. A deployed workflow without a valid key is not a completed cloud migration.

## Daily behavior

- Scheduled at **11:30 Asia/Shanghai** (`03:30 UTC`). GitHub can delay scheduled jobs; this is not an exact-time SLA.
- At most one open Issue authored by `CodingRouter-zane` with title beginning `[技术任务]` is selected. An existing open cloud PR prevents duplicate work for that Issue. Queue scans cover the oldest 100 open items; keep a small task queue.
- Without the chosen provider's key, endpoint or required model, the run reports the missing configuration and makes no model call. CodingRouter compatibility must still be tested with a real run; passing configuration checks does not prove API compatibility.
- Codex changes only `examples/` and `tests/`, using Python standard library and synthetic data. It cannot publish directly to `main` through this workflow.
- A fresh job runs actual unittest tests and Python compilation without the API secret or a write credential. Zero tests or failed tests block publication.
- A separate publisher creates a draft PR with the test count, base/head commits and run link. It does not execute generated code. ChatGPT reviews the diff and full logs before merging under the weekly publication quota.
- If `main` changes mid-run, the publisher stops; the next run retries from current `main`.
- Infrastructure pushes/PRs run the free controller smoke checks only, never Codex. No automatic replies or X posts are included.

## Costs and limits

Model usage is billed by the configured provider (CodingRouter or OpenAI). Configure provider spending controls before enabling real runs. Jobs have timeouts and process one Issue per day, but a timeout is not a hard monetary cap. GitHub-hosted runner usage follows your GitHub plan. No live model API acceptance tests or customer workloads are performed by generated examples.

## Operations

The shared public content index remains `docs/content-index.json`. ChatGPT adds technical Issues and reads resulting PRs; internal customer data, prices not approved for publication and marketing scores stay out of this repository. Weekly content frequency remains Monday/Wednesday/Friday, normally three items, with one additional verified product update at most. Controller maintenance and necessary fixes do not count as new articles.

Disable the workflow from its Actions page to stop cloud runs. Remove the secret to prevent model calls. Keep the desktop worker paused after verified cutover; do not run both against the same queue.
