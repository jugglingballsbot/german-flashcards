# AGENTS.md — Handover for AI Agents

> Read this first if you're picking up work on the German Flashcards Mini App.

## TL;DR — What This Is

A **Telegram Mini App** for learning German articles (der/die/das) and grammar (fill-in-the-blank). Single-page HTML + Express/SQLite backend + Telegram bot.

- **Frontend (Mini App):** `index.html` → hosted on GitHub Pages → https://jugglingballsbot.github.io/german-flashcards/
- **Backend API:** `backend/server.js` (Express + better-sqlite3) → port 3456 → proxied to `https://46.225.99.97.nip.io`
- **Bot:** `backend/bot.js` → separate pm2 process `flashcards-bot`
- **Telegram entry point:** `t.me/JugglingBallsBot/German` (BotFather Mini App)

## Server Layout

All work lives on this VPS (Hetzner, Ubuntu).

```
/root/.openclaw/workspace/projects/german-flashcards/
├── index.html              # The entire Mini App frontend
├── README.md               # User-facing docs
├── AGENTS.md               # This file (handover)
├── flag.png                # BotFather app icon
├── backend/
│   ├── server.js           # Express API (runs on port 3456)
│   ├── bot.js              # Telegram bot (pm2)
│   ├── .env                # BOT_TOKEN + MINI_APP_URL (NOT committed)
│   ├── package.json
│   └── data/
│       └── flashcards.db   # SQLite (auto-created)
└── scripts/
    ├── new_words.py        # Generate word entries from raw lists
    ├── recategorize.py     # Re-categorize all CARDS
    └── add_grammar.py      # Reference script used to build Grammar mode
```

## Running Services

Check with:
```bash
# API (systemd-owned; do not also run node server.js manually)
systemctl status german-flashcards-api.service --no-pager -l
curl -s http://127.0.0.1:3456/api/health   # should return {"ok":true,...}
curl -s https://46.225.99.97.nip.io/api/health   # public via nginx

# Bot (separate pm2 process)
pm2 status flashcards-bot
pm2 logs flashcards-bot --lines 20 --nostream
```

If API not running:
```bash
systemctl restart german-flashcards-api.service
```

If bot crashed:
```bash
pm2 restart flashcards-bot --update-env
```

## Credentials

`backend/.env` already exists on server and is **not committed**. It contains the Telegram bot token and Mini App URL. Do not paste the token into chat/logs; read it from the environment file only when operating the service.

The bot token is shared with **JugglingBallsBot** (the OpenClaw assistant bot). This is intentional — Antonio wants one bot to handle both AI assistance and Mini App launching.

## Deployment Flow

```
Edit index.html → commit → push → GitHub Pages auto-deploys in ~30s
Edit backend/server.js → systemctl restart german-flashcards-api.service
Edit backend/bot.js → pm2 restart flashcards-bot --update-env
```

GitHub remote: `https://github.com/jugglingballsbot/german-flashcards.git` (branch: `main`)

## Current Feature State

### Game Modes

**Articles 🏷️** — guess der/die/das for German nouns.
- 211 cards across 9 categories: `animals`, `food`, `home`, `office`, `city`, `leisure`, `people`, `colors`, `numbers`
- Difficulty: A1 / A2 / B1
- Filters: Mode (All / Weak Words), Category, Difficulty
- Practice All builds a 30-card set when possible: up to 10 per-user weak words first, then 20 fresh non-duplicate practice words
- Weak Words is per-user via Telegram `initDataUnsafe.user` / `/api/weak-words/:userId`
- Cards stored in `CARDS = [...]` array in `index.html` (~lines 640+)

**Grammar ✏️** — fill-in-the-blank sentences.
- 40 cards across 4 topics: `conjunctions`, `prepositions`, `modals`, `verbs` (sein/haben)
- All A1 currently (A2/B1 ready to be added)
- 4 multiple-choice options per card
- Filters: Topic + Difficulty (A1 / A2 / B1) — same UX as articles
- Cards stored in `GRAMMAR_CARDS = [...]` array in `index.html` (~lines 875+)

### Cross-Mode Features

- **Daily goal** (default 20) — both modes count toward it; saved per-user via API
- **Streak** (consecutive days hitting goal) — stored in localStorage
- **Spaced repetition** — article Practice All starts with up to 10 per-user weak words, then 20 fresh practice words (`/api/weak-words/:userId`)
- **Grammar result logging** — grammar answers are stored with `mode='grammar'`; `/api/weak-grammar/:userId` is available for future review UI
- **Keyboard shortcuts** — `1/2/3` for articles, `1/2/3/4` for grammar
- **Haptic feedback** — `Telegram.WebApp.HapticFeedback.notificationOccurred`
- **Audio feedback** — `playTone()` using Web Audio API
- **Telegram integration** — uses `initDataUnsafe.user` to identify the user

### NO Leaderboard

Removed 2026-06-14. Don't re-add unless explicitly asked. The `group_members` table was dropped from the DB and all `/api/group/*` endpoints removed.

## Code Patterns

### HTML structure of `index.html`

Three main `<div class="screen">` sections:
- `#startScreen` — menu with filters, daily goal, start button
- `#gameScreen` — both Article card AND Grammar card live here (toggled via display:none)
  - `#cardScene` + `#answers` + `#kbHint` + `#scoreRow` — article mode UI
  - `#grammarCard` — grammar mode UI
- `#doneScreen` — end-of-round summary (currently only shown after article rounds)

Switching modes is done in `selectPill()` when `g === 'gamemode'`:
- Show/hide `#articleFilters` and `#grammarCatSection`
- The article/grammar elements inside `#gameScreen` are toggled in `startGame()` / `startGrammarGame()` / `goMenu()`

### JS state (global)

```js
// Article state
let deck, idx, correct, wrong, answered, lastCards
let dailyGoal, dailyAnsweredToday, savedDeckWords, savedDeckIdx
let selectedMode, selectedCat, selectedDiff

// Grammar state
let grammarDeck, grammarIdx, grammarAnswered
let grammarSessionCorrect, grammarSessionWrong
let selectedGameMode  // 'articles' | 'grammar'
let selectedGrammarCat
```

### Backend API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET    | `/api/health` | Health check |
| POST   | `/api/card-result` | Log one card answer (article or grammar mode) |
| POST   | `/api/session` | Log end-of-round summary |
| GET    | `/api/stats/:userId` | All-time stats |
| GET    | `/api/weak-words/:userId` | Up to 10 per-user article review words |
| GET    | `/api/weak-grammar/:userId` | Grammar prompts user struggles with |
| GET    | `/api/daily/:userId` | Today's progress + goal |
| POST   | `/api/daily/:userId` | Upsert today's progress + goal |

**Note:** Grammar mode logs per-card results with `mode='grammar'`. The backend has `/api/weak-grammar/:userId`; the frontend still needs a dedicated weak-grammar review filter if Antonio wants that surfaced in the UI.

### DB schema

Tables in `backend/data/flashcards.db`:
- `sessions` — round summaries (userId, correct, wrong, total, durationMs)
- `card_results` — per-card answers (userId, word, article, chosen, correct)
- `user_settings` — per-user daily goal
- `daily_progress` — daily counter + resumable deck state

## How To Add Things

### Add new article-mode words

Edit `CARDS` array in `index.html`. Format:
```js
{ word:'Bett', article:'das', en:'bed', cat:'home', diff:'A1' },
```
Then commit + push. Or use `scripts/new_words.py` for bulk imports.

### Add new grammar cards

Edit `GRAMMAR_CARDS` array. Format:
```js
{ sentence:'Ich gehe ___ Hause.',
  answer:'nach',
  options:['nach','zu','bei','von'],
  topic:'prepositions',
  diff:'A1',
  translation:'I am going home.' },
```
- `options` must include `answer`
- Use exactly `___` (three underscores) for the blank
- Keep options thematically related (don't mix conjunctions and verbs as distractors)
- Order in `options` doesn't matter — they're shuffled at render time

### Add a new category

1. Add a pill to the `<div class="pill-row">` for `data-group="cat"` in `index.html`
2. Add cards with `cat:'newcategory'`
3. Optionally update `recategorize.py` if backfilling existing cards

### Add a new grammar topic

1. Add a pill in `#grammarCatSection` with `data-group="gcat"`
2. Add cards with `topic:'newtopic'`

## Conventions (READ THIS)

1. **After every change to this project: update README.md in the repo + push, and update the user's memory files** (`/root/.openclaw/workspace/memory/YYYY-MM-DD.md` + `MEMORY.md`).
2. **Don't introduce dependencies casually.** The frontend is intentionally a single HTML file with no build step. Backend uses minimal deps (express, cors, better-sqlite3, dotenv, node-telegram-bot-api). Keep it that way.
3. **Don't break the article-game flow.** The original game (der/die/das) is the core feature. Grammar mode was added without disrupting it.
4. **No tracking pixels, analytics, or external CDNs** beyond `telegram-web-app.js`.
5. **Keep the deployed page small** — `index.html` is ~50KB, that's fine. Adding 500KB of card data would be a problem.
6. **Commits should be small and focused** with descriptive messages.

## Gotchas

- **`initDataUnsafe.chat` is only set when the app is opened via an inline button sent by the bot inside a group.** Not from DM, not from `t.me/...` direct link. This was the original reason for the leaderboard bug.
- **Don't use the `everyday` category** — it was split into 5 sub-categories on 2026-06-14.
- **GitHub Pages cache** can take 30–120s to refresh; do a hard reload (close + reopen the Mini App) to verify changes.
- **Telegram Mini App caches aggressively.** Users may need to close the app from Telegram's Mini App list (`Settings → Privacy and Security → Active Sessions → Mini Apps` or similar).
- **Em-dash characters in code comments** — the file uses U+2500 (`─`) extensively in section dividers; exact-match string replacement tools may struggle. Use Python scripts for bulk edits when this trips you up.
- **The API server is NOT under pm2** — only the bot is. If you reboot the server, you need to manually restart `node server.js`. (TODO: move to systemd.)

## Recent Changes Log

See `README.md` → Changelog section.

## Owner & Context

Project owner: **Antonio Marsella** (`@marsantonio`, Telegram ID `283951220`).
- He's an Italian native learning German (A1 → B1 level).
- He prefers concise replies and direct action over questions.
- He always wants the README + memory updated after changes.
- He uses the app himself daily to track progress.

## When In Doubt

- Check `README.md` for feature docs
- Check `memory/2026-06-14.md` in the OpenClaw workspace for history of decisions made on this project
- Test changes by hitting `https://46.225.99.97.nip.io/api/health` and opening `t.me/JugglingBallsBot/German`
- Don't be clever — the codebase favors simplicity over abstraction
