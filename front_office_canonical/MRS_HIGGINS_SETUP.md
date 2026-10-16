# Mrs. Higgins — Setup & Launch Guide

## What You Have
A fully working passive income pipeline. She routes your SaaS packages to Fiverr, Upwork, and Nostr — writes the copy, creates Lightning invoices, tracks payments, and sends you Telegram alerts for anything unpaid.

## File Structure
Drop everything into one folder:

```
moto-2024-sd-r26/
├── mrs_higgins.sh        ← the main pipeline runner
├── front_desk_lady.py    ← routes packages + creates invoices
├── bookkeeper.py         ← checks which invoices got paid
├── the_closer.py         ← Telegram alerts for unpaid invoices
├── copywriter.py         ← AI writes Fiverr/Upwork/Nostr copy
├── scout.py              ← (disabled — replace with manual leads)
├── briefing.py           ← run this first each morning
├── front_desk_config.json  ← your API keys go here
└── saas_packages/
    ├── askhole.json
    ├── hotseat.json
    ├── vertical_ai.json
    └── business_scout.json
```

## Step 1 — Create front_desk_config.json
```json
{
  "lightning_account_id": "your@getalby.com",
  "voltage_api_key": "your_voltage_key_here"
}
```

## Step 2 — Set Environment Variables
```bash
export LNBITS_URL="https://your-lnbits-instance.com"
export LNBITS_INVOICE_KEY="your_lnbits_invoice_key"
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export TELEGRAM_CHAT_ID="your_telegram_chat_id"
```

### Getting your Telegram bot:
1. Open Telegram → search @BotFather
2. Send /newbot — follow prompts
3. Copy the token it gives you → TELEGRAM_BOT_TOKEN
4. Start a chat with your bot, then visit:
   https://api.telegram.org/bot{YOUR_TOKEN}/getUpdates
5. Copy the chat id from the response → TELEGRAM_CHAT_ID

## Step 3 — Test with Dry Run
```bash
bash mrs_higgins.sh --dry-run
```
This runs the full pipeline without creating real invoices or sending messages. Check the logs/ folder to see what happened.

## Step 4 — Run the Morning Briefing
```bash
python briefing.py
```
She'll tell you exactly what needs your attention.

## Step 5 — Go Live
```bash
bash mrs_higgins.sh
```

## Step 6 — Run for a Specific Platform Only
```bash
bash mrs_higgins.sh --platform Fiverr
bash mrs_higgins.sh --platform Upwork
bash mrs_higgins.sh --platform Nostr
```

## Note on Scout
scout.py is disabled because Upwork and Fiverr block scrapers.
Replace it with a simple manual leads file, or skip it — the rest of the pipeline works fine without it.

## What Gets Generated
- `front_desk_routing_log.json` — every package routed, every invoice
- `income_summary.json` — paid vs pending vs untracked
- `closer_sent.json` — which Telegram alerts were fired
- `copy_output/` — AI-written Fiverr/Upwork/Nostr copy for every package
- `logs/` — timestamped run logs

---
Pipeline by BleakNarratives / Michael Talbert — Wellington, Kansas

---

## Kindred bus listener (2026-08-29)

`higgins_kindred_listener.py` — front-office sidecar that tails the RootBase
gossip ledger for `kindred` events (forge/chat/story/pitch/rescue/rumor).

- Run once to drain backlog: `python3 higgins_kindred_listener.py --once`
- Run continuously: `python3 higgins_kindred_listener.py`
- Events logged to `logs/kindred_events.jsonl`; resume position in
  `state/kindred_listener_position` (ledger rotation handled).
