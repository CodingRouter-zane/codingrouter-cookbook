# Discord cloud operations

Runs on GitHub-hosted Ubuntu at **12:00 Asia/Shanghai** (04:00 UTC); GitHub may delay scheduled jobs. No personal-account token or self-bot is used. This is daily polling, not an always-online community moderator.

## Current status

The own-community cloud schedule was activated after successful read-only and private-delivery acceptance on 2026-10-17. External communities are not connected. The schedule remains daily 12:00 Asia/Shanghai. The content assistant in ChatGPT and this CodingRouter API worker are separate systems; no automatic private-message transfer between them is implemented.

The improved worker produces source-grounded English reply drafts, Chinese meanings, exact evidence excerpts and a pending technical-review checklist. It validates source URLs and excerpt membership before delivery. This does not verify that the generated advice is correct, that a conversation is unresolved, or that posting is permitted. Those checks remain with the reviewer. No relevant source text means no model call. A same-day review from this Bot skips source/model calls; duplicate markers posted by others do not suppress the job. Longer reviews use bounded embeds rather than silently cutting off the last source.

The own-community integration is configured and verified as of 2026-10-17. The user approved the source-message processing by CodingRouter and delivery to a private review channel. Bot Token and channel configuration are stored as repository Secrets. `DISCORD_CLOUD_ENABLED=true` has been saved and verified; the old local `codingrouter-discord` automation is paused. External community channels are not yet connected. The first future scheduled execution remains unverified.

## Configure privately

1. Create an official Discord application/Bot and invite it only to authorized servers. Enable Message Content intent as required/approved by Discord. Grant View Channel and Read Message History on sources, and Send Messages / Embed Links on a **private review channel**. It also needs to read its review history for daily deduplication. Do not grant Administrator.
2. Add GitHub Actions repository secret `DISCORD_BOT_TOKEN`. Never paste this token into chat, Issues or commits.
3. Add repository secret `DISCORD_CHANNEL_CONFIG` containing numeric IDs as strings. Use a private review channel; do not use a public community channel as the review destination. The example is a schema, not a working configuration:

```json
{
  "processing_approved": true,
  "review_delivery_approved": true,
  "review_channel_id": "REPLACE_WITH_REVIEW_CHANNEL_ID",
  "channels": [
    {"guild_id": "REPLACE_WITH_SERVER_ID", "channel_id": "REPLACE_WITH_CHANNEL_ID", "kind": "own"},
    {"guild_id": "REPLACE_WITH_EXTERNAL_SERVER_ID", "channel_id": "REPLACE_WITH_EXTERNAL_CHANNEL_ID", "kind": "external",
     "rules_reviewed": true, "admin_bot_approved": true,
     "source_processing_approved": true, "channel_scope_approved": true}
  ]
}
```

Set approval flags only after approving the specific sources, the CodingRouter API as processor, and private-review delivery. Selected recent message text and source links are sent to CodingRouter using the existing `CODINGROUTER_API_KEY`, model 6.1-Sol (uniquely resolved via `/v1/models`). Names/attachments are omitted and common mentions/email/key patterns are filtered; this is not a guarantee of anonymization. Do not configure channels containing customer secrets or restricted information. Raw messages/drafts are never uploaded as GitHub artifacts, summaries or commits. `store:false` requests no Responses storage, but is not a provider retention guarantee.

External servers require their administrators to allow the Bot. If unavailable, keep those communities in the manual/draft-assisted workflow; a server invite link alone does not grant Bot access.

The four external-source flags are attestations, not automatic proof. Only set them after checking current server rules, obtaining administrator permission for Bot access, and confirming the specific channel and processing scope with the user. Keep rule links and permission evidence privately; joining with a personal account does not satisfy these conditions. Existing own-source configurations do not need these additional flags.

## Operating roles and review

- **ChatGPT content operator:** public research, English wording, Chinese meaning, community fit and editorial review. It may use private discussions only when an actual authorized connection or user-supplied material is available. A ChatGPT schedule does not automatically gain Discord access.
- **CodingRouter API worker:** daily authorized source polling and private draft delivery. It is not the ChatGPT conversation and must not describe itself as one.
- **Codex technical operator:** implementation, reproducible examples, tests, deployment and debugging. Drafts list proposed checks as pending; this worker does not automatically invoke a Codex agent, run message-supplied code or create public Issues from private discussions.
- **Human reviewer:** confirms current channel rules, whether the issue is still open, technical evidence, affiliation disclosure and concrete publication scope. Sales DMs and friend requests require their own authorization.

The private review message is the operational record. Record actual posting and any reply outcome privately when those actions are separately authorized. Do not treat a proposed reply or API need as a qualified customer or a completed technical fix. No source content, draft, lead list or private channel ID is committed to this public repository.

## Verify and activate

Run this workflow manually with `check_only=true` to verify Bot authentication and source reads. No model call or delivery occurs. Then run with `check_only=false` for one real model draft delivered only to the approved private review channel. Confirm its content and destination. Afterwards set Actions variable `DISCORD_CLOUD_ENABLED=true` and pause the existing local `codingrouter-discord` automation to avoid duplicates.

For model-format acceptance, set `model_check=true`: this overrides `check_only` and sends one fixed synthetic technical question to the configured CodingRouter model. It validates the generated JSON, source URLs and excerpts, prints a content-free result, and performs no Discord read or delivery. It uses the existing model API key and normal account usage. A successful synthetic check verifies integration and formatting, not technical answer accuracy. Invalid/incomplete output fails without delivering a draft. Structured-output support by the third-party provider is not assumed; JSON is requested in the prompt and validated locally.

No community posting, member DMs, join operations or automatic public replies are implemented. A human reviews drafts and separately authorizes publication. The workflow cannot execute commands supplied by Discord messages. Source reads cover up to 100 recent messages per channel in a 24-hour window (up to 6 channels, at most 3 external, at most 20 usable messages per channel); high-volume channels may exceed coverage. Daily markers/nonce deduplicate review delivery, not all future reply recommendations. A review can remain a draft for an already addressed conversation.

GitHub/X schedules remain separate. Public context uses published titles and URLs from `docs/content-index.json`; it does not claim to have read article bodies. Model and GitHub usage follow their respective account limits. No performance or SLA guarantee is implied.

## Runtime evidence — 2026-10-17

- [Read-only connection check](https://github.com/CodingRouter-zane/codingrouter-cookbook/actions/runs/39007192617) succeeded: Bot authentication and configured source reads verified, without a model call or delivery.
- [Full generation and private delivery](https://github.com/CodingRouter-zane/codingrouter-cookbook/actions/runs/39007383383) succeeded. Logs report `Private review draft delivered.` The destination was also verified in Discord: the Bot's dated review message appeared in the private review channel.
- The review channel was verified private, with the server owner and the Bot in its access list. No public posts or member DMs were sent. Current configuration includes one own-community discussion source; external servers still require separately authorized Bot access and source configuration.
- No relevant recent human discussions were available during acceptance. The generated review therefore reported no relevant community messages; this run proves the integration and delivery, not lead generation or reply quality on a populated channel.
- Local and cloud offline suites passed 10 tests. The daily cloud schedule is 12:00 Asia/Shanghai; GitHub delays are possible. Keep the old desktop timer paused to avoid duplicates.
