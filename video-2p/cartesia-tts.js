// cartesia-tts.js - Cartesia TTS клиент для Node.js
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class CartesiaTTS {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseUrl = "https://api.cartesia.ai/tts/bytes";
    this.cacheDir = "tts_cache";
    this.ensureCacheDir();
    
    // Настройки по умолчанию
    this.defaultVoice = {
      "mode": "id",
      "id": "bfce5b7c-14a1-40b5-a9f5-28481cea5aa0"  // Постоянный голос
    };
    
    this.defaultOutputFormat = {
      "container": "mp3",
      "bit_rate": 128000,
      "sample_rate": 44100
    };
    
    this.headers = {
      "Cartesia-Version": "2025-04-16",
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    };
  }
  
  ensureCacheDir() {
    if (!fs.existsSync(this.cacheDir)) {
      fs.mkdirSync(this.cacheDir, { recursive: true });
    }
  }
  
  getCacheKey(text, voiceId, language) {
    const cacheString = `${text}_${voiceId}_${language}`;
    return crypto.createHash('md5').update(cacheString).digest('hex');
  }
  
  getCachedFile(cacheKey) {
    const cacheFile = path.join(this.cacheDir, `${cacheKey}.mp3`);
    if (fs.existsSync(cacheFile)) {
      return cacheFile;
    }
    return null;
  }
  
  saveToCache(cacheKey, audioData) {
    const cacheFile = path.join(this.cacheDir, `${cacheKey}.mp3`);
    fs.writeFileSync(cacheFile, audioData);
  }
  
  async synthesizeSpeech(text, voiceId = null, language = "ru", outputFile = null, useCache = true) {
    // Всегда используем постоянный голос
    const voice = { ...this.defaultVoice };
    
    // Проверяем кэш
    if (useCache) {
      const cacheKey = this.getCacheKey(text, voice.id, language);
      const cachedFile = this.getCachedFile(cacheKey);
      if (cachedFile) {
        console.log(`Используется кэшированный файл: ${cachedFile}`);
        return cachedFile;
      }
    }
    
    // Подготавливаем данные для запроса
    const payload = {
      "model_id": "sonic-2",
      "transcript": text,
      "voice": voice,
      "output_format": this.defaultOutputFormat,
      "language": language
    };
    
    console.log(`Синтезируем речь для текста: '${text.substring(0, 50)}${text.length > 50 ? '...' : ''}'`);
    
    try {
      // Используем fetch для Node.js (требует Node.js 18+)
      const response = await fetch(this.baseUrl, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const audioData = await response.arrayBuffer();
        
        // Определяем имя выходного файла
        if (!outputFile) {
          const timestamp = Date.now();
          outputFile = `speech_${timestamp}.mp3`;
        }
        
        // Сохраняем аудио
        fs.writeFileSync(outputFile, Buffer.from(audioData));
        
        // Сохраняем в кэш
        if (useCache) {
          const cacheKey = this.getCacheKey(text, voice.id, language);
          this.saveToCache(cacheKey, Buffer.from(audioData));
        }
        
        console.log(`Аудио успешно сохранено как ${outputFile}`);
        return outputFile;
        
      } else {
        console.error(`Ошибка API: ${response.status}`);
        const errorText = await response.text();
        console.error(`Ответ: ${errorText}`);
        return null;
      }
      
    } catch (error) {
      console.error(`Ошибка сети: ${error.message}`);
      return null;
    }
  }
  
  getAvailableVoices() {
    return {
      "permanent_voice": "bfce5b7c-14a1-40b5-a9f5-28481cea5aa0",
      "note": "Используется постоянный голос для всех синтезов"
    };
  }
  
  clearCache() {
    if (fs.existsSync(this.cacheDir)) {
      const files = fs.readdirSync(this.cacheDir);
      files.forEach(file => {
        if (file.endsWith('.mp3')) {
          fs.unlinkSync(path.join(this.cacheDir, file));
        }
      });
      console.log("Кэш очищен");
    } else {
      console.log("Кэш пуст");
    }
  }
  
  // Метод для получения аудио как base64 для отправки в браузер
  async synthesizeToBase64(text, voiceId = null, language = "ru", useCache = true) {
    const audioFile = await this.synthesizeSpeech(text, voiceId, language, null, useCache);
    if (audioFile) {
      const audioData = fs.readFileSync(audioFile);
      return audioData.toString('base64');
    }
    return null;
  }
}

module.exports = CartesiaTTS;
