#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import json
from datetime import datetime
import base64

class TemplateDatabase:
    """Класс для работы с базой данных шаблонов"""
    
    def __init__(self, db_path="templates.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализирует базу данных и создает таблицы"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создаем таблицу для хранения шаблонов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content TEXT,
                file_type TEXT,
                file_path TEXT,
                file_size INTEGER,
                pdf_path TEXT,
                pdf_size INTEGER,
                is_converted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавляем новые поля для вакансий, если их еще нет
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN job_title TEXT')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN job_description TEXT')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN application_deadline DATE')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN positions_count INTEGER')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN region TEXT')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN salary_min INTEGER')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN salary_max INTEGER')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN job_zone INTEGER')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN job_code TEXT')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN structured_data TEXT')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN skill_scores TEXT')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        try:
            cursor.execute('ALTER TABLE templates ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        except sqlite3.OperationalError:
            pass  # Поле уже существует
        
        conn.commit()
        conn.close()
    
    def add_template(self, name, content=None, file_type="txt", file_path=None, pdf_path=None):
        """Добавляет новый шаблон в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Получаем размер файла если указан путь
        file_size = None
        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
        
        # Получаем размер PDF файла если указан путь
        pdf_size = None
        if pdf_path and os.path.exists(pdf_path):
            pdf_size = os.path.getsize(pdf_path)
        
        # Определяем, конвертирован ли файл
        is_converted = pdf_path is not None and os.path.exists(pdf_path)
        
        cursor.execute('''
            INSERT INTO templates (name, content, file_type, file_path, file_size, pdf_path, pdf_size, is_converted, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, content, file_type, file_path, file_size, pdf_path, pdf_size, is_converted, datetime.now(), datetime.now()))
        
        template_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return template_id
    
    def add_vacancy(self, name, content=None, file_type="txt", file_path=None, pdf_path=None,
                   job_title=None, job_description=None, application_deadline=None, 
                   positions_count=None, region=None, salary_min=None, salary_max=None,
                   job_zone=None, job_code=None, structured_data=None, skill_scores=None):
        """Добавляет вакансию в базу данных с полной информацией"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Вычисляем размеры файлов
        file_size = 0
        pdf_size = 0
        is_converted = 0
        
        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
        
        if pdf_path and os.path.exists(pdf_path):
            pdf_size = os.path.getsize(pdf_path)
            is_converted = 1
        
        # Преобразуем structured_data и skill_scores в JSON строки
        structured_data_json = json.dumps(structured_data) if structured_data else None
        skill_scores_json = json.dumps(skill_scores) if skill_scores else None
        
        cursor.execute('''
            INSERT INTO templates (
                name, content, file_type, file_path, file_size, 
                pdf_path, pdf_size, is_converted,
                job_title, job_description, application_deadline, 
                positions_count, region, salary_min, salary_max,
                job_zone, job_code, structured_data, skill_scores
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, content, file_type, file_path, file_size,
            pdf_path, pdf_size, is_converted,
            job_title, job_description, application_deadline,
            positions_count, region, salary_min, salary_max,
            job_zone, job_code, structured_data_json, skill_scores_json
        ))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def delete_template(self, template_id):
        """Удаляет шаблон из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, существует ли шаблон
        cursor.execute('SELECT id FROM templates WHERE id = ?', (template_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Удаляем шаблон
        cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
        conn.commit()
        conn.close()
        
        return True
    
    def update_vacancy_data(self, template_id, structured_data=None, skill_scores=None):
        """Обновляет structured_data и skill_scores шаблона"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, существует ли шаблон
        cursor.execute('SELECT id FROM templates WHERE id = ?', (template_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Преобразуем данные в JSON строки
        structured_data_json = json.dumps(structured_data) if structured_data else None
        skill_scores_json = json.dumps(skill_scores) if skill_scores else None
        
        # Обновляем данные
        cursor.execute('''
            UPDATE templates 
            SET structured_data = ?, skill_scores = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (structured_data_json, skill_scores_json, template_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def update_vacancy_full(self, template_id, job_title=None, positions_count=None, region=None, 
                           application_deadline=None, structured_data=None, skill_scores=None):
        """Обновляет все поля вакансии"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, существует ли шаблон
        cursor.execute('SELECT id FROM templates WHERE id = ?', (template_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Преобразуем данные в JSON строки
        structured_data_json = json.dumps(structured_data) if structured_data else None
        skill_scores_json = json.dumps(skill_scores) if skill_scores else None
        
        # Обновляем все поля
        cursor.execute('''
            UPDATE templates 
            SET job_title = ?, positions_count = ?, region = ?, application_deadline = ?,
                structured_data = ?, skill_scores = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (job_title, positions_count, region, application_deadline, 
              structured_data_json, skill_scores_json, template_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_all_templates(self):
        """Получает все шаблоны из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, content, file_type, file_path, file_size, pdf_path, pdf_size, is_converted, created_at,
                   job_title, job_description, application_deadline, positions_count, region, 
                   salary_min, salary_max, job_zone, job_code, structured_data, skill_scores
            FROM templates
            ORDER BY created_at DESC
        ''')
        
        templates = cursor.fetchall()
        conn.close()
        
        return templates
    
    def get_template_by_id(self, template_id):
        """Получает шаблон по ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, content, file_type, file_path, file_size, pdf_path, pdf_size, is_converted, created_at,
                   job_title, job_description, application_deadline, positions_count, region, 
                   salary_min, salary_max, job_zone, job_code, structured_data, skill_scores
            FROM templates
            WHERE id = ?
        ''', (template_id,))
        
        template = cursor.fetchone()
        conn.close()
        
        return template
    
    def update_template(self, template_id, name=None, content=None, file_type=None):
        """Обновляет шаблон в базе данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Формируем запрос обновления только для переданных полей
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name = ?")
            params.append(name)
        
        if content is not None:
            update_fields.append("content = ?")
            params.append(content)
        
        if file_type is not None:
            update_fields.append("file_type = ?")
            params.append(file_type)
        
        update_fields.append("updated_at = ?")
        params.append(datetime.now())
        params.append(template_id)
        
        query = f"UPDATE templates SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
    
    def delete_template(self, template_id):
        """Удаляет шаблон из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
        
        conn.commit()
        conn.close()
    
    def search_templates(self, search_term):
        """Поиск шаблонов по названию или содержимому"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, content, file_type, file_path, file_size, pdf_path, pdf_size, is_converted, created_at
            FROM templates
            WHERE name LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{search_term}%', f'%{search_term}%'))
        
        templates = cursor.fetchall()
        conn.close()
        
        return templates
    
    def get_templates_count(self):
        """Возвращает количество шаблонов в базе данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM templates')
        count = cursor.fetchone()[0]
        
        conn.close()
        
        return count
    
    def add_file_template(self, file_path):
        """Добавляет файл как шаблон в базу данных"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        # Получаем информацию о файле
        filename = os.path.basename(file_path)
        file_extension = os.path.splitext(filename)[1].lower()
        file_size = os.path.getsize(file_path)
        
        # Определяем тип файла
        file_type = file_extension[1:] if file_extension else "unknown"
        
        # Читаем содержимое файла
        content = None
        try:
            if file_type in ['txt', 'md', 'py', 'js', 'html', 'css', 'json', 'xml', 'csv']:
                # Текстовые файлы
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # Бинарные файлы - кодируем в base64
                with open(file_path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Ошибка при чтении файла {filename}: {e}")
            return None
        
        # Добавляем в базу данных
        template_id = self.add_template(
            name=filename,
            content=content,
            file_type=file_type,
            file_path=file_path
        )
        
        return template_id
    
    def get_file_content(self, template_id):
        """Получает содержимое файла из базы данных"""
        template = self.get_template_by_id(template_id)
        if not template:
            return None
        
        template_id, name, content, file_type, file_path, file_size, created_at = template
        
        # Если это бинарный файл, декодируем из base64
        if file_type not in ['txt', 'md', 'py', 'js', 'html', 'css', 'json', 'xml', 'csv']:
            try:
                return base64.b64decode(content.encode('utf-8'))
            except Exception as e:
                print(f"Ошибка при декодировании файла: {e}")
                return None
        
        return content
    
    def update_pdf_info(self, template_id, pdf_path):
        """Обновляет информацию о PDF файле"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        pdf_size = None
        if pdf_path and os.path.exists(pdf_path):
            pdf_size = os.path.getsize(pdf_path)
        
        cursor.execute('''
            UPDATE templates 
            SET pdf_path = ?, pdf_size = ?, is_converted = 1, updated_at = ?
            WHERE id = ?
        ''', (pdf_path, pdf_size, datetime.now(), template_id))
        
        conn.commit()
        conn.close()
    
    def convert_file_to_pdf(self, template_id):
        """Конвертирует файл в PDF и обновляет информацию в БД"""
        from pdf_converter import PDFConverter
        
        template = self.get_template_by_id(template_id)
        if not template:
            print("Шаблон не найден")
            return None
        
        template_id, name, content, file_type, file_path, file_size, pdf_path, pdf_size, is_converted, created_at = template
        
        # Если уже конвертирован, возвращаем существующий PDF
        if is_converted and pdf_path and os.path.exists(pdf_path):
            print(f"PDF уже существует: {pdf_path}")
            return pdf_path
        
        # Если нет исходного файла, не можем конвертировать
        if not file_path or not os.path.exists(file_path):
            print(f"Исходный файл не найден: {file_path}")
            return None
        
        # Если это уже PDF, возвращаем его
        if file_type.lower() == 'pdf':
            print("Файл уже в формате PDF")
            self.update_pdf_info(template_id, file_path)
            return file_path
        
        # Проверяем доступность LibreOffice
        converter = PDFConverter()
        if not converter.is_libreoffice_available():
            print("LibreOffice не найден. Установите LibreOffice для конвертации файлов.")
            return None
        
        if not converter.can_convert(file_path):
            print(f"Файл не поддерживается для конвертации: {file_type}")
            return None
        
        print(f"Начинаем конвертацию файла: {name}")
        try:
            pdf_path = converter.convert_to_pdf(file_path)
            if pdf_path and os.path.exists(pdf_path):
                self.update_pdf_info(template_id, pdf_path)
                print(f"Конвертация успешна: {pdf_path}")
                return pdf_path
            else:
                print("PDF файл не был создан")
                return None
        except Exception as e:
            print(f"Ошибка при конвертации: {e}")
            return None
