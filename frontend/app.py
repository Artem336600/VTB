#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import traceback

# Add parent directory to path to import VTB modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'VTB'))

try:
    from database import TemplateDatabase
    from ai import AIStructuredExtractor # Back to using real AI
    from pdf_text_extractor import PDFTextExtractor
    from pdf_converter import PDFConverter
    from job.zone_job_bot import ZoneJobBot
    from knowledge_matcher import KnowledgeMatcher
except ImportError as e:
    print(f"Warning: Could not import VTB modules: {e}")
    print("Make sure you're running from the correct directory")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    """Extract text from uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file temporarily with proper extension
        original_filename = file.filename
        file_parts = original_filename.rsplit('.', 1)
        if len(file_parts) > 1:
            # Keep the extension safe
            name_part = secure_filename(file_parts[0])
            ext_part = file_parts[1].lower()
            filename = f"{name_part}.{ext_part}"
        else:
            filename = secure_filename(original_filename)
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Check if file needs conversion - use original filename for extension detection
            original_filename = file.filename
            file_parts = original_filename.rsplit('.', 1)
            file_ext = file_parts[1].lower() if len(file_parts) > 1 else 'unknown'
            
            if file_ext == 'pdf':
                # Direct PDF processing
                print(f"Processing PDF file directly: {file_path}")
                extractor = PDFTextExtractor(file_path)
                content = extractor.extract_all()
            else:
                # Convert to PDF first
                print(f"Converting {file_ext} file to PDF: {file_path}")
                converter = PDFConverter()
                if not converter.is_libreoffice_available():
                    error_message = (
                        "LibreOffice недоступен для автоматической конвертации. "
                        "Пожалуйста, воспользуйтесь одним из следующих способов:\n\n"
                        "1. Онлайн конвертеры:\n"
                        "   • SmallPDF (smallpdf.com)\n"
                        "   • ILovePDF (ilovepdf.com)\n"
                        "   • PDF24 (pdf24.org)\n\n"
                        "2. Программы:\n"
                        "   • Microsoft Word (Сохранить как PDF)\n"
                        "   • Google Docs (Скачать как PDF)\n"
                        "   • LibreOffice Writer\n\n"
                        "После конвертации загрузите полученный PDF файл."
                    )
                    return jsonify({'error': error_message}), 500
                
                if not converter.can_convert(file_path):
                    error_message = (
                        f"Файл типа '{file_ext}' не поддерживается для автоматической конвертации. "
                        "Пожалуйста, воспользуйтесь одним из следующих способов:\n\n"
                        "1. Онлайн конвертеры:\n"
                        "   • SmallPDF (smallpdf.com)\n"
                        "   • ILovePDF (ilovepdf.com)\n"
                        "   • PDF24 (pdf24.org)\n\n"
                        "2. Программы:\n"
                        "   • Microsoft Word (Сохранить как PDF)\n"
                        "   • Google Docs (Скачать как PDF)\n"
                        "   • LibreOffice Writer\n\n"
                        "После конвертации загрузите полученный PDF файл."
                    )
                    return jsonify({'error': error_message}), 400
                
                print(f"Starting conversion of {file_path}")
                pdf_path = converter.convert_to_pdf(file_path)
                if not pdf_path or not os.path.exists(pdf_path):
                    print(f"Conversion failed. PDF path: {pdf_path}")
                    # Предлагаем пользователю использовать сторонние сервисы
                    error_message = (
                        "Не удалось автоматически конвертировать файл в PDF. "
                        "Пожалуйста, воспользуйтесь одним из следующих способов:\n\n"
                        "1. Онлайн конвертеры:\n"
                        "   • SmallPDF (smallpdf.com)\n"
                        "   • ILovePDF (ilovepdf.com)\n"
                        "   • PDF24 (pdf24.org)\n\n"
                        "2. Программы:\n"
                        "   • Microsoft Word (Сохранить как PDF)\n"
                        "   • Google Docs (Скачать как PDF)\n"
                        "   • LibreOffice Writer\n\n"
                        "После конвертации загрузите полученный PDF файл."
                    )
                    return jsonify({'error': error_message}), 500
                
                print(f"Conversion successful. PDF created at: {pdf_path}")
                # Extract text from converted PDF
                extractor = PDFTextExtractor(pdf_path)
                content = extractor.extract_all()
                
                # Clean up converted PDF
                try:
                    os.remove(pdf_path)
                    print(f"Cleaned up temporary PDF: {pdf_path}")
                except Exception as e:
                    print(f"Failed to clean up PDF: {e}")
                    pass
            
            if not content or not content.full_text:
                error_message = (
                    "Не удалось извлечь текст из файла. Возможные причины:\n\n"
                    "1. Файл поврежден или имеет нестандартный формат\n"
                    "2. Файл защищен паролем\n"
                    "3. Файл содержит только изображения без текста\n\n"
                    "Попробуйте:\n"
                    "• Открыть файл в соответствующей программе и сохранить заново\n"
                    "• Конвертировать в PDF через онлайн-сервисы\n"
                    "• Проверить, что файл не поврежден"
                )
                return jsonify({'error': error_message}), 400
            
            # Prepare response
            result = {
                'full_text': content.full_text,
                'pages_count': content.pages_count,
                'title': content.title,
                'author': content.author,
                'structured_sections': content.structured_sections,
                'file_info': {
                    'name': filename,
                    'size': os.path.getsize(file_path),
                    'type': file_ext
                }
            }
            
            return jsonify(result)
            
        finally:
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except:
                pass
                
    except Exception as e:
        print(f"Error in extract_text: {e}")
        print(traceback.format_exc())
        error_message = (
            f"Произошла ошибка при обработке файла: {str(e)}\n\n"
            "Попробуйте:\n"
            "• Проверить, что файл не поврежден\n"
            "• Конвертировать файл в PDF через онлайн-сервисы\n"
            "• Убедиться, что файл не защищен паролем\n"
            "• Попробовать другой файл"
        )
        return jsonify({'error': error_message}), 500

@app.route('/api/structure-text', methods=['POST'])
def structure_text():
    """Structure text using AI"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        if not text.strip():
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Use AI to structure the text
        ai_extractor = AIStructuredExtractor()
        structured_data = ai_extractor.structure_vacancy_text(text)
        
        return jsonify(structured_data)
        
    except Exception as e:
        print(f"Error in structure_text: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Text structuring failed: {str(e)}'}), 500

@app.route('/api/analyze-job', methods=['POST'])
def analyze_job():
    """Analyze job and get detailed information with O*NET-based scoring"""
    try:
        data = request.get_json()
        if not data or 'job_title' not in data:
            return jsonify({'error': 'No job title provided'}), 400
        
        job_title = data['job_title']
        structured_data = data.get('structured_data', {})
        
        if not job_title or job_title == 'Не указано':
            return jsonify({'error': 'Invalid job title'}), 400
        
        result = {
            'job_details': '',
            'knowledge_analysis': '',
            'recommendations': [],
            'skill_scoring': {}
        }
        
        try:
            # Get job details using ZoneJobBot
            job_bot = ZoneJobBot()
            job_details = job_bot.process_request(job_title)
            result['job_details'] = job_details
            
            # NEW: Analyze requirements and score skills using AI + O*NET
            ai_extractor = AIStructuredExtractor()
            skill_scoring = ai_extractor.analyze_requirements_and_score(structured_data, job_title)
            result['skill_scoring'] = skill_scoring
            
            # Get job code for knowledge analysis
            job_code = job_bot.get_last_job_code()
            
            if job_code and hasattr(job_bot, 'knowledge_skills'):
                try:
                    job_knowledge = job_bot.get_knowledge_skills(job_code)
                    if job_knowledge.get('knowledge'):
                        # Analyze knowledge coverage
                        matcher = KnowledgeMatcher()
                        analysis = matcher.analyze_knowledge_coverage(structured_data, job_knowledge['knowledge'])
                        analysis_result = matcher.format_analysis_result(analysis)
                        result['knowledge_analysis'] = analysis_result
                        
                        # Generate recommendations
                        if analysis.get('missing_areas'):
                            recommendations = []
                            for area, score in analysis['missing_areas'][:3]:  # Top 3
                                recommendations.append(f"Рассмотрите добавление требований по области: {area} (важность: {score:.1f}/5.0)")
                            result['recommendations'] = recommendations
                except Exception as e:
                    print(f"Knowledge analysis error: {e}")
                    result['knowledge_analysis'] = "Анализ соответствия знаний недоступен"
            else:
                result['knowledge_analysis'] = "Данные о знаниях для этой профессии недоступны"
                
        except Exception as e:
            print(f"Job analysis error: {e}")
            result['job_details'] = f"Детальная информация о профессии недоступна: {str(e)}"
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analyze_job: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Job analysis failed: {str(e)}'}), 500

@app.route('/api/save-vacancy', methods=['POST'])
def save_vacancy():
    """Save vacancy to database"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        data_str = request.form.get('data')
        
        if not data_str:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid data format'}), 400
        
        # Save file temporarily with proper extension
        original_filename = file.filename
        file_parts = original_filename.rsplit('.', 1)
        if len(file_parts) > 1:
            # Keep the extension safe
            name_part = secure_filename(file_parts[0])
            ext_part = file_parts[1].lower()
            filename = f"{name_part}.{ext_part}"
        else:
            filename = secure_filename(original_filename)
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Extract information for saving
            structured_data = data.get('structured_data', {})
            extracted_data = data.get('extracted_data', {})
            
            job_title = structured_data.get('job_info', {}).get('Название должности', filename)
            job_description = extracted_data.get('full_text', '')
            region = data.get('region', '') or structured_data.get('job_info', {}).get('Местоположение', '')
            
            # Extract salary information
            salary_min = None
            salary_max = None
            salary_data = structured_data.get('salary', {})
            
            try:
                salary_from = salary_data.get('Зарплата от', '')
                if salary_from and salary_from != 'Не указано':
                    salary_min = int(''.join(filter(str.isdigit, str(salary_from))))
            except:
                pass
            
            try:
                salary_to = salary_data.get('Зарплата до', '')
                if salary_to and salary_to != 'Не указано':
                    salary_max = int(''.join(filter(str.isdigit, str(salary_to))))
            except:
                pass
            
            # Get job zone and code from analysis
            job_zone = None
            job_code = None
            
            try:
                # Try to get job code from analysis data
                analysis_data = data.get('analysis_data', {})
                if 'job_code' in analysis_data:
                    job_code = analysis_data['job_code']
                    job_zone = 3  # Default zone
            except:
                pass
            
            # Determine file type safely - use original filename
            original_filename = file.filename
            file_parts = original_filename.rsplit('.', 1)
            file_type = file_parts[1].lower() if len(file_parts) > 1 else 'unknown'
            
            # Save to database
            db = TemplateDatabase()
            vacancy_id = db.add_vacancy(
                name=filename,
                content=job_description,
                file_type=file_type,
                file_path=file_path,
                pdf_path=None,  # We don't keep the PDF
                job_title=job_title,
                job_description=job_description,
                application_deadline=data.get('application_deadline'),
                positions_count=data.get('positions_count'),
                region=region,
                salary_min=salary_min,
                salary_max=salary_max,
                job_zone=job_zone,
                job_code=job_code,
                structured_data=structured_data,
                skill_scores=data.get('skill_scores')
            )
            
            # Prepare response
            result = {
                'vacancy_id': vacancy_id,
                'job_title': job_title,
                'application_deadline': data.get('application_deadline'),
                'positions_count': data.get('positions_count'),
                'region': region,
                'salary_min': salary_min,
                'salary_max': salary_max
            }
            
            return jsonify(result)
            
        finally:
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except:
                pass
                
    except Exception as e:
        print(f"Error in save_vacancy: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to save vacancy: {str(e)}'}), 500

@app.route('/api/vacancies', methods=['GET'])
def get_vacancies():
    """Get all vacancies from database"""
    try:
        db = TemplateDatabase()
        templates = db.get_all_templates()
        
        vacancies = []
        for template in templates:
            template_id, name, content, file_type, file_path, file_size, pdf_path, pdf_size, is_converted, created_at = template[:10]
            
            # Get additional fields if they exist
            job_title = template[10] if len(template) > 10 else None
            job_description = template[11] if len(template) > 11 else None
            application_deadline = template[12] if len(template) > 12 else None
            positions_count = template[13] if len(template) > 13 else None
            region = template[14] if len(template) > 14 else None
            salary_min = template[15] if len(template) > 15 else None
            salary_max = template[16] if len(template) > 16 else None
            job_zone = template[17] if len(template) > 17 else None
            job_code = template[18] if len(template) > 18 else None
            structured_data = template[19] if len(template) > 19 else None
            skill_scores = template[20] if len(template) > 20 else None
            
            # Parse JSON fields
            try:
                structured_data = json.loads(structured_data) if structured_data else None
            except:
                structured_data = None
                
            try:
                skill_scores = json.loads(skill_scores) if skill_scores else None
            except:
                skill_scores = None
            
            vacancy = {
                'id': template_id,
                'name': name,
                'file_type': file_type,
                'file_size': file_size,
                'created_at': created_at,
                'job_title': job_title,
                'job_description': job_description,
                'application_deadline': application_deadline,
                'positions_count': positions_count,
                'region': region,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'job_zone': job_zone,
                'job_code': job_code,
                'structured_data': structured_data,
                'skill_scores': skill_scores
            }
            vacancies.append(vacancy)
        
        # Sort by creation date (newest first)
        vacancies.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify(vacancies)
        
    except Exception as e:
        print(f"Error in get_vacancies: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to get vacancies: {str(e)}'}), 500

@app.route('/api/vacancy/<int:vacancy_id>', methods=['GET'])
def get_vacancy(vacancy_id):
    """Get specific vacancy by ID"""
    try:
        db = TemplateDatabase()
        template = db.get_template_by_id(vacancy_id)
        
        if not template:
            return jsonify({'error': 'Vacancy not found'}), 404
        
        template_id, name, content, file_type, file_path, file_size, pdf_path, pdf_size, is_converted, created_at = template[:10]
        
        # Get additional fields if they exist
        job_title = template[10] if len(template) > 10 else None
        job_description = template[11] if len(template) > 11 else None
        application_deadline = template[12] if len(template) > 12 else None
        positions_count = template[13] if len(template) > 13 else None
        region = template[14] if len(template) > 14 else None
        salary_min = template[15] if len(template) > 15 else None
        salary_max = template[16] if len(template) > 16 else None
        job_zone = template[17] if len(template) > 17 else None
        job_code = template[18] if len(template) > 18 else None
        structured_data = template[19] if len(template) > 19 else None
        skill_scores = template[20] if len(template) > 20 else None
        
        # Parse JSON fields
        try:
            structured_data = json.loads(structured_data) if structured_data else None
        except:
            structured_data = None
            
        try:
            skill_scores = json.loads(skill_scores) if skill_scores else None
        except:
            skill_scores = None
        
        vacancy = {
            'id': template_id,
            'name': name,
            'content': content,
            'file_type': file_type,
            'file_size': file_size,
            'created_at': created_at,
            'job_title': job_title,
            'job_description': job_description,
            'application_deadline': application_deadline,
            'positions_count': positions_count,
            'region': region,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'job_zone': job_zone,
            'job_code': job_code,
            'structured_data': structured_data,
            'skill_scores': skill_scores
        }
        
        return jsonify(vacancy)
        
    except Exception as e:
        print(f"Error in get_vacancy: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to get vacancy: {str(e)}'}), 500

@app.route('/api/vacancy/<int:vacancy_id>', methods=['DELETE'])
def delete_vacancy(vacancy_id):
    """Delete vacancy from database"""
    try:
        db = TemplateDatabase()
        success = db.delete_template(vacancy_id)
        
        if not success:
            return jsonify({'error': 'Vacancy not found'}), 404
        
        return jsonify({'message': 'Vacancy deleted successfully'})
        
    except Exception as e:
        print(f"Error in delete_vacancy: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to delete vacancy: {str(e)}'}), 500

@app.route('/api/vacancy/<int:vacancy_id>', methods=['PUT'])
def update_vacancy(vacancy_id):
    """Update vacancy structured data and skill scores"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        db = TemplateDatabase()
        
        # Обновляем все поля
        job_title = data.get('job_title')
        positions_count = data.get('positions_count')
        region = data.get('region')
        application_deadline = data.get('application_deadline')
        structured_data = data.get('structured_data')
        skill_scores = data.get('skill_scores')
        
        success = db.update_vacancy_full(vacancy_id, job_title, positions_count, region, 
                                        application_deadline, structured_data, skill_scores)
        
        if not success:
            return jsonify({'error': 'Vacancy not found'}), 404
        return jsonify({'message': 'Vacancy updated successfully'})
        
    except Exception as e:
        print(f"Error in update_vacancy: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to update vacancy: {str(e)}'}), 500

@app.route('/api/save-template', methods=['POST'])
def save_template():
    """Save template from card data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        db = TemplateDatabase()
        
        # Создаем шаблон из данных карточки
        template_id = db.add_vacancy(
            name=data.get('job_title', 'Шаблон'),
            content='',  # Пустой контент для шаблона
            file_type='template',
            file_path=None,
            pdf_path=None,
            job_title=data.get('job_title'),
            job_description='',
            application_deadline=data.get('application_deadline'),
            positions_count=data.get('positions_count', 1),
            region=data.get('region'),
            salary_min=None,
            salary_max=None,
            job_zone=None,
            job_code=None,
            structured_data=data.get('structured_data'),
            skill_scores=data.get('skill_scores')
        )
        
        return jsonify({
            'template_id': template_id,
            'message': 'Template saved successfully'
        })
        
    except Exception as e:
        print(f"Error in save_template: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to save template: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 10MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    """Analyze a single resume against a vacancy"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        vacancy_id = request.form.get('vacancy_id')
        
        if not vacancy_id:
            return jsonify({'error': 'No vacancy ID provided'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get vacancy data
        db = TemplateDatabase()
        vacancy = db.get_template_by_id(int(vacancy_id))
        
        if not vacancy:
            return jsonify({'error': 'Vacancy not found'}), 404
        
        # Parse vacancy data - vacancy is a tuple, so we need to access by index
        # Columns: id, name, content, file_type, file_path, file_size, pdf_path, pdf_size, is_converted, created_at,
        #          job_title, job_description, application_deadline, positions_count, region, 
        #          salary_min, salary_max, job_zone, job_code, structured_data, skill_scores
        structured_data = json.loads(vacancy[19] if vacancy[19] else '{}')  # structured_data column
        skill_scores = json.loads(vacancy[20] if vacancy[20] else '{}')     # skill_scores column
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Convert to PDF if needed
            if not filename.lower().endswith('.pdf'):
                converter = PDFConverter()
                if converter.can_convert(file_path):
                    pdf_path = converter.convert_to_pdf(file_path)
                    if pdf_path and os.path.exists(pdf_path):
                        # Use converted PDF
                        file_path = pdf_path
                    else:
                        return jsonify({'error': 'Failed to convert file to PDF'}), 400
                else:
                    return jsonify({'error': f'File type {filename.split(".")[-1]} not supported for conversion'}), 400
            
            # Extract text from PDF
            extractor = PDFTextExtractor(file_path)
            extracted_content = extractor.extract_all()
            text = extracted_content.full_text
            
            if not text or len(text.strip()) < 50:
                return jsonify({'error': 'No text could be extracted from the file'}), 400
            
            # Analyze resume using AI
            ai_extractor = AIStructuredExtractor()
            resume_analysis = ai_extractor.analyze_resume_against_vacancy(
                resume_text=text,
                vacancy_structured_data=structured_data,
                vacancy_skill_scores=skill_scores
            )
            
            # Add filename to result
            resume_analysis['filename'] = filename
            
            return jsonify(resume_analysis)
            
        finally:
            # Clean up temporary files
            if os.path.exists(file_path):
                os.remove(file_path)
    
    except Exception as e:
        print(f"Error in analyze_resume: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Error analyzing resume: {str(e)}'}), 500

if __name__ == '__main__':
    # Check if we can import VTB modules
    try:
        from database import TemplateDatabase
        print("✓ VTB modules imported successfully")
    except ImportError as e:
        print(f"⚠ Warning: Could not import VTB modules: {e}")
        print("Make sure you're running from the correct directory")
    
    print("Starting Flask application...")
    print("Frontend will be available at: http://localhost:5000")
    print("Make sure the VTB backend modules are accessible")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
