#!/usr/bin/env python3
"""Add Grammar mode (fill-in-the-blank) to German Flashcards app."""
from pathlib import Path
import re

HTML = Path(__file__).parent.parent / 'index.html'
src = HTML.read_text()

# ────────────────────────────────────────────────────────────────────────────
# 1.  CSS additions
# ────────────────────────────────────────────────────────────────────────────
CSS_ADDITION = """
  /* ── Grammar mode ── */
  .gamemode-row { margin-bottom: 18px; }

  .topic-badge {
    display: inline-block; padding: 3px 10px;
    background: rgba(251,191,36,0.15); color: #fbbf24;
    border: 1px solid rgba(251,191,36,0.3);
    border-radius: 20px; font-size: 0.72rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.6px;
    margin-bottom: 10px;
  }

  .grammar-sentence {
    font-size: 1.25rem; font-weight: 600; text-align: center;
    line-height: 1.55; margin: 8px 0 6px;
  }
  .grammar-blank {
    display: inline-block; min-width: 60px;
    border-bottom: 2px solid #5b9cf6;
    color: #5b9cf6; font-weight: 800;
  }
  .grammar-translation {
    font-size: 0.8rem; opacity: 0.45; text-align: center;
    margin-top: 6px; min-height: 1.2em;
    transition: opacity 0.3s;
  }

  .btn-grammar-opts {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 10px; width: 100%; margin-top: 16px;
  }
  .btn-grammar-opt {
    padding: 13px 8px;
    background: rgba(255,255,255,0.06);
    border: 1.5px solid rgba(255,255,255,0.12);
    border-radius: 14px; font-size: 1rem; font-weight: 600;
    color: var(--tg-theme-text-color, #eee);
    cursor: pointer; transition: opacity 0.2s;
  }
  .btn-grammar-opt:active { opacity: 0.7; }
  .btn-grammar-opt.correct { background: rgba(74,222,128,0.3)  !important; border-color: #4ade80 !important; color: #4ade80 !important; }
  .btn-grammar-opt.wrong   { background: rgba(248,113,113,0.3) !important; border-color: #f87171 !important; color: #f87171 !important; opacity: 0.7; }
  .btn-grammar-opt:disabled { cursor: default; }
"""

# Insert before closing </style>
src = src.replace('\n</style>', CSS_ADDITION + '\n</style>', 1)

# ────────────────────────────────────────────────────────────────────────────
# 2.  HTML: game-mode selector before daily goal on start screen
# ────────────────────────────────────────────────────────────────────────────
GAMEMODE_HTML = """
  <!-- Game mode selector -->
  <div class="section-label gamemode-row">Game Mode</div>
  <div class="pill-row" style="margin-bottom:18px">
    <button class="pill active" data-group="gamemode" data-val="articles" onclick="selectPill(this)">Articles 🏷️</button>
    <button class="pill"        data-group="gamemode" data-val="grammar"  onclick="selectPill(this)">Grammar ✏️</button>
  </div>

"""
# Insert right before <!-- Daily goal progress -->
src = src.replace('  <!-- Daily goal progress -->', GAMEMODE_HTML + '  <!-- Daily goal progress -->', 1)

# ────────────────────────────────────────────────────────────────────────────
# 3.  HTML: grammar category pill row after article category row
# ────────────────────────────────────────────────────────────────────────────
GRAMMAR_CAT_HTML = """
  <!-- Grammar categories (visible in grammar mode only) -->
  <div id="grammarCatSection" style="display:none">
    <div class="section-label">Topic</div>
    <div class="pill-row">
      <button class="pill active" data-group="gcat" data-val="all"          onclick="selectPill(this)">All</button>
      <button class="pill"        data-group="gcat" data-val="conjunctions" onclick="selectPill(this)">Conjunctions 🔗</button>
      <button class="pill"        data-group="gcat" data-val="prepositions" onclick="selectPill(this)">Prepositions 📍</button>
      <button class="pill"        data-group="gcat" data-val="modals"       onclick="selectPill(this)">Modals ⚙️</button>
      <button class="pill"        data-group="gcat" data-val="verbs"        onclick="selectPill(this)">Verbs 🔄</button>
    </div>
  </div>
"""
# Insert after the difficulty section (before the Start button)
src = src.replace('  <button class="btn-start" id="startBtn"', GRAMMAR_CAT_HTML + '\n  <button class="btn-start" id="startBtn"', 1)

# ────────────────────────────────────────────────────────────────────────────
# 4.  HTML: grammar card elements inside game screen
# ────────────────────────────────────────────────────────────────────────────
GRAMMAR_GAME_HTML = """
    <!-- Grammar fill-in-the-blank (visible in grammar mode) -->
    <div id="grammarCard" style="display:none; width:100%; margin-top:8px">
      <div style="text-align:center; margin-bottom:4px">
        <span class="topic-badge" id="grammarTopic"></span>
      </div>
      <div class="grammar-sentence" id="grammarSentence"></div>
      <div class="grammar-translation" id="grammarTranslation"></div>
      <div class="btn-grammar-opts" id="grammarOpts"></div>
    </div>
"""
# Insert before the closing of game screen (before swipe-hint div)
src = src.replace('    <div class="swipe-hint">', GRAMMAR_GAME_HTML + '\n    <div class="swipe-hint" id="swipeHint">', 1)

# ────────────────────────────────────────────────────────────────────────────
# 5.  JS: data + logic
# ────────────────────────────────────────────────────────────────────────────
GRAMMAR_JS = r"""
// ── Grammar Cards Data ─────────────────────────────────────────────────────
const GRAMMAR_CARDS = [
  // Conjunctions
  { sentence:'Ich mag Kaffee ___ Tee.',                    answer:'und',     options:['und','aber','oder','weil'],    topic:'conjunctions', diff:'A1', translation:'I like coffee and tea.' },
  { sentence:'Das Buch ist gut, ___ sehr lang.',           answer:'aber',    options:['und','aber','oder','denn'],    topic:'conjunctions', diff:'A1', translation:'The book is good, but very long.' },
  { sentence:'Möchtest du Kaffee ___ Tee?',               answer:'oder',    options:['und','aber','oder','wenn'],    topic:'conjunctions', diff:'A1', translation:'Would you like coffee or tea?' },
  { sentence:'Ich lerne Deutsch, ___ es interessant ist.', answer:'weil',    options:['weil','denn','aber','oder'],   topic:'conjunctions', diff:'A1', translation:'I learn German because it is interesting.' },
  { sentence:'Ich bin müde, ___ ich habe nicht geschlafen.',answer:'denn',   options:['denn','weil','aber','und'],    topic:'conjunctions', diff:'A1', translation:'I am tired, for I did not sleep.' },
  { sentence:'Ich denke, ___ das richtig ist.',            answer:'dass',    options:['dass','weil','wenn','ob'],     topic:'conjunctions', diff:'A1', translation:'I think that this is correct.' },
  { sentence:'___ ich Zeit habe, lese ich ein Buch.',      answer:'Wenn',    options:['Wenn','Weil','Aber','Und'],    topic:'conjunctions', diff:'A1', translation:'When I have time, I read a book.' },
  { sentence:'Er ist klein, ___ sehr stark.',              answer:'aber',    options:['aber','oder','und','denn'],    topic:'conjunctions', diff:'A1', translation:'He is small but very strong.' },
  { sentence:'Ich wohne in Berlin ___ arbeite dort.',      answer:'und',     options:['und','oder','aber','wenn'],    topic:'conjunctions', diff:'A1', translation:'I live in Berlin and work there.' },
  { sentence:'Kommst du heute ___ morgen?',                answer:'oder',    options:['oder','und','aber','weil'],    topic:'conjunctions', diff:'A1', translation:'Are you coming today or tomorrow?' },

  // Prepositions
  { sentence:'Das Buch ist ___ der Tasche.',               answer:'in',      options:['in','an','auf','unter'],       topic:'prepositions', diff:'A1', translation:'The book is in the bag.' },
  { sentence:'Das Glas steht ___ dem Tisch.',              answer:'auf',     options:['auf','in','an','neben'],       topic:'prepositions', diff:'A1', translation:'The glass is on the table.' },
  { sentence:'Ich wohne ___ meinen Eltern.',               answer:'bei',     options:['bei','mit','von','zu'],        topic:'prepositions', diff:'A1', translation:'I live with my parents.' },
  { sentence:'Ich fahre ___ dem Bus.',                     answer:'mit',     options:['mit','bei','von','durch'],     topic:'prepositions', diff:'A1', translation:'I travel by bus.' },
  { sentence:'Wir fahren ___ Berlin.',                     answer:'nach',    options:['nach','zu','von','aus'],       topic:'prepositions', diff:'A1', translation:'We are going to Berlin.' },
  { sentence:'Er kommt ___ Deutschland.',                  answer:'aus',     options:['aus','von','nach','bei'],      topic:'prepositions', diff:'A1', translation:'He comes from Germany.' },
  { sentence:'Das ist ein Geschenk ___ meiner Mutter.',    answer:'von',     options:['von','aus','bei','mit'],       topic:'prepositions', diff:'A1', translation:'That is a gift from my mother.' },
  { sentence:'Ich gehe ___ dem Arzt.',                     answer:'zu',      options:['zu','nach','bei','mit'],       topic:'prepositions', diff:'A1', translation:'I am going to the doctor.' },
  { sentence:'Das Bild hängt ___ der Wand.',               answer:'an',      options:['an','auf','in','über'],        topic:'prepositions', diff:'A1', translation:'The picture hangs on the wall.' },
  { sentence:'Die Schule beginnt ___ 8 Uhr.',              answer:'um',      options:['um','an','in','auf'],          topic:'prepositions', diff:'A1', translation:'School starts at 8 o\'clock.' },
  { sentence:'Das ist ein Geschenk ___ dich.',             answer:'für',     options:['für','mit','von','zu'],        topic:'prepositions', diff:'A1', translation:'This is a gift for you.' },
  { sentence:'Wir fahren ___ den Tunnel.',                 answer:'durch',   options:['durch','über','um','an'],      topic:'prepositions', diff:'A1', translation:'We drive through the tunnel.' },
  { sentence:'Ich trinke Kaffee ___ Zucker.',              answer:'ohne',    options:['ohne','mit','für','durch'],    topic:'prepositions', diff:'A1', translation:'I drink coffee without sugar.' },
  { sentence:'Er wohnt ___ zwei Jahren in Berlin.',        answer:'seit',    options:['seit','vor','nach','bei'],     topic:'prepositions', diff:'A1', translation:'He has lived in Berlin for two years.' },

  // Modal verbs
  { sentence:'Ich ___ Deutsch sprechen.',                  answer:'kann',    options:['kann','muss','will','darf'],   topic:'modals', diff:'A1', translation:'I can speak German.' },
  { sentence:'Du ___ jetzt schlafen.',                     answer:'musst',   options:['musst','kannst','willst','darfst'], topic:'modals', diff:'A1', translation:'You must sleep now.' },
  { sentence:'Ich ___ nach Berlin fahren.',                answer:'will',    options:['will','muss','kann','soll'],   topic:'modals', diff:'A1', translation:'I want to go to Berlin.' },
  { sentence:'___ ich hier sitzen?',                       answer:'Darf',    options:['Darf','Muss','Will','Soll'],   topic:'modals', diff:'A1', translation:'May I sit here?' },
  { sentence:'Du ___ das nicht machen.',                   answer:'sollst',  options:['sollst','musst','kannst','willst'], topic:'modals', diff:'A1', translation:'You should not do that.' },
  { sentence:'Ich ___ einen Kaffee, bitte.',               answer:'möchte',  options:['möchte','muss','kann','soll'], topic:'modals', diff:'A1', translation:'I would like a coffee, please.' },
  { sentence:'Wir ___ heute ins Kino gehen.',              answer:'können',  options:['können','müssen','wollen','sollen'], topic:'modals', diff:'A1', translation:'We can go to the cinema today.' },
  { sentence:'Er ___ jeden Tag Sport machen.',             answer:'muss',    options:['muss','kann','will','darf'],   topic:'modals', diff:'A1', translation:'He has to do sport every day.' },

  // sein / haben
  { sentence:'Er ___ Lehrer von Beruf.',                   answer:'ist',     options:['ist','hat','sind','haben'],    topic:'verbs', diff:'A1', translation:'He is a teacher by profession.' },
  { sentence:'Wir ___ in Berlin.',                         answer:'sind',    options:['sind','haben','ist','hat'],    topic:'verbs', diff:'A1', translation:'We are in Berlin.' },
  { sentence:'Sie ___ ein Auto.',                          answer:'hat',     options:['hat','ist','haben','sind'],    topic:'verbs', diff:'A1', translation:'She has a car.' },
  { sentence:'Ich ___ Hunger.',                            answer:'habe',    options:['habe','bin','hat','ist'],      topic:'verbs', diff:'A1', translation:'I am hungry.' },
  { sentence:'Das ___ sehr gut!',                          answer:'ist',     options:['ist','hat','sind','haben'],    topic:'verbs', diff:'A1', translation:'That is very good!' },
  { sentence:'Ihr ___ viele Freunde.',                     answer:'habt',    options:['habt','seid','hat','sind'],    topic:'verbs', diff:'A1', translation:'You (pl.) have many friends.' },
  { sentence:'Sie (plural) ___ aus Italien.',              answer:'sind',    options:['sind','haben','ist','hat'],    topic:'verbs', diff:'A1', translation:'They are from Italy.' },
  { sentence:'Ich ___ müde.',                              answer:'bin',     options:['bin','habe','ist','hat'],      topic:'verbs', diff:'A1', translation:'I am tired.' },
];

// ── Grammar game state ─────────────────────────────────────────────────────
let grammarDeck        = [];
let grammarIdx         = 0;
let grammarAnswered    = false;
let selectedGameMode   = 'articles';  // 'articles' | 'grammar'
let selectedGrammarCat = 'all';

// ── Grammar helpers ────────────────────────────────────────────────────────
function getGrammarDeck() {
  const cat = selectedGrammarCat;
  return GRAMMAR_CARDS.filter(c => cat === 'all' || c.topic === cat)
    .sort(() => Math.random() - 0.5);
}

function loadGrammarCard() {
  if (grammarIdx >= grammarDeck.length) {
    grammarIdx = 0;
    grammarDeck = getGrammarDeck();
  }
  const card = grammarDeck[grammarIdx];
  grammarAnswered = false;

  // Render sentence (replace ___ with styled blank)
  const sentenceHtml = card.sentence.replace('___', '<span class="grammar-blank">___</span>');
  document.getElementById('grammarSentence').innerHTML = sentenceHtml;
  document.getElementById('grammarTopic').textContent  = card.topic;
  document.getElementById('grammarTranslation').style.opacity = '0';
  document.getElementById('grammarTranslation').textContent   = card.translation;

  // Render options (shuffle)
  const opts = [...card.options].sort(() => Math.random() - 0.5);
  document.getElementById('grammarOpts').innerHTML = opts.map(o =>
    `<button class="btn-grammar-opt" onclick="answerGrammar(this,'${escapeOpt(o)}','${escapeOpt(card.answer)}')">${o}</button>`
  ).join('');
}

function escapeOpt(s) {
  return s.replace(/'/g, "\\'");
}

function answerGrammar(btn, chosen, correct) {
  if (grammarAnswered) return;
  grammarAnswered = true;

  const isCorrect = chosen === correct;
  btn.classList.add(isCorrect ? 'correct' : 'wrong');

  // Disable all buttons & highlight correct answer
  document.querySelectorAll('.btn-grammar-opt').forEach(b => {
    b.disabled = true;
    if (b.textContent.trim() === correct && !isCorrect) b.classList.add('correct');
  });

  // Show translation
  document.getElementById('grammarTranslation').style.opacity = '1';

  // Fill in the blank with the correct answer
  document.getElementById('grammarSentence').innerHTML =
    grammarDeck[grammarIdx].sentence.replace(
      '___', `<span class="grammar-blank" style="color:#4ade80">${correct}</span>`
    );

  // Track daily progress
  if (isCorrect) {
    dailyAnsweredToday++;
    updateGoalUI();
    updateGoalBadge();
    if (dailyAnsweredToday === dailyGoal) showGoalToast();
    apiPost(`/daily/${USER_ID}`, { answeredToday: dailyAnsweredToday, goal: dailyGoal });
  }

  setTimeout(() => {
    grammarIdx++;
    loadGrammarCard();
  }, 1600);
}
"""

# Insert after CARDS definition (after the `];` that closes it)
# Find the end of CARDS array
cards_end = src.index('\n];', src.index('const CARDS = ['))
insert_pos = cards_end + 3  # after '];\n'
src = src[:insert_pos] + '\n' + GRAMMAR_JS + src[insert_pos:]

# ────────────────────────────────────────────────────────────────────────────
# 6.  JS: patch selectPill to handle new pill groups
# ────────────────────────────────────────────────────────────────────────────
OLD_SELECT = "  if (g === 'mode') selectedMode = btn.dataset.val;\n  if (g === 'cat')  selectedCat  = btn.dataset.val;\n  if (g === 'diff') selectedDiff = btn.dataset.val;"
NEW_SELECT = """  if (g === 'mode')     selectedMode     = btn.dataset.val;
  if (g === 'cat')      selectedCat      = btn.dataset.val;
  if (g === 'diff')     selectedDiff     = btn.dataset.val;
  if (g === 'gcat')     selectedGrammarCat = btn.dataset.val;
  if (g === 'gamemode') {
    selectedGameMode = btn.dataset.val;
    const isGrammar = selectedGameMode === 'grammar';
    document.getElementById('grammarCatSection').style.display = isGrammar ? '' : 'none';
    // Hide article-only UI in grammar mode
    document.querySelectorAll('[data-group="mode"]').forEach(el =>
      el.closest('.pill-row').previousElementSibling.style.display = isGrammar ? 'none' : '');
    document.querySelectorAll('[data-group="mode"]').forEach(el =>
      el.closest('.pill-row').style.display = isGrammar ? 'none' : '');
    document.querySelectorAll('[data-group="cat"]').forEach(el =>
      el.closest('.pill-row').previousElementSibling.style.display = isGrammar ? 'none' : '');
    document.querySelectorAll('[data-group="cat"]').forEach(el =>
      el.closest('.pill-row').style.display = isGrammar ? 'none' : '');
    document.querySelectorAll('[data-group="diff"]').forEach(el =>
      el.closest('.pill-row').previousElementSibling.style.display = isGrammar ? 'none' : '');
    document.querySelectorAll('[data-group="diff"]').forEach(el =>
      el.closest('.pill-row').style.display = isGrammar ? 'none' : '');
  }"""
src = src.replace(OLD_SELECT, NEW_SELECT, 1)

# ────────────────────────────────────────────────────────────────────────────
# 7.  JS: patch startGame() to branch on grammar mode
# ────────────────────────────────────────────────────────────────────────────
OLD_START_GAME = "function startGame(resume = false) {"
NEW_START_GAME = """function startGame(resume = false) {
  if (selectedGameMode === 'grammar') { startGrammarGame(); return; }"""
src = src.replace(OLD_START_GAME, NEW_START_GAME, 1)

# ────────────────────────────────────────────────────────────────────────────
# 8.  JS: add startGrammarGame() and show/hide grammar vs article card elements
# ────────────────────────────────────────────────────────────────────────────
GRAMMAR_START_FN = """
function startGrammarGame() {
  document.getElementById('startScreen').style.display = 'none';
  document.getElementById('doneScreen').style.display  = 'none';
  document.getElementById('gameScreen').style.display  = '';

  // Show grammar card, hide article card
  document.getElementById('grammarCard').style.display  = '';
  document.getElementById('cardArea').style.display     = 'none';
  document.getElementById('swipeHint').style.display    = 'none';
  document.querySelector('.btn-article-row').style.display = 'none';

  grammarDeck = getGrammarDeck();
  grammarIdx  = 0;
  loadGrammarCard();
}
"""
# Insert right before "function startGame"
src = src.replace('function startGame(resume = false) {', GRAMMAR_START_FN + '\nfunction startGame(resume = false) {', 1)

# ────────────────────────────────────────────────────────────────────────────
# 9.  JS: patch goMenu() to restore article card elements when returning
# ────────────────────────────────────────────────────────────────────────────
OLD_GO_MENU = "  document.getElementById('startScreen').style.display = '';\n  renderStreak('streakBadgeStart');\n  updateGoalUI();"
NEW_GO_MENU = """  document.getElementById('startScreen').style.display = '';
  // Restore article card elements (may have been hidden by grammar mode)
  const articleCard = document.getElementById('cardArea');
  if (articleCard) articleCard.style.display = '';
  const swipeHint = document.getElementById('swipeHint');
  if (swipeHint) swipeHint.style.display = '';
  const articleRow = document.querySelector('.btn-article-row');
  if (articleRow) articleRow.style.display = '';
  const grammarCardEl = document.getElementById('grammarCard');
  if (grammarCardEl) grammarCardEl.style.display = 'none';
  renderStreak('streakBadgeStart');
  updateGoalUI();"""
src = src.replace(OLD_GO_MENU, NEW_GO_MENU, 1)

# ────────────────────────────────────────────────────────────────────────────
# 10.  HTML: add class to article buttons row for easy targeting
# ────────────────────────────────────────────────────────────────────────────
src = src.replace(
  '<div class="btn-article-wrap">',
  '<div class="btn-article-wrap btn-article-row">',
  1
)

# Also wrap cardArea if not already wrapped
# The card area is the flip card div — add id if missing
src = src.replace('<div class="card-wrapper" id="cardWrapper">', '<div id="cardArea"><div class="card-wrapper" id="cardWrapper">', 1)
# Close it before the swipe hint
src = src.replace('</div>\n\n    <div class="swipe-hint" id="swipeHint">', '</div></div>\n\n    <div class="swipe-hint" id="swipeHint">', 1)

HTML.write_text(src)
print("Done!")
