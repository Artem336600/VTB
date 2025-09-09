from openai import OpenAI
import json
import re

class ZoneJobBot:
    def __init__(self):
        self.client = OpenAI(
            api_key="sk-7446c16774044136aa33ab1b74eb1b31", 
            base_url="https://api.deepseek.com"
        )
        
        self.job_zones = {
            1: {
                "name": "Зона 1: Минимальная подготовка", 
                "description": """
📚 ОБРАЗОВАНИЕ: Среднее образование или ниже
⏱️ ОПЫТ: Минимальный или отсутствует
🎓 ОБУЧЕНИЕ: Несколько дней - несколько месяцев
💼 ХАРАКТЕРИСТИКИ: Простые повторяющиеся задачи, работа по инструкциям, минимальная ответственность
📈 КАРЬЕРА: Ограниченные возможности роста, низкая заработная плата
🔧 НАВЫКИ: Базовые навыки общения, физическая выносливость, внимательность
                """.strip(),
                "examples": "Официанты, уборщики, грузчики, кассиры, охранники, дворники, разнорабочие, курьеры, упаковщики, контролеры"
            },
            2: {
                "name": "Зона 2: Некоторая подготовка", 
                "description": """
📚 ОБРАЗОВАНИЕ: Среднее образование обязательно
⏱️ ОПЫТ: Несколько месяцев - 1 год
🎓 ОБУЧЕНИЕ: 3-12 месяцев обучения или стажировки
💼 ХАРАКТЕРИСТИКИ: Работа с клиентами, базовые технические навыки, средняя ответственность
📈 КАРЬЕРА: Возможности роста до супервизора, средняя заработная плата
🔧 НАВЫКИ: Коммуникативные навыки, работа с техникой, решение простых проблем
                """.strip(),
                "examples": "Продавцы, операторы, помощники, лаборанты, техники, консультанты, секретари, кладовщики, операторы колл-центра"
            },
            3: {
                "name": "Зона 3: Средняя подготовка", 
                "description": """
📚 ОБРАЗОВАНИЕ: Профессиональное образование, сертификаты, степень младшего специалиста
⏱️ ОПЫТ: 1-3 года
🎓 ОБУЧЕНИЕ: 1-2 года профессиональной подготовки
💼 ХАРАКТЕРИСТИКИ: Специализированные навыки, работа с оборудованием, техническая ответственность
📈 КАРЬЕРА: Возможности стать мастером или супервизором, хорошая заработная плата
🔧 НАВЫКИ: Технические навыки, решение проблем, работа в команде, специализированные знания
                """.strip(),
                "examples": "Электрики, медсестры, техники по ремонту, специалисты по IT, мастера производства, инспекторы, фельдшеры, координаторы"
            },
            4: {
                "name": "Зона 4: Значительная подготовка", 
                "description": """
📚 ОБРАЗОВАНИЕ: Высшее образование (бакалавриат) обязательно
⏱️ ОПЫТ: 3-5 лет
🎓 ОБУЧЕНИЕ: 4+ года высшего образования + постоянное обучение
💼 ХАРАКТЕРИСТИКИ: Управленческие функции, сложные проекты, высокая ответственность
📈 КАРЬЕРА: Возможности стать директором, высокая заработная плата, престиж
🔧 НАВЫКИ: Лидерство, стратегическое мышление, управление проектами, аналитические способности
                """.strip(),
                "examples": "Разработчики программного обеспечения, веб-разработчики, Data Scientist, системные администраторы, менеджеры, инженеры, дизайнеры, аналитики, консультанты, руководители, бухгалтеры"
            },
            5: {
                "name": "Зона 5: Обширная подготовка", 
                "description": """
📚 ОБРАЗОВАНИЕ: Магистратура, докторантура, профессиональные степени (MD, JD, PhD)
⏱️ ОПЫТ: 5+ лет
🎓 ОБУЧЕНИЕ: 6-12+ лет образования + постоянное профессиональное развитие
💼 ХАРАКТЕРИСТИКИ: Экспертные знания, управление организациями, критическая ответственность
📈 КАРЬЕРА: Топ-менеджмент, академическая карьера, очень высокая заработная плата
🔧 НАВЫКИ: Экспертные знания, лидерство, инновации, управление кризисами, стратегическое планирование
                """.strip(),
                "examples": "Врачи, юристы, профессора, директора, ученые-исследователи, архитекторы, психологи, хирурги, адвокаты, доктора наук"
            }
        }
        
        # Определяем путь к папке job
        import os
        job_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            with open(os.path.join(job_dir, 'jobs_by_zones.json'), 'r', encoding='utf-8') as f:
                self.jobs_by_zone = json.load(f)
            print(f"✅ Загружено {sum(len(jobs) for jobs in self.jobs_by_zone.values())} профессий")
        except FileNotFoundError:
            print("❌ Файл jobs_by_zones.json не найден")
            self.jobs_by_zone = {}
        
        try:
            with open(os.path.join(job_dir, 'knowledge_skills.json'), 'r', encoding='utf-8') as f:
                self.knowledge_skills = json.load(f)
            print(f"✅ Загружено знаний и навыков для {len(self.knowledge_skills)} профессий")
        except FileNotFoundError:
            print("❌ Файл knowledge_skills.json не найден")
            self.knowledge_skills = {}
    
    def determine_job_zone(self, description: str) -> int:
        zone_prompt = f"""
        Analyze the job description and determine which job zone it belongs to.

        Description: "{description}"

        Job Zones:
        1. Zone 1: Little preparation needed - simple jobs requiring only high school education
        2. Zone 2: Some preparation needed - jobs requiring basic skills and experience
        3. Zone 3: Medium preparation needed - jobs requiring professional education
        4. Zone 4: Considerable preparation needed - jobs requiring bachelor's degree
        5. Zone 5: Extensive preparation needed - jobs requiring master's/PhD degree

        Respond with ONLY the zone number (1, 2, 3, 4, or 5).
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an expert in job classification. Respond only with the zone number."},
                    {"role": "user", "content": zone_prompt}
                ],
                temperature=0.1
            )
            
            zone_text = response.choices[0].message.content.strip()
            zone_match = re.search(r'\b([1-5])\b', zone_text)
            
            if zone_match:
                zone = int(zone_match.group(1))
                print(f"📊 Zone: {zone}")
                return zone
            else:
                return 3
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return 3
    
    def find_best_job_in_zone(self, zone: int, description: str) -> dict:
        available_jobs = self.jobs_by_zone.get(str(zone), [])
        
        if not available_jobs:
            return None
        
        job_titles = [job['title'] for job in available_jobs]
        
        job_prompt = f"""
        From the following list of job titles, select the ONE most suitable for this description:

        Description: "{description}"

        Available jobs in zone {zone}:
        {', '.join(job_titles)}

        Respond with ONLY the exact job title from the list.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an expert in job matching. Select the most suitable job title from the provided list."},
                    {"role": "user", "content": job_prompt}
                ],
                temperature=0.3
            )
            
            selected_title = response.choices[0].message.content.strip()
            print(f"💼 Selected: {selected_title}")
            
            for job in available_jobs:
                if job['title'] == selected_title:
                    return job
            
            for job in available_jobs:
                if selected_title.lower() in job['title'].lower() or job['title'].lower() in selected_title.lower():
                    return job
            
            return available_jobs[0]
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import random
            return random.choice(available_jobs)
    
    def get_knowledge_skills(self, job_code: str) -> dict:
        """Получает знания и навыки для профессии"""
        if job_code in self.knowledge_skills:
            return self.knowledge_skills[job_code]
        return {'knowledge': {}, 'skills': {}}
    
    def format_knowledge_skills(self, job_code: str) -> str:
        """Форматирует знания и навыки для отображения"""
        data = self.get_knowledge_skills(job_code)
        
        if not data['knowledge'] and not data['skills']:
            return "📊 Knowledge and skills data not available"
        
        result = []
        
        # Топ-5 знаний по важности
        if data['knowledge']:
            knowledge_items = []
            for name, scores in data['knowledge'].items():
                if 'IM' in scores:  # Importance
                    knowledge_items.append((name, scores['IM']))
            
            knowledge_items.sort(key=lambda x: x[1], reverse=True)
            top_knowledge = knowledge_items[:5]
            
            result.append("🧠 TOP KNOWLEDGE AREAS:")
            for name, score in top_knowledge:
                result.append(f"  • {name}: {score:.1f}/5.0")
        
        # Топ-5 навыков по важности
        if data['skills']:
            skills_items = []
            for name, scores in data['skills'].items():
                if 'IM' in scores:  # Importance
                    skills_items.append((name, scores['IM']))
            
            skills_items.sort(key=lambda x: x[1], reverse=True)
            top_skills = skills_items[:5]
            
            result.append("\n💪 TOP SKILLS:")
            for name, score in top_skills:
                result.append(f"  • {name}: {score:.1f}/5.0")
        
        return "\n".join(result)
    
    def process_request(self, description: str) -> str:
        zone = self.determine_job_zone(description)
        selected_job = self.find_best_job_in_zone(zone, description)
        
        if not selected_job:
            return "❌ No suitable job found in this zone."
        
        # Сохраняем выбранную профессию для дальнейшего использования
        self.last_selected_job = selected_job
        
        zone_info = self.job_zones[zone]
        knowledge_skills = self.format_knowledge_skills(selected_job['code'])
        
        result = f"""
🎯 JOB MATCHING RESULT

📊 Zone: {zone} - {zone_info['name']}
📝 {zone_info['description']}
💡 Examples: {zone_info['examples']}

💼 Recommended Job: {selected_job['title']}
📋 Code: {selected_job['code']}
📝 Description: {selected_job['description'][:200]}...

{knowledge_skills}

✨ This job matches your description and is in the appropriate zone!
        """.strip()
        
        return result
    
    def get_last_job_code(self) -> str:
        """Возвращает код последней выбранной профессии"""
        if hasattr(self, 'last_selected_job') and self.last_selected_job:
            return self.last_selected_job.get('code', '')
        return ''

if __name__ == "__main__":
    bot = ZoneJobBot()
    
    print("🤖 Zone Job Bot Ready!")
    print("=" * 50)
    
    while True:
        description = input("\n❓ Describe your desired job: ").strip()
        
        if description.lower() in ['exit', 'quit', 'выход']:
            print("👋 Good luck with your job search!")
            break
        
        if description:
            result = bot.process_request(description)
            print(f"\n📋 Result:\n{result}")
