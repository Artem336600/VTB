// interview-bot.js - Бот-интервьюер VTB для проведения структурированного интервью
const { v4: uuidv4 } = require('uuid');

class InterviewBot {
  constructor() {
    this.serverUrl = (process.env.NODE_ENV === 'production' ? 'wss:' : 'ws:') + '//localhost:3000';
    this.ws = null;
    this.roomId = null;
    this.botId = uuidv4();
    this.isConnected = false;
    this.botName = 'Бот-интервьюер VTB';
    
    // Настройки DeepSeek API
    this.apiKey = "sk-7446c16774044136aa33ab1b74eb1b31";
    this.baseUrl = "https://api.deepseek.com";
    this.model = "deepseek-chat";
    
    // Состояние интервью
    this.interviewState = 'waiting'; // waiting, part1, part2, part3, part4, completed
    this.currentPart = 0;
    this.interviewResponses = {};
    this.candidateInfo = {};
    
    // Стандартная схема интервью VTB
    this.interviewStructure = {
      part1: {
        title: "🤝 Часть 1: Дружелюбная разминка",
        duration: "5-10 минут",
        questions: [
          {
            text: "Добро пожаловать! Я бот-интервьюер VTB. Сегодня мы проведем собеседование, которое состоит из 3 частей:\n\n• Софт скиллы - обсуждение опыта работы и решения конфликтов\n• Хард скиллы - технические навыки и продуктивность\n• Договоренности о дальнейших шагах\n\nРасскажите коротко о вашем последнем проекте. Что это был за проект, какую роль вы выполняли, и какие результаты достигли?",
            type: "warmup"
          }
        ]
      },
      part2: {
        title: "💬 Часть 2: Софт скиллы",
        duration: "15-20 минут",
        questions: [
          {
            text: "Опишите ситуацию, когда вам пришлось быстро адаптироваться к новым условиям работы.\n\nАдаптивность (младший уровень)",
            type: "adaptability"
          },
          {
            text: "Опишите ситуацию, когда у вас было разногласие с руководителем. Как вы его решили?\n\nРешение конфликтов",
            type: "conflict_resolution"
          },
          {
            text: "Как вы мотивируете команду в сложные периоды проекта?\n\nМотивация команды",
            type: "team_motivation"
          }
        ]
      },
      part3: {
        title: "⚙️ Часть 3: Хард скиллы",
        duration: "20-25 минут",
        questions: [
          {
            text: "Отличные технические навыки! У вас высокий уровень экспертизы. Давайте обсудим ваши сильные стороны:\n\nОпишите ваш подход к архитектурному проектированию сложных систем.\n\nАрхитектура (высокий уровень)",
            type: "architecture"
          },
          {
            text: "Расскажите о вашем подходе к приоритизации задач.\n\nПродуктивность",
            type: "productivity"
          },
          {
            text: "Опишите проект, который лучше всего демонстрирует ваши технические навыки.\n\nДемонстрация навыков",
            type: "skills_demonstration"
          },
          {
            text: "Есть ли у вас опыт с технологиями, которые не отражены в резюме, но могут быть полезны для позиции?\n\nДополнительные технологии",
            type: "additional_technologies"
          }
        ]
      },
      part4: {
        title: "📅 Часть 4: Договоренности",
        duration: "5-10 минут",
        questions: [
          {
            text: "Когда вы сможете приступить к работе?\n\nВопрос о готовности",
            type: "availability"
          },
          {
            text: "Есть ли у вас вопросы о позиции \"ведущий специалист\" или компании?\n\nВопросы кандидата",
            type: "candidate_questions"
          }
        ]
      }
    };
    
    // Системный промпт для интервьюера
    this.systemPrompt = `Ты - профессиональный бот-интервьюер VTB. Твоя задача - провести структурированное интервью по стандартной схеме VTB.

ВАЖНЫЕ ПРИНЦИПЫ:
1. Строго следуй структуре интервью VTB
2. Будь профессиональным, но дружелюбным
3. Задавай вопросы точно по указанной схеме
4. Выслушивай ответы полностью
5. Переходи к следующему вопросу только после получения ответа
6. В конце проведи анализ и дай вердикт
7. Отвечай на русском языке
8. Используй эмодзи умеренно

СТРУКТУРА ИНТЕРВЬЮ VTB:

🤝 ЧАСТЬ 1: Дружелюбная разминка (5-10 минут)
- Приветствие и представление
- Рассказ о последнем проекте

💬 ЧАСТЬ 2: Софт скиллы (15-20 минут)
- Адаптивность (младший уровень)
- Решение конфликтов
- Мотивация команды

⚙️ ЧАСТЬ 3: Хард скиллы (20-25 минут)
- Архитектура (высокий уровень)
- Продуктивность
- Демонстрация навыков
- Дополнительные технологии

📅 ЧАСТЬ 4: Договоренности (5-10 минут)
- Вопрос о готовности
- Вопросы кандидата
- Следующие шаги

СТИЛЬ ОБЩЕНИЯ:
- Профессиональный, но теплый
- Заинтересованный в ответах кандидата
- Поддерживающий и понимающий
- Четкий и структурированный

ПОСЛЕ ИНТЕРВЬЮ:
- Проанализируй все ответы кандидата
- Оцени по критериям: коммуникация, технические навыки, мотивация, общая пригодность
- Дай четкий вердикт: "ПРОШЕЛ" или "НЕ ПРОШЕЛ"
- Объясни причины решения
- Покажи результат прямо в чате`;

    console.log('🎯 Бот-интервьюер VTB инициализирован');
  }

  async connect(roomId, candidateInfo = {}) {
    try {
      this.roomId = roomId;
      this.candidateInfo = candidateInfo;
      this.ws = new (require('ws'))(this.serverUrl);
      
      this.ws.on('open', () => {
        console.log('🎯 Бот-интервьюер подключился к серверу');
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
          console.log(`🎯 Получено сообщение от сервера:`, message);
          this.handleMessage(message);
        } catch (error) {
          console.error('🎯 Ошибка парсинга сообщения:', error);
        }
      });

      this.ws.on('close', () => {
        console.log('🎯 Бот-интервьюер отключился от сервера');
        this.isConnected = false;
      });

      this.ws.on('error', (error) => {
        console.error('🎯 Ошибка WebSocket:', error);
        this.isConnected = false;
      });

    } catch (error) {
      console.error('🎯 Ошибка подключения бота-интервьюера:', error);
    }
  }

  handleMessage(message) {
    console.log(`🎯 Обрабатываем сообщение типа: ${message.type}`);
    
    switch (message.type) {
      case 'waiting':
        console.log('🎯 Бот-интервьюер ждет кандидата...');
        break;
        
      case 'initiate':
        console.log('🎯 Бот-интервьюер готов к интервью!');
        this.startInterview();
        break;
        
      case 'peer-joined':
        console.log('🎯 Кандидат присоединился');
        this.startInterview();
        break;
        
      case 'chat':
        console.log('🎯 Получено сообщение чата, обрабатываем...');
        this.handleChatMessage(message);
        break;
        
      case 'peer-left':
        console.log('🎯 Кандидат покинул комнату');
        this.resetInterview();
        break;
        
      default:
        console.log(`🎯 Игнорируем сообщение типа: ${message.type}`);
        break;
    }
  }

  startInterview() {
    console.log('🎯 Начинаем интервью VTB');
    this.interviewState = 'part1';
    this.currentPart = 1;
    
    setTimeout(() => {
      this.sendInterviewMessage(this.interviewStructure.part1.questions[0].text);
    }, 2000);
  }

  async handleChatMessage(message) {
    if (message.text && !message.bot) {
      console.log(`🎯 Получен ответ от кандидата: ${message.text}`);
      
      // Сохраняем ответ
      const currentQuestion = this.getCurrentQuestion();
      if (currentQuestion) {
        this.interviewResponses[currentQuestion.type] = message.text;
      }
      
      // Переходим к следующему вопросу или завершаем интервью
      await this.processNextStep();
    }
  }

  getCurrentQuestion() {
    const part = this.interviewStructure[`part${this.currentPart}`];
    if (!part) return null;
    
    const questionIndex = Object.keys(this.interviewResponses).length;
    return part.questions[questionIndex] || null;
  }

  async processNextStep() {
    const currentQuestion = this.getCurrentQuestion();
    
    if (currentQuestion) {
      // Есть еще вопросы в текущей части
      setTimeout(() => {
        this.sendInterviewMessage(currentQuestion.text);
      }, 1000);
    } else {
      // Текущая часть завершена, переходим к следующей
      this.currentPart++;
      
      if (this.currentPart <= 4) {
        // Переходим к следующей части
        const nextPart = this.interviewStructure[`part${this.currentPart}`];
        if (nextPart) {
          setTimeout(() => {
            this.sendInterviewMessage(`\n${nextPart.title}\n⏱ ${nextPart.duration}\n\n${nextPart.questions[0].text}`);
          }, 2000);
        }
      } else {
        // Интервью завершено, проводим анализ
        await this.completeInterview();
      }
    }
  }

  async completeInterview() {
    console.log('🎯 Интервью завершено, проводим анализ...');
    this.interviewState = 'completed';
    
    setTimeout(async () => {
      const analysis = await this.analyzeInterview();
      this.sendInterviewMessage(analysis);
    }, 3000);
  }

  async analyzeInterview() {
    try {
      console.log('🎯 Анализируем результаты интервью...');
      
      // Подготавливаем данные для анализа
      const analysisPrompt = `Проанализируй результаты интервью кандидата и дай вердикт.

ИНФОРМАЦИЯ О КАНДИДАТЕ:
${JSON.stringify(this.candidateInfo, null, 2)}

ОТВЕТЫ КАНДИДАТА:
${JSON.stringify(this.interviewResponses, null, 2)}

КРИТЕРИИ ОЦЕНКИ:
1. Коммуникативные навыки (0-25 баллов)
2. Технические навыки (0-25 баллов) 
3. Мотивация и заинтересованность (0-25 баллов)
4. Общая пригодность (0-25 баллов)

ВЕРДИКТ:
- ПРОШЕЛ: 70+ баллов из 100
- НЕ ПРОШЕЛ: менее 70 баллов

Дай четкий анализ и вердикт в формате:

📊 РЕЗУЛЬТАТЫ ИНТЕРВЬЮ VTB

🎯 ОБЩИЙ БАЛЛ: X/100

📋 ДЕТАЛЬНАЯ ОЦЕНКА:
• Коммуникативные навыки: X/25
• Технические навыки: X/25
• Мотивация: X/25
• Общая пригодность: X/25

✅ ВЕРДИКТ: ПРОШЕЛ / ❌ НЕ ПРОШЕЛ

📝 ОБОСНОВАНИЕ:
[Краткое объяснение решения]

🎉 Спасибо за участие в собеседовании! Результаты будут переданы HR-менеджеру.`;

      const response = await fetch(`${this.baseUrl}/v1/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: this.model,
          messages: [
            { role: 'system', content: this.systemPrompt },
            { role: 'user', content: analysisPrompt }
          ],
          temperature: 0.3,
          max_tokens: 500,
          stream: false
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.choices && data.choices[0] && data.choices[0].message) {
        const analysisResult = data.choices[0].message.content.trim();
        
        // Добавляем финальное сообщение
        setTimeout(() => {
          this.sendInterviewMessage("🎉 Спасибо за участие в собеседовании! Результаты будут переданы HR-менеджеру.");
        }, 2000);
        
        return analysisResult;
      } else {
        throw new Error('Неверный формат ответа от API');
      }
      
    } catch (error) {
      console.error('🎯 Ошибка при анализе интервью:', error);
      return `❌ Ошибка при анализе результатов интервью: ${error.message}`;
    }
  }

  sendInterviewMessage(text) {
    console.log(`🎯 Отправляем сообщение: ${text}`);
    
    if (this.ws && this.isConnected) {
      const message = {
        type: 'chat',
        text: text,
        bot: true,
        name: this.botName,
        timestamp: new Date().toISOString()
      };
      
      this.ws.send(JSON.stringify(message));
      console.log(`🎯 Сообщение отправлено: ${text}`);
    } else {
      console.error(`🎯 Не удалось отправить сообщение - WebSocket не подключен`);
    }
  }

  resetInterview() {
    this.interviewState = 'waiting';
    this.currentPart = 0;
    this.interviewResponses = {};
    console.log('🎯 Интервью сброшено');
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.isConnected = false;
      console.log('🎯 Бот-интервьюер отключен');
    }
  }
}

module.exports = InterviewBot;
