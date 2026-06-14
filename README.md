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
- Pick the correct word from 4 options
- Correct answer fills in the blank (green), translation shown below
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

**40 grammar cards** across 4 topics (all A1):

| Topic | Count |
|-------|------:|
| Conjunctions 🔗 | 10 |
| Prepositions 📍 | 14 |
| Modals ⚙️ | 8 |
| Verbs (sein/haben) 🔄 | 8 |

---

## Architecture

```
Telegram Mini App (GitHub Pages)
        │
        │ POST /api/card-result
        │ POST /api/session
        │ GET  /api/weak-words/:id
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
{ "userId":"283951220","word":"Hund","article":"der","chosen":"die","correct":false,"sessionId":"uuid" }
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
# Start bot via pm2
pm2 start bot.js --name flashcards-bot
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
- [x] Grammar mode (fill-in-the-blank, 40 cards)
- [ ] More grammar cards (negation, accusative, adjective endings)
- [ ] A2/B1 grammar cards
- [ ] Translation mode (German → English multiple choice)
- [ ] Weekly progress report from bot
