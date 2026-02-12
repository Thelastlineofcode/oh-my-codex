# Configure Notifications Skill

Set up notifications for session events.

## Supported Channels

| Channel | Setup Required |
|---------|----------------|
| Telegram | Bot token + Chat ID |
| Discord | Webhook URL |
| Slack | Webhook URL |
| File | Output path |

## Telegram Setup

### 1. Create Bot
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Follow prompts to get token

### 2. Get Chat ID
1. Message your bot
2. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Find `chat.id` in response

### 3. Configure
```bash
omx config-notify telegram \
  --token "123456:ABC-DEF" \
  --chat-id "-1001234567890"
```

## Discord Setup

### 1. Create Webhook
1. Server Settings → Integrations → Webhooks
2. Create new webhook
3. Copy URL

### 2. Configure
```bash
omx config-notify discord \
  --webhook "https://discord.com/api/webhooks/..."
```

## Configuration File

### ~/.codex/notifications.toml

```toml
[telegram]
enabled = true
token = "123456:ABC-DEF"
chat_id = "-1001234567890"
events = ["session_complete", "error", "milestone"]
tag_list = ["@username"]

[discord]
enabled = true
webhook = "https://discord.com/api/webhooks/..."
events = ["session_complete", "error"]
tag_list = ["@here", "123456789"]

[file]
enabled = false
path = "~/.codex/notifications.log"
```

## Event Types

| Event | When |
|-------|------|
| `session_start` | Orchestration begins |
| `session_complete` | Orchestration ends |
| `milestone` | Significant progress |
| `error` | Failure occurred |
| `warning` | Potential issue |

## Tag Options

### Telegram
- `@username` - Mention user

### Discord
- `@here` - Notify online members
- `@everyone` - Notify all
- `123456789` - User ID
- `role:987654321` - Role ID

## Usage

```
configure-notifications: set up Telegram alerts

configure-notifications: add Discord webhook

configure-notifications: enable file logging
```

## Message Format

```markdown
## 🚀 Session Complete

**Task:** Build auth system
**Duration:** 15m 23s
**Status:** ✅ Success
**Tokens:** 45,234 (~$0.15)

### Summary
- Implemented login/logout
- Added JWT validation
- Created user endpoints
```
