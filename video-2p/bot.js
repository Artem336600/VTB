// bot.js - Бот-участник для видеозвонков
const WebSocket = require('ws');
const { v4: uuidv4 } = require('uuid');

class VideoChatBot {
  constructor(serverUrl = 'ws://localhost:3000') {
    this.serverUrl = serverUrl;
    this.ws = null;
    this.roomId = null;
    this.botId = uuidv4();
    this.isConnected = false;
    this.botName = 'Бот-Ассистент';
    this.responses = [
      'Да, понимаю!',
      'Ага, интересно!',
      'Понятно, расскажите еще!',
      'Хм, а что дальше?',
      'Да, да, продолжайте!',
      'Ух ты, как интересно!',
      'Вау, не знал об этом!',
      'Ого, это круто!',
      'Да, согласен!',
      'Понял вас!',
      'Ага, ага!',
      'Да, это правда!',
      'Хм, не думал об этом!',
      'Да, вы правы!',
      'Интересно получается!',
      'Да, точно!',
      'Ага, понятно!',
      'Да, это логично!'
    ];
  }

  connect(roomId) {
    this.roomId = roomId;
    this.ws = new WebSocket(this.serverUrl);
    
    this.ws.on('open', () => {
      console.log(`🤖 Бот подключился к серверу`);
      this.isConnected = true;
      this.joinRoom();
    });

    this.ws.on('message', (data) => {
      try {
        const message = JSON.parse(data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Ошибка парсинга сообщения:', error);
      }
    });

    this.ws.on('close', () => {
      console.log('🤖 Бот отключился от сервера');
      this.isConnected = false;
    });

    this.ws.on('error', (error) => {
      console.error('🤖 Ошибка WebSocket:', error);
    });
  }

  joinRoom() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'join',
        room: this.roomId,
        bot: true,
        name: this.botName
      }));
      console.log(`🤖 Бот присоединился к комнате: ${this.roomId}`);
      
      // Отправляем приветственное сообщение
      setTimeout(() => {
        this.sendChatMessage('Привет! Как дела?');
      }, 1000);
    }
  }

  handleMessage(message) {
    console.log('🤖 Получено сообщение:', message.type);

    switch (message.type) {
      case 'waiting':
        console.log('🤖 Ожидание второго участника...');
        break;
        
      case 'initiate':
        console.log('🤖 Второй участник подключился, создаю предложение...');
        this.createOffer();
        break;
        
      case 'peer-joined':
        console.log('🤖 К боту присоединился участник');
        break;
        
      case 'offer':
        console.log('🤖 Получено предложение, создаю ответ...');
        this.createAnswer(message.sdp);
        break;
        
      case 'answer':
        console.log('🤖 Получен ответ, соединение установлено');
        break;
        
      case 'candidate':
        console.log('🤖 Получен ICE кандидат');
        break;
        
      case 'full':
        console.log('🤖 Комната полна');
        break;
        
      case 'peer-left':
        console.log('🤖 Участник покинул комнату');
        break;
        
      case 'chat':
        this.handleChatMessage(message);
        break;
    }
  }

  createOffer() {
    // Имитируем создание WebRTC предложения
    const mockOffer = {
      type: 'offer',
      sdp: `v=0\r\no=bot ${this.botId} 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0\r\na=msid-semantic: WMS\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:${this.botId}\r\na=ice-pwd:botpassword\r\na=ice-options:trickle\r\na=fingerprint:sha-256 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00\r\na=setup:actpass\r\na=mid:0\r\na=sendrecv\r\na=rtcp-mux\r\na=rtcp-rsize\r\na=rtpmap:96 VP8/90000\r\na=rtcp-fb:96 goog-remb\r\na=rtcp-fb:96 transport-cc\r\na=rtcp-fb:96 ccm fir\r\na=rtcp-fb:96 nack\r\na=rtcp-fb:96 nack pli\r\na=rtcp-fb:96 goog-lntf\r\na=fmtp:96 x-google-start-bitrate=800\r\na=ssrc:1234567890 cname:bot\r\na=ssrc:1234567890 msid:bot video\r\na=ssrc:1234567890 mslabel:bot\r\na=ssrc:1234567890 label:video\r\n`
    };
    
    setTimeout(() => {
      this.ws.send(JSON.stringify(mockOffer));
      console.log('🤖 Отправлено предложение');
    }, 1000);
  }

  createAnswer(offerSdp) {
    // Имитируем создание WebRTC ответа
    const mockAnswer = {
      type: 'answer',
      sdp: `v=0\r\no=bot ${this.botId} 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE 0\r\na=msid-semantic: WMS\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:${this.botId}\r\na=ice-pwd:botpassword\r\na=ice-options:trickle\r\na=fingerprint:sha-256 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00\r\na=setup:active\r\na=mid:0\r\na=sendrecv\r\na=rtcp-mux\r\na=rtcp-rsize\r\na=rtpmap:96 VP8/90000\r\na=rtcp-fb:96 goog-remb\r\na=rtcp-fb:96 transport-cc\r\na=rtcp-fb:96 ccm fir\r\na=rtcp-fb:96 nack\r\na=rtcp-fb:96 nack pli\r\na=rtcp-fb:96 goog-lntf\r\na=fmtp:96 x-google-start-bitrate=800\r\na=ssrc:1234567890 cname:bot\r\na=ssrc:1234567890 msid:bot video\r\na=ssrc:1234567890 mslabel:bot\r\na=ssrc:1234567890 label:video\r\n`
    };
    
    setTimeout(() => {
      this.ws.send(JSON.stringify(mockAnswer));
      console.log('🤖 Отправлен ответ');
    }, 1000);
  }

  handleChatMessage(message) {
    if (message.text && !message.bot) {
      console.log(`🤖 Получено сообщение от пользователя: ${message.text}`);
      
      // Анализируем сообщение для более умного ответа
      const userText = message.text.toLowerCase();
      let response = '';
      
      // Специальные ответы на определенные фразы
      if (userText.includes('привет') || userText.includes('здравствуй')) {
        response = 'Привет! Как дела?';
      } else if (userText.includes('как дела') || userText.includes('как ты')) {
        response = 'Нормально! А у тебя как?';
      } else if (userText.includes('что делаешь') || userText.includes('чем занимаешься')) {
        response = 'С тобой общаюсь!';
      } else if (userText.includes('пока') || userText.includes('до свидания')) {
        response = 'Пока! Увидимся!';
      } else if (userText.includes('спасибо')) {
        response = 'Пожалуйста!';
      } else if (userText.includes('погода')) {
        response = 'Не знаю, какая погода. А у вас как?';
      } else if (userText.includes('время') || userText.includes('который час')) {
        response = 'Время не знаю, но день хороший!';
      } else {
        // Обычный случайный ответ
        response = this.responses[Math.floor(Math.random() * this.responses.length)];
      }
      
      // Отвечаем с задержкой
      setTimeout(() => {
        this.sendChatMessage(response);
      }, 1000 + Math.random() * 2000); // Задержка 1-3 секунды
    }
  }

  sendChatMessage(text) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'chat',
        text: text,
        bot: true,
        name: this.botName
      }));
      console.log(`🤖 Отправлено сообщение: ${text}`);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }

  // Метод для автоматического присоединения к случайной комнате
  joinRandomRoom() {
    const randomRoomId = Math.random().toString(36).slice(2, 9);
    console.log(`🤖 Присоединяюсь к случайной комнате: ${randomRoomId}`);
    this.connect(randomRoomId);
  }
}

// Экспорт для использования в других файлах
module.exports = VideoChatBot;

// Если файл запущен напрямую, создаем бота
if (require.main === module) {
  const bot = new VideoChatBot();
  
  // Присоединяемся к случайной комнате
  bot.joinRandomRoom();
  
  // Обработка завершения процесса
  process.on('SIGINT', () => {
    console.log('\n🤖 Завершение работы бота...');
    bot.disconnect();
    process.exit(0);
  });
}
