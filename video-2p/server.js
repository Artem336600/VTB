// server.js
const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const { v4: uuidv4 } = require('uuid');
const VideoChatBot = require('./bot');
const AIChatBot = require('./ai-chat-bot');
const InterviewBot = require('./interview-bot');
const CartesiaTTS = require('./cartesia-tts');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(express.static('public'));
app.use(express.json());

const rooms = new Map(); // roomId -> array of {id, ws}
const activeBots = new Map(); // roomId -> bot instance
const activeAIBots = new Map(); // roomId -> ai bot instance
const activeInterviewBots = new Map(); // roomId -> interview bot instance

// Инициализируем Cartesia TTS
const CARTESIA_API_KEY = "sk_car_ithVK1dG72ckm9M9FEKoPF";
const tts = new CartesiaTTS(CARTESIA_API_KEY);

wss.on('connection', (ws) => {
  let myRoom = null;
  let myId = uuidv4();

  ws.on('message', (msg) => {
    try {
      const data = JSON.parse(msg);
      if (data.type === 'join') {
        const roomId = data.room;
        myRoom = roomId;
        if (!rooms.has(roomId)) rooms.set(roomId, []);
        const arr = rooms.get(roomId);

        if (arr.length >= 2) {
          ws.send(JSON.stringify({ type: 'full' }));
          return;
        }

        arr.push({ id: myId, ws, bot: data.bot || false, name: data.name || 'Пользователь' });
        // notify
        if (arr.length === 2) {
          // Tell the newcomer to initiate (create offer)
          ws.send(JSON.stringify({ type: 'initiate' }));
          // Optionally notify the other peer
          const other = arr.find(x => x.id !== myId);
          if (other) other.ws.send(JSON.stringify({ 
            type: 'peer-joined', 
            bot: data.bot || false, 
            name: data.name || 'Пользователь' 
          }));
        } else {
          // first in room -> wait
          ws.send(JSON.stringify({ type: 'waiting' }));
        }
        return;
      }

      // relay signaling messages to the other peer
      if (data.type === 'offer' || data.type === 'answer' || data.type === 'candidate') {
        const arr = rooms.get(myRoom) || [];
        const other = arr.find(x => x.ws !== ws);
        if (other) {
          other.ws.send(JSON.stringify(data));
        }
        return;
      }

                  // relay chat messages to the other peer
                  if (data.type === 'chat') {
                    console.log(`📨 Получено сообщение в комнате ${myRoom}:`, data);
                    const arr = rooms.get(myRoom) || [];
                    const other = arr.find(x => x.ws !== ws);
                    if (other) {
                      console.log(`📤 Пересылаем сообщение другому участнику:`, other.id);
                      other.ws.send(JSON.stringify(data));
                    } else {
                      console.log(`❌ Не найден другой участник для пересылки сообщения`);
                    }
                    return;
                  }


      // optional: leave
      if (data.type === 'leave') {
        ws.close();
      }
    } catch (e) {
      console.error('bad msg', e);
    }
  });

  ws.on('close', () => {
    if (!myRoom) return;
    const arr = rooms.get(myRoom) || [];
    const idx = arr.findIndex(x => x.id === myId);
    if (idx !== -1) arr.splice(idx, 1);
    // notify remaining peer
    if (arr.length === 1) {
      arr[0].ws.send(JSON.stringify({ type: 'peer-left' }));
    }
                if (arr.length === 0) {
                  rooms.delete(myRoom);
                  // Stop bots if they were active in this room
                  if (activeBots.has(myRoom)) {
                    activeBots.get(myRoom).disconnect();
                    activeBots.delete(myRoom);
                  }
                  if (activeAIBots.has(myRoom)) {
                    activeAIBots.get(myRoom).disconnect();
                    activeAIBots.delete(myRoom);
                  }
                  if (activeInterviewBots.has(myRoom)) {
                    activeInterviewBots.get(myRoom).disconnect();
                    activeInterviewBots.delete(myRoom);
                  }
                }
  });
});

// API endpoint to start a bot
app.post('/start-bot', (req, res) => {
  const { roomId } = req.body;
  
  if (!roomId) {
    return res.status(400).json({ error: 'Room ID is required' });
  }
  
  // Check if bot is already active in this room
  if (activeBots.has(roomId)) {
    return res.json({ message: 'Bot is already active in this room' });
  }
  
  // Create and start bot
  const bot = new VideoChatBot();
  bot.connect(roomId);
  activeBots.set(roomId, bot);
  
  res.json({ message: 'Bot started successfully', roomId });
});

// API endpoint to stop a bot
app.post('/stop-bot', (req, res) => {
  const { roomId } = req.body;

  if (!roomId) {
    return res.status(400).json({ error: 'Room ID is required' });
  }

  if (activeBots.has(roomId)) {
    activeBots.get(roomId).disconnect();
    activeBots.delete(roomId);
    res.json({ message: 'Bot stopped successfully' });
  } else {
    res.json({ message: 'No bot active in this room' });
  }
});

// API endpoint to start an AI bot
app.post('/start-ai-bot', (req, res) => {
  const { roomId } = req.body;

  if (!roomId) {
    return res.status(400).json({ error: 'Room ID is required' });
  }

  // Check if AI bot is already active in this room
  if (activeAIBots.has(roomId)) {
    return res.json({ message: 'AI Bot is already active in this room' });
  }

  // Create and start AI bot
  const aiBot = new AIChatBot();
  aiBot.connect(roomId);
  activeAIBots.set(roomId, aiBot);

  res.json({ message: 'AI Bot started successfully', roomId });
});

// API endpoint to stop an AI bot
app.post('/stop-ai-bot', (req, res) => {
  const { roomId } = req.body;

  if (!roomId) {
    return res.status(400).json({ error: 'Room ID is required' });
  }

  if (activeAIBots.has(roomId)) {
    activeAIBots.get(roomId).disconnect();
    activeAIBots.delete(roomId);
    res.json({ message: 'AI Bot stopped successfully' });
  } else {
    res.json({ message: 'No AI bot active in this room' });
  }
});

// API endpoint to start an interview bot
app.post('/start-interview-bot', (req, res) => {
  const { roomId, candidateInfo } = req.body;

  if (!roomId) {
    return res.status(400).json({ error: 'Room ID is required' });
  }

  // Check if interview bot is already active in this room
  if (activeInterviewBots.has(roomId)) {
    return res.json({ message: 'Interview Bot is already active in this room' });
  }

  // Create and start interview bot
  const interviewBot = new InterviewBot();
  interviewBot.connect(roomId, candidateInfo || {});
  activeInterviewBots.set(roomId, interviewBot);

  res.json({ message: 'Interview Bot started successfully', roomId });
});

// API endpoint to stop an interview bot
app.post('/stop-interview-bot', (req, res) => {
  const { roomId } = req.body;

  if (!roomId) {
    return res.status(400).json({ error: 'Room ID is required' });
  }

  if (activeInterviewBots.has(roomId)) {
    activeInterviewBots.get(roomId).disconnect();
    activeInterviewBots.delete(roomId);
    res.json({ message: 'Interview Bot stopped successfully' });
  } else {
    res.json({ message: 'No interview bot active in this room' });
  }
});

// API endpoint для синтеза речи
app.post('/synthesize-speech', async (req, res) => {
  try {
    const { text, language = 'ru' } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'Текст обязателен' });
    }
    
    console.log(`Запрос на синтез речи: "${text}"`);
    
    // Синтезируем речь
    const audioFile = await tts.synthesizeSpeech(text, null, language);
    
    if (audioFile) {
      // Читаем аудио файл и отправляем как base64
      const audioData = require('fs').readFileSync(audioFile);
      const base64Audio = audioData.toString('base64');
      
      res.json({
        success: true,
        audio: base64Audio,
        format: 'mp3'
      });
      
      // Удаляем временный файл
      require('fs').unlinkSync(audioFile);
    } else {
      res.status(500).json({ error: 'Ошибка синтеза речи' });
    }
    
  } catch (error) {
    console.error('Ошибка в /synthesize-speech:', error);
    res.status(500).json({ error: 'Внутренняя ошибка сервера' });
  }
});

// API endpoint для очистки кэша TTS
app.post('/clear-tts-cache', (req, res) => {
  try {
    tts.clearCache();
    res.json({ success: true, message: 'Кэш TTS очищен' });
  } catch (error) {
    console.error('Ошибка при очистке кэша:', error);
    res.status(500).json({ error: 'Ошибка при очистке кэша' });
  }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
