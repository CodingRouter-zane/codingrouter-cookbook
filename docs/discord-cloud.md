# Discord cloud operations

Runs on GitHub-hosted Ubuntu at **12:00 Asia/Shanghai** (04:00 UTC); GitHub may delay scheduled jobs. No personal-account token or self-bot is used. This is daily polling, not an always-online community moderator.

## Current status

Deployment infrastructure is prepared. Bot credentials, source channels and a private review destination have not yet been supplied or verified. Scheduled operations are gated by `DISCORD_CLOUD_ENABLED`; leave it unset until runtime verification. Passing offline tests is not live Discord verification.

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
    {"guild_id": "REPLACE_WITH_EXTERNAL_SERVER_ID", "channel_id": "REPLACE_WITH_EXTERNAL_CHANNEL_ID", "kind": "external"}
  ]
}
```

Set approval flags only after approving the specific sources, the CodingRouter API as processor, and private-review delivery. Selected recent message text and source links are sent to CodingRouter using the existing `CODINGROUTER_API_KEY`, model 6.1-Sol (uniquely resolved via `/v1/models`). Names/attachments are omitted and common mentions/email/key patterns are filtered; this is not a guarantee of anonymization. Do not configure channels containing customer secrets or restricted information. Raw messages/drafts are never uploaded as GitHub artifacts, summaries or commits. `store:false` requests no Responses storage, but is not a provider retention guarantee.

External servers require their administrators to allow the Bot. If unavailable, keep those communities in the manual/draft-assisted workflow; a server invite link alone does not grant Bot access.

## Verify and activate

Run this workflow manually with `check_only=true` to verify Bot authentication and source reads. No model call or delivery occurs. Then run with `check_only=false` for one real model draft delivered only to the approved private review channel. Confirm its content and destination. Afterwards set Actions variable `DISCORD_CLOUD_ENABLED=true` and pause the existing local `codingrouter-discord` automation to avoid duplicates.

No community posting, member DMs, join operations or automatic public replies are implemented. A human reviews drafts and separately authorizes publication. The workflow cannot execute commands supplied by Discord messages. Source reads cover up to 100 recent messages per channel in a 24-hour window (up to 6 channels, at most 3 external, at most 20 usable messages per channel); high-volume channels may exceed coverage. Daily markers/nonce deduplicate review delivery, not all future reply recommendations. A review can remain a draft for an already addressed conversation.

GitHub/X schedules remain separate. Public context uses published titles and URLs from `docs/content-index.json`; it does not claim to have read article bodies. Model and GitHub usage follow their respective account limits. No performance or SLA guarantee is implied.
