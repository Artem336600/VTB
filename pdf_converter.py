#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import tempfile
import shutil
from pathlib import Path

class PDFConverter:
    """Класс для конвертации файлов в PDF с помощью LibreOffice"""
    
    def __init__(self):
        self.libreoffice_path = self._find_libreoffice()
    
    def _find_libreoffice(self):
        """Находит путь к LibreOffice"""
        possible_paths = [
            # Windows
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            r"C:\Program Files\LibreOffice 7.6\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice 7.6\program\soffice.exe",
            # Linux
            "/usr/bin/libreoffice",
            "/usr/local/bin/libreoffice",
            "/snap/bin/libreoffice",
            # macOS
            "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def is_libreoffice_available(self):
        """Проверяет, доступен ли LibreOffice"""
        return self.libreoffice_path is not None
    
    def convert_to_pdf(self, input_file_path, output_dir=None):
        """
        Конвертирует файл в PDF
        
        Args:
            input_file_path (str): Путь к исходному файлу
            output_dir (str): Директория для сохранения PDF (по умолчанию - та же директория)
        
        Returns:
            str: Путь к созданному PDF файлу или None в случае ошибки
        """
        if not self.is_libreoffice_available():
            raise Exception("LibreOffice не найден. Установите LibreOffice для конвертации файлов.")
        
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Файл не найден: {input_file_path}")
        
        # Определяем выходную директорию
        if output_dir is None:
            # По умолчанию сохраняем PDF в папку database_files
            output_dir = "database_files"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        
        # Создаем временную директорию для LibreOffice
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Команда для конвертации
            cmd = [
                self.libreoffice_path,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", temp_dir,
                input_file_path
            ]
            
            # Выполняем конвертацию
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # Таймаут 60 секунд
            )
            
            if result.returncode != 0:
                print(f"Ошибка конвертации: {result.stderr}")
                return None
            
            # Ищем созданный PDF файл
            input_filename = os.path.basename(input_file_path)
            input_name = os.path.splitext(input_filename)[0]
            pdf_filename = f"{input_name}.pdf"
            temp_pdf_path = os.path.join(temp_dir, pdf_filename)
            
            if not os.path.exists(temp_pdf_path):
                print(f"PDF файл не был создан: {pdf_filename}")
                return None
            
            # Перемещаем PDF в целевую директорию
            final_pdf_path = os.path.join(output_dir, pdf_filename)
            
            # Если файл уже существует, добавляем номер
            counter = 1
            original_path = final_pdf_path
            while os.path.exists(final_pdf_path):
                name, ext = os.path.splitext(original_path)
                final_pdf_path = f"{name}_{counter}{ext}"
                counter += 1
            
            shutil.move(temp_pdf_path, final_pdf_path)
            
            print(f"Файл успешно конвертирован в PDF: {final_pdf_path}")
            return final_pdf_path
            
        except subprocess.TimeoutExpired:
            print("Таймаут при конвертации файла")
            return None
        except Exception as e:
            print(f"Ошибка при конвертации: {e}")
            return None
        finally:
            # Очищаем временную директорию
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def get_supported_formats(self):
        """Возвращает список поддерживаемых форматов для конвертации"""
        return [
            'doc', 'docx', 'odt', 'rtf', 'txt',
            'xls', 'xlsx', 'ods', 'csv',
            'ppt', 'pptx', 'odp',
            'html', 'htm', 'xml'
        ]
    
    def can_convert(self, file_path):
        """Проверяет, можно ли конвертировать файл в PDF"""
        if not file_path:
            return False
        
        file_ext = os.path.splitext(file_path)[1].lower()[1:]  # Убираем точку
        return file_ext in self.get_supported_formats()

def test_converter():
    """Тестирует конвертер"""
    converter = PDFConverter()
    
    print("=== Тест PDF конвертера ===")
    print(f"LibreOffice найден: {converter.is_libreoffice_available()}")
    
    if converter.is_libreoffice_available():
        print(f"Путь к LibreOffice: {converter.libreoffice_path}")
        print(f"Поддерживаемые форматы: {', '.join(converter.get_supported_formats())}")
    else:
        print("LibreOffice не найден. Установите LibreOffice для работы с конвертацией.")
        print("Скачать можно с: https://www.libreoffice.org/")

if __name__ == "__main__":
    test_converter()
