#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Структурированное извлечение текста из PDF файлов
Поддерживает различные форматы PDF и извлекает текст с сохранением структуры
"""

import os
import sys
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

try:
    import PyPDF2
    import pdfplumber
    from pdfplumber import PDF
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Установите необходимые библиотеки: pip install PyPDF2 pdfplumber")
    sys.exit(1)


@dataclass
class TextBlock:
    """Класс для представления блока текста"""
    text: str
    page_number: int
    x0: float
    y0: float
    x1: float
    y1: float
    font_size: Optional[float] = None
    font_name: Optional[str] = None
    is_bold: bool = False
    is_italic: bool = False


@dataclass
class ExtractedContent:
    """Класс для хранения извлеченного контента"""
    title: str
    author: str
    pages_count: int
    text_blocks: List[TextBlock]
    full_text: str
    structured_sections: Dict[str, str]


class PDFTextExtractor:
    """Класс для структурированного извлечения текста из PDF"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.extracted_content = None
        
    def extract_with_pypdf2(self) -> str:
        """Извлечение текста с помощью PyPDF2"""
        text = ""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Страница {page_num + 1} ---\n"
                    text += page_text
        except Exception as e:
            print(f"Ошибка при извлечении с PyPDF2: {e}")
        return text
    
    def extract_with_pdfplumber(self) -> ExtractedContent:
        """Извлечение структурированного текста с помощью pdfplumber"""
        text_blocks = []
        full_text = ""
        structured_sections = {}
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Получаем метаданные
                metadata = pdf.metadata or {}
                title = metadata.get('Title', 'Неизвестный документ')
                author = metadata.get('Author', 'Неизвестный автор')
                
                for page_num, page in enumerate(pdf.pages):
                    # Извлекаем текст с координатами
                    words = page.extract_words()
                    
                    # Извлекаем текст построчно
                    page_text = page.extract_text()
                    if page_text:
                        lines = page_text.split('\n')
                        for line in lines:
                            if line.strip():
                                text_block = TextBlock(
                                    text=line.strip(),
                                    page_number=page_num + 1,
                                    x0=0,
                                    y0=0,
                                    x1=0,
                                    y1=0
                                )
                                text_blocks.append(text_block)
                                full_text += line.strip() + "\n"
                    
                    # Извлекаем таблицы если есть
                    tables = page.extract_tables()
                    if tables:
                        for table_num, table in enumerate(tables):
                            table_text = f"\n--- Таблица {table_num + 1} на странице {page_num + 1} ---\n"
                            for row in table:
                                table_text += " | ".join([cell or "" for cell in row]) + "\n"
                            full_text += table_text
                
                # Структурируем контент по секциям
                structured_sections = self._structure_content(full_text)
                
                return ExtractedContent(
                    title=title,
                    author=author,
                    pages_count=len(pdf.pages),
                    text_blocks=text_blocks,
                    full_text=full_text,
                    structured_sections=structured_sections
                )
                
        except Exception as e:
            print(f"Ошибка при извлечении с pdfplumber: {e}")
            return None
    
    def _structure_content(self, text: str) -> Dict[str, str]:
        """Структурирование контента по секциям"""
        sections = {}
        
        # Паттерны для различных секций резюме
        patterns = {
            'Личная информация': r'(?i)(имя|фамилия|отчество|телефон|email|адрес|дата рождения)',
            'Опыт работы': r'(?i)(опыт работы|трудовой стаж|места работы|должности)',
            'Образование': r'(?i)(образование|университет|институт|колледж|диплом)',
            'Навыки': r'(?i)(навыки|умения|компетенции|технологии)',
            'Достижения': r'(?i)(достижения|награды|проекты|результаты)',
            'Языки': r'(?i)(языки|знание языков|английский|русский)',
            'Сертификаты': r'(?i)(сертификаты|курсы|обучение)'
        }
        
        lines = text.split('\n')
        current_section = 'Общая информация'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Проверяем, является ли строка заголовком секции
            section_found = False
            for section_name, pattern in patterns.items():
                if re.search(pattern, line):
                    # Сохраняем предыдущую секцию
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Начинаем новую секцию
                    current_section = section_name
                    current_content = [line]
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Сохраняем последнюю секцию
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def extract_all(self) -> ExtractedContent:
        """Извлечение текста всеми доступными методами"""
        print(f"Извлечение текста из: {self.pdf_path}")
        
        # Основной метод - pdfplumber
        content = self.extract_with_pdfplumber()
        
        if content is None:
            print("Ошибка при извлечении с pdfplumber, пробуем PyPDF2...")
            # Резервный метод - PyPDF2
            text = self.extract_with_pypdf2()
            content = ExtractedContent(
                title="Неизвестный документ",
                author="Неизвестный автор",
                pages_count=0,
                text_blocks=[],
                full_text=text,
                structured_sections={}
            )
        
        self.extracted_content = content
        return content
    
    def save_to_json(self, output_path: str):
        """Сохранение извлеченного контента в JSON"""
        if self.extracted_content is None:
            print("Сначала выполните извлечение текста")
            return
        
        # Конвертируем в словарь для JSON
        content_dict = {
            'title': self.extracted_content.title,
            'author': self.extracted_content.author,
            'pages_count': self.extracted_content.pages_count,
            'text_blocks': [asdict(block) for block in self.extracted_content.text_blocks],
            'full_text': self.extracted_content.full_text,
            'structured_sections': self.extracted_content.structured_sections
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(content_dict, f, ensure_ascii=False, indent=2)
        
        print(f"Результат сохранен в: {output_path}")
    
    def save_to_txt(self, output_path: str):
        """Сохранение извлеченного контента в текстовый файл"""
        if self.extracted_content is None:
            print("Сначала выполните извлечение текста")
            return
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Заголовок: {self.extracted_content.title}\n")
            f.write(f"Автор: {self.extracted_content.author}\n")
            f.write(f"Количество страниц: {self.extracted_content.pages_count}\n")
            f.write("=" * 50 + "\n\n")
            
            # Структурированные секции
            for section_name, content in self.extracted_content.structured_sections.items():
                f.write(f"\n=== {section_name.upper()} ===\n")
                f.write(content)
                f.write("\n" + "-" * 30 + "\n")
            
            # Полный текст
            f.write("\n\n=== ПОЛНЫЙ ТЕКСТ ===\n")
            f.write(self.extracted_content.full_text)
        
        print(f"Результат сохранен в: {output_path}")
    
    def print_summary(self):
        """Вывод краткой информации об извлеченном контенте"""
        if self.extracted_content is None:
            print("Сначала выполните извлечение текста")
            return
        
        content = self.extracted_content
        print("\n" + "=" * 50)
        print("КРАТКАЯ ИНФОРМАЦИЯ О ДОКУМЕНТЕ")
        print("=" * 50)
        print(f"Заголовок: {content.title}")
        print(f"Автор: {content.author}")
        print(f"Количество страниц: {content.pages_count}")
        print(f"Количество текстовых блоков: {len(content.text_blocks)}")
        print(f"Количество секций: {len(content.structured_sections)}")
        
        print("\nНайденные секции:")
        for section_name in content.structured_sections.keys():
            print(f"  - {section_name}")
        
        print("\nПервые 200 символов текста:")
        print(content.full_text[:200] + "..." if len(content.full_text) > 200 else content.full_text)


def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("Использование: python pdf_text_extractor.py <путь_к_pdf>")
        print("Пример: python pdf_text_extractor.py 'Образец-резюме-1-Бизнес-аналитик.pdf'")
        return
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"Файл не найден: {pdf_path}")
        return
    
    # Создаем экстрактор
    extractor = PDFTextExtractor(pdf_path)
    
    # Извлекаем текст
    content = extractor.extract_all()
    
    if content:
        # Выводим краткую информацию
        extractor.print_summary()
        
        # Сохраняем результаты
        base_name = os.path.splitext(pdf_path)[0]
        extractor.save_to_json(f"{base_name}_extracted.json")
        extractor.save_to_txt(f"{base_name}_extracted.txt")
        
        print(f"\nИзвлечение завершено успешно!")
    else:
        print("Ошибка при извлечении текста")


if __name__ == "__main__":
    main()
