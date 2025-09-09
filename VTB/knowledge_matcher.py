#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Any, Tuple
import re

class KnowledgeMatcher:
    """Класс для сопоставления требований вакансии с Knowledge Areas"""
    
    def __init__(self):
        # Маппинг русских терминов на английские Knowledge Areas
        self.knowledge_mapping = {
            # Технические области
            "программирование": ["Computer and Electronics", "Programming"],
            "python": ["Computer and Electronics", "Programming"],
            "javascript": ["Computer and Electronics", "Programming"],
            "java": ["Computer and Electronics", "Programming"],
            "c++": ["Computer and Electronics", "Programming"],
            "разработка": ["Computer and Electronics", "Programming"],
            "веб-разработка": ["Computer and Electronics", "Programming"],
            "базы данных": ["Computer and Electronics", "Data Base Management"],
            "sql": ["Computer and Electronics", "Data Base Management"],
            "postgresql": ["Computer and Electronics", "Data Base Management"],
            "mysql": ["Computer and Electronics", "Data Base Management"],
            "git": ["Computer and Electronics", "Programming"],
            "docker": ["Computer and Electronics", "Programming"],
            "kubernetes": ["Computer and Electronics", "Programming"],
            "linux": ["Computer and Electronics", "Operating Systems"],
            "windows": ["Computer and Electronics", "Operating Systems"],
            "сети": ["Computer and Electronics", "Telecommunications"],
            "lan": ["Computer and Electronics", "Telecommunications"],
            "san": ["Computer and Electronics", "Telecommunications"],
            "сервер": ["Computer and Electronics", "Telecommunications"],
            "оборудование": ["Computer and Electronics", "Telecommunications"],
            "hardware": ["Computer and Electronics", "Telecommunications"],
            
            # Управление и администрирование
            "управление": ["Administration and Management"],
            "менеджмент": ["Administration and Management"],
            "проект": ["Administration and Management", "Project Management"],
            "планирование": ["Administration and Management"],
            "координация": ["Administration and Management"],
            "руководство": ["Administration and Management"],
            "лидерство": ["Administration and Management"],
            "стратегия": ["Administration and Management"],
            
            # Клиентский сервис
            "клиент": ["Customer and Personal Service"],
            "пользователь": ["Customer and Personal Service"],
            "поддержка": ["Customer and Personal Service"],
            "сервис": ["Customer and Personal Service"],
            "консультация": ["Customer and Personal Service"],
            
            # Коммуникации
            "английский": ["English Language", "Foreign Language"],
            "язык": ["English Language", "Foreign Language"],
            "коммуникация": ["Communications and Media"],
            "презентация": ["Communications and Media"],
            "документация": ["Communications and Media", "Clerical"],
            "отчет": ["Communications and Media", "Clerical"],
            
            # Бизнес и финансы
            "бизнес": ["Business and Economics"],
            "экономика": ["Business and Economics"],
            "финансы": ["Business and Economics", "Economics and Accounting"],
            "бухгалтерия": ["Economics and Accounting"],
            "бюджет": ["Economics and Accounting"],
            "анализ": ["Business and Economics", "Mathematics"],
            "статистика": ["Mathematics"],
            "математика": ["Mathematics"],
            
            # HR и персонал
            "персонал": ["Personnel and Human Resources"],
            "hr": ["Personnel and Human Resources"],
            "рекрутинг": ["Personnel and Human Resources"],
            "обучение": ["Personnel and Human Resources", "Education and Training"],
            "тренинг": ["Personnel and Human Resources", "Education and Training"],
            
            # Образование
            "образование": ["Education and Training"],
            "педагогика": ["Education and Training"],
            "преподавание": ["Education and Training"],
            
            # Право
            "право": ["Law and Government"],
            "юридический": ["Law and Government"],
            "закон": ["Law and Government"],
            "договор": ["Law and Government"],
            
            # Медицина
            "медицина": ["Medicine and Dentistry"],
            "здоровье": ["Medicine and Dentistry"],
            "медицинский": ["Medicine and Dentistry"],
            
            # Дизайн и творчество
            "дизайн": ["Design", "Fine Arts"],
            "графика": ["Design", "Fine Arts"],
            "ui": ["Design", "Fine Arts"],
            "ux": ["Design", "Fine Arts"],
            "интерфейс": ["Design", "Fine Arts"],
            
            # Маркетинг и продажи
            "маркетинг": ["Sales and Marketing"],
            "продажи": ["Sales and Marketing"],
            "реклама": ["Sales and Marketing"],
            "smm": ["Sales and Marketing"],
            "seo": ["Sales and Marketing"],
            
            # Производство
            "производство": ["Production and Processing"],
            "изготовление": ["Production and Processing"],
            "сборка": ["Production and Processing"],
            "контроль качества": ["Production and Processing"],
            
            # Безопасность
            "безопасность": ["Public Safety and Security"],
            "охрана": ["Public Safety and Security"],
            "защита": ["Public Safety and Security"],
            
            # Транспорт
            "транспорт": ["Transportation"],
            "логистика": ["Transportation"],
            "доставка": ["Transportation"],
            
            # Строительство
            "строительство": ["Building and Construction"],
            "ремонт": ["Building and Construction"],
            "монтаж": ["Building and Construction"],
            
            # Офисные навыки
            "excel": ["Clerical"],
            "word": ["Clerical"],
            "powerpoint": ["Clerical"],
            "офис": ["Clerical"],
            "делопроизводство": ["Clerical"],
            "архив": ["Clerical"],
            
            # Личные качества (общие)
            "ответственность": ["General Skills"],
            "командная работа": ["General Skills"],
            "адаптивность": ["General Skills"],
            "креативность": ["General Skills"],
            "аналитическое мышление": ["General Skills"],
            "решение проблем": ["General Skills"]
        }
    
    def extract_requirements_from_vacancy(self, structured_data: Dict[str, Any]) -> List[str]:
        """Извлекает все требования из структурированных данных вакансии"""
        requirements = []
        
        # Из требований
        if structured_data.get("requirements"):
            req_dict = structured_data["requirements"]
            for key, value in req_dict.items():
                if value and value != "Не указано":
                    requirements.append(f"{key}: {value}")
        
        # Из обязанностей
        if structured_data.get("responsibilities"):
            for resp in structured_data["responsibilities"]:
                if resp and resp != "Не указано":
                    requirements.append(f"Обязанность: {resp}")
        
        # Из дополнительной информации
        if structured_data.get("additional_info"):
            add_info = structured_data["additional_info"]
            for key, value in add_info.items():
                if value and value != "Не указано" and key != "Контактная информация":
                    requirements.append(f"{key}: {value}")
        
        return requirements
    
    def find_matching_knowledge_areas(self, requirements: List[str], available_knowledge: Dict[str, Any]) -> Dict[str, List[str]]:
        """Находит соответствия между требованиями и Knowledge Areas"""
        matches = {}
        
        for req in requirements:
            req_lower = req.lower()
            matched_areas = []
            
            # Ищем совпадения в маппинге
            for term, knowledge_areas in self.knowledge_mapping.items():
                if term in req_lower:
                    for area in knowledge_areas:
                        if area in available_knowledge:
                            matched_areas.append(area)
            
            if matched_areas:
                matches[req] = matched_areas
        
        return matches
    
    def find_missing_knowledge_areas(self, matched_areas: Dict[str, List[str]], available_knowledge: Dict[str, Any]) -> List[str]:
        """Находит Knowledge Areas, которые есть в базе, но не покрыты требованиями"""
        used_areas = set()
        for areas in matched_areas.values():
            used_areas.update(areas)
        
        missing_areas = []
        for area, data in available_knowledge.items():
            # Извлекаем важность (IM) из структуры данных
            if isinstance(data, dict) and 'IM' in data:
                importance = data['IM']
            elif isinstance(data, (int, float)):
                importance = data
            else:
                continue
                
            if area not in used_areas and importance >= 3.0:  # Только важные области (3.0+)
                missing_areas.append((area, importance))
        
        return missing_areas
    
    def calculate_knowledge_scores(self, job_knowledge: Dict[str, Any], top_areas: List[Tuple[str, float]] = None) -> Dict[str, float]:
        """Распределяет 100 баллов между TOP Knowledge Areas в зависимости от их рейтинга"""
        # Если переданы топ-области, используем их, иначе берем все
        if top_areas:
            knowledge_ratings = dict(top_areas)
        else:
            # Извлекаем рейтинги важности (IM) для всех областей
            knowledge_ratings = {}
            for area, data in job_knowledge.items():
                if isinstance(data, dict) and 'IM' in data:
                    knowledge_ratings[area] = data['IM']
                elif isinstance(data, (int, float)):
                    knowledge_ratings[area] = data
        
        if not knowledge_ratings:
            return {}
        
        # Сортируем по рейтингу (от низкого к высокому)
        sorted_areas = sorted(knowledge_ratings.items(), key=lambda x: x[1])
        
        # Вычисляем веса для обратного распределения
        # Чем выше рейтинг, тем меньше баллов (меньше внимания требуется)
        total_weight = 0
        weights = {}
        
        for area, rating in sorted_areas:
            # Обратный вес: 6.0 - rating (максимальный рейтинг 5.0, добавляем 1.0 для избежания нуля)
            weight = 6.0 - rating
            weights[area] = weight
            total_weight += weight
        
        # Распределяем 100 баллов пропорционально весам
        scores = {}
        for area, weight in weights.items():
            score = (weight / total_weight) * 100
            scores[area] = round(score, 1)
        
        return scores
    
    def get_top_knowledge_areas(self, job_knowledge: Dict[str, Any], limit: int = 5) -> List[Tuple[str, float]]:
        """Извлекает топ-N областей знаний по важности"""
        knowledge_items = []
        for name, data in job_knowledge.items():
            if isinstance(data, dict) and 'IM' in data:
                knowledge_items.append((name, data['IM']))
            elif isinstance(data, (int, float)):
                knowledge_items.append((name, data))
        
        # Сортируем по важности (от большего к меньшему)
        knowledge_items.sort(key=lambda x: x[1], reverse=True)
        return knowledge_items[:limit]
    
    def find_unmatched_requirements(self, requirements: List[str], matches: Dict[str, List[str]]) -> List[str]:
        """Находит требования, которые не подошли ни под какую категорию"""
        matched_requirements = set(matches.keys())
        unmatched = []
        
        for req in requirements:
            if req not in matched_requirements:
                unmatched.append(req)
        
        return unmatched
    
    def distribute_unmatched_scores(self, unmatched_requirements: List[str]) -> Dict[str, float]:
        """Распределяет 100 баллов между несоответствующими требованиями"""
        if not unmatched_requirements:
            return {}
        
        # Равномерно распределяем 100 баллов между всеми несоответствующими требованиями
        score_per_requirement = 100.0 / len(unmatched_requirements)
        
        scores = {}
        for req in unmatched_requirements:
            scores[req] = round(score_per_requirement, 1)
        
        return scores
    
    def analyze_knowledge_coverage(self, structured_data: Dict[str, Any], job_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Основная функция анализа покрытия знаний"""
        # Извлекаем требования
        requirements = self.extract_requirements_from_vacancy(structured_data)
        
        # Находим соответствия
        matches = self.find_matching_knowledge_areas(requirements, job_knowledge)
        
        # Находим недостающие области
        missing_areas = self.find_missing_knowledge_areas(matches, job_knowledge)
        
        # Сортируем недостающие области по важности
        missing_areas.sort(key=lambda x: x[1], reverse=True)
        
        # Получаем топ-5 областей знаний
        top_knowledge_areas = self.get_top_knowledge_areas(job_knowledge, 5)
        
        # Вычисляем баллы только для топ-областей знаний (100 баллов)
        knowledge_scores = self.calculate_knowledge_scores(job_knowledge, top_knowledge_areas)
        
        # Находим требования, которые не подошли ни под какую категорию
        unmatched_requirements = self.find_unmatched_requirements(requirements, matches)
        
        # Распределяем 100 баллов между несоответствующими требованиями
        unmatched_scores = self.distribute_unmatched_scores(unmatched_requirements)
        
        return {
            "requirements": requirements,
            "matches": matches,
            "missing_areas": missing_areas,
            "top_knowledge_areas": top_knowledge_areas,
            "knowledge_scores": knowledge_scores,
            "unmatched_requirements": unmatched_requirements,
            "unmatched_scores": unmatched_scores,
            "coverage_percentage": len(set().union(*matches.values())) / len(job_knowledge) * 100 if matches else 0
        }
    
    def format_analysis_result(self, analysis: Dict[str, Any]) -> str:
        """Форматирует результат анализа для вывода"""
        result = []
        
        result.append("🔍 АНАЛИЗ СООТВЕТСТВИЯ ТРЕБОВАНИЙ И ЗНАНИЙ")
        result.append("=" * 50)
        
        # Покрытие
        result.append(f"\n📊 Покрытие знаний: {analysis['coverage_percentage']:.1f}%")
        
        # Распределение баллов для TOP Knowledge Areas
        if analysis.get('knowledge_scores') and analysis.get('top_knowledge_areas'):
            result.append(f"\n🎯 РАСПРЕДЕЛЕНИЕ БАЛЛОВ - ГРУППА 1 (100 баллов среди TOP Knowledge Areas):")
            result.append("Области знаний, отсортированные по приоритету развития:")
            
            # Сортируем по баллам (от большего к меньшему)
            sorted_scores = sorted(analysis['knowledge_scores'].items(), key=lambda x: x[1], reverse=True)
            
            for i, (area, score) in enumerate(sorted_scores, 1):
                # Находим оригинальный рейтинг для этой области
                original_rating = next((rating for name, rating in analysis['top_knowledge_areas'] if name == area), 0)
                result.append(f"   {i:2d}. {area}: {score} баллов (рейтинг: {original_rating:.1f}/5.0)")
        
        # Распределение баллов для несоответствующих требований
        if analysis.get('unmatched_scores'):
            result.append(f"\n🎯 РАСПРЕДЕЛЕНИЕ БАЛЛОВ - ГРУППА 2 (100 баллов для несоответствующих требований):")
            result.append("Требования, которые не подошли ни под какую категорию:")
            
            for i, (req, score) in enumerate(analysis['unmatched_scores'].items(), 1):
                result.append(f"   {i:2d}. {req}: {score} баллов")
        
        # Соответствия
        if analysis['matches']:
            result.append(f"\n✅ НАЙДЕННЫЕ СООТВЕТСТВИЯ:")
            for req, areas in analysis['matches'].items():
                result.append(f"\n📋 Требование: {req}")
                for area in areas:
                    score = analysis.get('knowledge_scores', {}).get(area, 0)
                    result.append(f"   → {area} ({score} баллов)")
        
        # Недостающие области
        if analysis['missing_areas']:
            result.append(f"\n⚠️ РЕКОМЕНДУЕМЫЕ ДОПОЛНЕНИЯ:")
            result.append("Следующие важные области знаний не покрыты требованиями:")
            for area, importance in analysis['missing_areas'][:5]:  # Топ-5
                score = analysis.get('knowledge_scores', {}).get(area, 0)
                result.append(f"   • {area} (важность: {importance:.1f}/5.0, баллов: {score})")
        
        return "\n".join(result)

def main():
    """Тестовая функция"""
    matcher = KnowledgeMatcher()
    
    # Тестовые данные
    test_vacancy = {
        "requirements": {
            "Технические навыки": "Python, Django, PostgreSQL, Git",
            "Опыт работы": "2-3 года",
            "Иностранные языки": "Английский intermediate"
        },
        "responsibilities": [
            "Разработка веб-приложений",
            "Работа с базами данных",
            "Управление проектами"
        ]
    }
    
    test_knowledge = {
        "Computer and Electronics": {"IM": 4.5, "LV": 5.0},
        "Programming": {"IM": 4.2, "LV": 4.8},
        "Data Base Management": {"IM": 3.8, "LV": 4.2},
        "English Language": {"IM": 3.5, "LV": 3.8},
        "Administration and Management": {"IM": 4.0, "LV": 4.5},
        "Customer and Personal Service": {"IM": 3.2, "LV": 3.5}
    }
    
    analysis = matcher.analyze_knowledge_coverage(test_vacancy, test_knowledge)
    result = matcher.format_analysis_result(analysis)
    print(result)

if __name__ == "__main__":
    main()
