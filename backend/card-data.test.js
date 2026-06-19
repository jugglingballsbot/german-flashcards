const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const indexHtml = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const serverJs = fs.readFileSync(path.join(__dirname, 'server.js'), 'utf8');

function extractArrayLiteral(name) {
  const start = indexHtml.indexOf(`const ${name} = [`);
  assert.notEqual(start, -1, `${name} array exists`);

  const open = indexHtml.indexOf('[', start);
  let depth = 0;
  let quote = null;
  let escaped = false;

  for (let i = open; i < indexHtml.length; i++) {
    const ch = indexHtml[i];
    if (quote) {
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === quote) quote = null;
      continue;
    }
    if (ch === '"' || ch === "'" || ch === '`') {
      quote = ch;
      continue;
    }
    if (ch === '[') depth++;
    if (ch === ']') {
      depth--;
      if (depth === 0) return indexHtml.slice(open, i + 1);
    }
  }
  throw new Error(`Could not extract ${name}`);
}

function extractFunction(name) {
  const start = indexHtml.indexOf(`function ${name}(`);
  assert.notEqual(start, -1, `${name} exists`);
  const open = indexHtml.indexOf('{', start);
  let depth = 0;
  let quote = null;
  let escaped = false;
  for (let i = open; i < indexHtml.length; i++) {
    const ch = indexHtml[i];
    if (quote) {
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === quote) quote = null;
      continue;
    }
    if (ch === '"' || ch === "'" || ch === '`') {
      quote = ch;
      continue;
    }
    if (ch === '{') depth++;
    if (ch === '}') {
      depth--;
      if (depth === 0) return indexHtml.slice(start, i + 1);
    }
  }
  throw new Error(`Could not extract ${name}`);
}

const CARDS = Function(`return ${extractArrayLiteral('CARDS')}`)();
const GRAMMAR_CARDS = Function(`return ${extractArrayLiteral('GRAMMAR_CARDS')}`)();

test('article card data is valid and non-duplicated', () => {
  const words = new Set();
  for (const card of CARDS) {
    assert.match(card.word, /\S/, 'word is present');
    assert.match(card.en, /\S/, `${card.word} has English gloss`);
    assert.ok(['der', 'die', 'das'].includes(card.article), `${card.word} has valid article`);
    assert.ok(['A1', 'A2', 'B1'].includes(card.diff), `${card.word} has valid difficulty`);
    assert.match(card.cat, /\S/, `${card.word} has category`);
    assert.equal(words.has(card.word), false, `${card.word} is unique`);
    words.add(card.word);
  }
});

test('grammar card data is valid for fill-in-the-blank practice', () => {
  for (const card of GRAMMAR_CARDS) {
    assert.ok(card.sentence.includes('___'), `${card.sentence} includes blank marker`);
    assert.equal(card.options.length, 4, `${card.sentence} has four options`);
    assert.equal(new Set(card.options).size, 4, `${card.sentence} options are unique`);
    assert.ok(card.options.includes(card.answer), `${card.sentence} options include answer`);
    assert.match(card.translation, /\S/, `${card.sentence} has translation`);
    assert.ok(['A1', 'A2', 'B1'].includes(card.diff), `${card.sentence} has valid difficulty`);
    assert.match(card.topic, /\S/, `${card.sentence} has topic`);
  }
});

test('grammar answers are logged like article answers', () => {
  const answerGrammar = extractFunction('answerGrammar');
  const startGrammarGame = extractFunction('startGrammarGame');
  assert.match(answerGrammar, /apiPost\('\/card-result'/, 'answerGrammar posts per-card results');
  assert.match(answerGrammar, /mode:\s*'grammar'/, 'grammar result payload is marked as grammar mode');
  assert.match(startGrammarGame, /currentSessionId\s*=/, 'grammar sessions get a session id');
});

test('all article practice starts with 10 per-user weak words then 20 fresh practice words', () => {
  const buildArticlePracticeDeck = extractFunction('buildArticlePracticeDeck');
  const fn = Function(`const REVIEW_WORD_LIMIT = 10; const NEW_WORD_LIMIT = 20; ${buildArticlePracticeDeck}; return buildArticlePracticeDeck;`)();
  const cards = Array.from({ length: 35 }, (_, i) => ({
    word: `Word${i + 1}`,
    article: ['der', 'die', 'das'][i % 3],
    en: `word ${i + 1}`,
    cat: 'test',
    diff: 'A1',
  }));
  const weak = ['Word12', 'Word4', 'Word1', 'Word9', 'Word18', 'Word21', 'Word22', 'Word23', 'Word24', 'Word25', 'Word26'];

  const deck = fn(cards, weak, 'all');

  assert.equal(deck.length, 30);
  assert.deepEqual(deck.slice(0, 10).map(c => c.word), weak.slice(0, 10));
  assert.equal(new Set(deck.map(c => c.word)).size, 30, 'deck has unique words');
  assert.equal(deck.slice(10).length, 20, 'all mode appends exactly 20 new practice words');
  assert.equal(deck.slice(10).some(c => weak.slice(0, 10).includes(c.word)), false, 'new words do not duplicate review words');
});

test('weak-word API is per-user and returns up to 10 review words for spaced repetition', () => {
  const weakWordsRoute = serverJs.slice(
    serverJs.indexOf("app.get('/api/weak-words/:userId'"),
    serverJs.indexOf("app.get('/api/weak-grammar/:userId'")
  );
  assert.match(weakWordsRoute, /WHERE userId = \? AND mode = 'articles'/, 'weak words are scoped to one user');
  assert.match(weakWordsRoute, /LIMIT 10/, 'weak words endpoint can supply the 10-card review block');
});

test('weak words UI can refresh after answers without duplicating fetch logic', () => {
  const refreshWeakWordsUI = extractFunction('refreshWeakWordsUI');
  const setupStart = extractFunction('setupStart');
  const answer = extractFunction('answer');

  assert.match(refreshWeakWordsUI, /apiGet\(`\/weak-words\/\$\{USER_ID\}`\)/, 'weak-word refresh fetches the per-user weak words endpoint');
  assert.match(refreshWeakWordsUI, /weakPill/, 'weak-word refresh updates the Weak Words pill');
  assert.match(setupStart, /refreshWeakWordsUI\(\)/, 'start screen refreshes weak words on first load');
  assert.match(answer, /refreshWeakWordsUI\(\)/, 'article answers refresh weak-word count after logging');
});

test('theory screen has contextual navigation and starts practice for the visible topic', () => {
  assert.match(indexHtml, /id="theoryPrevBtn"/, 'theory screen has previous navigation');
  assert.match(indexHtml, /id="theoryNextBtn"/, 'theory screen has next navigation');
  assert.match(indexHtml, /onclick="startTheoryPractice\(\)"/, 'theory practice button starts selected topic');

  const orderLiteral = extractArrayLiteral('THEORY_ORDER');
  const order = Function(`return ${orderLiteral}`)();
  assert.deepEqual(order, ['articles', 'conjunctions', 'prepositions', 'modals', 'verbs', 'imperatives', 'pronouns', 'conjugations']);

  const startTheoryPractice = extractFunction('startTheoryPractice');
  assert.match(startTheoryPractice, /selectedGameMode\s*=\s*'grammar'/, 'grammar theory starts grammar practice');
  assert.match(startTheoryPractice, /setPillActive\('gcat',\s*currentTheoryKey\)/, 'grammar theory selects matching topic');
  assert.match(startTheoryPractice, /startGame\(\)/, 'practice starts directly from theory');
});

test('practice screen exposes a question-mark theory shortcut', () => {
  assert.match(indexHtml, /id="theoryHelpBtn"/, 'practice header has theory help button');
  assert.match(indexHtml, /onclick="showPracticeTheory\(\)"/, 'help button opens practice theory');

  const showPracticeTheory = extractFunction('showPracticeTheory');
  assert.match(showPracticeTheory, /showTheory\(getCurrentPracticeTheoryKey\(\),\s*'gameScreen'\)/, 'practice theory preserves return-to-game context');
});
