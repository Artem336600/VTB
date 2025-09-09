from openai import OpenAI
import json
from typing import Dict, Any

class AIStructuredExtractor:
    """Класс для структурирования текста резюме с помощью ИИ"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key="sk-7446c16774044136aa33ab1b74eb1b31", 
            base_url="https://api.deepseek.com"
        )
    
    def structure_vacancy_text(self, extracted_text: str) -> Dict[str, Any]:
        """Структурирует текст вакансии в формат 'название поля - значение'"""
        
        system_prompt = """Ты - эксперт по анализу вакансий. Твоя задача - извлечь и структурировать информацию из текста вакансии в четкий формат "название поля - значение".

Верни результат в формате JSON со следующими полями:
{
    "job_info": {
        "Название должности": "значение",
        "Компания": "значение",
        "Тип занятости": "значение",
        "График работы": "значение",
        "Местоположение": "значение",
        "Уровень": "значение"
    },
    "salary": {
        "Зарплата от": "значение",
        "Зарплата до": "значение",
        "Валюта": "значение",
        "Тип оплаты": "значение",
        "Бонусы": "значение"
    },
    "requirements": {
        "Опыт работы": "значение",
        "Образование": "значение",
        "Технические навыки": "значение",
        "Языки программирования": "значение",
        "Инструменты": "значение",
        "Иностранные языки": "значение",
        "Личные качества": "значение"
    },
    "responsibilities": [
        "обязанность 1",
        "обязанность 2",
        "обязанность 3"
    ],
    "benefits": [
        "преимущество 1",
        "преимущество 2",
        "преимущество 3"
    ],
    "additional_info": {
        "Описание компании": "значение",
        "Дополнительные требования": "значение",
        "Процесс отбора": "значение",
        "Контактная информация": "значение"
    }
}

Если какая-то информация не найдена, используй "Не указано" или пустую строку.
Отвечай ТОЛЬКО JSON без дополнительных комментариев."""

        user_prompt = f"""Проанализируй следующий текст вакансии и структурируй его согласно требованиям:

{extracted_text}"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False,
                temperature=0.1
            )
            
            # Пытаемся распарсить JSON ответ
            result_text = response.choices[0].message.content.strip()
            
            # Убираем возможные markdown блоки
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            structured_data = json.loads(result_text)
            return structured_data
            
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            print(f"Ответ ИИ: {result_text}")
            return self._create_fallback_structure(extracted_text)
        except Exception as e:
            print(f"Ошибка при обращении к ИИ: {e}")
            return self._create_fallback_structure(extracted_text)
    
    def _create_fallback_structure(self, text: str) -> Dict[str, Any]:
        """Создает базовую структуру если ИИ недоступен"""
        return {
            "job_info": {
                "Название должности": "Не указано",
                "Компания": "Не указано",
                "Тип занятости": "Не указано",
                "График работы": "Не указано",
                "Местоположение": "Не указано",
                "Уровень": "Не указано"
            },
            "salary": {
                "Зарплата от": "Не указано",
                "Зарплата до": "Не указано",
                "Валюта": "Не указано",
                "Тип оплаты": "Не указано",
                "Бонусы": "Не указано"
            },
            "requirements": {
                "Опыт работы": "Не указано",
                "Образование": "Не указано",
                "Технические навыки": "Не указано",
                "Языки программирования": "Не указано",
                "Инструменты": "Не указано",
                "Иностранные языки": "Не указано",
                "Личные качества": "Не указано"
            },
            "responsibilities": [],
            "benefits": [],
            "additional_info": {
                "Описание компании": "Не указано",
                "Дополнительные требования": "Не указано",
                "Процесс отбора": "Не указано",
                "Контактная информация": text[:500] + "..." if len(text) > 500 else text
            }
        }
    
    def format_structured_data(self, structured_data: Dict[str, Any]) -> str:
        """Форматирует структурированные данные для вывода"""
        result = []
        
        # Информация о вакансии
        if structured_data.get("job_info"):
            result.append("=== ИНФОРМАЦИЯ О ВАКАНСИИ ===")
            for key, value in structured_data["job_info"].items():
                if value and value != "Не указано":
                    result.append(f"{key}: {value}")
            result.append("")
        
        # Зарплата
        if structured_data.get("salary"):
            result.append("=== ЗАРПЛАТА ===")
            for key, value in structured_data["salary"].items():
                if value and value != "Не указано":
                    result.append(f"{key}: {value}")
            result.append("")
        
        # Требования
        if structured_data.get("requirements"):
            result.append("=== ТРЕБОВАНИЯ ===")
            for key, value in structured_data["requirements"].items():
                if value and value != "Не указано":
                    result.append(f"{key}: {value}")
            result.append("")
        
        # Обязанности
        if structured_data.get("responsibilities"):
            result.append("=== ОБЯЗАННОСТИ ===")
            for i, resp in enumerate(structured_data["responsibilities"], 1):
                if resp and resp != "Не указано":
                    result.append(f"{i}. {resp}")
            result.append("")
        
        # Преимущества
        if structured_data.get("benefits"):
            result.append("=== ПРЕИМУЩЕСТВА ===")
            for i, benefit in enumerate(structured_data["benefits"], 1):
                if benefit and benefit != "Не указано":
                    result.append(f"{i}. {benefit}")
            result.append("")
        
        # Дополнительная информация
        if structured_data.get("additional_info"):
            result.append("=== ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ===")
            for key, value in structured_data["additional_info"].items():
                if value and value != "Не указано":
                    result.append(f"{key}: {value}")
        
        return "\n".join(result)

def main():
    """Тестовая функция"""
    extractor = AIStructuredExtractor()
    
    # Тестовый текст вакансии
    test_text = """
    Python Developer
    Компания: ООО "Технологии"
    Зарплата: от 80 000 до 150 000 руб.
    
    Требования:
    - Опыт работы с Python от 2 лет
    - Знание Django/Flask
    - Опыт работы с базами данных (PostgreSQL, MySQL)
    - Знание Git
    - Английский язык (intermediate)
    
    Обязанности:
    - Разработка веб-приложений
    - Создание API
    - Работа с базами данных
    - Code review
    - Участие в планировании спринтов
    
    Условия:
    - Удаленная работа
    - Гибкий график
    - Медицинская страховка
    - Обучение за счет компании
    """
    
    structured = extractor.structure_vacancy_text(test_text)
    formatted = extractor.format_structured_data(structured)
    print(formatted)

if __name__ == "__main__":
    main()