# 🇩🇪 German Articles Flashcards

A Telegram Mini App for learning German articles (der / die / das) with spaced repetition and progress tracking.

**Live app:** [t.me/JugglingBallsBot/German](https://t.me/JugglingBallsBot/German)  
**Hosted at:** https://jugglingballsbot.github.io/german-flashcards/

---

## How It Works

1. A card shows a German noun + English translation
2. You tap **der**, **die**, or **das**
3. The card flips to reveal the correct answer
4. At the end of a round, you see which words you got wrong
5. Your results are sent to the backend — weak words appear more often next time (spaced repetition)

---

## Architecture

```
Telegram Mini App (GitHub Pages)
        │
        │ POST /api/card-result   (after each card)
        │ POST /api/session        (end of round)
        │ GET  /api/weak-words/:id (on load, to prioritize weak cards)
        ▼
  nginx (HTTPS, 46.225.99.97.nip.io)
        │
        ▼
  Node.js API (port 3456)
        │
        ▼
  SQLite (backend/data/flashcards.db)
        │
        ▼
  JugglingBallsBot (Telegram) ← can query stats anytime
```

---

## File Structure

```
german-flashcards/
├── index.html          # Mini App frontend (deployed to GitHub Pages)
├── README.md           # This file
├── flag.png            # BotFather app photo (640x360)
└── backend/
    ├── server.js       # Express API server
    ├── package.json
    └── data/
        └── flashcards.db   # SQLite database (auto-created)
```

---

## API Reference

### `POST /api/card-result`
Record a single card answer.

```json
{
  "userId": "283951220",
  "word": "Hund",
  "article": "der",
  "chosen": "die",
  "correct": false,
  "sessionId": "uuid-string"
}
```

### `POST /api/session`
Record end-of-session summary.

```json
{
  "userId": "283951220",
  "sessionId": "uuid-string",
  "correct": 12,
  "wrong": 3,
  "total": 15,
  "durationMs": 45000
}
```

### `GET /api/stats/:userId`
Returns progress summary for a user.

```json
{
  "userId": "283951220",
  "totalSessions": 8,
  "totalCards": 120,
  "totalCorrect": 98,
  "accuracy": 82,
  "weakWords": ["Fenster", "Schule"],
  "lastSession": "2026-06-12T20:00:00Z"
}
```

### `GET /api/weak-words/:userId`
Returns list of words the user struggles with (wrong > correct, or recently wrong).

```json
["Fenster", "Schule", "Kind"]
```

---

## Backend Setup (VPS)

### Requirements
- Node.js 18+
- nginx
- certbot (for HTTPS)

### Install & Run

```bash
cd /root/.openclaw/workspace/projects/german-flashcards/backend
npm install
node server.js   # or via systemd (see below)
```

### Systemd Service

Service file: `/etc/systemd/system/german-flashcards-api.service`

```bash
# Start
systemctl start german-flashcards-api

# Stop
systemctl stop german-flashcards-api

# Restart after code changes
systemctl restart german-flashcards-api

# View logs
journalctl -u german-flashcards-api -f
```

### Nginx Config

Located at `/etc/nginx/sites-available/german-flashcards-api`

Proxies `https://46.225.99.97.nip.io/api/*` → `http://localhost:3456/`

```bash
# Test config
nginx -t

# Reload
systemctl reload nginx
```

### SSL Certificate

Issued by Let's Encrypt for `46.225.99.97.nip.io` via certbot.

```bash
# Renew (auto via cron, or manually)
certbot renew
```

---

## Adding More Words

Edit the `CARDS` array in `index.html`:

```js
{ word: "Tür",    article: "die", en: "door" },
{ word: "Stuhl",  article: "der", en: "chair" },
{ word: "Bett",   article: "das", en: "bed" },
```

Then push to GitHub — Pages auto-deploys within ~30 seconds.

---

## Asking the Bot for Your Stats

In Telegram, just ask:
> "How am I doing on the German flashcards?"
> "Which German words do I keep getting wrong?"
> "Show me my flashcard progress"

The bot can query the API and give you a summary.

---

## Sharing

- **Direct link:** https://jugglingballsbot.github.io/german-flashcards/
- **Telegram link:** https://t.me/JugglingBallsBot/German
- **In a chat:** the bot can send an inline button that opens the app

---

## Roadmap

- [ ] More word categories (colors, numbers, body parts, food)
- [ ] Difficulty levels (A1 → B2)
- [ ] Weekly progress report from bot
- [ ] Leaderboard for groups
- [ ] Other languages (Spanish, Italian...)
