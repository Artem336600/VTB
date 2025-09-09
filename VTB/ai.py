from openai import OpenAI
import json
from typing import Dict, Any

class AIStructuredExtractor:
    """Класс для структурирования текста резюме с помощью ИИ"""
    
    def __init__(self):
        try:
            self.client = OpenAI(
                api_key="sk-7446c16774044136aa33ab1b74eb1b31", 
                base_url="https://api.deepseek.com"
            )
        except Exception as e:
            print(f"Ошибка инициализации OpenAI клиента: {e}")
            # Fallback - создаем клиент без дополнительных параметров
            self.client = None
    
    def structure_vacancy_text(self, extracted_text: str) -> Dict[str, Any]:
        """Структурирует текст вакансии в формат 'название поля - значение'"""
        
        system_prompt = """Ты - эксперт по анализу вакансий с глубоким пониманием HR-процессов. Твоя задача - тщательно проанализировать текст вакансии и извлечь ВСЮ доступную информацию, структурировав её в четкий формат "название поля - значение".

ВАЖНЫЕ ПРИНЦИПЫ АНАЛИЗА:
1. Внимательно читай ВЕСЬ текст, не пропускай детали
2. Извлекай информацию даже если она написана неявно или косвенно
3. Группируй связанную информацию логически
4. Если информация частично указана, дополняй её контекстом
5. Анализируй не только явные требования, но и подразумеваемые

СТРУКТУРА АНАЛИЗА:
{
    "job_info": {
        "Название должности": "точное название позиции",
        "Компания": "название работодателя",
        "Тип занятости": "полная/частичная/удаленная/стажировка",
        "График работы": "рабочий график и режим",
        "Местоположение": "город/регион/удаленно",
        "Уровень": "junior/middle/senior/lead",
        "Опыт работы": "требуемый опыт в годах",
        "Образование": "требования к образованию"
    },
    "salary": {
        "Зарплата от": "минимальная сумма",
        "Зарплата до": "максимальная сумма", 
        "Валюта": "RUB/USD/EUR",
        "Тип оплаты": "оклад/почасовая/процентная",
        "Бонусы": "дополнительные выплаты",
        "Форма оплаты": "наличные/безнал/смешанная"
    },
    "requirements": {
        "Опыт работы": "детальные требования к опыту",
        "Образование": "требования к образованию",
        "Технические навыки": "все технические требования",
        "Языки программирования": "список языков",
        "Инструменты": "инструменты разработки",
        "Иностранные языки": "требования к языкам",
        "Личные качества": "soft skills",
        "Сертификаты": "требуемые сертификаты",
        "Возраст": "возрастные ограничения"
    },
    "responsibilities": [
        "детальное описание обязанностей"
    ],
    "benefits": [
        "все преимущества и льготы"
    ],
    "company_info": {
        "Описание компании": "информация о работодателе",
        "Сфера деятельности": "отрасль компании",
        "Размер компании": "количество сотрудников",
        "Стадия развития": "стартап/средний/крупный бизнес"
    },
    "contact_info": {
        "Контактное лицо": "HR/рекрутер",
        "Email": "электронная почта",
        "Телефон": "контактный телефон",
        "Сайт": "сайт компании"
    },
    "additional_info": {
        "Процесс отбора": "этапы собеседования",
        "Дополнительные требования": "особые условия",
        "Сроки": "сроки подачи/начала работы",
        "Примечания": "дополнительная информация"
    }
}

ПРАВИЛА ЗАПОЛНЕНИЯ:
- Если информация не найдена, используй "Не указано"
- Для списков используй массив строк
- Извлекай максимум информации из текста
- Группируй связанные данные
- Сохраняй оригинальную формулировку где возможно

Отвечай ТОЛЬКО валидным JSON без дополнительных комментариев."""

        user_prompt = f"""Проанализируй следующий текст вакансии и структурируй его согласно требованиям:

{extracted_text}"""

        try:
            if self.client is None:
                print("OpenAI клиент не инициализирован, используем fallback")
                return self._create_fallback_structure(extracted_text)
            
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
                "Уровень": "Не указано",
                "Опыт работы": "Не указано",
                "Образование": "Не указано"
            },
            "salary": {
                "Зарплата от": "Не указано",
                "Зарплата до": "Не указано",
                "Валюта": "RUB",
                "Тип оплаты": "Не указано",
                "Бонусы": "Не указано",
                "Форма оплаты": "Не указано"
            },
            "requirements": {
                "Опыт работы": "Не указано",
                "Образование": "Не указано",
                "Технические навыки": "Не указано",
                "Языки программирования": "Не указано",
                "Инструменты": "Не указано",
                "Иностранные языки": "Не указано",
                "Личные качества": "Не указано",
                "Сертификаты": "Не указано",
                "Возраст": "Не указано"
            },
            "responsibilities": [],
            "benefits": [],
            "company_info": {
                "Описание компании": "Не указано",
                "Сфера деятельности": "Не указано",
                "Размер компании": "Не указано",
                "Стадия развития": "Не указано"
            },
            "contact_info": {
                "Контактное лицо": "Не указано",
                "Email": "Не указано",
                "Телефон": "Не указано",
                "Сайт": "Не указано"
            },
            "additional_info": {
                "Процесс отбора": "Не указано",
                "Дополнительные требования": "Не указано",
                "Сроки": "Не указано",
                "Примечания": text[:500] + "..." if len(text) > 500 else text
            }
        }
    
    def analyze_requirements_and_score(self, structured_data: Dict[str, Any], job_title: str) -> Dict[str, Any]:
        """Анализирует требования и распределяет баллы на основе O*NET"""
        
        if not structured_data.get("requirements"):
            return {"error": "Требования не найдены"}
        
        requirements = structured_data["requirements"]
        
        # Собираем все требования в один текст для анализа
        requirements_text = ""
        for key, value in requirements.items():
            if value and value != "Не указано":
                requirements_text += f"{key}: {value}\n"
        
        system_prompt = """Ты - эксперт по анализу требований к профессиям на основе базы данных O*NET. Твоя задача - проанализировать требования к вакансии и распределить 200 баллов между всеми навыками, знаниями и компетенциями.

ВАЖНЫЕ ПРИНЦИПЫ:
1. Используй знания O*NET для определения важности навыков
2. Распределяй баллы пропорционально важности для профессии
3. Учитывай современные требования IT-сферы
4. Общая сумма должна быть ровно 200 баллов
5. Минимальный балл для навыка - 5, максимальный - 50

КАТЕГОРИИ НАВЫКОВ:
- Технические навыки (программирование, фреймворки, технологии)
- Языки программирования (Python, JavaScript, Java, C++, etc.)
- Инструменты разработки (Git, Docker, IDE, базы данных)
- Soft skills (коммуникация, лидерство, работа в команде)
- Специализированные знания (домен, методологии)

ФОРМАТ ОТВЕТА (JSON):
{
    "technical_skills": {
        "название навыка": балл,
        "другой навык": балл
    },
    "programming_languages": {
        "язык программирования": балл
    },
    "tools": {
        "инструмент": балл
    },
    "soft_skills": {
        "навык": балл
    },
    "domain_knowledge": {
        "знание": балл
    },
    "total_score": 200,
    "analysis_summary": "краткое объяснение распределения баллов"
}

Отвечай ТОЛЬКО валидным JSON без дополнительных комментариев."""

        user_prompt = f"""Проанализируй требования к профессии "{job_title}" и распредели 200 баллов между всеми навыками:

ТРЕБОВАНИЯ:
{requirements_text}

Распредели баллы на основе важности каждого навыка для данной профессии согласно стандартам O*NET."""

        try:
            if self.client is None:
                return self._create_fallback_scoring(requirements)
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Убираем возможные markdown блоки
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            scoring_data = json.loads(result_text)
            
            # Валидация: проверяем, что сумма = 200
            total = 0
            for category in ['technical_skills', 'programming_languages', 'tools', 'soft_skills', 'domain_knowledge']:
                if category in scoring_data:
                    for skill, score in scoring_data[category].items():
                        total += score
            
            if total != 200:
                # Нормализуем до 200
                if total > 0:
                    multiplier = 200 / total
                    for category in ['technical_skills', 'programming_languages', 'tools', 'soft_skills', 'domain_knowledge']:
                        if category in scoring_data:
                            for skill in scoring_data[category]:
                                scoring_data[category][skill] = round(scoring_data[category][skill] * multiplier)
            
            scoring_data['total_score'] = 200
            return scoring_data
            
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON в анализе требований: {e}")
            print(f"Ответ ИИ: {result_text}")
            return self._create_fallback_scoring(requirements)
        except Exception as e:
            print(f"Ошибка при анализе требований: {e}")
            return self._create_fallback_scoring(requirements)
    
    def _create_fallback_scoring(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Создает базовое распределение баллов если ИИ недоступен"""
        
        # Извлекаем навыки из требований
        technical_skills = {}
        programming_languages = {}
        tools = {}
        
        # Анализируем технические навыки
        if requirements.get('Технические навыки') and requirements['Технические навыки'] != 'Не указано':
            import re
            tech_skills = re.split(r'[,;]', requirements['Технические навыки'])
            for skill in tech_skills:
                skill = skill.strip()
                if skill:
                    technical_skills[skill] = 20
        
        # Анализируем языки программирования
        if requirements.get('Языки программирования') and requirements['Языки программирования'] != 'Не указано':
            import re
            prog_langs = re.split(r'[,;]', requirements['Языки программирования'])
            for lang in prog_langs:
                lang = lang.strip()
                if lang:
                    programming_languages[lang] = 25
        
        # Анализируем инструменты
        if requirements.get('Инструменты') and requirements['Инструменты'] != 'Не указано':
            import re
            tools_list = re.split(r'[,;]', requirements['Инструменты'])
            for tool in tools_list:
                tool = tool.strip()
                if tool:
                    tools[tool] = 15
        
        # Если навыки не найдены, добавляем примеры
        if not technical_skills and not programming_languages and not tools:
            technical_skills = {"Python": 30, "JavaScript": 25, "React": 20, "Node.js": 15}
            programming_languages = {"Python": 40, "JavaScript": 35, "Java": 25}
            tools = {"Git": 20, "Docker": 15, "VS Code": 10}
        
        return {
            "technical_skills": technical_skills,
            "programming_languages": programming_languages,
            "tools": tools,
            "soft_skills": {},
            "domain_knowledge": {},
            "total_score": 200,
            "analysis_summary": "Базовое распределение баллов (ИИ недоступен)"
        }

    def analyze_resume_against_vacancy(self, resume_text: str, vacancy_structured_data: Dict[str, Any], vacancy_skill_scores: Dict[str, Any]) -> Dict[str, Any]:
        """Анализирует резюме против вакансии и возвращает сопоставление"""
        
        if not self.client:
            return self._create_fallback_resume_analysis(resume_text, vacancy_structured_data, vacancy_skill_scores)
        
        try:
            # Подготавливаем данные вакансии для анализа
            vacancy_info = self._prepare_vacancy_data_for_analysis(vacancy_structured_data, vacancy_skill_scores)
            
            system_prompt = """Ты - эксперт по анализу резюме и сопоставлению кандидатов с вакансиями. Твоя задача - проанализировать резюме кандидата и сопоставить его с требованиями вакансии.

АНАЛИЗ ДОЛЖЕН ВКЛЮЧАТЬ:
1. Сопоставление полей вакансии с данными из резюме
2. Анализ опыта работы (общий и релевантный)
3. Оценка навыков и компетенций
4. Подсчет общего балла соответствия (максимум 200 баллов)

ФОРМАТ ОТВЕТА (строго JSON):
{
    "field_matches": {
        "название_поля_вакансии": {
            "value": "найденное_значение_в_резюме",
            "score": балл_за_это_поле
        }
    },
    "experience": {
        "total_years": "общий_опыт_в_годах",
        "relevant_years": "релевантный_опыт_в_годах", 
        "score": балл_за_опыт
    },
    "skills_matches": {
        "навык": {
            "level": "уровень_владения",
            "score": балл_за_навык
        }
    },
    "total_score": общий_балл_из_200
}

ПРИНЦИПЫ ОЦЕНКИ:
- За полное соответствие требованиям: максимальный балл
- За частичное соответствие: 50-80% от максимального
- За отсутствие: 0 баллов
- Общий балл не должен превышать 200"""
            
            user_prompt = f"""ДАННЫЕ ВАКАНСИИ:
{vacancy_info}

ТЕКСТ РЕЗЮМЕ:
{resume_text}

Проанализируй резюме и сопоставь его с требованиями вакансии. Верни результат в формате JSON."""
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Пытаемся извлечь JSON из ответа
            if result_text.startswith('```json'):
                result_text = result_text[7:-3]
            elif result_text.startswith('```'):
                result_text = result_text[3:-3]
            
            result = json.loads(result_text)
            
            # Валидируем результат
            if not isinstance(result, dict):
                raise ValueError("Результат не является словарем")
            
            # Убеждаемся, что есть все необходимые поля
            if 'field_matches' not in result:
                result['field_matches'] = {}
            if 'experience' not in result:
                result['experience'] = {}
            if 'skills_matches' not in result:
                result['skills_matches'] = {}
            if 'total_score' not in result:
                result['total_score'] = 0
            
            return result
            
        except Exception as e:
            print(f"Ошибка при анализе резюме ИИ: {e}")
            return self._create_fallback_resume_analysis(resume_text, vacancy_structured_data, vacancy_skill_scores)
    
    def _prepare_vacancy_data_for_analysis(self, structured_data: Dict[str, Any], skill_scores: Dict[str, Any]) -> str:
        """Подготавливает данные вакансии для анализа"""
        
        result = []
        
        # Добавляем структурированные данные
        if structured_data:
            result.append("=== ТРЕБОВАНИЯ ВАКАНСИИ ===")
            for block_name, block_data in structured_data.items():
                if isinstance(block_data, dict):
                    result.append(f"\n{block_name}:")
                    for field_name, field_value in block_data.items():
                        if field_value and field_value != 'Не указано':
                            result.append(f"  - {field_name}: {field_value}")
                elif isinstance(block_data, list):
                    result.append(f"\n{block_name}:")
                    for item in block_data:
                        if item and item != 'Не указано':
                            result.append(f"  - {item}")
        
        # Добавляем навыки с баллами
        if skill_scores:
            result.append("\n=== НАВЫКИ И БАЛЛЫ ===")
            for category, skills in skill_scores.items():
                if isinstance(skills, dict) and skills:
                    result.append(f"\n{category}:")
                    for skill, score in skills.items():
                        result.append(f"  - {skill}: {score} баллов")
        
        return "\n".join(result)
    
    def _create_fallback_resume_analysis(self, resume_text: str, vacancy_structured_data: Dict[str, Any], vacancy_skill_scores: Dict[str, Any]) -> Dict[str, Any]:
        """Создает базовый анализ резюме если ИИ недоступен"""
        
        # Простой анализ на основе ключевых слов
        resume_lower = resume_text.lower()
        
        field_matches = {}
        skills_matches = {}
        
        # Анализируем основные поля
        if 'образование' in resume_lower or 'университет' in resume_lower or 'институт' in resume_lower:
            field_matches['Образование'] = {'value': 'Найдено в резюме', 'score': 20}
        
        if 'опыт' in resume_lower or 'работал' in resume_lower or 'стаж' in resume_lower:
            field_matches['Опыт работы'] = {'value': 'Найден в резюме', 'score': 25}
        
        # Анализируем навыки
        common_skills = ['python', 'javascript', 'java', 'react', 'angular', 'vue', 'node.js', 'git', 'docker', 'sql']
        for skill in common_skills:
            if skill in resume_lower:
                skills_matches[skill.title()] = {'level': 'Упоминается', 'score': 15}
        
        # Простой анализ опыта
        experience = {
            'total_years': 'Не определен',
            'relevant_years': 'Не определен', 
            'score': 20
        }
        
        return {
            'field_matches': field_matches,
            'experience': experience,
            'skills_matches': skills_matches,
            'total_score': sum([match['score'] for match in field_matches.values()]) + 
                          sum([match['score'] for match in skills_matches.values()]) + 
                          experience['score']
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
        
        # Информация о компании
        if structured_data.get("company_info"):
            result.append("=== ИНФОРМАЦИЯ О КОМПАНИИ ===")
            for key, value in structured_data["company_info"].items():
                if value and value != "Не указано":
                    result.append(f"{key}: {value}")
            result.append("")
        
        # Контактная информация
        if structured_data.get("contact_info"):
            result.append("=== КОНТАКТНАЯ ИНФОРМАЦИЯ ===")
            for key, value in structured_data["contact_info"].items():
                if value and value != "Не указано":
                    result.append(f"{key}: {value}")
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