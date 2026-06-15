# 🇩🇪 German Articles Flashcards

A Telegram Mini App for learning German articles (der / die / das) and grammar (fill-in-the-blank) with spaced repetition and progress tracking.

**Live app:** [t.me/JugglingBallsBot/German](https://t.me/JugglingBallsBot/German)  
**Hosted at:** https://jugglingballsbot.github.io/german-flashcards/

---

## Game Modes

### Articles 🏷️
- A card shows a German noun + English translation
- Tap **der**, **die**, or **das**
- Card flips to reveal the correct article
- Wrong answers are tracked for spaced repetition

### Grammar ✏️ (fill-in-the-blank)
- A sentence is shown with a `___` blank
- Pick the correct word from 4 options (or press **1–4** on keyboard)
- Correct answer fills in the blank (green), translation shown below
- Per-card grammar answers are logged for future weak-grammar review
- A deliberate **Next** step gives you time to read the correction
- Live session counter (✅ / ❌) in the header
- Haptic + audio feedback on each answer
- Correct answers count toward your **daily goal**
- Topics: Conjunctions · Prepositions · Modals · Verbs (sein/haben)

---

## Word Library

**211 article cards** across 9 categories (all A1–B1):

| Category | Count |
|----------|------:|
| Food 🍎 | 67 |
| Office 💼 | 31 |
| City 🏛️ | 26 |
| Home 🏠 | 23 |
| Leisure ⚽ | 17 |
| Animals 🐾 | 15 |
| People 👥 | 12 |
| Colors 🎨 | 10 |
| Numbers 🔢 | 10 |

**40 grammar cards** across 4 topics (all A1, A2/B1 ready to be added):

| Topic | A1 |
|-------|---:|
| Conjunctions 🔗 | 10 |
| Prepositions 📍 | 14 |
| Modals ⚙️ | 8 |
| Verbs (sein/haben) 🔄 | 8 |

Grammar mode has both **Topic** and **Difficulty** filters (A1 / A2 / B1).

---

## Architecture

```
Telegram Mini App (GitHub Pages)
        │
        │ POST /api/card-result
        │ POST /api/session
        │ GET  /api/weak-words/:id
        │ GET  /api/weak-grammar/:id
        │ GET  /api/daily/:id
        │ POST /api/daily/:id
        ▼
  nginx (HTTPS, 46.225.99.97.nip.io)
        │
        ▼
  Node.js API (port 3456, server.js)
        │
        ▼
  SQLite (backend/data/flashcards.db)

  JugglingBallsBot (bot.js, pm2: flashcards-bot)
  → responds to /flashcards in Telegram groups
  → sends inline button that opens the Mini App
```

---

## File Structure

```
german-flashcards/
├── index.html              # Mini App frontend (deployed to GitHub Pages)
├── README.md               # This file
├── flag.png                # BotFather app photo
├── backend/
│   ├── server.js           # Express API server
│   ├── bot.js              # Telegram bot (pm2: flashcards-bot)
│   ├── .env                # BOT_TOKEN + MINI_APP_URL (not committed)
│   ├── package.json
│   └── data/
│       └── flashcards.db   # SQLite database (auto-created)
└── scripts/
    ├── new_words.py        # Script to generate word entries from raw lists
    ├── recategorize.py     # Script to re-categorize all cards
    └── add_grammar.py      # Script that added Grammar mode
```

---

## API Reference

### `POST /api/card-result`
Record a single card answer.
```json
{ "userId":"283951220","mode":"articles","word":"Hund","article":"der","chosen":"die","correct":false,"sessionId":"uuid" }
```

### `POST /api/session`
Record end-of-session summary.
```json
{ "userId":"283951220","sessionId":"uuid","correct":12,"wrong":3,"total":15,"durationMs":45000 }
```

### `GET /api/stats/:userId`
Returns all-time progress summary.

### `GET /api/weak-words/:userId`
Returns words the user struggles with (wrong > correct).

### `GET /api/weak-grammar/:userId`
Returns grammar prompts the user struggles with (wrong >= correct).

### `GET /api/daily/:userId`
Returns today's progress + daily goal + resumable deck state.

### `POST /api/daily/:userId`
Upserts today's progress. Optionally updates goal.
```json
{ "answeredToday":12,"goal":20,"deckWords":[...],"deckCurrentIdx":12 }
```

---

## Backend Setup (VPS)

```bash
cd /root/.openclaw/workspace/projects/german-flashcards/backend
npm install
# Start API (direct)
node server.js
# Start bot separately via pm2
pm2 start bot.js --name flashcards-bot --update-env
pm2 save
```

API runs at `http://127.0.0.1:3456`, proxied by nginx to `https://46.225.99.97.nip.io`.

---

## Adding More Words

Edit the `CARDS` array in `index.html` following the existing pattern, or use `scripts/new_words.py` to generate entries from a word list. Then push — GitHub Pages auto-deploys in ~30s.

Categories: `animals` · `food` · `home` · `office` · `city` · `leisure` · `people` · `colors` · `numbers`

## Adding Grammar Cards

Add entries to the `GRAMMAR_CARDS` array in `index.html`:
```js
{ sentence:'Ich gehe ___ Hause.',
  answer:'nach',
  options:['nach','zu','bei','von'],
  topic:'prepositions',
  diff:'A1',
  translation:'I am going home.' }
```
Topics: `conjunctions` · `prepositions` · `modals` · `verbs`

---

## Roadmap

- [x] Article guessing game (der/die/das)
- [x] 9 word categories (211 cards, A1–B1)
- [x] Daily goal + streak tracking
- [x] Spaced repetition (weak words surfaced more often)
- [x] Grammar mode (fill-in-the-blank, 40 cards, 4 topics)
- [x] Keyboard support (1–4 for grammar, 1–3 for articles)
- [x] Haptic + audio feedback in both modes
- [ ] More grammar cards (negation, accusative, adjective endings)
- [ ] A2/B1 grammar cards
- [ ] Translation mode (German → English multiple choice)
- [ ] Weekly progress report from bot
- [x] Grammar per-card tracking
- [x] Card-data validation tests
- [x] Separate API and bot entrypoints
- [ ] Grammar weak-card review mode
- [ ] Grammar mode session summary screen

---

## Changelog

### 2026-06-15
- Split API and Telegram bot entrypoints so `server.js` no longer starts Telegram polling as a side effect
- Added `npm run bot` for the bot process
- Added grammar per-card logging through `/api/card-result` with `mode: "grammar"`
- Added `/api/weak-grammar/:userId` as a backend hook for future grammar SRS/review mode
- Changed daily progress date calculation to Europe/Berlin instead of UTC
- Changed grammar practice flow from auto-advance to answer → read correction → **Next**
- Added backend tests for architecture split and flashcard data validation

### 2026-06-14
- Added Grammar mode (fill-in-the-blank, 40 cards)
- Added 141 new A1 words; total now 211 cards
- Expanded categories: split `everyday` into `home`, `office`, `city`, `leisure`, `people`
- Removed leaderboard
- Added Telegram bot (`bot.js`) for `/flashcards` command in groups
- Polished grammar mode: keyboard nav, haptics, audio, session counter
