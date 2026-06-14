require('dotenv').config();

const DEFAULT_MINI_APP_URL = 'https://jugglingballsbot.github.io/german-flashcards/';

function isGroupChat(chat = {}) {
  return chat.type === 'group' || chat.type === 'supergroup';
}

function buildOpenFlashcardsOptions(miniAppUrl) {
  return {
    reply_markup: {
      inline_keyboard: [[{
        text: 'Open Flashcards 🃏',
        web_app: { url: miniAppUrl },
      }]],
    },
  };
}

function shouldPin(value) {
  return value === true || value === 'true' || value === '1' || value === 'yes';
}

function registerLeaderboardHandlers(bot, { miniAppUrl = DEFAULT_MINI_APP_URL, pin = false } = {}) {
  const handler = async (msg) => {
    const chat = msg?.chat;
    if (!isGroupChat(chat)) return;

    const sent = await bot.sendMessage(
      chat.id,
      'Open the group flashcards leaderboard:',
      buildOpenFlashcardsOptions(miniAppUrl)
    );

    if (shouldPin(pin) && sent?.message_id && typeof bot.pinChatMessage === 'function') {
      await bot.pinChatMessage(chat.id, sent.message_id, { disable_notification: true });
    }
  };

  bot.onText(/\/(start|leaderboard|play|flashcards)(?:@\w+)?(?:\s|$)/, handler);
}

class TelegramBotClient {
  constructor(token, { fetchImpl = fetch } = {}) {
    this.token = token;
    this.fetch = fetchImpl;
    this.offset = 0;
    this.textHandlers = [];
    this.polling = false;
  }

  onText(pattern, handler) {
    this.textHandlers.push({ pattern, handler });
  }

  async request(method, payload) {
    const response = await this.fetch(`https://api.telegram.org/bot${this.token}/${method}`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    if (!body.ok) throw new Error(body.description || `${method} failed`);
    return body.result;
  }

  sendMessage(chatId, text, options = {}) {
    return this.request('sendMessage', { chat_id: chatId, text, ...options });
  }

  pinChatMessage(chatId, messageId, options = {}) {
    return this.request('pinChatMessage', {
      chat_id: chatId,
      message_id: messageId,
      ...options,
    });
  }

  async handleUpdate(update) {
    const message = update.message;
    const text = message?.text;
    if (!message || !text) return;

    for (const { pattern, handler } of this.textHandlers) {
      pattern.lastIndex = 0;
      if (pattern.test(text)) await handler(message);
    }
  }

  async pollOnce(timeout = 25) {
    const updates = await this.request('getUpdates', {
      offset: this.offset,
      timeout,
      allowed_updates: ['message'],
    });

    for (const update of updates) {
      this.offset = update.update_id + 1;
      await this.handleUpdate(update);
    }
  }

  startPolling() {
    this.polling = true;
    const loop = async () => {
      while (this.polling) {
        try {
          await this.pollOnce();
        } catch (error) {
          console.error('Telegram bot polling error:', error.message);
          await new Promise(resolve => setTimeout(resolve, 5000));
        }
      }
    };
    loop();
  }
}

function startTelegramBot({ token, miniAppUrl, pin } = {}) {
  const botToken = token || process.env.TELEGRAM_BOT_TOKEN || process.env.BOT_TOKEN;
  if (!botToken) return null;

  const bot = new TelegramBotClient(botToken);
  registerLeaderboardHandlers(bot, {
    miniAppUrl: miniAppUrl || process.env.MINI_APP_URL || DEFAULT_MINI_APP_URL,
    pin: pin ?? process.env.PIN_LEADERBOARD_MESSAGE,
  });
  bot.startPolling();
  console.log('German Flashcards Telegram bot started');
  return bot;
}

if (require.main === module) {
  const bot = startTelegramBot({});
  if (!bot) {
    console.error('TELEGRAM_BOT_TOKEN is not set');
    process.exit(1);
  }
}

module.exports = {
  DEFAULT_MINI_APP_URL,
  TelegramBotClient,
  buildOpenFlashcardsOptions,
  isGroupChat,
  registerLeaderboardHandlers,
  shouldPin,
  startTelegramBot,
};
