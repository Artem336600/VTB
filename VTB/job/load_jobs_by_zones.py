# Скрипт для загрузки профессий по зонам из базы данных
import pandas as pd

def load_jobs_by_zones():
    """Загружает все профессии, сгруппированные по зонам"""
    
    # Читаем файл с зонами
    zones_df = pd.read_csv('db_30_0_text/Job Zones.txt', sep='\t')
    
    # Читаем файл с профессиями
    jobs_df = pd.read_csv('db_30_0_text/Occupation Data.txt', sep='\t')
    
    # Объединяем данные
    merged_df = zones_df.merge(jobs_df, on='O*NET-SOC Code', how='inner')
    
    # Группируем по зонам
    jobs_by_zone = {}
    
    for zone in range(1, 6):
        zone_jobs = merged_df[merged_df['Job Zone'] == zone]
        jobs_list = []
        
        for _, row in zone_jobs.iterrows():
            jobs_list.append({
                'code': row['O*NET-SOC Code'],
                'title': row['Title'],
                'description': row['Description']
            })
        
        jobs_by_zone[zone] = jobs_list
        print(f"Зона {zone}: {len(jobs_list)} профессий")
    
    return jobs_by_zone

if __name__ == "__main__":
    jobs = load_jobs_by_zones()
    
    # Сохраняем в JSON для использования в боте
    import json
    with open('jobs_by_zones.json', 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    print("✅ Данные сохранены в jobs_by_zones.json")
