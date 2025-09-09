#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Простой тестовый сервер для проверки подключения фронтенда
"""

from flask import Flask, render_template, request, jsonify
import os
import time

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """Тестовый endpoint для извлечения текста"""
    try:
        # Имитируем обработку файла
        time.sleep(2)  # Имитируем задержку
        
        # Возвращаем тестовые данные
        return jsonify({
            'full_text': '''Тестовая вакансия

Должность: Python Developer
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
- Обучение за счет компании''',
            'pages_count': 1,
            'title': 'Тестовая вакансия',
            'author': 'HR отдел',
            'structured_sections': {
                'Требования': 'Опыт работы с Python от 2 лет',
                'Обязанности': 'Разработка веб-приложений',
                'Условия': 'Удаленная работа'
            },
            'file_info': {
                'name': 'test_vacancy.txt',
                'size': 1024,
                'type': 'txt'
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/api/structure-text', methods=['POST'])
def structure_text():
    """Тестовый endpoint для структурирования текста"""
    try:
        time.sleep(1)  # Имитируем задержку
        
        return jsonify({
            'job_info': {
                'Название должности': 'Python Developer',
                'Компания': 'ООО "Технологии"',
                'Тип занятости': 'Полная занятость',
                'График работы': 'Гибкий график',
                'Местоположение': 'Удаленно',
                'Уровень': 'Middle'
            },
            'salary': {
                'Зарплата от': '80000',
                'Зарплата до': '150000',
                'Валюта': 'RUB',
                'Тип оплаты': 'Ежемесячно',
                'Бонусы': 'Премии по результатам'
            },
            'requirements': {
                'Опыт работы': 'от 2 лет',
                'Образование': 'Высшее техническое',
                'Технические навыки': 'Python, Django, Flask, PostgreSQL, MySQL, Git',
                'Языки программирования': 'Python',
                'Инструменты': 'Git, Docker, Linux',
                'Иностранные языки': 'Английский (intermediate)',
                'Личные качества': 'Ответственность, коммуникабельность'
            },
            'responsibilities': [
                'Разработка веб-приложений',
                'Создание API',
                'Работа с базами данных',
                'Code review',
                'Участие в планировании спринтов'
            ],
            'benefits': [
                'Удаленная работа',
                'Гибкий график',
                'Медицинская страховка',
                'Обучение за счет компании'
            ],
            'additional_info': {
                'Описание компании': 'IT компания, занимающаяся разработкой веб-приложений',
                'Дополнительные требования': 'Опыт работы в команде',
                'Процесс отбора': 'Техническое интервью + собеседование с HR',
                'Контактная информация': 'hr@company.com'
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/api/analyze-job', methods=['POST'])
def analyze_job():
    """Тестовый endpoint для анализа профессии"""
    try:
        time.sleep(1)  # Имитируем задержку
        
        return jsonify({
            'job_details': '''
            <h4>Детали профессии Python Developer</h4>
            <p><strong>Код профессии:</strong> 15-1132.00</p>
            <p><strong>Зона:</strong> 4 (требует значительной подготовки)</p>
            <p><strong>Описание:</strong> Разработка программного обеспечения с использованием Python</p>
            <p><strong>Средняя зарплата:</strong> $95,000 - $120,000</p>
            ''',
            'knowledge_analysis': '''
            <h4>Анализ соответствия знаний</h4>
            <p><strong>Покрытие требований:</strong> 85%</p>
            <p><strong>Основные области знаний:</strong></p>
            <ul>
                <li>Программирование - 90%</li>
                <li>Базы данных - 80%</li>
                <li>Веб-технологии - 85%</li>
                <li>Системы контроля версий - 90%</li>
            </ul>
            ''',
            'recommendations': [
                'Рассмотрите добавление требований по области: Машинное обучение (важность: 4.2/5.0)',
                'Рассмотрите добавление требований по области: DevOps (важность: 3.8/5.0)',
                'Рассмотрите добавление требований по области: Тестирование (важность: 3.5/5.0)'
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/api/save-vacancy', methods=['POST'])
def save_vacancy():
    """Тестовый endpoint для сохранения вакансии"""
    try:
        time.sleep(1)  # Имитируем задержку
        
        return jsonify({
            'vacancy_id': 12345,
            'job_title': 'Python Developer',
            'application_deadline': '2024-12-31',
            'positions_count': 2,
            'region': 'Удаленно',
            'salary_min': 80000,
            'salary_max': 150000
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/api/vacancies', methods=['GET'])
def get_vacancies():
    """Тестовый endpoint для получения списка вакансий"""
    try:
        return jsonify([
            {
                'id': 1,
                'name': 'Python Developer',
                'file_type': 'txt',
                'file_size': 1024,
                'created_at': '2024-01-15T10:30:00',
                'job_title': 'Python Developer',
                'job_description': 'Разработка веб-приложений на Python',
                'application_deadline': '2024-12-31',
                'positions_count': 2,
                'region': 'Удаленно',
                'salary_min': 80000,
                'salary_max': 150000
            },
            {
                'id': 2,
                'name': 'Frontend Developer',
                'file_type': 'pdf',
                'file_size': 2048,
                'created_at': '2024-01-14T15:45:00',
                'job_title': 'Frontend Developer',
                'job_description': 'Разработка пользовательских интерфейсов',
                'application_deadline': '2024-12-30',
                'positions_count': 1,
                'region': 'Москва',
                'salary_min': 70000,
                'salary_max': 120000
            }
        ])
        
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка состояния сервера"""
    return jsonify({
        'status': 'healthy',
        'message': 'Тестовый сервер работает',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    print("Запуск тестового сервера...")
    print("Фронтенд будет доступен по адресу: http://localhost:5000")
    print("Для остановки нажмите Ctrl+C")
    app.run(debug=True, host='0.0.0.0', port=5000)
