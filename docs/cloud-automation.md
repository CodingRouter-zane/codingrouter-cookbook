# Cloud technical automation

The technical worker runs on GitHub-hosted Ubuntu runners. Your computer and phone do not need to stay on. ChatGPT continues to handle editorial selection, documentation and X drafts.

## Setup

1. In repository **Settings → Secrets and variables → Actions**, add repository secret `CODINGROUTER_API_KEY`. The user-confirmed endpoint defaults to `https://api.codingrouter.ai/v1/responses`; optional variable `CODEX_RESPONSES_API_URL` overrides it. The requested model defaults to `6.1-Sol`; the worker queries `/v1/models` and resolves an exact or uniquely matching `gpt-`/case-normalized API ID. It never substitutes a different model. Optional `CODEX_MODEL` sets an exact ID if required. The endpoint must implement Responses API semantics compatible with Codex; Chat Completions support alone is insufficient. Alternatively, an OpenAI configuration uses repository secret `OPENAI_API_KEY`. CodingRouter takes precedence when its key is present. Never put a key in an Issue, commit or chat.
2. In **Settings → Actions → General**, allow GitHub Actions to create pull requests. Keep the workflow permissions as declared; do not grant administration access.
3. In **Actions → CodingRouter cloud technical agent → Run workflow**, first keep `dry_run=true`. This checks the task queue and controller without calling a model.
4. For a billable, read-only connection test, keep `dry_run=true` and enable `connection_check`. This resolves the requested CodingRouter model and verifies a real Codex response without developing code or creating a PR.
5. To develop a genuine queued task, use `dry_run=false`, `connection_check=false` and an eligible owner-created Issue number (or 0 for the oldest eligible task). An existing open cloud or desktop PR causes that Issue to be skipped. Do not create artificial tasks solely to make the deployment look complete.
6. Read actual run logs and draft PR evidence. A successful connection test proves credentials/model/proxy compatibility; it does not prove the full development, validation and PR publication chain.

## Daily behavior

- Scheduled at **11:30 Asia/Shanghai** (`03:30 UTC`). GitHub can delay scheduled jobs; this is not an exact-time SLA.
- At most one open Issue authored by `CodingRouter-zane` with title beginning `[技术任务]` is selected. An existing open cloud or desktop technical PR prevents duplicate work for that Issue. Queue scans cover the oldest 100 open items; keep a small task queue.
- Without the chosen provider's key, endpoint or required model, the run reports the missing configuration and makes no model call. Passing configuration checks alone does not prove API compatibility; use the isolated connection check to verify actual Codex integration.
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

## Verified deployment status — 2026-10-15

- The user added `CODINGROUTER_API_KEY` and explicitly authorized the repository's Actions create/approve PR setting. The worker only creates draft PRs; it never approves or merges them.
- Actual Codex connection check [run #5](https://github.com/CodingRouter-zane/codingrouter-cookbook/actions/runs/38727482758) succeeded with resolved model `gpt-6.1-sol` and exact response `READY`. Controller tests also passed (10 tests).
- The old desktop automation `3-ai` is paused to prevent duplicate scheduled work. GitHub-hosted scheduled runs do not depend on the user's computer or phone being on.
- Issue #1 already has open PR #2 and was correctly skipped. The user subsequently explicitly requested full verification; the clearly labeled acceptance Issue #4 was created for this purpose. This fixture is not a new article or product performance claim.
- Existing open PRs require separate review or maintenance; the cloud selector does not automatically revise them.

## Full workflow acceptance — 2026-10-15

At the user's explicit request, [run #6](https://github.com/CodingRouter-zane/codingrouter-cookbook/actions/runs/38729260706) processed [acceptance Issue #4](https://github.com/CodingRouter-zane/codingrouter-cookbook/issues/4). The actual CodingRouter-backed Codex development, allowed-patch export, isolated unittest validation and trusted PR publisher all succeeded. The independent validator ran **11 tests** on Python **3.12.3** and compiled the generated Python files.

The publisher created [draft PR #5](https://github.com/CodingRouter-zane/codingrouter-cookbook/pull/5), head `80ccd6002507fef0d54dea98ef75991f50435dad`, based on `91e26bf420624faaf5fe4b96dc2710cae03ae323`. Review confirmed exactly three added acceptance files and no deleted files. The generated code remained on its branch: immediately after the run, `main` still matched the selected base. This acceptance PR must remain unmerged unless the user separately requests its publication.

This verifies one manually triggered full cloud task. The first future scheduled run, existing-PR revisions, X account connectivity and post scheduling are separate checks; none are proven by this run. It is not an availability, model-identity, throughput or SLA guarantee.

## Isolation startup compatibility maintenance — 2026-11-24

Scheduled [run 45409843844](https://github.com/CodingRouter-zane/codingrouter-cookbook/actions/runs/45409843844) failed during Codex startup on Ubuntu 26.04 while checking access to `/run/dbus/system_bus_socket`. Model ID resolution succeeded, but patch export, independent validation and PR publication did not run. This is not a failed SSE unit test or evidence of completed development.

[Maintenance PR #15](https://github.com/CodingRouter-zane/codingrouter-cookbook/pull/15) updated both existing Codex Action references to upstream fixed commit `306c6a196a99dcc6582530c396a19d2672d5e9ec` ([upstream PR #192](https://github.com/openai/codex-action/pull/192)). The fix uses an ACL-aware socket access probe and retains isolation. Merge commit: `d1823f58e8aa34cd40289e6951d8f70e3185717d`.

The maintenance changes only the two Action pins and a review-date comment. Runner labels, `drop-sudo`, permissions, secrets, model/endpoint, allowed task paths and the existing schedule are unchanged. PR [run 45420683230](https://github.com/CodingRouter-zane/codingrouter-cookbook/actions/runs/45420683230) passed 29 controller tests; development, connection-check, validation and PR publication were skipped as intended for infrastructure PRs. The subsequent main push smoke run [45420842728](https://github.com/CodingRouter-zane/codingrouter-cookbook/actions/runs/45420842728) also succeeded.

These smoke checks do **not** establish recovery of real Codex startup or delivery of [Issue #14](https://github.com/CodingRouter-zane/codingrouter-cookbook/issues/14). That existing task remains pending a fresh current-main run and its independent acceptance evidence. Rerunning a historical run would reuse its old workflow revision; use the current-main workflow instead. Keep old PR #13 draft until the new work is accepted. No additional connection or live-model acceptance test was performed for this maintenance.

## Scheduled real-task recovery evidence — 2026-11-26 review

The first observed real-task run after the Action pin repair, [45621951523](https://github.com/CodingRouter-zane/codingrouter-cookbook/actions/runs/45621951523), started on 2026-11-25 at 21:16:46 Asia/Shanghai. It selected existing Issue #14 at base `4c1084cb6d599fb3c10681f4e9735d2a2b63b8f4`. Plan, development, independent validation and draft-PR publication all succeeded; no separate connection-check ran.

The independent validator used Python **3.14.4**, ran **13 unittest tests**, and logged the actual interpreter command and the limited `py_compile` command with return code **0**. The validated artifact's SHA-256 matches GitHub's digest, and its `validation.json` identifies the same Issue/base and offline scope. The publisher created [draft PR #16](https://github.com/CodingRouter-zane/codingrouter-cookbook/pull/16), head `dc8c6e82579b8f41018a6eb1fb2cbe1efc2347e9`.

This demonstrates recovery of one scheduled real development-to-draft-PR chain, not a reliability/SLA guarantee or completed SSE publication. Review found an extra file beyond Issue #14's exact path scope and a README example that cannot import the parser when copied from the repository root. PR #16 remains draft pending separate revision and precise-head evidence; the selector does not revise it automatically. Old PR #13 also remains draft. The 13 tests are the discovered SSE suite, not proof that all historical examples were regression-tested. No live model API acceptance or performance test was run; authorized Codex development usage is distinct from the offline example/test cost.
