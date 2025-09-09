#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from database import TemplateDatabase

def clear_screen():
    """Очищает экран консоли"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_main_menu():
    """Показывает главное меню"""
    print("=" * 50)
    print("           СИСТЕМА УПРАВЛЕНИЯ ВАКАНСИЯМИ")
    print("=" * 50)
    print()
    print("Выберите действие:")
    print("1. Создать новую вакансию")
    print("2. Выбрать существующую вакансию")
    print("0. Выход")
    print()

def show_template_menu():
    """Показывает меню выбора шаблона"""
    print("=" * 50)
    print("           СОЗДАНИЕ НОВОЙ ВАКАНСИИ")
    print("=" * 50)
    print()
    print("Выберите тип шаблона:")
    print("1. Создать новый шаблон")
    print("2. Использовать готовый шаблон")
    print("0. Назад в главное меню")
    print()

def format_file_size(size_bytes):
    """Форматирует размер файла в читаемый вид"""
    if size_bytes is None:
        return "N/A"
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_application_deadline():
    """Получает дату окончания набора от пользователя"""
    from datetime import datetime
    
    while True:
        try:
            deadline_input = input("\n📅 До какого числа набор на должность? (формат: ДД.ММ.ГГГГ или ДД/ММ/ГГГГ): ").strip()
            
            if not deadline_input:
                print("❌ Дата не может быть пустой")
                continue
            
            # Пробуем разные форматы даты
            date_formats = ["%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
            deadline_date = None
            
            for fmt in date_formats:
                try:
                    deadline_date = datetime.strptime(deadline_input, fmt)
                    break
                except ValueError:
                    continue
            
            if deadline_date:
                # Проверяем, что дата в будущем
                if deadline_date.date() < datetime.now().date():
                    print("❌ Дата должна быть в будущем")
                    continue
                
                return deadline_date.strftime("%Y-%m-%d")
            else:
                print("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ или ДД/ММ/ГГГГ")
                
        except KeyboardInterrupt:
            print("\n❌ Отменено пользователем")
            return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def get_positions_count():
    """Получает количество человек на должность от пользователя"""
    while True:
        try:
            count_input = input("\n👥 Количество человек на эту должность: ").strip()
            
            if not count_input:
                print("❌ Количество не может быть пустым")
                continue
            
            count = int(count_input)
            
            if count <= 0:
                print("❌ Количество должно быть больше 0")
                continue
            
            if count > 1000:
                print("❌ Количество не может быть больше 1000")
                continue
            
            return count
            
        except ValueError:
            print("❌ Введите корректное число")
        except KeyboardInterrupt:
            print("\n❌ Отменено пользователем")
            return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def get_user_choice(min_choice, max_choice):
    """Получает выбор пользователя с валидацией"""
    while True:
        try:
            choice = int(input("Введите номер выбора: "))
            if min_choice <= choice <= max_choice:
                return choice
            else:
                print(f"Пожалуйста, введите число от {min_choice} до {max_choice}")
        except ValueError:
            print("Пожалуйста, введите корректное число")

def show_files_from_uploads():
    """Показывает список файлов из папки uploads"""
    uploads_dir = "uploads"
    
    if not os.path.exists(uploads_dir):
        print("Папка uploads не найдена.")
        return []
    
    files = []
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        if os.path.isfile(file_path):
            files.append(file_path)
    
    if not files:
        print("В папке uploads нет файлов.")
        return []
    
    print("=" * 60)
    print("           ДОСТУПНЫЕ ФАЙЛЫ ИЗ ПАПКИ UPLOADS")
    print("=" * 60)
    print()
    print(f"{'№':<3} {'Название':<35} {'Тип':<8} {'Размер':<10}")
    print("-" * 70)
    
    for i, file_path in enumerate(files, 1):
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower()[1:] if os.path.splitext(filename)[1] else "unknown"
        file_size = os.path.getsize(file_path)
        
        # Обрезаем название если оно слишком длинное
        display_name = filename[:32] + "..." if len(filename) > 35 else filename
        size_str = format_file_size(file_size)
        
        print(f"{i:<3} {display_name:<35} {file_ext:<8} {size_str:<10}")
    
    print("0. Назад")
    print()
    return files

def handle_new_vacancy():
    """Обрабатывает создание новой вакансии"""
    while True:
        clear_screen()
        show_template_menu()
        choice = get_user_choice(0, 2)
        
        if choice == 1:
            handle_create_new_template()
            break
        elif choice == 2:
            print("\nВыбрано: Использовать готовый шаблон")
            input("Нажмите Enter для продолжения...")
            # Здесь будет логика выбора готового шаблона
            break
        elif choice == 0:
            break

def handle_create_new_template():
    """Обрабатывает создание нового шаблона с выбором файла из uploads"""
    while True:
        clear_screen()
        files = show_files_from_uploads()
        
        if not files:
            input("Нажмите Enter для возврата...")
            break
        
        max_choice = len(files)
        choice = get_user_choice(0, max_choice)
        
        if choice == 0:
            break
        else:
            selected_file = files[choice - 1]
            filename = os.path.basename(selected_file)
            file_ext = os.path.splitext(filename)[1].lower()[1:] if os.path.splitext(filename)[1] else "unknown"
            file_size = os.path.getsize(selected_file)
            
            print(f"\nВыбран файл: {filename}")
            print(f"Тип файла: {file_ext}")
            print(f"Размер файла: {format_file_size(file_size)}")
            
            # Автоматически обрабатываем файл
            if file_ext.lower() == 'pdf':
                print(f"\nИзвлечение текста из PDF файла '{filename}'...")
                
                try:
                    from pdf_text_extractor import PDFTextExtractor
                    extractor = PDFTextExtractor(selected_file)
                    content = extractor.extract_all()
                    
                    if content:
                        print(f"✓ Текст успешно извлечен из PDF!")
                        print(f"  - Страниц: {content.pages_count}")
                        print(f"  - Секций найдено: {len(content.structured_sections)}")
                        
                        # Показываем краткую информацию о документе
                        print(f"\nИнформация о документе:")
                        print(f"  - Заголовок: {content.title}")
                        print(f"  - Автор: {content.author}")
                        
                        # Показываем найденные секции
                        if content.structured_sections:
                            print(f"\nНайденные секции:")
                            for section_name in content.structured_sections.keys():
                                print(f"  - {section_name}")
                        
                        # Показываем первые 200 символов текста
                        print(f"\nНачало текста:")
                        preview = content.full_text[:200] + "..." if len(content.full_text) > 200 else content.full_text
                        print(f"  {preview}")
                        
                        # Структурируем текст с помощью ИИ
                        print(f"\nСтруктурирование текста с помощью ИИ...")
                        try:
                            from ai import AIStructuredExtractor
                            ai_extractor = AIStructuredExtractor()
                            structured_data = ai_extractor.structure_vacancy_text(content.full_text)
                            formatted_data = ai_extractor.format_structured_data(structured_data)
                            
                            print(f"✓ Текст успешно структурирован!")
                            print(f"\n{formatted_data}")
                            
                            # Получаем детальную информацию через ZoneJobBot
                            job_title = structured_data.get("job_info", {}).get("Название должности", "")
                            if job_title and job_title != "Не указано":
                                print(f"\n🔍 Получение детальной информации для вакансии: '{job_title}'...")
                                try:
                                    sys.path.append(os.path.join(os.path.dirname(__file__), 'job'))
                                    from zone_job_bot import ZoneJobBot
                                    
                                    job_bot = ZoneJobBot()
                                    job_details = job_bot.process_request(job_title)
                                    
                                    print(f"✓ Детальная информация получена!")
                                    print(f"\n{job_details}")
                                    
                                    # Анализируем соответствие требований и Knowledge Areas
                                    print(f"\n🔍 Анализ соответствия требований и областей знаний...")
                                    try:
                                        from knowledge_matcher import KnowledgeMatcher
                                        
                                        # Получаем код профессии из job_bot
                                        job_code = job_bot.get_last_job_code()
                                        
                                        if job_code and hasattr(job_bot, 'knowledge_skills'):
                                            job_knowledge = job_bot.get_knowledge_skills(job_code)
                                            if job_knowledge.get('knowledge'):
                                                matcher = KnowledgeMatcher()
                                                analysis = matcher.analyze_knowledge_coverage(structured_data, job_knowledge['knowledge'])
                                                analysis_result = matcher.format_analysis_result(analysis)
                                                
                                                print(f"✓ Анализ соответствия завершен!")
                                                print(f"\n{analysis_result}")
                                                
                                                # Предлагаем пользователю дополнить недостающие области
                                                if analysis['missing_areas']:
                                                    print(f"\n💡 РЕКОМЕНДАЦИИ:")
                                                    print("Рассмотрите возможность добавления следующих требований:")
                                                    for area, score in analysis['missing_areas'][:3]:  # Топ-3
                                                        print(f"   • {area} (важность: {score:.1f}/5.0)")
                                            else:
                                                print("⚠️ Данные о знаниях для этой профессии недоступны")
                                        else:
                                            print("⚠️ Не удалось найти код профессии для анализа знаний")
                                            
                                    except ImportError:
                                        print("✗ Модуль анализа знаний не найден")
                                    except Exception as e:
                                        print(f"✗ Ошибка при анализе знаний: {e}")
                                    
                                except ImportError:
                                    print("✗ Модуль ZoneJobBot не найден")
                                except Exception as e:
                                    print(f"✗ Ошибка при получении детальной информации: {e}")
                            else:
                                print("⚠️ Название вакансии не найдено, детальная информация недоступна")
                            
                        except ImportError:
                            print("✗ Модуль ИИ не найден")
                        except Exception as e:
                            print(f"✗ Ошибка при структурировании: {e}")
                        
                        print(f"\n✓ Файл '{filename}' обработан и готов для создания вакансии!")
                        
                        # Собираем дополнительную информацию от пользователя
                        print(f"\n📝 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ДЛЯ ВАКАНСИИ")
                        print("=" * 50)
                        
                        # Получаем дату окончания набора
                        application_deadline = get_application_deadline()
                        if application_deadline is None:
                            print("❌ Создание вакансии отменено")
                            input("Нажмите Enter для продолжения...")
                            break
                        
                        # Получаем количество человек
                        positions_count = get_positions_count()
                        if positions_count is None:
                            print("❌ Создание вакансии отменено")
                            input("Нажмите Enter для продолжения...")
                            break
                        
                        # Сохраняем вакансию в базу данных
                        print(f"\n💾 Сохранение вакансии в базу данных...")
                        try:
                            db = TemplateDatabase()
                            
                            # Извлекаем информацию для сохранения
                            job_title = structured_data.get("job_info", {}).get("Название должности", filename)
                            job_description = content.full_text if 'content' in locals() else ""
                            region = structured_data.get("job_info", {}).get("Местоположение", "")
                            salary_min = structured_data.get("salary", {}).get("Зарплата от", "")
                            salary_max = structured_data.get("salary", {}).get("Зарплата до", "")
                            
                            # Пытаемся извлечь числовые значения зарплаты
                            try:
                                if salary_min and salary_min != "Не указано":
                                    salary_min = int(''.join(filter(str.isdigit, str(salary_min))))
                                else:
                                    salary_min = None
                            except:
                                salary_min = None
                                
                            try:
                                if salary_max and salary_max != "Не указано":
                                    salary_max = int(''.join(filter(str.isdigit, str(salary_max))))
                                else:
                                    salary_max = None
                            except:
                                salary_max = None
                            
                            # Получаем информацию о зоне и коде профессии из job_bot если доступно
                            job_zone = None
                            job_code = None
                            if 'job_bot' in locals() and hasattr(job_bot, 'last_selected_job'):
                                job_zone = 3  # По умолчанию зона 3
                                job_code = job_bot.get_last_job_code()
                            
                            vacancy_id = db.add_vacancy(
                                name=filename,
                                content=job_description,
                                file_type=file_type,
                                file_path=selected_file,
                                pdf_path=pdf_path if 'pdf_path' in locals() else None,
                                job_title=job_title,
                                job_description=job_description,
                                application_deadline=application_deadline,
                                positions_count=positions_count,
                                region=region,
                                salary_min=salary_min,
                                salary_max=salary_max,
                                job_zone=job_zone,
                                job_code=job_code
                            )
                            
                            print(f"✓ Вакансия успешно сохранена в базу данных!")
                            print(f"  ID вакансии: {vacancy_id}")
                            print(f"  Название: {job_title}")
                            print(f"  Дата окончания набора: {application_deadline}")
                            print(f"  Количество позиций: {positions_count}")
                            print(f"  Регион: {region}")
                            
                        except Exception as e:
                            print(f"✗ Ошибка при сохранении в базу данных: {e}")
                        
                    else:
                        print("✗ Ошибка при извлечении текста из PDF")
                        
                except ImportError:
                    print("✗ Библиотеки для извлечения текста не установлены")
                    print("  Установите: pip install PyPDF2 pdfplumber")
                except Exception as e:
                    print(f"✗ Ошибка при извлечении текста: {e}")
                
                input("Нажмите Enter для продолжения...")
                break
            else:
                # Конвертируем в PDF
                print(f"\nКонвертация файла '{filename}' в PDF...")
                from pdf_converter import PDFConverter
                
                converter = PDFConverter()
                if not converter.is_libreoffice_available():
                    print("✗ LibreOffice не найден. Установите LibreOffice для конвертации файлов.")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                if not converter.can_convert(selected_file):
                    print(f"✗ Файл не поддерживается для конвертации: {file_ext}")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                try:
                    pdf_path = converter.convert_to_pdf(selected_file)
                    if pdf_path:
                        print(f"✓ Файл успешно конвертирован в PDF: {os.path.basename(pdf_path)}")
                        
                        # Извлекаем текст из конвертированного PDF
                        print(f"Извлечение текста из конвертированного PDF...")
                        try:
                            from pdf_text_extractor import PDFTextExtractor
                            extractor = PDFTextExtractor(pdf_path)
                            content = extractor.extract_all()
                            
                            if content:
                                print(f"✓ Текст успешно извлечен из конвертированного PDF!")
                                print(f"  - Страниц: {content.pages_count}")
                                print(f"  - Секций найдено: {len(content.structured_sections)}")
                                
                                # Показываем краткую информацию
                                print(f"\nИнформация о документе:")
                                print(f"  - Заголовок: {content.title}")
                                print(f"  - Автор: {content.author}")
                                
                                # Показываем найденные секции
                                if content.structured_sections:
                                    print(f"\nНайденные секции:")
                                    for section_name in content.structured_sections.keys():
                                        print(f"  - {section_name}")
                                
                                # Показываем первые 200 символов текста
                                print(f"\nНачало текста:")
                                preview = content.full_text[:200] + "..." if len(content.full_text) > 200 else content.full_text
                                print(f"  {preview}")
                                
                                # Структурируем текст с помощью ИИ
                                print(f"\nСтруктурирование текста с помощью ИИ...")
                                try:
                                    from ai import AIStructuredExtractor
                                    ai_extractor = AIStructuredExtractor()
                                    structured_data = ai_extractor.structure_vacancy_text(content.full_text)
                                    formatted_data = ai_extractor.format_structured_data(structured_data)
                                    
                                    print(f"✓ Текст успешно структурирован!")
                                    print(f"\n{formatted_data}")
                                    
                                    # Получаем детальную информацию через ZoneJobBot
                                    job_title = structured_data.get("job_info", {}).get("Название должности", "")
                                    if job_title and job_title != "Не указано":
                                        print(f"\n🔍 Получение детальной информации для вакансии: '{job_title}'...")
                                        try:
                                            sys.path.append(os.path.join(os.path.dirname(__file__), 'job'))
                                            from zone_job_bot import ZoneJobBot
                                            
                                            job_bot = ZoneJobBot()
                                            job_details = job_bot.process_request(job_title)
                                            
                                            print(f"✓ Детальная информация получена!")
                                            print(f"\n{job_details}")
                                            
                                            # Анализируем соответствие требований и Knowledge Areas
                                            print(f"\n🔍 Анализ соответствия требований и областей знаний...")
                                            try:
                                                from knowledge_matcher import KnowledgeMatcher
                                                
                                                # Получаем код профессии из job_bot
                                                job_code = job_bot.get_last_job_code()
                                                
                                                if job_code and hasattr(job_bot, 'knowledge_skills'):
                                                    job_knowledge = job_bot.get_knowledge_skills(job_code)
                                                    if job_knowledge.get('knowledge'):
                                                        matcher = KnowledgeMatcher()
                                                        analysis = matcher.analyze_knowledge_coverage(structured_data, job_knowledge['knowledge'])
                                                        analysis_result = matcher.format_analysis_result(analysis)
                                                        
                                                        print(f"✓ Анализ соответствия завершен!")
                                                        print(f"\n{analysis_result}")
                                                        
                                                        # Предлагаем пользователю дополнить недостающие области
                                                        if analysis['missing_areas']:
                                                            print(f"\n💡 РЕКОМЕНДАЦИИ:")
                                                            print("Рассмотрите возможность добавления следующих требований:")
                                                            for area, score in analysis['missing_areas'][:3]:  # Топ-3
                                                                print(f"   • {area} (важность: {score:.1f}/5.0)")
                                                    else:
                                                        print("⚠️ Данные о знаниях для этой профессии недоступны")
                                                else:
                                                    print("⚠️ Не удалось найти код профессии для анализа знаний")
                                                    
                                            except ImportError:
                                                print("✗ Модуль анализа знаний не найден")
                                            except Exception as e:
                                                print(f"✗ Ошибка при анализе знаний: {e}")
                                            
                                        except ImportError:
                                            print("✗ Модуль ZoneJobBot не найден")
                                        except Exception as e:
                                            print(f"✗ Ошибка при получении детальной информации: {e}")
                                    else:
                                        print("⚠️ Название вакансии не найдено, детальная информация недоступна")
                                    
                                except ImportError:
                                    print("✗ Модуль ИИ не найден")
                                except Exception as e:
                                    print(f"✗ Ошибка при структурировании: {e}")
                                
                                print(f"\n✓ Файл '{filename}' конвертирован и обработан для создания вакансии!")
                                
                                # Собираем дополнительную информацию от пользователя
                                print(f"\n📝 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ДЛЯ ВАКАНСИИ")
                                print("=" * 50)
                                
                                # Получаем дату окончания набора
                                application_deadline = get_application_deadline()
                                if application_deadline is None:
                                    print("❌ Создание вакансии отменено")
                                    input("Нажмите Enter для продолжения...")
                                    break
                                
                                # Получаем количество человек
                                positions_count = get_positions_count()
                                if positions_count is None:
                                    print("❌ Создание вакансии отменено")
                                    input("Нажмите Enter для продолжения...")
                                    break
                                
                                # Сохраняем вакансию в базу данных
                                print(f"\n💾 Сохранение вакансии в базу данных...")
                                try:
                                    db = TemplateDatabase()
                                    
                                    # Извлекаем информацию для сохранения
                                    job_title = structured_data.get("job_info", {}).get("Название должности", filename)
                                    job_description = content.full_text if 'content' in locals() else ""
                                    region = structured_data.get("job_info", {}).get("Местоположение", "")
                                    salary_min = structured_data.get("salary", {}).get("Зарплата от", "")
                                    salary_max = structured_data.get("salary", {}).get("Зарплата до", "")
                                    
                                    # Пытаемся извлечь числовые значения зарплаты
                                    try:
                                        if salary_min and salary_min != "Не указано":
                                            salary_min = int(''.join(filter(str.isdigit, str(salary_min))))
                                        else:
                                            salary_min = None
                                    except:
                                        salary_min = None
                                        
                                    try:
                                        if salary_max and salary_max != "Не указано":
                                            salary_max = int(''.join(filter(str.isdigit, str(salary_max))))
                                        else:
                                            salary_max = None
                                    except:
                                        salary_max = None
                                    
                                    # Получаем информацию о зоне и коде профессии из job_bot если доступно
                                    job_zone = None
                                    job_code = None
                                    if 'job_bot' in locals() and hasattr(job_bot, 'last_selected_job'):
                                        job_zone = 3  # По умолчанию зона 3
                                        job_code = job_bot.get_last_job_code()
                                    
                                    vacancy_id = db.add_vacancy(
                                        name=filename,
                                        content=job_description,
                                        file_type=file_type,
                                        file_path=selected_file,
                                        pdf_path=pdf_path,
                                        job_title=job_title,
                                        job_description=job_description,
                                        application_deadline=application_deadline,
                                        positions_count=positions_count,
                                        region=region,
                                        salary_min=salary_min,
                                        salary_max=salary_max,
                                        job_zone=job_zone,
                                        job_code=job_code
                                    )
                                    
                                    print(f"✓ Вакансия успешно сохранена в базу данных!")
                                    print(f"  ID вакансии: {vacancy_id}")
                                    print(f"  Название: {job_title}")
                                    print(f"  Дата окончания набора: {application_deadline}")
                                    print(f"  Количество позиций: {positions_count}")
                                    print(f"  Регион: {region}")
                                    
                                except Exception as e:
                                    print(f"✗ Ошибка при сохранении в базу данных: {e}")
                                
                            else:
                                print("✗ Ошибка при извлечении текста из конвертированного PDF")
                                
                        except ImportError:
                            print("✗ Библиотеки для извлечения текста не установлены")
                            print("  Установите: pip install PyPDF2 pdfplumber")
                        except Exception as e:
                            print(f"✗ Ошибка при извлечении текста: {e}")
                            print(f"✓ Файл '{filename}' конвертирован в PDF, но извлечение текста не удалось")
                    else:
                        print("✗ Ошибка при конвертации файла в PDF")
                except Exception as e:
                    print(f"✗ Ошибка при конвертации: {e}")
                
                input("Нажмите Enter для продолжения...")
                break

def handle_existing_vacancy():
    """Обрабатывает выбор существующей вакансии"""
    print("\nВыбрано: Выбрать существующую вакансию")
    input("Нажмите Enter для продолжения...")
    # Здесь будет логика выбора существующей вакансии

def main():
    """Основная функция приложения"""
    while True:
        clear_screen()
        show_main_menu()
        choice = get_user_choice(0, 2)
        
        if choice == 1:
            handle_new_vacancy()
        elif choice == 2:
            handle_existing_vacancy()
        elif choice == 0:
            print("\nДо свидания!")
            sys.exit(0)

if __name__ == "__main__":
    main()
