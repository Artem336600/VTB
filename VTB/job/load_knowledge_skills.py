import pandas as pd
import json

def load_knowledge_skills():
    """Загружает знания и навыки для каждой профессии"""
    
    # Читаем файлы с знаниями и навыками
    knowledge_df = pd.read_csv('db_30_0_text/Knowledge.txt', sep='\t')
    skills_df = pd.read_csv('db_30_0_text/Skills.txt', sep='\t')
    
    # Создаем словарь для хранения данных по профессиям
    job_data = {}
    
    # Обрабатываем знания
    for _, row in knowledge_df.iterrows():
        code = row['O*NET-SOC Code']
        element_name = row['Element Name']
        scale_id = row['Scale ID']
        data_value = row['Data Value']
        
        if code not in job_data:
            job_data[code] = {'knowledge': {}, 'skills': {}}
        
        # Берем только значения уровня (LV) и важности (IM)
        if scale_id in ['LV', 'IM']:
            if element_name not in job_data[code]['knowledge']:
                job_data[code]['knowledge'][element_name] = {}
            job_data[code]['knowledge'][element_name][scale_id] = data_value
    
    # Обрабатываем навыки
    for _, row in skills_df.iterrows():
        code = row['O*NET-SOC Code']
        element_name = row['Element Name']
        scale_id = row['Scale ID']
        data_value = row['Data Value']
        
        if code not in job_data:
            job_data[code] = {'knowledge': {}, 'skills': {}}
        
        # Берем только значения уровня (LV) и важности (IM)
        if scale_id in ['LV', 'IM']:
            if element_name not in job_data[code]['skills']:
                job_data[code]['skills'][element_name] = {}
            job_data[code]['skills'][element_name][scale_id] = data_value
    
    # Сохраняем в JSON
    with open('knowledge_skills.json', 'w', encoding='utf-8') as f:
        json.dump(job_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Загружено данных для {len(job_data)} профессий")
    print("✅ Данные сохранены в knowledge_skills.json")
    
    return job_data

if __name__ == "__main__":
    load_knowledge_skills()
