// ai-chat-bot.js - ИИ-бот для общения с DeepSeek API
const { v4: uuidv4 } = require('uuid');

class AIChatBot {
  constructor() {
    this.serverUrl = (process.env.NODE_ENV === 'production' ? 'wss:' : 'ws:') + '//localhost:3000';
    this.ws = null;
    this.roomId = null;
    this.botId = uuidv4();
    this.isConnected = false;
    this.botName = 'ИИ-Собеседник';
    
    // Настройки DeepSeek API
    this.apiKey = "sk-7446c16774044136aa33ab1b74eb1b31";
    this.baseUrl = "https://api.deepseek.com";
    this.model = "deepseek-chat";
    
    // История разговора для контекста
    this.conversationHistory = [];
    this.maxHistoryLength = 10; // Максимум 10 последних сообщений
    
    // Системный промпт для ИИ
    this.systemPrompt = `Ты - дружелюбный и интересный собеседник. Твоя задача - вести естественную и увлекательную беседу.

ВАЖНЫЕ ПРИНЦИПЫ:
1. Отвечай как обычный человек, а не как ИИ
2. Будь дружелюбным, но не навязчивым
3. Задавай интересные вопросы
4. Показывай искренний интерес к собеседнику
5. Используй эмодзи умеренно
6. Отвечай на русском языке
7. Держи ответы в разумных пределах (1-3 предложения)
8. Не упоминай, что ты ИИ или бот
9. Будь естественным и спонтанным

СТИЛЬ ОБЩЕНИЯ:
- Неформальный, но вежливый
- Интересующийся и любознательный
- С легким юмором, когда уместно
- Поддерживающий и понимающий

ИЗБЕГАЙ:
- Формальных фраз типа "Как дела?"
- Повторения одних и тех же ответов
- Упоминания о том, что ты ИИ
- Слишком длинных ответов
- Шаблонных фраз`;

    console.log('🤖 ИИ-бот инициализирован');
  }

  async connect(roomId) {
    try {
      this.roomId = roomId;
      this.ws = new (require('ws'))(this.serverUrl);
      
      this.ws.on('open', () => {
        console.log('🤖 ИИ-бот подключился к серверу');
        this.isConnected = true;
        
        // Присоединяемся к комнате
        this.ws.send(JSON.stringify({
          type: 'join',
          room: roomId,
          bot: true,
          name: this.botName
        }));
      });

      this.ws.on('message', (data) => {
        try {
          const message = JSON.parse(data);
          console.log(`🤖 Получено сообщение от сервера:`, message);
          this.handleMessage(message);
        } catch (error) {
          console.error('🤖 Ошибка парсинга сообщения:', error);
        }
      });

      this.ws.on('close', () => {
        console.log('🤖 ИИ-бот отключился от сервера');
        this.isConnected = false;
      });

      this.ws.on('error', (error) => {
        console.error('🤖 Ошибка WebSocket:', error);
        this.isConnected = false;
      });

    } catch (error) {
      console.error('🤖 Ошибка подключения ИИ-бота:', error);
    }
  }

  handleMessage(message) {
    console.log(`🤖 Обрабатываем сообщение типа: ${message.type}`);
    
    switch (message.type) {
      case 'waiting':
        console.log('🤖 ИИ-бот ждет собеседника...');
        break;
        
      case 'initiate':
        console.log('🤖 ИИ-бот готов к общению!');
        // Отправляем приветствие
        setTimeout(() => {
          this.sendChatMessage('Привет! Рад познакомиться! 😊');
        }, 1000);
        break;
        
      case 'peer-joined':
        console.log('🤖 Собеседник присоединился');
        // Приветствуем нового собеседника
        setTimeout(() => {
          this.sendChatMessage('Привет! Как дела? Что интересного расскажешь?');
        }, 1500);
        break;
        
      case 'chat':
        console.log('🤖 Получено сообщение чата, обрабатываем...');
        this.handleChatMessage(message);
        break;
        
      case 'peer-left':
        console.log('🤖 Собеседник покинул комнату');
        // Очищаем историю разговора
        this.conversationHistory = [];
        break;
        
      default:
        console.log(`🤖 Игнорируем сообщение типа: ${message.type}`);
        break;
    }
  }

  async handleChatMessage(message) {
    if (message.text && !message.bot) {
      console.log(`🤖 Получено сообщение от пользователя: ${message.text}`);
      
      // Добавляем сообщение пользователя в историю
      this.conversationHistory.push({
        role: 'user',
        content: message.text
      });
      
      // Ограничиваем длину истории
      if (this.conversationHistory.length > this.maxHistoryLength) {
        this.conversationHistory = this.conversationHistory.slice(-this.maxHistoryLength);
      }
      
      console.log(`🤖 История разговора: ${JSON.stringify(this.conversationHistory, null, 2)}`);
      
      try {
        console.log('🤖 Отправляем запрос к DeepSeek API...');
        // Получаем ответ от ИИ
        const aiResponse = await this.getAIResponse(message.text);
        
        if (aiResponse) {
          console.log(`🤖 Получен ответ от DeepSeek: ${aiResponse}`);
          // Добавляем ответ ИИ в историю
          this.conversationHistory.push({
            role: 'assistant',
            content: aiResponse
          });
          
          // Отправляем ответ с задержкой (как будто думаем)
          const delay = 1000 + Math.random() * 2000; // 1-3 секунды
          console.log(`🤖 Отправляем ответ через ${delay}ms`);
          setTimeout(() => {
            this.sendChatMessage(aiResponse);
          }, delay);
        } else {
          console.error('🤖 Не удалось получить ответ от DeepSeek API - ответ пустой');
          // Не отправляем никакого ответа, если ИИ не ответил
        }
        
      } catch (error) {
        console.error('🤖 Ошибка при получении ответа от ИИ:', error);
        console.error('🤖 Детали ошибки:', error.message);
        // Не отправляем никакого ответа при ошибке
      }
    }
  }

  async getAIResponse(userMessage) {
    // Подготавливаем сообщения для API
    const messages = [
      { role: 'system', content: this.systemPrompt }
    ];
    
    // Добавляем историю разговора
    messages.push(...this.conversationHistory);
    
    console.log(`🤖 Отправляем запрос к DeepSeek API: ${this.baseUrl}/v1/chat/completions`);
    console.log(`🤖 Модель: ${this.model}`);
    console.log(`🤖 Сообщения: ${JSON.stringify(messages, null, 2)}`);
    
    // Отправляем запрос к DeepSeek API
    const response = await fetch(`${this.baseUrl}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: this.model,
        messages: messages,
        temperature: 0.8,
        max_tokens: 150,
        stream: false
      })
    });
    
    console.log(`🤖 Статус ответа: ${response.status}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`🤖 Ошибка HTTP: ${response.status} - ${errorText}`);
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log(`🤖 Полный ответ от API: ${JSON.stringify(data, null, 2)}`);
    
    if (data.choices && data.choices[0] && data.choices[0].message) {
      const aiResponse = data.choices[0].message.content.trim();
      console.log(`🤖 DeepSeek ответ: ${aiResponse}`);
      return aiResponse;
    } else {
      console.error(`🤖 Неверный формат ответа: ${JSON.stringify(data, null, 2)}`);
      throw new Error('Неверный формат ответа от DeepSeek API');
    }
  }

  sendChatMessage(text) {
    console.log(`🤖 Попытка отправить сообщение: ${text}`);
    console.log(`🤖 WebSocket подключен: ${this.ws ? 'да' : 'нет'}`);
    console.log(`🤖 Состояние подключения: ${this.isConnected ? 'подключен' : 'отключен'}`);
    
    if (this.ws && this.isConnected) {
      const message = {
        type: 'chat',
        text: text,
        bot: true,
        name: this.botName,
        timestamp: new Date().toISOString()
      };
      
      console.log(`🤖 Отправляем сообщение: ${JSON.stringify(message, null, 2)}`);
      this.ws.send(JSON.stringify(message));
      console.log(`🤖 Сообщение отправлено успешно: ${text}`);
    } else {
      console.error(`🤖 Не удалось отправить сообщение - WebSocket не подключен`);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.isConnected = false;
      console.log('🤖 ИИ-бот отключен');
    }
  }
}

module.exports = AIChatBot;
