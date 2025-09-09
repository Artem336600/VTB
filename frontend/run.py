#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для запуска фронтенда VTB HR System
"""

import os
import sys
from app import app

def main():
    """Основная функция запуска"""
    print("=" * 60)
    print("           VTB HR SYSTEM - FRONTEND")
    print("=" * 60)
    print()
    
    # Проверяем доступность VTB модулей
    vtb_path = os.path.join(os.path.dirname(__file__), '..', 'VTB')
    if os.path.exists(vtb_path):
        print("✓ VTB backend модули найдены")
    else:
        print("⚠ VTB backend модули не найдены")
        print("  Убедитесь, что папка VTB находится в родительской директории")
    
    # Проверяем наличие базы данных
    db_path = os.path.join(os.path.dirname(__file__), '..', 'VTB', 'templates.db')
    if os.path.exists(db_path):
        print("✓ База данных найдена")
    else:
        print("⚠ База данных не найдена")
        print("  Будет создана при первом запуске")
    
    print()
    print("Запуск веб-сервера...")
    print("Фронтенд будет доступен по адресу: http://localhost:5000")
    print("Для остановки нажмите Ctrl+C")
    print()
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\nСервер остановлен пользователем")
    except Exception as e:
        print(f"\nОшибка при запуске сервера: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
