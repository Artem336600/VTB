import json
import re
from typing import Dict, Any

class AIStructuredExtractor:
    """Класс для структурирования текста резюме с помощью простого анализа"""
    
    def __init__(self):
        # Простая версия без внешних API
        pass
    
    def structure_vacancy_text(self, extracted_text: str) -> Dict[str, Any]:
        """Структурирует текст вакансии с помощью улучшенного анализа"""
        
        # Улучшенный анализ текста для извлечения информации
        job_info = self._extract_job_info(extracted_text)
        salary = self._extract_salary(extracted_text)
        requirements = self._extract_requirements(extracted_text)
        responsibilities = self._extract_responsibilities(extracted_text)
        benefits = self._extract_benefits(extracted_text)
        company_info = self._extract_company_info(extracted_text)
        contact_info = self._extract_contact_info(extracted_text)
        
        return {
            "job_info": job_info,
            "salary": salary,
            "requirements": requirements,
            "responsibilities": responsibilities,
            "benefits": benefits,
            "company_info": company_info,
            "contact_info": contact_info,
            "additional_info": {
                "Процесс отбора": self._extract_selection_process(extracted_text),
                "Дополнительные требования": self._extract_additional_requirements(extracted_text),
                "Сроки": self._extract_deadlines(extracted_text)
            }
        }
    
    def _extract_job_info(self, text: str) -> Dict[str, str]:
        """Извлекает основную информацию о вакансии с улучшенным анализом"""
        job_info = {
            "Название должности": "Не указано",
            "Компания": "Не указано",
            "Тип занятости": "Не указано",
            "График работы": "Не указано",
            "Местоположение": "Не указано",
            "Уровень": "Не указано",
            "Опыт работы": "Не указано",
            "Образование": "Не указано"
        }
        
        lines = text.split('\n')
        
        # Поиск названия должности - более точный
        job_titles = [
            'разработчик', 'developer', 'программист', 'аналитик', 'менеджер', 
            'дизайнер', 'тестировщик', 'архитектор', 'лид', 'lead', 'senior',
            'junior', 'middle', 'стажер', 'инженер', 'специалист', 'консультант'
        ]
        
        for i, line in enumerate(lines[:15]):  # Ищем в первых 15 строках
            line = line.strip()
            if line and len(line) > 3 and len(line) < 100:
                # Проверяем, что это не заголовок секции
                if not any(section in line.lower() for section in ['требования', 'обязанности', 'условия', 'зарплата', 'контакты']):
                    if any(title in line.lower() for title in job_titles):
                        job_info["Название должности"] = line
                        break
        
        # Поиск компании - улучшенный
        company_patterns = [
            r'компания[:\s]+([^\n]+)',
            r'ооо[:\s]+([^\n]+)',
            r'зао[:\s]+([^\n]+)',
            r'оао[:\s]+([^\n]+)',
            r'ип[:\s]+([^\n]+)',
            r'работодатель[:\s]+([^\n]+)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if len(company) > 2 and len(company) < 100:
                    job_info["Компания"] = company
                    break
        
        # Поиск типа занятости
        employment_types = {
            'полная занятость': ['полная занятость', 'full-time', 'полный день'],
            'частичная занятость': ['частичная занятость', 'part-time', 'частичный день'],
            'проектная работа': ['проектная работа', 'project work', 'проект'],
            'стажировка': ['стажировка', 'internship', 'стажер'],
            'удаленная работа': ['удаленная работа', 'remote', 'удаленно']
        }
        
        for emp_type, keywords in employment_types.items():
            if any(keyword in text.lower() for keyword in keywords):
                job_info["Тип занятости"] = emp_type
                break
        
        # Поиск графика работы
        schedule_patterns = [
            r'график[:\s]+([^\n]+)',
            r'режим работы[:\s]+([^\n]+)',
            r'рабочий день[:\s]+([^\n]+)'
        ]
        
        for pattern in schedule_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                schedule = match.group(1).strip()
                if len(schedule) > 2 and len(schedule) < 50:
                    job_info["График работы"] = schedule
                    break
        
        # Поиск местоположения - улучшенный
        location_patterns = [
            r'местоположение[:\s]+([^\n]+)',
            r'адрес[:\s]+([^\n]+)',
            r'город[:\s]+([^\n]+)',
            r'расположение[:\s]+([^\n]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 2 and len(location) < 100:
                    job_info["Местоположение"] = location
                    break
        
        # Если не нашли через паттерны, ищем по ключевым словам
        if job_info["Местоположение"] == "Не указано":
            location_keywords = ['москва', 'санкт-петербург', 'екатеринбург', 'новосибирск', 'удаленно', 'remote', 'офис', 'гибрид']
            for line in lines:
                for keyword in location_keywords:
                    if keyword in line.lower():
                        job_info["Местоположение"] = line.strip()
                        break
                if job_info["Местоположение"] != "Не указано":
                    break
        
        # Поиск уровня позиции
        level_keywords = {
            'Junior': ['junior', 'джуниор', 'стажер', 'начинающий'],
            'Middle': ['middle', 'мидл', 'средний'],
            'Senior': ['senior', 'сеньор', 'старший', 'ведущий'],
            'Lead': ['lead', 'лид', 'руководитель', 'team lead']
        }
        
        for level, keywords in level_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                job_info["Уровень"] = level
                break
        
        return job_info
    
    def _extract_salary(self, text: str) -> Dict[str, str]:
        """Извлекает информацию о зарплате с улучшенным анализом"""
        salary = {
            "Зарплата от": "Не указано",
            "Зарплата до": "Не указано",
            "Валюта": "RUB",
            "Тип оплаты": "Не указано",
            "Бонусы": "Не указано",
            "Форма оплаты": "Не указано"
        }
        
        # Улучшенные паттерны для поиска зарплаты
        salary_patterns = [
            # Диапазон зарплат
            r'от\s+(\d+[\s\d]*)\s*до\s+(\d+[\s\d]*)\s*(руб|₽|rub|usd|\$|eur|€)',
            r'(\d+[\s\d]*)\s*-\s*(\d+[\s\d]*)\s*(руб|₽|rub|usd|\$|eur|€)',
            r'(\d+[\s\d]*)\s*\.\.\.\s*(\d+[\s\d]*)\s*(руб|₽|rub|usd|\$|eur|€)',
            r'(\d+[\s\d]*)\s*—\s*(\d+[\s\d]*)\s*(руб|₽|rub|usd|\$|eur|€)',
            
            # От определенной суммы
            r'от\s+(\d+[\s\d]*)\s*(руб|₽|rub|usd|\$|eur|€)',
            r'от\s+(\d+[\s\d]*)\s*тыс\.?\s*(руб|₽|rub)',
            
            # До определенной суммы
            r'до\s+(\d+[\s\d]*)\s*(руб|₽|rub|usd|\$|eur|€)',
            r'до\s+(\d+[\s\d]*)\s*тыс\.?\s*(руб|₽|rub)',
            
            # Фиксированная зарплата
            r'(\d+[\s\d]*)\s*(руб|₽|rub|usd|\$|eur|€)',
            r'(\d+[\s\d]*)\s*тыс\.?\s*(руб|₽|rub)',
            
            # Зарплата в тысячах
            r'от\s+(\d+)\s*тыс\.?\s*до\s+(\d+)\s*тыс\.?\s*(руб|₽|rub)',
            r'(\d+)\s*тыс\.?\s*-\s*(\d+)\s*тыс\.?\s*(руб|₽|rub)'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                # Определяем валюту
                if len(groups) >= 3 and groups[2]:
                    currency_map = {
                        'руб': 'RUB', '₽': 'RUB', 'rub': 'RUB',
                        'usd': 'USD', '$': 'USD',
                        'eur': 'EUR', '€': 'EUR'
                    }
                    salary["Валюта"] = currency_map.get(groups[2].lower(), 'RUB')
                
                # Обрабатываем суммы
                if len(groups) >= 2 and groups[0] and groups[1]:
                    # Диапазон зарплат
                    if 'тыс' in pattern:
                        # Зарплата в тысячах
                        salary["Зарплата от"] = str(int(groups[0]) * 1000)
                        salary["Зарплата до"] = str(int(groups[1]) * 1000)
                    else:
                        salary["Зарплата от"] = groups[0].replace(' ', '')
                        salary["Зарплата до"] = groups[1].replace(' ', '')
                elif len(groups) >= 1 and groups[0]:
                    # Одна сумма
                    amount = groups[0].replace(' ', '')
                    if 'тыс' in pattern:
                        amount = str(int(amount) * 1000)
                    
                    if 'от' in match.group(0).lower():
                        salary["Зарплата от"] = amount
                    elif 'до' in match.group(0).lower():
                        salary["Зарплата до"] = amount
                    else:
                        # Фиксированная зарплата
                        salary["Зарплата от"] = amount
                        salary["Зарплата до"] = amount
                
                break
        
        # Поиск типа оплаты
        payment_types = {
            'Оклад': ['оклад', 'salary', 'фиксированная'],
            'Почасовая': ['почасовая', 'hourly', 'час'],
            'Процентная': ['процентная', 'percentage', '%'],
            'Сдельная': ['сдельная', 'piecework', 'за проект']
        }
        
        for payment_type, keywords in payment_types.items():
            if any(keyword in text.lower() for keyword in keywords):
                salary["Тип оплаты"] = payment_type
                break
        
        # Поиск бонусов
        bonus_patterns = [
            r'бонус[ы]?[:\s]+([^\n]+)',
            r'преми[ия]?[:\s]+([^\n]+)',
            r'дополнительно[:\s]+([^\n]+)'
        ]
        
        for pattern in bonus_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                bonus = match.group(1).strip()
                if len(bonus) > 2 and len(bonus) < 100:
                    salary["Бонусы"] = bonus
                    break
        
        return salary
    
    def _extract_requirements(self, text: str) -> Dict[str, str]:
        """Извлекает требования с улучшенным анализом"""
        requirements = {
            "Опыт работы": "Не указано",
            "Образование": "Не указано",
            "Технические навыки": "Не указано",
            "Языки программирования": "Не указано",
            "Инструменты": "Не указано",
            "Иностранные языки": "Не указано",
            "Личные качества": "Не указано",
            "Сертификаты": "Не указано",
            "Возраст": "Не указано"
        }
        
        # Поиск опыта работы - улучшенный
        experience_patterns = [
            r'опыт\s+работы[:\s]+(\d+[\s\d]*\s*лет)',
            r'(\d+[\s\d]*\s*лет)\s+опыта',
            r'опыт[:\s]+(\d+[\s\d]*\s*лет)',
            r'стаж[:\s]+(\d+[\s\d]*\s*лет)',
            r'от\s+(\d+)\s*лет\s+опыта',
            r'не\s+менее\s+(\d+)\s*лет'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                requirements["Опыт работы"] = match.group(1)
                break
        
        # Поиск образования
        education_patterns = [
            r'образование[:\s]+([^\n]+)',
            r'высшее\s+образование[:\s]+([^\n]+)',
            r'среднее\s+образование[:\s]+([^\n]+)',
            r'университет[:\s]+([^\n]+)',
            r'институт[:\s]+([^\n]+)'
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                education = match.group(1).strip()
                if len(education) > 2 and len(education) < 100:
                    requirements["Образование"] = education
                    break
        
        # Поиск технических навыков - расширенный список
        tech_skills = []
        tech_keywords = {
            'Языки программирования': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'haskell', 'clojure', 'erlang'
            ],
            'Фреймворки': [
                'django', 'flask', 'fastapi', 'spring', 'hibernate', 'react', 'vue', 'angular', 'ember',
                'backbone', 'express', 'koa', 'laravel', 'symfony', 'rails', 'sinatra', 'gin', 'echo'
            ],
            'Базы данных': [
                'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'oracle',
                'sqlite', 'mariadb', 'neo4j', 'influxdb', 'couchdb', 'dynamodb'
            ],
            'Инструменты': [
                'git', 'docker', 'kubernetes', 'jenkins', 'ansible', 'terraform', 'vagrant',
                'nginx', 'apache', 'rabbitmq', 'kafka', 'grafana', 'prometheus', 'splunk'
            ],
            'Облачные платформы': [
                'aws', 'azure', 'gcp', 'heroku', 'digitalocean', 'linode', 'vultr'
            ]
        }
        
        for category, keywords in tech_keywords.items():
            found_skills = []
            for keyword in keywords:
                if keyword in text.lower():
                    found_skills.append(keyword.title())
            
            if found_skills:
                if category == 'Языки программирования':
                    requirements["Языки программирования"] = ', '.join(found_skills)
                elif category == 'Инструменты':
                    requirements["Инструменты"] = ', '.join(found_skills)
                else:
                    if requirements["Технические навыки"] == "Не указано":
                        requirements["Технические навыки"] = f"{category}: {', '.join(found_skills)}"
                    else:
                        requirements["Технические навыки"] += f"; {category}: {', '.join(found_skills)}"
        
        # Поиск иностранных языков
        language_patterns = [
            r'английский[:\s]+([^\n]+)',
            r'english[:\s]+([^\n]+)',
            r'немецкий[:\s]+([^\n]+)',
            r'французский[:\s]+([^\n]+)',
            r'китайский[:\s]+([^\n]+)',
            r'японский[:\s]+([^\n]+)'
        ]
        
        languages = []
        for pattern in language_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                language_info = match.group(1).strip()
                if len(language_info) > 1 and len(language_info) < 50:
                    languages.append(f"{pattern.split('[')[0]}: {language_info}")
        
        if languages:
            requirements["Иностранные языки"] = '; '.join(languages)
        
        # Поиск личных качеств
        personal_qualities = []
        quality_keywords = [
            'ответственность', 'коммуникабельность', 'стрессоустойчивость', 'аналитическое мышление',
            'креативность', 'лидерство', 'командная работа', 'самообучение', 'инициативность',
            'внимательность', 'пунктуальность', 'целеустремленность'
        ]
        
        for quality in quality_keywords:
            if quality in text.lower():
                personal_qualities.append(quality)
        
        if personal_qualities:
            requirements["Личные качества"] = ', '.join(personal_qualities)
        
        # Поиск сертификатов
        cert_patterns = [
            r'сертификат[ы]?[:\s]+([^\n]+)',
            r'certificate[:\s]+([^\n]+)',
            r'certification[:\s]+([^\n]+)'
        ]
        
        for pattern in cert_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cert = match.group(1).strip()
                if len(cert) > 2 and len(cert) < 100:
                    requirements["Сертификаты"] = cert
                    break
        
        # Поиск возраста
        age_patterns = [
            r'возраст[:\s]+(\d+[\s\d]*\s*лет)',
            r'от\s+(\d+)\s*до\s+(\d+)\s*лет',
            r'не\s+старше\s+(\d+)\s*лет',
            r'не\s+младше\s+(\d+)\s*лет'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    requirements["Возраст"] = f"от {match.group(1)} до {match.group(2)} лет"
                else:
                    requirements["Возраст"] = match.group(1)
                break
        
        return requirements
    
    def _extract_responsibilities(self, text: str) -> list:
        """Извлекает обязанности"""
        responsibilities = []
        
        # Ищем секцию с обязанностями
        lines = text.split('\n')
        in_responsibilities = False
        
        for line in lines:
            line = line.strip()
            if 'обязанности' in line.lower() or 'задачи' in line.lower():
                in_responsibilities = True
                continue
            
            if in_responsibilities:
                if line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')):
                    # Убираем маркеры списка
                    clean_line = re.sub(r'^[-•*]\s*|\d+\.\s*', '', line)
                    if clean_line and len(clean_line) > 10:
                        responsibilities.append(clean_line)
                elif line and not line.startswith(('Требования', 'Условия', 'Зарплата')):
                    if len(line) > 10:
                        responsibilities.append(line)
                else:
                    break
        
        return responsibilities[:10]  # Ограничиваем количество
    
    def _extract_benefits(self, text: str) -> list:
        """Извлекает преимущества"""
        benefits = []
        
        # Ищем секцию с условиями/преимуществами
        lines = text.split('\n')
        in_benefits = False
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['условия', 'преимущества', 'бонусы', 'что мы предлагаем']):
                in_benefits = True
                continue
            
            if in_benefits:
                if line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')):
                    # Убираем маркеры списка
                    clean_line = re.sub(r'^[-•*]\s*|\d+\.\s*', '', line)
                    if clean_line and len(clean_line) > 5:
                        benefits.append(clean_line)
                elif line and not line.startswith(('Требования', 'Обязанности', 'Зарплата')):
                    if len(line) > 5:
                        benefits.append(line)
                else:
                    break
        
        return benefits[:10]  # Ограничиваем количество
    
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
