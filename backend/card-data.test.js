const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const indexHtml = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

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
