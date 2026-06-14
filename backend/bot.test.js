const test = require('node:test');
const assert = require('node:assert/strict');

const {
  buildOpenFlashcardsOptions,
  isGroupChat,
  registerLeaderboardHandlers,
} = require('./bot');

test('isGroupChat detects Telegram group contexts only', () => {
  assert.equal(isGroupChat({ type: 'group' }), true);
  assert.equal(isGroupChat({ type: 'supergroup' }), true);
  assert.equal(isGroupChat({ type: 'private' }), false);
  assert.equal(isGroupChat({}), false);
});

test('buildOpenFlashcardsOptions creates a Telegram web_app inline button', () => {
  const options = buildOpenFlashcardsOptions('https://example.com/app');

  assert.deepEqual(options, {
    reply_markup: {
      inline_keyboard: [[{
        text: 'Open Flashcards 🃏',
        web_app: { url: 'https://example.com/app' },
      }]],
    },
  });
});

test('registerLeaderboardHandlers replies with the Mini App button in groups and pins when enabled', async () => {
  const handlers = new Map();
  const calls = [];
  const bot = {
    onText(pattern, handler) { handlers.set(pattern.toString(), handler); },
    async sendMessage(chatId, text, options) {
      calls.push(['sendMessage', chatId, text, options]);
      return { message_id: 42 };
    },
    async pinChatMessage(chatId, messageId, options) {
      calls.push(['pinChatMessage', chatId, messageId, options]);
    },
  };

  registerLeaderboardHandlers(bot, {
    miniAppUrl: 'https://example.com/app',
    pin: true,
  });

  const handler = handlers.get('/\\/(start|leaderboard)(?:@\\w+)?(?:\\s|$)/.toString()') || [...handlers.values()][0];
  assert.ok(handler, 'expected a /start or /leaderboard handler to be registered');

  await handler({ chat: { id: -100123, type: 'supergroup' } });

  assert.deepEqual(calls, [
    ['sendMessage', -100123, 'Open the group flashcards leaderboard:', {
      reply_markup: {
        inline_keyboard: [[{
          text: 'Open Flashcards 🃏',
          web_app: { url: 'https://example.com/app' },
        }]],
      },
    }],
    ['pinChatMessage', -100123, 42, { disable_notification: true }],
  ]);
});

test('registerLeaderboardHandlers ignores private chats', async () => {
  const handlers = [];
  const calls = [];
  const bot = {
    onText(pattern, handler) { handlers.push(handler); },
    async sendMessage(...args) { calls.push(args); },
    async pinChatMessage(...args) { calls.push(args); },
  };

  registerLeaderboardHandlers(bot, {
    miniAppUrl: 'https://example.com/app',
    pin: true,
  });

  await handlers[0]({ chat: { id: 123, type: 'private' } });

  assert.deepEqual(calls, []);
});
