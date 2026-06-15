const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const serverJs = fs.readFileSync(path.join(__dirname, 'server.js'), 'utf8');
const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));

test('API server does not start Telegram polling as a side effect', () => {
  assert.doesNotMatch(serverJs, /startTelegramBot\s*\(/, 'server.js should not start the bot');
  assert.doesNotMatch(serverJs, /require\(['"]\.\/bot['"]\)/, 'server.js should not import bot.js');
});

test('package exposes separate API and bot entrypoints', () => {
  assert.equal(packageJson.scripts.start, 'node server.js');
  assert.equal(packageJson.scripts.bot, 'node bot.js');
});
