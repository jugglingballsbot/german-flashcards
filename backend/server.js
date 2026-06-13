const express = require('express');
const cors = require('cors');
const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3456;
const DB_PATH = path.join(__dirname, 'data', 'flashcards.db');

fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });

const db = new Database(DB_PATH);
db.exec(`
  CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    userId     TEXT    NOT NULL,
    sessionId  TEXT    NOT NULL,
    correct    INTEGER,
    wrong      INTEGER,
    total      INTEGER,
    durationMs INTEGER,
    createdAt  TEXT    DEFAULT (datetime('now'))
  );

  CREATE TABLE IF NOT EXISTS card_results (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    userId    TEXT    NOT NULL,
    word      TEXT    NOT NULL,
    article   TEXT    NOT NULL,
    chosen    TEXT    NOT NULL,
    correct   INTEGER NOT NULL,
    sessionId TEXT    NOT NULL,
    createdAt TEXT    DEFAULT (datetime('now'))
  );

  -- Per-user settings (goal etc.)
  CREATE TABLE IF NOT EXISTS user_settings (
    userId    TEXT    PRIMARY KEY,
    dailyGoal INTEGER NOT NULL DEFAULT 20,
    updatedAt TEXT    DEFAULT (datetime('now'))
  );

  -- One row per (user, date) — stores daily progress + resumable deck state
  CREATE TABLE IF NOT EXISTS daily_progress (
    userId        TEXT    NOT NULL,
    date          TEXT    NOT NULL,   -- YYYY-MM-DD
    answeredToday INTEGER NOT NULL DEFAULT 0,
    deckWords     TEXT,               -- JSON array of word strings (compact)
    deckCurrentIdx INTEGER NOT NULL DEFAULT 0,
    deckFilters   TEXT,               -- JSON {mode, cat, diff}
    updatedAt     TEXT    DEFAULT (datetime('now')),
    PRIMARY KEY (userId, date)
  );

  CREATE INDEX IF NOT EXISTS idx_cr_userId  ON card_results(userId);
  CREATE INDEX IF NOT EXISTS idx_ses_userId ON sessions(userId);
  CREATE INDEX IF NOT EXISTS idx_dp_userId  ON daily_progress(userId);
`);

app.use(cors());
app.use(express.json());

// ── Health ────────────────────────────────────────────────────────────────
app.get('/api/health', (req, res) => {
  res.json({ ok: true, ts: new Date().toISOString() });
});

// ── Card result ───────────────────────────────────────────────────────────
app.post('/api/card-result', (req, res) => {
  const { userId = 'anonymous', word, article, chosen, correct, sessionId } = req.body;
  if (!word || !article || !chosen || sessionId === undefined)
    return res.status(400).json({ error: 'Missing fields' });
  db.prepare(`
    INSERT INTO card_results (userId, word, article, chosen, correct, sessionId)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(userId, word, article, chosen, correct ? 1 : 0, sessionId);
  res.json({ ok: true });
});

// ── Session summary ───────────────────────────────────────────────────────
app.post('/api/session', (req, res) => {
  const { userId = 'anonymous', sessionId, correct, wrong, total, durationMs } = req.body;
  if (!sessionId) return res.status(400).json({ error: 'Missing sessionId' });
  db.prepare(`
    INSERT INTO sessions (userId, sessionId, correct, wrong, total, durationMs)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(userId, sessionId, correct, wrong, total, durationMs);
  res.json({ ok: true });
});

// ── All-time stats ────────────────────────────────────────────────────────
app.get('/api/stats/:userId', (req, res) => {
  const { userId } = req.params;
  const s = db.prepare(`
    SELECT COUNT(*)       AS totalSessions,
           SUM(correct)   AS totalCorrect,
           SUM(wrong)     AS totalWrong,
           SUM(total)     AS totalCards,
           MAX(createdAt) AS lastSession
    FROM sessions WHERE userId = ?
  `).get(userId);
  const accuracy = s.totalCards > 0
    ? Math.round(s.totalCorrect / s.totalCards * 100) : 0;
  const weakWords = db.prepare(`
    SELECT word
    FROM card_results
    WHERE userId = ?
    GROUP BY word
    HAVING SUM(1 - correct) > SUM(correct)
       OR  (SUM(correct) = 0 AND COUNT(*) > 0)
    ORDER BY (SUM(1 - correct) - SUM(correct)) DESC
    LIMIT 10
  `).all(userId).map(r => r.word);
  res.json({
    userId,
    totalSessions: s.totalSessions || 0,
    totalCards:    s.totalCards    || 0,
    totalCorrect:  s.totalCorrect  || 0,
    totalWrong:    s.totalWrong    || 0,
    accuracy,
    weakWords,
    lastSession: s.lastSession || null
  });
});

// ── Weak words ────────────────────────────────────────────────────────────
app.get('/api/weak-words/:userId', (req, res) => {
  const { userId } = req.params;
  const rows = db.prepare(`
    SELECT word,
           SUM(correct)       AS rights,
           SUM(1 - correct)   AS wrongs,
           MAX(createdAt)     AS lastSeen
    FROM card_results WHERE userId = ?
    GROUP BY word
    HAVING wrongs >= rights
    ORDER BY (wrongs - rights) DESC, lastSeen ASC
    LIMIT 8
  `).all(userId);
  res.json(rows.map(r => r.word));
});

// ── Daily progress (GET) ──────────────────────────────────────────────────
// Returns goal + today's answered count + resumable deck state
app.get('/api/daily/:userId', (req, res) => {
  const { userId } = req.params;
  const today = new Date().toISOString().slice(0, 10);

  const settings = db.prepare(
    'SELECT dailyGoal FROM user_settings WHERE userId = ?'
  ).get(userId);
  const goal = settings?.dailyGoal ?? 20;

  const prog = db.prepare(
    'SELECT * FROM daily_progress WHERE userId = ? AND date = ?'
  ).get(userId, today);

  res.json({
    goal,
    date:          today,
    answeredToday: prog?.answeredToday  ?? 0,
    deckWords:     prog?.deckWords      ? JSON.parse(prog.deckWords)    : null,
    deckCurrentIdx:prog?.deckCurrentIdx ?? 0,
    deckFilters:   prog?.deckFilters    ? JSON.parse(prog.deckFilters)  : null,
    goalReached:   (prog?.answeredToday ?? 0) >= goal
  });
});

// ── Daily progress (POST) ─────────────────────────────────────────────────
// Upserts today's progress; optionally updates goal setting.
// Body: { answeredToday, deckWords?, deckCurrentIdx?, deckFilters?, goal? }
app.post('/api/daily/:userId', (req, res) => {
  const { userId } = req.params;
  const today = new Date().toISOString().slice(0, 10);
  const { answeredToday, deckWords, deckCurrentIdx, deckFilters, goal } = req.body;

  if (Number.isInteger(goal) && goal >= 1) {
    db.prepare(`
      INSERT INTO user_settings (userId, dailyGoal, updatedAt)
      VALUES (?, ?, datetime('now'))
      ON CONFLICT(userId) DO UPDATE SET
        dailyGoal = excluded.dailyGoal,
        updatedAt = excluded.updatedAt
    `).run(userId, goal);
  }

  db.prepare(`
    INSERT INTO daily_progress
      (userId, date, answeredToday, deckWords, deckCurrentIdx, deckFilters, updatedAt)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    ON CONFLICT(userId, date) DO UPDATE SET
      answeredToday  = excluded.answeredToday,
      deckWords      = excluded.deckWords,
      deckCurrentIdx = excluded.deckCurrentIdx,
      deckFilters    = excluded.deckFilters,
      updatedAt      = excluded.updatedAt
  `).run(
    userId, today,
    answeredToday  ?? 0,
    deckWords      ? JSON.stringify(deckWords)   : null,
    deckCurrentIdx ?? 0,
    deckFilters    ? JSON.stringify(deckFilters) : null
  );

  res.json({ ok: true });
});

app.listen(PORT, '127.0.0.1', () => {
  console.log(`German flashcards API running on port ${PORT}`);
  console.log(`DB: ${DB_PATH}`);
});
