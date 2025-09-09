import requests
import re
from statistics import mean
from typing import Dict, Any

BASE_URL = "http://opendata.trudvsem.ru/api/v1/vacancies"

def get_vacancies(query="Программист", region=None, limit=50, offset=0):
    """
    Получаем вакансии с Trudvsem API
    """
    params = {
        "text": query,
        "limit": limit,
        "offset": offset
    }
    if region:
        params["region"] = region
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("results", {}).get("vacancies", [])

def extract_salary_info(vacancy):
    """
    Извлекаем зарплаты, бонусы и премии
    """
    comp = vacancy.get("vacancy", {})
    salary_min = comp.get("salary_min")
    salary_max = comp.get("salary_max")
    base_salary = comp.get("baseSalary")  # если есть
    description = comp.get("description", "")

    # Пробуем найти бонусы/премии в тексте
    bonuses = re.findall(r"\b(?:бонус|преми[яи]|комисси[яя])[:\s]?(\d+)", description, flags=re.I)
    bonuses = [int(b) for b in bonuses]

    # Возвращаем словарь
    return {
        "title": comp.get("profession"),
        "company": comp.get("companyName"),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "base_salary": base_salary,
        "bonuses": bonuses,
        "currency": comp.get("salaryCurrency", "RUB"),
        "employment_type": comp.get("employmentType"),
        "schedule": comp.get("workSchedule"),
        "experience_from": comp.get("experienceFrom"),
        "experience_to": comp.get("experienceTo"),
        "education": comp.get("educationType"),
        "region": comp.get("region", {}).get("name"),
        "description": description
    }

def get_region_name_by_code(region_code):
    """Получение названия региона по коду"""
    regions = {
        "7700000000000": "Москва",
        "7800000000000": "Санкт-Петербург", 
        "5400000000000": "Новосибирск",
        "6600000000000": "Екатеринбург",
        "5200000000000": "Нижний Новгород",
        "1600000000000": "Казань",
        "6300000000000": "Самара",
        "5500000000000": "Омск",
        "7400000000000": "Челябинск",
        "6100000000000": "Ростов-на-Дону"
    }
    return regions.get(region_code, "Неизвестный регион")

def filter_by_region(vacancies, target_region_code):
    """Фильтрация вакансий по региону"""
    if not target_region_code:
        return vacancies
    
    filtered = []
    target_region_name = get_region_name_by_code(target_region_code)
    
    for vac in vacancies:
        vacancy = vac.get("vacancy", {})
        region_info = vacancy.get("region", {})
        region_code = region_info.get("region_code")
        
        # Проверяем точное совпадение кода региона
        if region_code == target_region_code:
            filtered.append(vac)
    
    return filtered

def analyze_vacancies(query="Программист", region=None):
    vacancies = get_vacancies(query=query, region=region, limit=100)  # Увеличиваем лимит для лучшей фильтрации
    
    # Фильтруем по региону на стороне клиента
    if region:
        vacancies = filter_by_region(vacancies, region)
        region_name = get_region_name_by_code(region)
        print(f"Найдено {len(vacancies)} вакансий в регионе: {region_name}\n")
    else:
        print(f"Найдено {len(vacancies)} вакансий по всей России\n")
    
    results = []
    all_salaries = []
    
    for vac in vacancies:
        info = extract_salary_info(vac)
        results.append(info)
        
        # Средняя зарплата для анализа
        sal_min = info.get("salary_min")
        sal_max = info.get("salary_max")
        if sal_min and sal_max and sal_min > 0 and sal_max > 0:
            all_salaries.append((sal_min + sal_max) / 2)
        # Добавляем бонусы
        if info.get("bonuses"):
            all_salaries.extend(info["bonuses"])

    # Показываем только вакансии с полезной информацией
    valid_results = [r for r in results if r.get('title') and r.get('company')]
    
    for i, r in enumerate(valid_results[:20], 1):  # Показываем только первые 20
        title = r.get('title', 'Не указано')
        company = r.get('company', 'Не указано')
        region_name = r.get('region', 'Не указано')
        
        print(f"{i}. {title} | {company} | {region_name}")
        
        sal_min = r.get('salary_min', 0)
        sal_max = r.get('salary_max', 0)
        if sal_min > 0 and sal_max > 0:
            print(f"   Зарплата: {sal_min:,.0f}–{sal_max:,.0f} {r.get('currency', 'RUB')}")
        else:
            print(f"   Зарплата: не указана")
            
        if r.get("bonuses"):
            print(f"   Бонусы/премии: {r['bonuses']}")
            
        schedule = r.get('schedule', 'Не указано')
        employment = r.get('employment_type', 'Не указано')
        print(f"   График: {schedule} | Тип занятости: {employment}")
        
        exp_from = r.get('experience_from', 'Не указано')
        exp_to = r.get('experience_to', 'Не указано')
        education = r.get('education', 'Не указано')
        print(f"   Опыт: {exp_from}–{exp_to} лет | Образование: {education}")
        
        description = r.get('description', '')
        if description and len(description) > 10:
            print(f"   Описание: {description[:100]}...")
        print()

    if all_salaries:
        print(f"=== СТАТИСТИКА ===")
        print(f"Вакансий с указанной зарплатой: {len(all_salaries)}")
        print(f"Средняя зарплата: {mean(all_salaries):,.0f} ₽")
        print(f"Минимальная: {min(all_salaries):,.0f} ₽ | Максимальная: {max(all_salaries):,.0f} ₽")
    else:
        print("Нет вакансий с указанной зарплатой")

def get_region_code():
    """Получение кода региона от пользователя"""
    regions = {
        "1": ("7700000000000", "Москва"),
        "2": ("7800000000000", "Санкт-Петербург"),
        "3": ("5400000000000", "Новосибирск"),
        "4": ("6600000000000", "Екатеринбург"),
        "5": ("5200000000000", "Нижний Новгород"),
        "6": ("1600000000000", "Казань"),
        "7": ("6300000000000", "Самара"),
        "8": ("5500000000000", "Омск"),
        "9": ("7400000000000", "Челябинск"),
        "10": ("6100000000000", "Ростов-на-Дону")
    }
    
    print("\nВыберите регион (или нажмите Enter для поиска по всей России):")
    for key, (code, name) in regions.items():
        print(f"{key}. {name}")
    print("0. Вся Россия")
    
    choice = input("\nВаш выбор: ").strip()
    
    if choice == "0" or choice == "":
        return None
    elif choice in regions:
        code, name = regions[choice]
        print(f"Выбран регион: {name}")
        return code
    else:
        print("Неверный выбор, поиск по всей России")
        return None


def analyze_salary_for_position(job_title: str, region_name: str = None) -> Dict[str, Any]:
    """
    Анализирует зарплату для конкретной должности и региона
    Возвращает статистику зарплат
    """
    try:
        # Определяем код региона по названию
        region_code = None
        if region_name:
            region_mapping = {
                "москва": "7700000000000",
                "санкт-петербург": "7800000000000", 
                "питер": "7800000000000",
                "новосибирск": "5400000000000",
                "екатеринбург": "6600000000000",
                "нижний новгород": "5200000000000",
                "казань": "1600000000000",
                "самара": "6300000000000",
                "омск": "5500000000000",
                "челябинск": "7400000000000",
                "ростов-на-дону": "6100000000000"
            }
            
            region_lower = region_name.lower()
            for key, code in region_mapping.items():
                if key in region_lower:
                    region_code = code
                    break
        
        # Получаем вакансии
        vacancies = get_vacancies(query=job_title, region=region_code, limit=50)
        
        # Фильтруем по региону если нужно
        if region_code:
            vacancies = filter_by_region(vacancies, region_code)
        
        # Анализируем зарплаты
        all_salaries = []
        salary_ranges = []
        
        for vac in vacancies:
            info = extract_salary_info(vac)
            sal_min = info.get("salary_min")
            sal_max = info.get("salary_max")
            
            if sal_min and sal_max and sal_min > 0 and sal_max > 0:
                all_salaries.append((sal_min + sal_max) / 2)
                salary_ranges.append((sal_min, sal_max))
        
        if all_salaries:
            return {
                "found_vacancies": len(vacancies),
                "with_salary": len(all_salaries),
                "average_salary": round(mean(all_salaries)),
                "min_salary": min(all_salaries),
                "max_salary": max(all_salaries),
                "salary_ranges": salary_ranges[:10],  # Топ-10 диапазонов
                "region": region_name or "Вся Россия"
            }
        else:
            return {
                "found_vacancies": len(vacancies),
                "with_salary": 0,
                "average_salary": 0,
                "min_salary": 0,
                "max_salary": 0,
                "salary_ranges": [],
                "region": region_name or "Вся Россия"
            }
            
    except Exception as e:
        return {
            "error": str(e),
            "found_vacancies": 0,
            "with_salary": 0,
            "average_salary": 0,
            "min_salary": 0,
            "max_salary": 0,
            "salary_ranges": [],
            "region": region_name or "Вся Россия"
        }

def format_salary_analysis(salary_data: Dict[str, Any]) -> str:
    """Форматирует результат анализа зарплаты для вывода"""
    if salary_data.get("error"):
        return f"❌ Ошибка при анализе зарплаты: {salary_data['error']}"
    
    result = []
    result.append("💰 АНАЛИЗ ЗАРПЛАТЫ")
    result.append("=" * 30)
    
    result.append(f"Регион: {salary_data['region']}")
    result.append(f"Найдено вакансий: {salary_data['found_vacancies']}")
    result.append(f"С указанной зарплатой: {salary_data['with_salary']}")
    
    if salary_data['with_salary'] > 0:
        result.append(f"\n📊 СТАТИСТИКА ЗАРПЛАТ:")
        result.append(f"Средняя зарплата: {salary_data['average_salary']:,.0f} ₽")
        result.append(f"Минимальная: {salary_data['min_salary']:,.0f} ₽")
        result.append(f"Максимальная: {salary_data['max_salary']:,.0f} ₽")
        
        if salary_data['salary_ranges']:
            result.append(f"\n📋 ПРИМЕРЫ ДИАПАЗОНОВ ЗАРПЛАТ:")
            for i, (min_sal, max_sal) in enumerate(salary_data['salary_ranges'][:5], 1):
                result.append(f"   {i}. {min_sal:,.0f} - {max_sal:,.0f} ₽")
    else:
        result.append(f"\n⚠️ Нет вакансий с указанной зарплатой")
    
    return "\n".join(result)

def main():
    print("=== Анализатор вакансий ===")
    print("Поиск вакансий через API 'Труд всем'")
    
    # Получение поискового запроса
    query = input("\nВведите поисковый запрос (например: 'Python разработчик'): ").strip()
    if not query:
        query = "Программист"
        print(f"Используется запрос по умолчанию: '{query}'")
    
    # Получение региона
    region_code = get_region_code()
    
    print(f"\nПоиск вакансий: '{query}'")
    if region_code:
        print("Регион: выбранный")
    else:
        print("Регион: вся Россия")
    print("\nЗагружаем данные...")
    
    try:
        analyze_vacancies(query=query, region=region_code)
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        print("Проверьте подключение к интернету и попробуйте снова")


if __name__ == "__main__":
    main()
