// Main Application Class
class VacancyProcessor {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 5;
        this.selectedFile = null;
        this.extractedData = null;
        this.structuredData = null;
        this.originalStructuredData = null; // Backup for editing
        this.analysisData = null;
        this.vacancyId = null;
        this.isEditMode = false;
        this.editingTemplateId = null;
        this.customCategories = {}; // Для хранения пользовательских категорий
        this.skillScores = {}; // Для хранения баллов навыков
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateProgress();
    }

    bindEvents() {
        // Welcome screen buttons
        document.getElementById('createTemplateBtn').addEventListener('click', () => this.startProcess());
        document.getElementById('chooseTemplateBtn').addEventListener('click', () => this.viewExistingTemplates());
        document.getElementById('viewActiveVacanciesBtn').addEventListener('click', () => this.viewActiveVacancies());
        document.getElementById('uploadResumesBtn').addEventListener('click', () => this.uploadResumes());
        document.getElementById('logoBtn').addEventListener('click', () => this.backToWelcome());
        document.getElementById('backToWelcomeBtn').addEventListener('click', () => this.backToWelcome());

        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        document.getElementById('removeFileBtn').addEventListener('click', () => this.removeFile());

        // Step navigation
        document.getElementById('nextStep1Btn').addEventListener('click', () => this.nextStep());
        document.getElementById('nextStep2Btn').addEventListener('click', () => this.nextStep());
        document.getElementById('nextStep3Btn').addEventListener('click', () => this.nextStep());
        document.getElementById('nextStep4Btn').addEventListener('click', () => this.nextStep());
        
        document.getElementById('prevStep2Btn').addEventListener('click', () => this.prevStep());
        document.getElementById('prevStep3Btn').addEventListener('click', () => this.prevStep());
        document.getElementById('prevStep4Btn').addEventListener('click', () => this.prevStep());
        document.getElementById('prevStep5Btn').addEventListener('click', () => this.prevStep());

        // Save vacancy
        document.getElementById('saveVacancyBtn').addEventListener('click', () => this.saveVacancy());
        
        // Quick add field functionality
        document.getElementById('quickAddFieldBtn').addEventListener('click', () => this.addQuickField());
        document.getElementById('quickFieldName').addEventListener('input', (e) => this.showQuickFieldSuggestions(e.target.value));
        document.getElementById('quickFieldCategory').addEventListener('change', () => this.handleCategoryChange());
        
        // Enter key support for quick add
        document.getElementById('quickFieldValue').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.addQuickField();
            }
        });
        
        // Success actions

        // Modal
        document.getElementById('errorModalClose').addEventListener('click', () => this.closeErrorModal());
        document.getElementById('errorModalOk').addEventListener('click', () => this.closeErrorModal());
    }

    // Welcome Screen Methods
    startProcess() {
        document.getElementById('welcomeScreen').style.display = 'none';
        document.getElementById('processContainer').style.display = 'block';
        this.showStep(1);
    }

    viewExistingVacancies() {
        document.getElementById('welcomeScreen').style.display = 'none';
        document.getElementById('existingVacancies').style.display = 'block';
        
        // Обновляем заголовок для существующих вакансий
        const header = document.querySelector('.vacancies-header h2');
        if (header) {
            header.textContent = 'Существующие вакансии';
        }
        
        this.loadExistingVacancies();
    }

    viewActiveVacancies() {
        document.getElementById('welcomeScreen').style.display = 'none';
        document.getElementById('existingVacancies').style.display = 'block';
        
        // Обновляем заголовок для активных вакансий
        const header = document.querySelector('.vacancies-header h2');
        if (header) {
            header.textContent = 'Действующие вакансии';
        }
        
        this.loadExistingVacancies();
    }
    
    viewExistingTemplates() {
        document.getElementById('welcomeScreen').style.display = 'none';
        document.getElementById('existingVacancies').style.display = 'block';
        
        // Обновляем заголовок для шаблонов
        const header = document.querySelector('.vacancies-header h2');
        if (header) {
            header.textContent = 'Выберите существующий шаблон';
        }
        
        this.loadExistingTemplates();
    }

    backToWelcome() {
        try {
            // Скрываем все экраны
            const processContainer = document.getElementById('processContainer');
            const existingVacancies = document.getElementById('existingVacancies');
            const welcomeScreen = document.getElementById('welcomeScreen');
            
            if (processContainer) processContainer.style.display = 'none';
            if (existingVacancies) existingVacancies.style.display = 'none';
            
            // Показываем главный экран
            if (welcomeScreen) welcomeScreen.style.display = 'block';
            
            // Сбрасываем процесс только если он был запущен
            if (this.currentStep > 1) {
                this.resetProcess();
            }
        } catch (error) {
            console.error('Error in backToWelcome:', error);
            // Fallback - просто показываем главный экран
            const welcomeScreen = document.getElementById('welcomeScreen');
            if (welcomeScreen) welcomeScreen.style.display = 'block';
        }
    }

    // File Upload Methods
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    processFile(file) {
        // Validate file type
        const allowedTypes = ['application/pdf', 'application/msword', 
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                             'text/plain'];
        
        if (!allowedTypes.includes(file.type)) {
            this.showError('Неподдерживаемый тип файла. Разрешены: PDF, DOC, DOCX, TXT');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.showError('Файл слишком большой. Максимальный размер: 10MB');
            return;
        }

        this.selectedFile = file;
        this.displayFileInfo(file);
        document.getElementById('nextStep1Btn').disabled = false;
    }

    displayFileInfo(file) {
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileType = document.getElementById('fileType');
        const fileInfo = document.getElementById('fileInfo');

        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        fileType.textContent = this.getFileTypeLabel(file.type);

        fileInfo.style.display = 'block';
    }

    removeFile() {
        this.selectedFile = null;
        document.getElementById('fileInput').value = '';
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('nextStep1Btn').disabled = true;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getFileTypeLabel(type) {
        const types = {
            'application/pdf': 'PDF',
            'application/msword': 'DOC',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
            'text/plain': 'TXT'
        };
        return types[type] || 'Unknown';
    }

    // Step Navigation Methods
    nextStep() {
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.updateProgress();
            this.showStep(this.currentStep);
            
            // Process current step
            this.processCurrentStep();
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateProgress();
            this.showStep(this.currentStep);
        }
    }

    showStep(stepNumber) {
        // Hide all step panels
        const panels = document.querySelectorAll('.step-panel');
        panels.forEach(panel => {
            panel.classList.remove('active');
            panel.style.display = 'none';
        });

        // Show current step panel
        const currentPanel = document.getElementById(`step${stepNumber}`);
        if (currentPanel) {
            currentPanel.classList.add('active');
            currentPanel.style.display = 'block';
        }

        // Update step indicators
        const steps = document.querySelectorAll('.step');
        steps.forEach((step, index) => {
            step.classList.remove('active', 'completed');
            if (index + 1 < stepNumber) {
                step.classList.add('completed');
            } else if (index + 1 === stepNumber) {
                step.classList.add('active');
            }
        });
    }

    updateProgress() {
        const progress = (this.currentStep / this.totalSteps) * 100;
        document.getElementById('progressFill').style.width = `${progress}%`;
    }

    // Step Processing Methods
    async processCurrentStep() {
        switch (this.currentStep) {
            case 2:
                await this.processTextExtraction();
                break;
            case 3:
                await this.processAIStructuring();
                break;
            case 4:
                this.prepareSkillsScoring();
                break;
            case 5:
                this.prepareSaveStep();
                break;
        }
    }

    async processTextExtraction() {
        this.disableNextButton();
        
        try {
            const formData = new FormData();
            formData.append('file', this.selectedFile);

            // Добавляем таймаут для запроса
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 секунд

            const response = await fetch('/api/extract-text', {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                // Пытаемся распознать ошибки конвертации и сразу просим загрузить PDF
                let friendly = 'Пожалуйста, загрузите PDF-файл. Если исходник не PDF — сконвертируйте через SmallPDF / ILovePDF / PDF24 и попробуйте снова.';
                try {
                    const text = await response.text();
                    try {
                        const json = JSON.parse(text);
                        const err = (json && json.error ? String(json.error) : '').toLowerCase();
                        if (
                            err.includes('не поддерживается для автоматической конвертации') ||
                            err.includes('libreoffice недоступен') ||
                            err.includes('failed to convert') ||
                            err.includes('cannot be converted') ||
                            err.includes('file type')
                        ) {
                            throw new Error(friendly);
                        }
                        throw new Error(`Ошибка сервера: ${response.status} - ${json.error || text}`);
                    } catch {
                        // text не JSON
                        if (
                            text.toLowerCase().includes('не поддерживается для автоматической конвертации') ||
                            text.toLowerCase().includes('libreoffice') ||
                            text.toLowerCase().includes('failed to convert') ||
                            text.toLowerCase().includes('cannot be converted') ||
                            text.toLowerCase().includes('file type')
                        ) {
                            throw new Error(friendly);
                        }
                        throw new Error(`Ошибка сервера: ${response.status} - ${text}`);
                    }
                } catch (e) {
                    throw e;
                }
            }

            this.extractedData = await response.json();
            this.displayExtractionResult();
            
        } catch (error) {
            if (error.name === 'AbortError') {
                this.showError('Превышено время ожидания. Проверьте подключение к серверу.');
            } else if (error.message.includes('Failed to fetch')) {
                this.showError('Не удается подключиться к серверу. Убедитесь, что бэкенд запущен на порту 5000.');
            } else {
                this.showError('Ошибка при извлечении текста: ' + error.message);
            }
        } finally {
            const processingArea = document.querySelector('#step2 .processing-area');
            if (processingArea) processingArea.style.display = 'none';
            this.enableNextButton();
        }
    }

    displayExtractionResult() {
        const result = document.getElementById('extractionResult');
        const pagesCount = document.getElementById('pagesCount');
        const sectionsCount = document.getElementById('sectionsCount');
        const charCount = document.getElementById('charCount');
        const textPreview = document.getElementById('textPreview');

        pagesCount.textContent = this.extractedData.pages_count || 'N/A';
        sectionsCount.textContent = this.extractedData.structured_sections ? 
            Object.keys(this.extractedData.structured_sections).length : 'N/A';
        charCount.textContent = this.extractedData.full_text ? 
            this.extractedData.full_text.length.toLocaleString() : 'N/A';

        if (this.extractedData.full_text) {
            // Показываем весь текст, но ограничиваем высоту контейнера
            textPreview.textContent = this.extractedData.full_text;
        }

        result.style.display = 'block';
        
        // Скрываем область загрузки
        const processingArea = document.querySelector('#step2 .processing-area');
        if (processingArea) {
            processingArea.style.display = 'none';
        }
    }

    async processAIStructuring() {
        this.disableNextButton();
        
        try {
            const response = await fetch('/api/structure-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: this.extractedData.full_text
                })
            });

            if (!response.ok) {
                throw new Error('Ошибка при структурировании текста');
            }

            this.structuredData = await response.json();
            this.displayStructuredData();
            // НЕ переходим автоматически - пользователь должен нажать "Далее" для перехода к разбаловке
            
        } catch (error) {
            this.showError('Ошибка при структурировании текста: ' + error.message);
        } finally {
            const processingArea = document.querySelector('#step3 .processing-area');
            if (processingArea) processingArea.style.display = 'none';
            this.enableNextButton();
        }
    }

    displayStructuredData() {
        // Job Info
        this.displayDataGrid('jobInfoGrid', this.structuredData.job_info);
        
        // Salary
        this.displayDataGrid('salaryGrid', this.structuredData.salary);
        
        // Requirements
        this.displayDataGrid('requirementsGrid', this.structuredData.requirements);
        
        // Responsibilities
        this.displayList('responsibilitiesList', this.structuredData.responsibilities, 'responsibility-item');
        
        // Benefits
        this.displayList('benefitsList', this.structuredData.benefits, 'benefit-item');

        document.getElementById('aiResult').style.display = 'block';
        
        // Скрываем область загрузки
        const processingArea = document.querySelector('#step3 .processing-area');
        if (processingArea) {
            processingArea.style.display = 'none';
        }
    }
    
    showScores() {
        // Просто переходим к следующему шагу (анализ профессии)
        this.nextStep();
    }
    

    
    

    displayDataGrid(containerId, data) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        if (!data) return;

        Object.entries(data).forEach(([key, value]) => {
            if (value && value !== 'Не указано') {
                const item = document.createElement('div');
                item.className = 'data-item editable';
                item.innerHTML = `
                    <div class="field-content">
                        <div class="data-label">${key}</div>
                        <div class="data-value">${value}</div>
                    </div>
                    <div class="field-actions">
                        <button class="btn-edit" onclick="app.editField(this)" title="Редактировать">
                            <span>✏️</span>
                        </button>
                        <button class="btn-delete" onclick="app.deleteField(this)" title="Удалить">
                            <span>🗑️</span>
                        </button>
                    </div>
                `;
                container.appendChild(item);
            }
        });
    }

    displayList(containerId, items, itemClass) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        if (!items || !Array.isArray(items)) return;

        items.forEach((item, index) => {
            if (item && item !== 'Не указано') {
                const itemElement = document.createElement('div');
                itemElement.className = `${itemClass} editable`;
                itemElement.innerHTML = `
                    <div class="list-item-content">
                        <span class="list-item-text">${item}</span>
                    </div>
                    <div class="list-item-actions">
                        <button class="btn-edit" onclick="app.editListItem(this, '${containerId}', ${index})" title="Редактировать">
                            <span>✏️</span>
                        </button>
                        <button class="btn-delete" onclick="app.deleteListItem(this, '${containerId}', ${index})" title="Удалить">
                            <span>🗑️</span>
                        </button>
                    </div>
                `;
                container.appendChild(itemElement);
            }
        });
        
        // Кнопка добавления теперь в общем меню
    }

    async processJobAnalysis() {
        this.disableNextButton();
        
        try {
            const jobTitle = this.structuredData.job_info?.['Название должности'];
            if (!jobTitle || jobTitle === 'Не указано') {
                throw new Error('Название должности не найдено');
            }

            const response = await fetch('/api/analyze-job', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_title: jobTitle,
                    structured_data: this.structuredData
                })
            });

            if (!response.ok) {
                throw new Error('Ошибка при анализе профессии');
            }

            this.analysisData = await response.json();
            this.displayAnalysisResult();
            
        } catch (error) {
            this.showError('Ошибка при анализе профессии: ' + error.message);
        } finally {
            this.enableNextButton();
        }
    }

    displayJobDetails() {
        // Создаем или находим контейнер для деталей работы
        let jobDetails = document.getElementById('jobDetails');
        if (!jobDetails) {
            jobDetails = document.createElement('div');
            jobDetails.id = 'jobDetails';
            jobDetails.className = 'job-details';
            
            // Добавляем в начало analysisResult
            const analysisResult = document.getElementById('analysisResult');
            if (analysisResult) {
                analysisResult.insertBefore(jobDetails, analysisResult.firstChild);
            }
        }
        
        if (this.analysisData && this.analysisData.job_details) {
            jobDetails.innerHTML = this.analysisData.job_details;
        } else {
            // Fallback - показываем информацию из структурированных данных
            jobDetails.innerHTML = `
                <div class="job-detail-item">
                    <strong>Должность:</strong> ${this.structuredData?.job_info?.['Название должности'] || 'Не указано'}
                </div>
                <div class="job-detail-item">
                    <strong>Компания:</strong> ${this.structuredData?.job_info?.['Компания'] || 'Не указано'}
                </div>
                <div class="job-detail-item">
                    <strong>Местоположение:</strong> ${this.structuredData?.job_info?.['Местоположение'] || 'Не указано'}
                </div>
                <div class="job-detail-item">
                    <strong>Уровень:</strong> ${this.structuredData?.job_info?.['Уровень'] || 'Не указано'}
                </div>
            `;
        }
    }
    
    displayKnowledgeAnalysis() {
        const knowledgeAnalysis = document.getElementById('knowledgeAnalysis');
        if (this.analysisData && this.analysisData.knowledge_analysis) {
            knowledgeAnalysis.innerHTML = this.analysisData.knowledge_analysis;
        } else {
            knowledgeAnalysis.innerHTML = `
                <div class="analysis-item">
                    <h4>Анализ соответствия знаний</h4>
                    <p>Анализ основан на структурированных данных вакансии. Рекомендуется детальное изучение требований.</p>
                </div>
            `;
        }
    }
    
    displayRecommendations() {
        const recommendationsList = document.getElementById('recommendationsList');
        if (this.analysisData && this.analysisData.recommendations && Array.isArray(this.analysisData.recommendations)) {
            recommendationsList.innerHTML = '';
            this.analysisData.recommendations.forEach(rec => {
                const item = document.createElement('div');
                item.className = 'recommendation-item';
                item.textContent = rec;
                recommendationsList.appendChild(item);
            });
        } else {
            recommendationsList.innerHTML = `
                <div class="recommendation-item">
                    <div class="recommendation-icon">📚</div>
                    <div class="recommendation-content">
                        <div class="recommendation-title">Изучение требований</div>
                        <div class="recommendation-description">Внимательно изучите все требования к позиции и оцените свой уровень соответствия.</div>
                    </div>
                </div>
                <div class="recommendation-item">
                    <div class="recommendation-icon">💼</div>
                    <div class="recommendation-content">
                        <div class="recommendation-title">Подготовка к собеседованию</div>
                        <div class="recommendation-description">Подготовьте примеры проектов и кейсов, демонстрирующих ваши навыки.</div>
                    </div>
                </div>
            `;
        }
    }

    prepareSkillsScoring() {
        // Инициализируем баллы навыков
        this.initializeSkillScores();
        
        // Отображаем интерфейс редактирования
        this.displaySkillsScoringInterface();
    }

    initializeSkillScores() {
        // Используем данные от ИИ, если они есть
        if (this.analysisData && this.analysisData.skill_scoring) {
            const aiScoring = this.analysisData.skill_scoring;
            
            this.skillScores = {
                technical: aiScoring.technical_skills || {},
                programming: aiScoring.programming_languages || {},
                tools: aiScoring.tools || {}
            };
            
            // Добавляем soft skills и domain knowledge в technical, если они есть
            if (aiScoring.soft_skills) {
                Object.assign(this.skillScores.technical, aiScoring.soft_skills);
            }
            if (aiScoring.domain_knowledge) {
                Object.assign(this.skillScores.technical, aiScoring.domain_knowledge);
            }
        } else {
            // Fallback: получаем все навыки из структурированных данных
            const allSkills = this.extractAllSkills();
            
            // Инициализируем баллы (равномерное распределение)
            this.skillScores = {
                technical: {},
                programming: {},
                tools: {}
            };
            
            const totalSkills = allSkills.technical.length + allSkills.programming.length + allSkills.tools.length;
            const pointsPerSkill = totalSkills > 0 ? Math.floor(200 / totalSkills) : 0;
            
            allSkills.technical.forEach(skill => {
                this.skillScores.technical[skill] = pointsPerSkill;
            });
            
            allSkills.programming.forEach(skill => {
                this.skillScores.programming[skill] = pointsPerSkill;
            });
            
            allSkills.tools.forEach(skill => {
                this.skillScores.tools[skill] = pointsPerSkill;
            });
        }
    }

    extractAllSkills() {
        const skills = {
            technical: [],
            programming: [],
            tools: []
        };
        
        if (this.structuredData && this.structuredData.requirements) {
            const requirements = this.structuredData.requirements;
            
            // Извлекаем технические навыки
            if (requirements['Технические навыки'] && requirements['Технические навыки'] !== 'Не указано') {
                const techSkills = requirements['Технические навыки'].split(/[,;]/).map(s => s.trim());
                skills.technical = techSkills.filter(s => s && s !== 'Не указано' && s.length > 0);
            }
            
            // Извлекаем языки программирования
            if (requirements['Языки программирования'] && requirements['Языки программирования'] !== 'Не указано') {
                const progLanguages = requirements['Языки программирования'].split(/[,;]/).map(s => s.trim());
                skills.programming = progLanguages.filter(s => s && s !== 'Не указано' && s.length > 0);
            }
            
            // Извлекаем инструменты
            if (requirements['Инструменты'] && requirements['Инструменты'] !== 'Не указано') {
                const toolsList = requirements['Инструменты'].split(/[,;]/).map(s => s.trim());
                skills.tools = toolsList.filter(s => s && s !== 'Не указано' && s.length > 0);
            }
        }
        
        // Если навыки не найдены, добавляем примеры для демонстрации
        if (skills.technical.length === 0 && skills.programming.length === 0 && skills.tools.length === 0) {
            skills.technical = ['Python', 'JavaScript', 'React', 'Node.js'];
            skills.programming = ['Python', 'JavaScript', 'Java', 'C++'];
            skills.tools = ['Git', 'Docker', 'VS Code', 'Postman'];
        }
        
        return skills;
    }

    displaySkillsScoringInterface() {
        // Отображаем технические навыки
        this.displaySkillCategory('technicalSkillsScoring', this.skillScores.technical);
        
        // Отображаем языки программирования
        this.displaySkillCategory('programmingSkillsScoring', this.skillScores.programming);
        
        // Отображаем инструменты
        this.displaySkillCategory('toolsScoring', this.skillScores.tools);
        
        // Обновляем общую сумму
        this.updateTotalScore();
    }

    displaySkillCategory(containerId, skills) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        // Панель добавления нового навыка
        const addBar = document.createElement('div');
        addBar.className = 'skill-score-item';
        addBar.innerHTML = `
            <input type="text" class="form-input" placeholder="Новый навык" id="${containerId}-newName">
            <div class="skill-score-input">
                <input type="number" value="0" min="0" max="200" id="${containerId}-newScore">
                <button class="btn-primary" onclick="app.addSkill('${containerId}')">Добавить</button>
            </div>
        `;
        container.appendChild(addBar);

        Object.entries(skills).forEach(([skillName, score]) => {
            const item = document.createElement('div');
            item.className = 'skill-score-item';
            item.innerHTML = `
                <span class="skill-name">${skillName}</span>
                <div class="skill-score-input">
                    <input type="number" value="${score}" min="0" max="200" 
                           onchange="app.updateSkillScore('${skillName}', this.value, '${containerId}')">
                    <span>баллов</span>
                    <button class="btn-secondary" onclick="app.removeSkill('${skillName}', '${containerId}')">Удалить</button>
                </div>
            `;
            container.appendChild(item);
        });
    }

    updateSkillScore(skillName, newScore, containerId) {
        const score = parseInt(newScore) || 0;
        
        // Определяем категорию по containerId
        let category = 'technical';
        if (containerId === 'programmingSkillsScoring') category = 'programming';
        else if (containerId === 'toolsScoring') category = 'tools';
        
        // Обновляем балл
        this.skillScores[category][skillName] = score;
        
        // Обновляем общую сумму
        this.updateTotalScore();
    }

    addSkill(containerId) {
        const nameInput = document.getElementById(`${containerId}-newName`);
        const scoreInput = document.getElementById(`${containerId}-newScore`);
        const skillName = (nameInput?.value || '').trim();
        const score = parseInt(scoreInput?.value || '0') || 0;
        if (!skillName) {
            this.showError('Введите название навыка');
            return;
        }
        let category = 'technical';
        if (containerId === 'programmingSkillsScoring') category = 'programming';
        else if (containerId === 'toolsScoring') category = 'tools';
        this.skillScores[category][skillName] = score;
        this.displaySkillCategory(containerId, this.skillScores[category]);
        this.updateTotalScore();
    }

    removeSkill(skillName, containerId) {
        let category = 'technical';
        if (containerId === 'programmingSkillsScoring') category = 'programming';
        else if (containerId === 'toolsScoring') category = 'tools';
        delete this.skillScores[category][skillName];
        this.displaySkillCategory(containerId, this.skillScores[category]);
        this.updateTotalScore();
    }

    updateTotalScore() {
        let total = 0;
        
        // Суммируем все баллы
        Object.values(this.skillScores.technical).forEach(score => total += score);
        Object.values(this.skillScores.programming).forEach(score => total += score);
        Object.values(this.skillScores.tools).forEach(score => total += score);
        
        // Обновляем отображение
        document.getElementById('totalScoreValue').textContent = total;
        const fillElement = document.getElementById('totalScoreFill');
        const percentage = Math.min((total / 200) * 100, 100);
        fillElement.style.width = `${percentage}%`;
        
        // Меняем цвет в зависимости от суммы
        if (total === 200) {
            fillElement.style.background = 'linear-gradient(90deg, var(--accent-success), var(--accent-primary))';
        } else if (total > 200) {
            fillElement.style.background = 'linear-gradient(90deg, var(--accent-danger), var(--accent-warning))';
        } else {
            fillElement.style.background = 'linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))';
        }
    }

    prepareSaveStep() {
        // Pre-fill form with extracted data
        const region = this.structuredData.job_info?.['Местоположение'];
        if (region && region !== 'Не указано') {
            document.getElementById('region').value = region;
        }

        // Display summary
        this.displayVacancySummary();
    }

    displayVacancySummary() {
        const summary = document.getElementById('vacancySummary');
        const jobTitle = this.structuredData.job_info?.['Название должности'] || 'Не указано';
        const company = this.structuredData.job_info?.['Компания'] || 'Не указано';
        const salary = this.getSalaryRange();
        
        summary.innerHTML = `
            <div class="summary-item">
                <strong>Должность:</strong> ${jobTitle}
            </div>
            <div class="summary-item">
                <strong>Компания:</strong> ${company}
            </div>
            <div class="summary-item">
                <strong>Зарплата:</strong> ${salary}
            </div>
            <div class="summary-item">
                <strong>Файл:</strong> ${this.selectedFile.name}
            </div>
        `;
    }

    getSalaryRange() {
        const salaryFrom = this.structuredData.salary?.['Зарплата от'];
        const salaryTo = this.structuredData.salary?.['Зарплата до'];
        
        if (salaryFrom && salaryFrom !== 'Не указано' && salaryTo && salaryTo !== 'Не указано') {
            return `${salaryFrom} - ${salaryTo}`;
        } else if (salaryFrom && salaryFrom !== 'Не указано') {
            return `от ${salaryFrom}`;
        } else if (salaryTo && salaryTo !== 'Не указано') {
            return `до ${salaryTo}`;
        }
        return 'Не указано';
    }

    async saveVacancy() {
        // Validate form
        const deadline = document.getElementById('applicationDeadline').value;
        const positionsCount = document.getElementById('positionsCount').value;
        
        if (!deadline) {
            this.showError('Пожалуйста, укажите дату окончания набора');
            return;
        }
        
        if (!positionsCount || positionsCount < 1) {
            this.showError('Пожалуйста, укажите количество позиций');
            return;
        }

        this.disableNextButton();

        try {
            const saveData = {
                file: this.selectedFile,
                extracted_data: this.extractedData,
                structured_data: this.structuredData,
                analysis_data: this.analysisData,
                skill_scores: this.skillScores, // Добавляем разбаловки
                application_deadline: deadline,
                positions_count: parseInt(positionsCount),
                region: document.getElementById('region').value
            };

            const formData = new FormData();
            formData.append('file', this.selectedFile);
            formData.append('data', JSON.stringify(saveData));

            const response = await fetch('/api/save-vacancy', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Ошибка при сохранении вакансии');
            }

            const result = await response.json();
            this.vacancyId = result.vacancy_id;
            
            // Показываем карточку созданной вакансии
            this.showCreatedVacancyCard(result);
            
        } catch (error) {
            this.showError('Ошибка при сохранении вакансии: ' + error.message);
        } finally {
            this.enableNextButton();
        }
    }


    // Existing Vacancies Methods
    async loadExistingVacancies() {
        try {
            const response = await fetch('/api/vacancies');
            if (!response.ok) {
                throw new Error('Ошибка при загрузке вакансий');
            }

            const vacancies = await response.json();
            this.displayVacancies(vacancies);
            
        } catch (error) {
            this.showError('Ошибка при загрузке вакансий: ' + error.message);
        }
    }
    
    async loadExistingTemplates() {
        try {
            const response = await fetch('/api/vacancies');
            if (!response.ok) {
                throw new Error('Ошибка при загрузке шаблонов');
            }

            const templates = await response.json();
            
            if (templates.length === 0) {
                this.displayNoTemplatesMessage();
            } else {
                this.displayTemplatesForEditing(templates);
            }
            
        } catch (error) {
            this.showError('Ошибка при загрузке шаблонов: ' + error.message);
        }
    }
    
    displayNoTemplatesMessage() {
        const container = document.getElementById('templatesList');
        if (container) {
            container.innerHTML = `
                <div class="no-templates">
                    <div class="no-templates-icon">📋</div>
                    <h3>Нет сохраненных шаблонов</h3>
                    <p>Создайте первый шаблон, чтобы начать работу</p>
                    <button class="btn btn-primary" onclick="app.startProcess()">
                        Создать новый шаблон
                    </button>
                </div>
            `;
        }
    }

    displayVacancies(vacancies) {
        const container = document.getElementById('vacanciesList');
        container.innerHTML = '';

        if (vacancies.length === 0) {
            container.innerHTML = `
                <div class="no-vacancies">
                    <i class="fas fa-inbox"></i>
                    <h3>Нет сохраненных вакансий</h3>
                    <p>Создайте первую вакансию, чтобы начать работу</p>
                </div>
            `;
            return;
        }

        vacancies.forEach(vacancy => {
            const card = document.createElement('div');
            card.className = 'vacancy-card';
            card.innerHTML = `
                <div class="vacancy-header">
                    <div class="vacancy-title">${vacancy.job_title || vacancy.name || 'Без названия'}</div>
                    <button class="btn-primary" onclick="app.viewVacancyDetails(${vacancy.id})">
                        Подробнее
                    </button>
                </div>
                <div class="vacancy-content">
                    <div class="vacancy-info-row">
                        <div class="info-item">
                            <span class="info-label">Позиций:</span>
                            <span class="info-value">${vacancy.positions_count || 1}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Регион:</span>
                            <span class="info-value">${vacancy.region || 'Не указан'}</span>
                        </div>
                    </div>
                    <div class="vacancy-dates-row">
                        <div class="date-item">
                            <span class="date-label">Создано:</span>
                            <span class="date-value">${new Date(vacancy.created_at).toLocaleDateString('ru-RU')}</span>
                        </div>
                        ${vacancy.application_deadline ? `
                            <div class="date-item">
                                <span class="date-label">До:</span>
                                <span class="date-value deadline">${new Date(vacancy.application_deadline).toLocaleDateString('ru-RU')}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    }
    
    displayTemplatesForEditing(templates) {
        const container = document.getElementById('vacanciesList');
        container.innerHTML = '';
        
        if (!templates || templates.length === 0) {
            const noTemplates = document.createElement('div');
            noTemplates.className = 'no-vacancies';
            noTemplates.innerHTML = `
                <div class="no-vacancies-content">
                    <h3>Шаблоны не найдены</h3>
                    <p>Создайте первый шаблон, чтобы начать работу</p>
                    <button class="btn-primary" onclick="app.backToWelcome()">
                        Создать новый шаблон
                    </button>
                </div>
            `;
            container.appendChild(noTemplates);
            return;
        }
        
        templates.forEach(template => {
            const card = document.createElement('div');
            card.className = 'vacancy-card template-card compact-template';
            card.innerHTML = `
                <div class="vacancy-header" onclick="app.toggleTemplateExpansion(${template.id})">
                    <div class="vacancy-title">
                        <input type="text" class="edit-input template-title" value="${template.job_title || template.name || 'Без названия'}" 
                               data-template-id="${template.id}" data-field="job_title" placeholder="Название шаблона" readonly>
                    </div>
                    <div class="template-actions">
                        <button class="btn-danger btn-sm" onclick="event.stopPropagation(); app.deleteTemplate(${template.id})">
                            🗑️ Удалить
                        </button>
                        <!-- Иконка разворачивания удалена - теперь используется полноэкранный модал -->
                    </div>
                </div>
                <div class="vacancy-content compact-content">
                    <div class="vacancy-dates-row">
                        <div class="date-item">
                            <span class="date-label">Создано:</span>
                            <span class="date-value">${new Date(template.created_at).toLocaleDateString('ru-RU')}</span>
                        </div>
                        ${template.application_deadline ? `
                            <div class="date-item">
                                <span class="date-label">До:</span>
                                <span class="date-value deadline">${new Date(template.application_deadline).toLocaleDateString('ru-RU')}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Развернутый контент теперь показывается в полноэкранном модале -->
            `;
            container.appendChild(card);
        });
    }

    async viewVacancyDetails(vacancyId) {
        try {
            // Загружаем детальную информацию о вакансии
            const response = await fetch(`/api/vacancy/${vacancyId}`);
            if (!response.ok) {
                throw new Error('Ошибка при загрузке деталей вакансии');
            }
            
            const vacancy = await response.json();
            
            // Создаем модальное окно с подробной информацией
            this.showVacancyDetailsModal(vacancy);
            
        } catch (error) {
            this.showError('Ошибка при загрузке деталей вакансии: ' + error.message);
        }
    }
    
    showVacancyDetailsModal(vacancy) {
        // Создаем модальное окно с карточкой вакансии (только для просмотра)
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 900px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h3>📋 Детали вакансии</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">[X]</button>
                </div>
                <div class="modal-body">
                    <div class="success-vacancy-card">
                        <div class="vacancy-header">
                            <div class="vacancy-title">${vacancy.job_title || 'Без названия'}</div>
                            <div class="vacancy-id">ID: ${vacancy.id}</div>
                        </div>
                        <div class="vacancy-content">
                            <div class="vacancy-info-row">
                                <div class="info-item">
                                    <span class="info-label">Позиций:</span>
                                    <span class="info-value">${vacancy.positions_count || 1}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Регион:</span>
                                    <span class="info-value">${vacancy.region || 'Не указан'}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Срок подачи:</span>
                                    <span class="info-value">${vacancy.application_deadline ? new Date(vacancy.application_deadline).toLocaleDateString('ru-RU') : 'Не указан'}</span>
                                </div>
                            </div>
                            
                            <div class="vacancy-dates-row">
                                <div class="date-item">
                                    <span class="date-label">Создано:</span>
                                    <span class="date-value">${new Date(vacancy.created_at).toLocaleDateString('ru-RU')}</span>
                                </div>
                                ${vacancy.updated_at ? `
                                    <div class="date-item">
                                        <span class="date-label">Обновлено:</span>
                                        <span class="date-value">${new Date(vacancy.updated_at).toLocaleDateString('ru-RU')}</span>
                                    </div>
                                ` : ''}
                            </div>
                            
                            ${vacancy.structured_data ? `
                                <div class="detail-section">
                                    <h4>Структурированные данные</h4>
                                    <div class="structured-data-preview">
                                        ${this.formatStructuredDataForModal(vacancy.structured_data)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${vacancy.skill_scores ? `
                                <div class="detail-section">
                                    <h4>Распределение баллов по навыкам</h4>
                                    <div class="skills-scoring-preview">
                                        ${this.formatSkillScoresForModal(vacancy.skill_scores)}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Закрыть</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    formatStructuredDataForModal(data) {
        let html = '';
        
        if (data.job_info) {
            html += '<div class="data-section"><h5>Информация о вакансии</h5>';
            Object.entries(data.job_info).forEach(([key, value]) => {
                if (value && value !== 'Не указано') {
                    html += `<div class="data-item"><strong>${key}:</strong> ${value}</div>`;
                }
            });
            html += '</div>';
        }
        
        if (data.salary) {
            html += '<div class="data-section"><h5>Зарплата</h5>';
            Object.entries(data.salary).forEach(([key, value]) => {
                if (value && value !== 'Не указано') {
                    html += `<div class="data-item"><strong>${key}:</strong> ${value}</div>`;
                }
            });
            html += '</div>';
        }
        
        if (data.requirements) {
            html += '<div class="data-section"><h5>Требования</h5>';
            Object.entries(data.requirements).forEach(([key, value]) => {
                if (value && value !== 'Не указано') {
                    html += `<div class="data-item"><strong>${key}:</strong> ${value}</div>`;
                }
            });
            html += '</div>';
        }
        
        return html || '<p>Структурированные данные недоступны</p>';
    }
    
    formatSkillScoresForModal(skillScores) {
        let html = '';
        let totalScore = 0;
        
        if (skillScores.technical && Object.keys(skillScores.technical).length > 0) {
            html += '<div class="skills-category"><h5>Технические навыки</h5>';
            Object.entries(skillScores.technical).forEach(([skill, score]) => {
                html += `<div class="skill-item"><span class="skill-name">${skill}:</span> <span class="skill-score">${score} баллов</span></div>`;
                totalScore += parseInt(score) || 0;
            });
            html += '</div>';
        }
        
        if (skillScores.programming && Object.keys(skillScores.programming).length > 0) {
            html += '<div class="skills-category"><h5>Языки программирования</h5>';
            Object.entries(skillScores.programming).forEach(([skill, score]) => {
                html += `<div class="skill-item"><span class="skill-name">${skill}:</span> <span class="skill-score">${score} баллов</span></div>`;
                totalScore += parseInt(score) || 0;
            });
            html += '</div>';
        }
        
        if (skillScores.tools && Object.keys(skillScores.tools).length > 0) {
            html += '<div class="skills-category"><h5>Инструменты</h5>';
            Object.entries(skillScores.tools).forEach(([skill, score]) => {
                html += `<div class="skill-item"><span class="skill-name">${skill}:</span> <span class="skill-score">${score} баллов</span></div>`;
                totalScore += parseInt(score) || 0;
            });
            html += '</div>';
        }
        
        if (totalScore > 0) {
            html += `<div class="total-score-summary"><strong>Общая сумма: ${totalScore}/200 баллов</strong></div>`;
        }
        
        return html || '<p>Разбаловки недоступны</p>';
    }
    
    formatStructuredDataForEdit(data, templateId) {
        let html = '';
        
        if (data.job_info) {
            html += '<div class="data-section"><h5>Информация о вакансии</h5>';
            Object.entries(data.job_info).forEach(([key, value]) => {
                html += `<div class="data-item">
                    <strong>${key}:</strong> 
                    <input type="text" class="edit-input edit-field" value="${value || ''}" 
                           data-template-id="${templateId}" data-section="job_info" data-field="${key}" placeholder="Введите значение">
                </div>`;
            });
            html += '</div>';
        }
        
        if (data.salary) {
            html += '<div class="data-section"><h5>Зарплата</h5>';
            Object.entries(data.salary).forEach(([key, value]) => {
                html += `<div class="data-item">
                    <strong>${key}:</strong> 
                    <input type="text" class="edit-input edit-field" value="${value || ''}" 
                           data-template-id="${templateId}" data-section="salary" data-field="${key}" placeholder="Введите значение">
                </div>`;
            });
            html += '</div>';
        }
        
        if (data.requirements) {
            html += '<div class="data-section"><h5>Требования</h5>';
            Object.entries(data.requirements).forEach(([key, value]) => {
                html += `<div class="data-item">
                    <strong>${key}:</strong> 
                    <input type="text" class="edit-input edit-field" value="${value || ''}" 
                           data-template-id="${templateId}" data-section="requirements" data-field="${key}" placeholder="Введите значение">
                </div>`;
            });
            html += '</div>';
        }
        
        if (data.responsibilities) {
            html += '<div class="data-section"><h5>Обязанности</h5>';
            if (Array.isArray(data.responsibilities)) {
                data.responsibilities.forEach((item, index) => {
                    html += `<div class="data-item">
                        <input type="text" class="edit-input edit-list-item" value="${item || ''}" 
                               data-template-id="${templateId}" data-section="responsibilities" data-index="${index}" placeholder="Обязанность">
                        <button class="btn-danger btn-sm" onclick="app.removeListItem('responsibilities', ${index}, this)">×</button>
                    </div>`;
                });
            }
            html += '<button class="btn-secondary btn-sm" onclick="app.addListItem(\'responsibilities\', this)">+ Добавить обязанность</button>';
            html += '</div>';
        }
        
        if (data.benefits) {
            html += '<div class="data-section"><h5>Преимущества</h5>';
            if (Array.isArray(data.benefits)) {
                data.benefits.forEach((item, index) => {
                    html += `<div class="data-item">
                        <input type="text" class="edit-input edit-list-item" value="${item || ''}" 
                               data-template-id="${templateId}" data-section="benefits" data-index="${index}" placeholder="Преимущество">
                        <button class="btn-danger btn-sm" onclick="app.removeListItem('benefits', ${index}, this)">×</button>
                    </div>`;
                });
            }
            html += '<button class="btn-secondary btn-sm" onclick="app.addListItem(\'benefits\', this)">+ Добавить преимущество</button>';
            html += '</div>';
        }
        
        return html || '<p>Структурированные данные недоступны</p>';
    }
    
    formatSkillScoresForEdit(skillScores, templateId) {
        let html = '';
        let totalScore = 0;
        
        if (skillScores.technical && Object.keys(skillScores.technical).length > 0) {
            html += '<div class="skills-category"><h5>Технические навыки</h5>';
            Object.entries(skillScores.technical).forEach(([skill, score]) => {
                html += `<div class="skill-item">
                    <span class="skill-name">${skill}:</span> 
                    <input type="number" class="edit-input edit-skill-score" value="${score}" 
                           data-template-id="${templateId}" data-category="technical" data-skill="${skill}" min="0" max="200">
                    <span class="skill-unit">баллов</span>
                </div>`;
                totalScore += parseInt(score) || 0;
            });
            html += '</div>';
        }
        
        if (skillScores.programming && Object.keys(skillScores.programming).length > 0) {
            html += '<div class="skills-category"><h5>Языки программирования</h5>';
            Object.entries(skillScores.programming).forEach(([skill, score]) => {
                html += `<div class="skill-item">
                    <span class="skill-name">${skill}:</span> 
                    <input type="number" class="edit-input edit-skill-score" value="${score}" 
                           data-template-id="${templateId}" data-category="programming" data-skill="${skill}" min="0" max="200">
                    <span class="skill-unit">баллов</span>
                </div>`;
                totalScore += parseInt(score) || 0;
            });
            html += '</div>';
        }
        
        if (skillScores.tools && Object.keys(skillScores.tools).length > 0) {
            html += '<div class="skills-category"><h5>Инструменты</h5>';
            Object.entries(skillScores.tools).forEach(([skill, score]) => {
                html += `<div class="skill-item">
                    <span class="skill-name">${skill}:</span> 
                    <input type="number" class="edit-input edit-skill-score" value="${score}" 
                           data-template-id="${templateId}" data-category="tools" data-skill="${skill}" min="0" max="200">
                    <span class="skill-unit">баллов</span>
                </div>`;
                totalScore += parseInt(score) || 0;
            });
            html += '</div>';
        }
        
        if (totalScore > 0) {
            html += `<div class="total-score-summary"><strong>Общая сумма: <span id="totalScoreDisplay">${totalScore}</span>/200 баллов</strong></div>`;
        }
        
        return html || '<p>Разбаловки недоступны</p>';
    }
    
    async editTemplate(templateId) {
        try {
            // Загружаем данные шаблона
            const response = await fetch(`/api/vacancy/${templateId}`);
            if (!response.ok) {
                throw new Error('Ошибка при загрузке шаблона');
            }
            
            const template = await response.json();
            
            // Загружаем данные в форму для редактирования
            this.loadTemplateForEditing(template);
            
            // Переходим сразу к редактированию структурированных данных
            this.showEditMode(template);
            
        } catch (error) {
            this.showError('Ошибка при загрузке шаблона: ' + error.message);
        }
    }
    
    async deleteTemplate(templateId) {
        if (!confirm('Вы уверены, что хотите удалить этот шаблон? Это действие нельзя отменить.')) {
            return;
        }
        
        try {
            this.showLoading('Удаляем шаблон...');
            
            const response = await fetch(`/api/vacancy/${templateId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                
                // Если шаблон не найден, просто обновляем список
                if (response.status === 404) {
                    this.hideLoading();
                    alert('Шаблон уже был удален');
                    this.loadExistingTemplates();
                    return;
                }
                
                throw new Error(errorData.error || 'Ошибка при удалении шаблона');
            }
            
            this.hideLoading();
            
            // Показываем уведомление об успехе
            alert('Шаблон успешно удален!');
            
            // Обновляем список шаблонов
            this.loadExistingTemplates();
            
        } catch (error) {
            this.hideLoading();
            this.showError('Ошибка при удалении шаблона: ' + error.message);
        }
    }
    
    loadTemplateForEditing(template) {
        // Загружаем данные шаблона в форму
        if (template.structured_data) {
            this.structuredData = template.structured_data;
        }
        
        if (template.skill_scores) {
            this.skillScores = template.skill_scores;
        }
        
        // Сохраняем ID шаблона для обновления
        this.editingTemplateId = template.id;
        
        // Можно добавить загрузку других полей по необходимости
        console.log('Шаблон загружен для редактирования:', template);
    }
    
    showEditMode(template) {
        // Скрываем welcome screen и показываем модальное окно редактирования
        document.getElementById('welcomeScreen').style.display = 'none';
        document.getElementById('existingVacancies').style.display = 'none';
        
        // Создаем модальное окно редактирования
        this.showEditModal(template);
    }
    
    showEditModal(template) {
        // Создаем модальное окно с карточкой для редактирования
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 1000px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h3>✏️ Редактирование шаблона</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove(); app.viewExistingTemplates();">[X]</button>
                </div>
                <div class="modal-body">
                    <div class="edit-vacancy-card">
                        <div class="vacancy-header">
                            <div class="vacancy-title">
                                <input type="text" class="edit-input" value="${template.job_title || 'Без названия'}" 
                                       data-field="job_title" placeholder="Название вакансии">
                            </div>
                            <div class="vacancy-id">ID: ${template.id}</div>
                        </div>
                        <div class="vacancy-content">
                            <div class="vacancy-info-row">
                                <div class="info-item">
                                    <span class="info-label">Позиций:</span>
                                    <input type="number" class="edit-input edit-number" value="${template.positions_count || 1}" 
                                           data-field="positions_count" min="1">
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Регион:</span>
                                    <input type="text" class="edit-input" value="${template.region || ''}" 
                                           data-field="region" placeholder="Регион">
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Дата создания:</span>
                                    <span class="info-value">${new Date(template.created_at).toLocaleDateString('ru-RU')}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">До:</span>
                                    <input type="date" class="edit-input edit-date" value="${template.application_deadline ? new Date(template.application_deadline).toISOString().split('T')[0] : ''}" 
                                           data-field="application_deadline">
                                </div>
                            </div>
                        </div>
                        
                        ${template.structured_data ? `
                            <div class="detail-section">
                                <h4>Структурированные данные</h4>
                                <div class="structured-data-edit">
                                    ${this.formatStructuredDataForEdit(template.structured_data)}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${template.skill_scores ? `
                            <div class="detail-section">
                                <h4>Распределение баллов по навыкам</h4>
                                <div class="skills-scoring-edit">
                                    ${this.formatSkillScoresForEdit(template.skill_scores)}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="this.closest('.modal').remove(); app.viewExistingTemplates();">
                        Отмена
                    </button>
                    <button class="btn-primary" onclick="app.saveTemplateChangesFromModal(${template.id}, this.closest('.modal'));">
                        Сохранить изменения
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    async saveTemplateChanges() {
        try {
            this.showLoading('Сохраняем изменения...');
            
            const response = await fetch(`/api/vacancy/${this.editingTemplateId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    structured_data: this.structuredData,
                    skill_scores: this.skillScores
                })
            });
            
            if (!response.ok) {
                throw new Error('Ошибка при сохранении изменений');
            }
            
            this.hideLoading();
            alert('Изменения успешно сохранены!');
            
            // Возвращаемся к списку шаблонов
            this.viewExistingTemplates();
            
        } catch (error) {
            this.hideLoading();
            this.showError('Ошибка при сохранении изменений: ' + error.message);
        }
    }
    
    cancelEdit() {
        // Возвращаемся к списку шаблонов
        this.viewExistingTemplates();
    }
    
    async saveTemplateChangesFromModal(templateId, modal) {
        try {
            // Собираем данные из формы
            const updatedData = this.collectEditData(modal);
            
            this.showLoading('Сохраняем изменения...');
            
            const response = await fetch(`/api/vacancy/${templateId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedData)
            });
            
            if (!response.ok) {
                throw new Error('Ошибка при сохранении изменений');
            }
            
            this.hideLoading();
            alert('Изменения успешно сохранены!');
            
            // Закрываем модальное окно и возвращаемся к списку
            modal.remove();
            this.viewExistingTemplates();
            
        } catch (error) {
            this.hideLoading();
            this.showError('Ошибка при сохранении изменений: ' + error.message);
        }
    }
    
    collectEditData(modal) {
        const data = {
            job_title: modal.querySelector('[data-field="job_title"]')?.value || '',
            positions_count: parseInt(modal.querySelector('[data-field="positions_count"]')?.value) || 1,
            region: modal.querySelector('[data-field="region"]')?.value || '',
            application_deadline: modal.querySelector('[data-field="application_deadline"]')?.value || null,
            structured_data: {},
            skill_scores: {}
        };
        
        // Собираем структурированные данные
        const fieldInputs = modal.querySelectorAll('.edit-field');
        fieldInputs.forEach(input => {
            const section = input.dataset.section;
            const field = input.dataset.field;
            
            if (!data.structured_data[section]) {
                data.structured_data[section] = {};
            }
            data.structured_data[section][field] = input.value;
        });
        
        // Собираем данные списков (обязанности, преимущества)
        const listInputs = modal.querySelectorAll('.edit-list-item');
        const lists = {};
        listInputs.forEach(input => {
            const section = input.dataset.section;
            const index = parseInt(input.dataset.index);
            
            if (!lists[section]) {
                lists[section] = [];
            }
            lists[section][index] = input.value;
        });
        
        // Добавляем списки в structured_data
        Object.keys(lists).forEach(section => {
            data.structured_data[section] = lists[section].filter(item => item.trim() !== '');
        });
        
        // Собираем баллы навыков
        const skillInputs = modal.querySelectorAll('.edit-skill-score');
        skillInputs.forEach(input => {
            const category = input.dataset.category;
            const skill = input.dataset.skill;
            const score = parseInt(input.value) || 0;
            
            if (!data.skill_scores[category]) {
                data.skill_scores[category] = {};
            }
            data.skill_scores[category][skill] = score;
        });
        
        return data;
    }
    
    addListItem(section, button) {
        const sectionDiv = button.closest('.data-section');
        const newItem = document.createElement('div');
        newItem.className = 'data-item';
        
        const maxIndex = sectionDiv.querySelectorAll('.edit-list-item').length;
        
        newItem.innerHTML = `
            <input type="text" class="edit-input edit-list-item" value="" 
                   data-section="${section}" data-index="${maxIndex}" placeholder="${section === 'responsibilities' ? 'Обязанность' : section === 'benefits' ? 'Преимущество' : 'Элемент списка'}">
            <button class="btn-danger btn-sm" onclick="app.removeListItem('${section}', ${maxIndex}, this)">×</button>
        `;
        
        button.parentNode.insertBefore(newItem, button);
    }
    
    removeListItem(section, index, button) {
        button.parentNode.remove();
        
        // Обновляем индексы оставшихся элементов
        const sectionDiv = button.closest('.data-section');
        const remainingItems = sectionDiv.querySelectorAll('.edit-list-item');
        remainingItems.forEach((input, newIndex) => {
            input.dataset.index = newIndex;
            const removeBtn = input.closest('.data-item').querySelector('.btn-danger');
            if (removeBtn) {
                removeBtn.setAttribute('onclick', `app.removeListItem('${section}', ${newIndex}, this)`);
            }
        });
    }
    
    async saveTemplateFromCard(templateId) {
        try {
            // Находим карточку шаблона
            const templateCard = document.querySelector(`[data-template-id="${templateId}"]`).closest('.editable-template');
            if (!templateCard) {
                throw new Error('Карточка шаблона не найдена');
            }
            
            // Собираем данные из карточки
            const updatedData = this.collectEditDataFromCard(templateCard, templateId);
            
            this.showLoading('Сохраняем изменения...');
            
            const response = await fetch(`/api/vacancy/${templateId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedData)
            });
            
            if (!response.ok) {
                throw new Error('Ошибка при сохранении изменений');
            }
            
            this.hideLoading();
            alert('Изменения успешно сохранены!');
            
        } catch (error) {
            this.hideLoading();
            this.showError('Ошибка при сохранении изменений: ' + error.message);
        }
    }
    
    collectEditDataFromCard(templateCard, templateId) {
        const data = {
            job_title: templateCard.querySelector(`[data-template-id="${templateId}"][data-field="job_title"]`)?.value || '',
            positions_count: parseInt(templateCard.querySelector(`[data-template-id="${templateId}"][data-field="positions_count"]`)?.value) || 1,
            region: templateCard.querySelector(`[data-template-id="${templateId}"][data-field="region"]`)?.value || '',
            application_deadline: templateCard.querySelector(`[data-template-id="${templateId}"][data-field="application_deadline"]`)?.value || null,
            structured_data: {},
            skill_scores: {}
        };
        
        // Собираем структурированные данные
        const fieldInputs = templateCard.querySelectorAll(`[data-template-id="${templateId}"].edit-field`);
        fieldInputs.forEach(input => {
            const section = input.dataset.section;
            const field = input.dataset.field;
            
            if (!data.structured_data[section]) {
                data.structured_data[section] = {};
            }
            data.structured_data[section][field] = input.value;
        });
        
        // Собираем данные списков (обязанности, преимущества)
        const listInputs = templateCard.querySelectorAll(`[data-template-id="${templateId}"].edit-list-item`);
        const lists = {};
        listInputs.forEach(input => {
            const section = input.dataset.section;
            const index = parseInt(input.dataset.index);
            
            if (!lists[section]) {
                lists[section] = [];
            }
            lists[section][index] = input.value;
        });
        
        // Добавляем списки в structured_data
        Object.keys(lists).forEach(section => {
            data.structured_data[section] = lists[section].filter(item => item.trim() !== '');
        });
        
        // Собираем баллы навыков
        const skillInputs = templateCard.querySelectorAll(`[data-template-id="${templateId}"].edit-skill-score`);
        skillInputs.forEach(input => {
            const category = input.dataset.category;
            const skill = input.dataset.skill;
            const score = parseInt(input.value) || 0;
            
            if (!data.skill_scores[category]) {
                data.skill_scores[category] = {};
            }
            data.skill_scores[category][skill] = score;
        });
        
        return data;
    }
    
    toggleTemplateExpansion(templateId) {
        // Загружаем полные данные шаблона и показываем карточку как при создании
        this.loadTemplateForCard(templateId);
    }
    
    async loadTemplateForCard(templateId) {
        try {
            this.showLoading('Загружаем шаблон...');
            
            const response = await fetch(`/api/vacancy/${templateId}`);
            if (!response.ok) {
                throw new Error('Ошибка при загрузке шаблона');
            }
            
            const template = await response.json();
            this.hideLoading();
            
            // Показываем шаблон в том же формате, что и после создания
            this.showTemplateCard(template);
            
        } catch (error) {
            this.hideLoading();
            this.showError('Ошибка при загрузке шаблона: ' + error.message);
        }
    }
    
    showTemplateCard(template) {
        // Создаем модальное окно с редактируемой карточкой шаблона
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 1000px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h3>📋 Редактирование шаблона</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove();">[X]</button>
                </div>
                <div class="modal-body">
                    <div class="edit-vacancy-card">
                        <div class="vacancy-header">
                            <div class="vacancy-title">
                                <input type="text" class="edit-input" value="${template.job_title || 'Без названия'}" 
                                       data-field="job_title" data-template-id="${template.id}" placeholder="Название вакансии">
                            </div>
                            <div class="vacancy-id">ID: ${template.id}</div>
                        </div>
                        <div class="vacancy-content">
                            <div class="vacancy-info-row">
                                <div class="info-item">
                                    <span class="info-label">Позиций:</span>
                                    <input type="number" class="edit-input edit-number" value="${template.positions_count || 1}" 
                                           data-field="positions_count" data-template-id="${template.id}" min="1">
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Регион:</span>
                                    <input type="text" class="edit-input" value="${template.region || ''}" 
                                           data-field="region" data-template-id="${template.id}" placeholder="Регион">
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Срок подачи:</span>
                                    <input type="date" class="edit-input edit-date" value="${template.application_deadline ? new Date(template.application_deadline).toISOString().split('T')[0] : ''}" 
                                           data-field="application_deadline" data-template-id="${template.id}">
                                </div>
                            </div>
                            
                            ${template.structured_data ? `
                                <div class="detail-section">
                                    <h4>Структурированные данные</h4>
                                    <div class="structured-data-edit">
                                        ${this.formatStructuredDataForEdit(template.structured_data, template.id)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${template.skill_scores ? `
                                <div class="detail-section">
                                    <h4>Распределение баллов по навыкам</h4>
                                    <div class="skills-scoring-edit">
                                        ${this.formatSkillScoresForEdit(template.skill_scores, template.id)}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove();">Отмена</button>
                    <button class="btn btn-primary" onclick="app.saveTemplateFromCard(${template.id}, this.closest('.modal'));">Сохранить изменения</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    editTemplateFromCard(templateId) {
        // Загружаем шаблон для редактирования в полноэкранном модале
        this.loadTemplateForFullscreen(templateId);
    }
    
    async saveTemplateFromCard(templateId, modal) {
        try {
            this.showLoading('Сохраняем изменения...');
            
            const data = this.collectEditData(modal);
            
            const response = await fetch(`/api/vacancy/${templateId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Ошибка при сохранении');
            }
            
            this.hideLoading();
            modal.remove();
            alert('Шаблон успешно сохранен!');
            
            // Обновляем список шаблонов
            this.loadExistingTemplates();
            
        } catch (error) {
            this.hideLoading();
            this.showError('Ошибка при сохранении: ' + error.message);
        }
    }
    
    collectEditData(modal) {
        const data = {
            structured_data: {},
            skill_scores: {}
        };
        
        // Собираем основные поля
        const mainFields = ['job_title', 'positions_count', 'region', 'application_deadline'];
        mainFields.forEach(field => {
            const input = modal.querySelector(`[data-field="${field}"]`);
            if (input) {
                data[field] = field === 'positions_count' ? parseInt(input.value) : input.value;
            }
        });
        
        // Собираем структурированные данные (используем data-section)
        const structuredInputs = modal.querySelectorAll('[data-section]:not([data-skill])');
        structuredInputs.forEach(input => {
            const sectionName = input.dataset.section;
            const field = input.dataset.field;
            const index = input.dataset.index;
            
            if (!data.structured_data[sectionName]) {
                data.structured_data[sectionName] = {};
            }
            
            if (index !== undefined) {
                // Это элемент списка
                if (!Array.isArray(data.structured_data[sectionName])) {
                    data.structured_data[sectionName] = [];
                }
                data.structured_data[sectionName][parseInt(index)] = input.value;
            } else if (field) {
                // Это поле объекта
                data.structured_data[sectionName][field] = input.value;
            } else {
                // Это простое значение
                data.structured_data[sectionName] = input.value;
            }
        });
        
        // Собираем баллы навыков
        const skillInputs = modal.querySelectorAll('[data-skill]');
        skillInputs.forEach(input => {
            const skill = input.dataset.skill;
            data.skill_scores[skill] = parseInt(input.value) || 0;
        });
        
        return data;
    }
    
    async loadTemplateForFullscreen(templateId) {
        try {
            this.showLoading('Загружаем шаблон...');
            
            const response = await fetch(`/api/vacancy/${templateId}`);
            if (!response.ok) {
                throw new Error('Ошибка при загрузке шаблона');
            }
            
            const template = await response.json();
            this.hideLoading();
            
            // Показываем шаблон в полноэкранном модале
            this.showFullscreenTemplateModal(template);
            
        } catch (error) {
            this.hideLoading();
            this.showError('Ошибка при загрузке шаблона: ' + error.message);
        }
    }
    
    showFullscreenTemplateModal(template) {
        // Создаем полноэкранный модал
        const modal = document.createElement('div');
        modal.className = 'fullscreen-modal';
        modal.innerHTML = `
            <div class="fullscreen-modal-content">
                <div class="fullscreen-modal-header">
                    <h2>Редактирование шаблона</h2>
                    <button class="close-fullscreen-btn" onclick="app.closeFullscreenModal()">✕</button>
                </div>
                <div class="fullscreen-modal-body">
                    ${this.formatTemplateForFullscreen(template)}
                </div>
                <div class="fullscreen-modal-footer">
                    <button class="btn btn-secondary" onclick="app.closeFullscreenModal()">Отмена</button>
                    <button class="btn btn-primary" onclick="app.saveFullscreenTemplate(${template.id})">Сохранить</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Блокируем скролл страницы
        document.body.style.overflow = 'hidden';
    }
    
    formatTemplateForFullscreen(template) {
        const structuredData = template.structured_data || {};
        const skillScores = template.skill_scores || {};
        
        return `
            <div class="fullscreen-template-card">
                <div class="template-header">
                    <div class="template-title-section">
                        <label>Название вакансии:</label>
                        <input type="text" class="fullscreen-input" value="${template.job_title || ''}" 
                               data-field="job_title" data-template-id="${template.id}">
                    </div>
                </div>
                
                <div class="template-info-grid">
                    <div class="info-section">
                        <label>Количество позиций:</label>
                        <input type="number" class="fullscreen-input" value="${template.positions_count || 1}" 
                               data-field="positions_count" data-template-id="${template.id}" min="1">
                    </div>
                    <div class="info-section">
                        <label>Регион:</label>
                        <input type="text" class="fullscreen-input" value="${template.region || ''}" 
                               data-field="region" data-template-id="${template.id}">
                    </div>
                    <div class="info-section">
                        <label>Срок подачи заявок:</label>
                        <input type="date" class="fullscreen-input" value="${template.application_deadline || ''}" 
                               data-field="application_deadline" data-template-id="${template.id}">
                    </div>
                </div>
                
                <div class="structured-data-section">
                    <h3>Структурированные данные</h3>
                    <div class="structured-data-grid">
                        ${this.formatStructuredDataForFullscreen(structuredData, template.id)}
                    </div>
                </div>
                
                <div class="skills-section">
                    <h3>Баллы по навыкам</h3>
                    <div class="skills-grid">
                        ${this.formatSkillScoresForFullscreen(skillScores, template.id)}
                    </div>
                </div>
            </div>
        `;
    }
    
    formatStructuredDataForFullscreen(data, templateId) {
        let html = '';
        
        for (const [blockName, blockData] of Object.entries(data)) {
            html += `
                <div class="data-block">
                    <h4>${blockName}</h4>
                    <div class="data-fields">
                        ${this.formatBlockDataForFullscreen(blockData, blockName, templateId)}
                    </div>
                </div>
            `;
        }
        
        return html;
    }
    
    formatBlockDataForFullscreen(blockData, blockName, templateId) {
        let html = '';
        
        if (Array.isArray(blockData)) {
            // Список
            blockData.forEach((item, index) => {
                html += `
                    <div class="list-item">
                        <input type="text" class="fullscreen-input" value="${item}" 
                               data-block="${blockName}" data-index="${index}" data-template-id="${templateId}">
                        <button class="remove-item-btn" onclick="app.removeFullscreenListItem('${blockName}', ${index}, ${templateId})">✕</button>
                    </div>
                `;
            });
            html += `
                <button class="add-item-btn" onclick="app.addFullscreenListItem('${blockName}', ${templateId})">
                    + Добавить элемент
                </button>
            `;
        } else if (typeof blockData === 'object' && blockData !== null) {
            // Объект
            for (const [key, value] of Object.entries(blockData)) {
                html += `
                    <div class="field-item">
                        <label>${key}:</label>
                        <input type="text" class="fullscreen-input" value="${value}" 
                               data-block="${blockName}" data-field="${key}" data-template-id="${templateId}">
                    </div>
                `;
            }
        } else {
            // Простое значение
            html += `
                <div class="field-item">
                    <input type="text" class="fullscreen-input" value="${blockData}" 
                           data-block="${blockName}" data-template-id="${templateId}">
                </div>
            `;
        }
        
        return html;
    }
    
    formatSkillScoresForFullscreen(skillScores, templateId) {
        let html = '';
        
        if (!skillScores || Object.keys(skillScores).length === 0) {
            html = '<p>Нет данных о навыках</p>';
        } else {
            for (const [skill, score] of Object.entries(skillScores)) {
                html += `
                    <div class="skill-item">
                        <label>${skill}:</label>
                        <input type="number" class="fullscreen-input skill-score" value="${score}" 
                               data-skill="${skill}" data-template-id="${templateId}" min="0" max="200">
                    </div>
                `;
            }
        }
        
        return html;
    }
    
    closeFullscreenModal() {
        const modal = document.querySelector('.fullscreen-modal');
        if (modal) {
            modal.remove();
        }
        
        // Разблокируем скролл страницы
        document.body.style.overflow = '';
    }
    
    async saveFullscreenTemplate(templateId) {
        try {
            this.showLoading('Сохраняем изменения...');
            
            const modal = document.querySelector('.fullscreen-modal');
            const data = this.collectFullscreenData(modal, templateId);
            
            const response = await fetch(`/api/vacancy/${templateId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Ошибка при сохранении');
            }
            
            this.hideLoading();
            this.closeFullscreenModal();
            alert('Шаблон успешно сохранен!');
            
            // Обновляем список шаблонов
            this.loadExistingTemplates();
            
        } catch (error) {
            this.hideLoading();
            this.showError('Ошибка при сохранении: ' + error.message);
        }
    }
    
    collectFullscreenData(modal, templateId) {
        const data = {
            structured_data: {},
            skill_scores: {}
        };
        
        // Собираем основные поля
        const mainFields = ['job_title', 'positions_count', 'region', 'application_deadline'];
        mainFields.forEach(field => {
            const input = modal.querySelector(`[data-field="${field}"][data-template-id="${templateId}"]`);
            if (input) {
                data[field] = field === 'positions_count' ? parseInt(input.value) : input.value;
            }
        });
        
        // Собираем структурированные данные
        const structuredInputs = modal.querySelectorAll(`[data-block][data-template-id="${templateId}"]:not([data-skill])`);
        structuredInputs.forEach(input => {
            const blockName = input.dataset.block;
            const field = input.dataset.field;
            const index = input.dataset.index;
            
            if (!data.structured_data[blockName]) {
                data.structured_data[blockName] = {};
            }
            
            if (index !== undefined) {
                // Это элемент списка
                if (!Array.isArray(data.structured_data[blockName])) {
                    data.structured_data[blockName] = [];
                }
                data.structured_data[blockName][parseInt(index)] = input.value;
            } else if (field) {
                // Это поле объекта
                data.structured_data[blockName][field] = input.value;
            } else {
                // Это простое значение
                data.structured_data[blockName] = input.value;
            }
        });
        
        // Собираем баллы навыков
        const skillInputs = modal.querySelectorAll(`[data-skill][data-template-id="${templateId}"]`);
        skillInputs.forEach(input => {
            const skill = input.dataset.skill;
            const score = parseInt(input.value) || 0;
            data.skill_scores[skill] = score;
        });
        return data;
    }
    
    addFullscreenListItem(blockName, templateId) {
        const modal = document.querySelector('.fullscreen-modal');
        const blockElement = modal.querySelector(`[data-block="${blockName}"][data-template-id="${templateId}"]`);
        
        if (blockElement) {
            const listContainer = blockElement.closest('.data-fields');
            const newIndex = listContainer.querySelectorAll('.list-item').length;
            
            const newItem = document.createElement('div');
            newItem.className = 'list-item';
            newItem.innerHTML = `
                <input type="text" class="fullscreen-input" value="" 
                       data-block="${blockName}" data-index="${newIndex}" data-template-id="${templateId}">
                <button class="remove-item-btn" onclick="app.removeFullscreenListItem('${blockName}', ${newIndex}, ${templateId})">✕</button>
            `;
            
            const addButton = listContainer.querySelector('.add-item-btn');
            listContainer.insertBefore(newItem, addButton);
        }
    }
    
    removeFullscreenListItem(blockName, index, templateId) {
        const modal = document.querySelector('.fullscreen-modal');
        const item = modal.querySelector(`[data-block="${blockName}"][data-index="${index}"][data-template-id="${templateId}"]`);
        
        if (item) {
            item.closest('.list-item').remove();
            
            // Обновляем индексы оставшихся элементов
            const remainingItems = modal.querySelectorAll(`[data-block="${blockName}"][data-template-id="${templateId}"]`);
            remainingItems.forEach((input, newIndex) => {
                input.dataset.index = newIndex;
                const removeBtn = input.closest('.list-item').querySelector('.remove-item-btn');
                if (removeBtn) {
                    removeBtn.setAttribute('onclick', `app.removeFullscreenListItem('${blockName}', ${newIndex}, ${templateId})`);
                }
            });
        }
    }
    
    uploadResumes() {
        // Сначала загружаем список вакансий для выбора
        this.loadVacanciesForResumeUpload();
    }
    
    async loadVacanciesForResumeUpload() {
        try {
            const response = await fetch('/api/vacancies');
            const vacancies = await response.json();
            
            if (vacancies.length === 0) {
                this.showError('Нет доступных вакансий. Сначала создайте шаблон вакансии.');
                return;
            }
            
            this.showVacancySelectionModal(vacancies);
        } catch (error) {
            this.showError('Ошибка при загрузке вакансий: ' + error.message);
        }
    }
    
    showVacancySelectionModal(vacancies) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 900px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h3>📄 Загрузка резюме кандидатов</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">[X]</button>
                </div>
                <div class="modal-body">
                    <div class="vacancy-selection-section">
                        <h4>Выберите вакансию для сопоставления резюме:</h4>
                        <div class="vacancy-selection-list">
                            ${vacancies.map(vacancy => `
                                <div class="vacancy-selection-item" onclick="app.selectVacancyForResumes(${vacancy.id}, '${vacancy.job_title || 'Без названия'}')">
                                    <div class="vacancy-selection-info">
                                        <div class="vacancy-selection-title">${vacancy.job_title || 'Без названия'}</div>
                                        <div class="vacancy-selection-details">
                                            <span>Позиций: ${vacancy.positions_count || 1}</span>
                                            <span>Регион: ${vacancy.region || 'Не указан'}</span>
                                            <span>Создано: ${new Date(vacancy.created_at).toLocaleDateString('ru-RU')}</span>
                                        </div>
                                    </div>
                                    <div class="vacancy-selection-arrow">→</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Закрыть</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    selectVacancyForResumes(vacancyId, vacancyTitle) {
        // Закрываем модальное окно выбора вакансии
        document.querySelector('.modal').remove();
        
        // Сохраняем выбранную вакансию
        this.selectedVacancyId = vacancyId;
        this.selectedVacancyTitle = vacancyTitle;
        
        // Показываем модальное окно загрузки резюме
        this.showResumeUploadModal();
    }
    
    showResumeUploadModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h3>📄 Загрузка резюме для: ${this.selectedVacancyTitle}</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">[X]</button>
                </div>
                <div class="modal-body">
                    <div class="resume-upload-section">
                        <div class="upload-area" id="resumeUploadArea">
                            <div class="upload-content">
                                <div class="upload-icon">📄</div>
                                <h3>Перетащите резюме сюда или нажмите для выбора</h3>
                                <p>Поддерживаемые форматы: PDF, DOC, DOCX, TXT</p>
                                <input type="file" id="resumeFileInput" accept=".pdf,.doc,.docx,.txt" multiple style="display: none;">
                            </div>
                        </div>
                        
                        <div class="resume-list" id="resumeList" style="display: none;">
                            <h4>Загруженные резюме:</h4>
                            <div class="resume-items" id="resumeItems"></div>
                        </div>
                        
                        <div class="resume-actions" id="resumeActions" style="display: none;">
                            <button class="btn btn-primary" onclick="app.analyzeResumes()">Анализировать резюме</button>
                            <button class="btn btn-secondary" onclick="app.clearResumes()">Очистить список</button>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Закрыть</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Настраиваем обработчики событий для загрузки резюме
        this.setupResumeUpload(modal);
    }
    
    setupResumeUpload(modal) {
        const uploadArea = modal.querySelector('#resumeUploadArea');
        const fileInput = modal.querySelector('#resumeFileInput');
        const resumeList = modal.querySelector('#resumeList');
        const resumeItems = modal.querySelector('#resumeItems');
        const resumeActions = modal.querySelector('#resumeActions');
        
        this.uploadedResumes = [];
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        uploadArea.addEventListener('drop', (e) => this.handleResumeDrop(e, resumeItems, resumeList, resumeActions));
        
        fileInput.addEventListener('change', (e) => this.handleResumeFileSelect(e, resumeItems, resumeList, resumeActions));
    }
    
    handleResumeDrop(e, resumeItems, resumeList, resumeActions) {
        e.preventDefault();
        e.stopPropagation();
        
        const files = Array.from(e.dataTransfer.files);
        this.addResumesToList(files, resumeItems, resumeList, resumeActions);
    }
    
    handleResumeFileSelect(e, resumeItems, resumeList, resumeActions) {
        const files = Array.from(e.target.files);
        this.addResumesToList(files, resumeItems, resumeList, resumeActions);
    }
    
    addResumesToList(files, resumeItems, resumeList, resumeActions) {
        files.forEach(file => {
            if (this.isValidResumeFile(file)) {
                const resumeItem = document.createElement('div');
                resumeItem.className = 'resume-item';
                resumeItem.innerHTML = `
                    <div class="resume-info">
                        <div class="resume-name">${file.name}</div>
                        <div class="resume-size">${this.formatFileSize(file.size)}</div>
                    </div>
                    <button class="btn-danger btn-sm" onclick="app.removeResume(this)">×</button>
                `;
                
                resumeItems.appendChild(resumeItem);
                this.uploadedResumes.push(file);
            }
        });
        
        if (this.uploadedResumes.length > 0) {
            resumeList.style.display = 'block';
            resumeActions.style.display = 'block';
        }
    }
    
    isValidResumeFile(file) {
        const validTypes = ['.pdf', '.doc', '.docx', '.txt'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        return validTypes.includes(fileExtension);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    removeResume(button) {
        const resumeItem = button.closest('.resume-item');
        const resumeName = resumeItem.querySelector('.resume-name').textContent;
        
        // Удаляем из массива
        this.uploadedResumes = this.uploadedResumes.filter(file => file.name !== resumeName);
        
        // Удаляем из DOM
        resumeItem.remove();
        
        // Скрываем список и действия, если нет резюме
        if (this.uploadedResumes.length === 0) {
            document.getElementById('resumeList').style.display = 'none';
            document.getElementById('resumeActions').style.display = 'none';
        }
    }
    
    clearResumes() {
        this.uploadedResumes = [];
        document.getElementById('resumeItems').innerHTML = '';
        document.getElementById('resumeList').style.display = 'none';
        document.getElementById('resumeActions').style.display = 'none';
    }
    
    async analyzeResumes() {
        if (this.uploadedResumes.length === 0) {
            this.showError('Нет загруженных резюме для анализа');
            return;
        }
        
        if (!this.selectedVacancyId) {
            this.showError('Не выбрана вакансия для сопоставления');
            return;
        }
        
        this.showLoading('Анализируем резюме кандидатов...');
        
        try {
            const results = [];
            
            // Обрабатываем каждое резюме по очереди
            for (let i = 0; i < this.uploadedResumes.length; i++) {
                const resume = this.uploadedResumes[i];
                this.showLoading(`Анализируем резюме ${i + 1} из ${this.uploadedResumes.length}: ${resume.name}`);
                
                const result = await this.analyzeSingleResume(resume);
                results.push(result);
            }
            
            this.hideLoading();
            this.showResumeAnalysisResults(results);
            
        } catch (error) {
            this.hideLoading();
            this.showError('Ошибка при анализе резюме: ' + error.message);
        }
    }
    
    async analyzeSingleResume(resumeFile) {
        const formData = new FormData();
        formData.append('file', resumeFile);
        formData.append('vacancy_id', this.selectedVacancyId);
        
        const response = await fetch('/api/analyze-resume', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Ошибка при анализе резюме');
        }
        
        return await response.json();
    }
    
    showResumeAnalysisResults(results) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 1200px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h3>📊 Результаты анализа резюме</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">[X]</button>
                </div>
                <div class="modal-body">
                    <div class="resume-analysis-results">
                        <div class="analysis-summary">
                            <h4>Сводка по вакансии: ${this.selectedVacancyTitle}</h4>
                            <p>Проанализировано резюме: ${results.length}</p>
                        </div>
                        
                        <div class="resume-results-list">
                            ${results.map((result, index) => `
                                <div class="resume-result-item">
                                    <div class="resume-result-header">
                                        <h5>${result.filename}</h5>
                                        <div class="resume-result-score">
                                            Общий балл: <span class="score-value">${result.total_score || 0}/200</span>
                                        </div>
                                    </div>
                                    
                                    <div class="resume-result-content">
                                        <div class="field-matching">
                                            <h6>Сопоставление полей:</h6>
                                            <div class="field-matches">
                                                ${Object.entries(result.field_matches || {}).map(([field, match]) => `
                                                    <div class="field-match">
                                                        <span class="field-name">${field}:</span>
                                                        <span class="field-value">${match.value || 'Не найдено'}</span>
                                                        <span class="field-score">${match.score || 0} баллов</span>
                                                    </div>
                                                `).join('')}
                                            </div>
                                        </div>
                                        
                                        <div class="experience-analysis">
                                            <h6>Анализ опыта:</h6>
                                            <div class="experience-details">
                                                <div class="experience-item">
                                                    <span>Общий опыт:</span>
                                                    <span>${result.experience?.total_years || 'Не определен'}</span>
                                                </div>
                                                <div class="experience-item">
                                                    <span>Релевантный опыт:</span>
                                                    <span>${result.experience?.relevant_years || 'Не определен'}</span>
                                                </div>
                                                <div class="experience-item">
                                                    <span>Балл за опыт:</span>
                                                    <span>${result.experience?.score || 0}</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="skills-analysis">
                                            <h6>Анализ навыков:</h6>
                                            <div class="skills-matches">
                                                ${Object.entries(result.skills_matches || {}).map(([skill, match]) => `
                                                    <div class="skill-match">
                                                        <span class="skill-name">${skill}:</span>
                                                        <span class="skill-level">${match.level || 'Не найден'}</span>
                                                        <span class="skill-score">${match.score || 0} баллов</span>
                                                    </div>
                                                `).join('')}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="app.exportResults()">Экспортировать результаты</button>
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Закрыть</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    exportResults() {
        // Заглушка для экспорта результатов
        alert('Функция экспорта результатов будет реализована позже');
    }
    
    showCreatedVacancyCard(result) {
        // Создаем объект вакансии для отображения
        const vacancy = {
            id: result.vacancy_id,
            job_title: result.job_title,
            region: result.region,
            positions_count: result.positions_count,
            application_deadline: result.application_deadline,
            created_at: new Date().toISOString(),
            structured_data: this.structuredData,
            skill_scores: this.skillScores
        };
        
        // Создаем модальное окно с карточкой вакансии
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 900px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h3>✅ Вакансия успешно создана!</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove(); app.backToWelcome();">[X]</button>
                </div>
                <div class="modal-body">
                    <div class="success-vacancy-card">
                        <div class="vacancy-header">
                            <div class="vacancy-title">${vacancy.job_title || 'Без названия'}</div>
                            <div class="vacancy-id">ID: ${vacancy.id}</div>
                        </div>
                        <div class="vacancy-content">
                            <div class="vacancy-info-row">
                                <div class="info-item">
                                    <span class="info-label">Позиций:</span>
                                    <span class="info-value">${vacancy.positions_count || 1}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Регион:</span>
                                    <span class="info-value">${vacancy.region || 'Не указан'}</span>
                                </div>
                                <div class="info-item">
                                    <span class="info-label">Дата создания:</span>
                                    <span class="info-value">${new Date(vacancy.created_at).toLocaleDateString('ru-RU')}</span>
                                </div>
                                ${vacancy.application_deadline ? `
                                    <div class="info-item">
                                        <span class="info-label">До:</span>
                                        <span class="info-value deadline">${new Date(vacancy.application_deadline).toLocaleDateString('ru-RU')}</span>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                        
                        ${vacancy.structured_data ? `
                            <div class="detail-section">
                                <h4>Структурированные данные</h4>
                                <div class="structured-data-preview">
                                    ${this.formatStructuredDataForModal(vacancy.structured_data)}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${vacancy.skill_scores ? `
                            <div class="detail-section">
                                <h4>Распределение баллов по навыкам</h4>
                                <div class="skills-scoring-preview">
                                    ${this.formatSkillScoresForModal(vacancy.skill_scores)}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" onclick="this.closest('.modal').remove(); app.backToWelcome();">
                        Вернуться в главное меню
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Автоматически закрываем модальное окно через 5 секунд и возвращаемся в главное меню
        setTimeout(() => {
            if (modal && modal.parentNode) {
                modal.remove();
                this.backToWelcome();
            }
        }, 5000);
    }
    


    // Utility Methods
    showLoading(text = 'Обработка...') {
        document.getElementById('loadingText').textContent = text;
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
    
    disableNextButton() {
        const currentStep = this.currentStep;
        const nextButton = document.getElementById(`nextStep${currentStep}Btn`);
        if (nextButton) {
            nextButton.disabled = true;
        }
    }
    
    enableNextButton() {
        const currentStep = this.currentStep;
        const nextButton = document.getElementById(`nextStep${currentStep}Btn`);
        if (nextButton) {
            nextButton.disabled = false;
        }
    }

    showError(message) {
        // Заменяем \n на <br> для правильного отображения переносов строк
        const formattedMessage = message.replace(/\n/g, '<br>');
        document.getElementById('errorMessage').innerHTML = formattedMessage;
        document.getElementById('errorModal').style.display = 'flex';
    }

    closeErrorModal() {
        document.getElementById('errorModal').style.display = 'none';
    }

    showSuccess(message) {
        // Создаем временное уведомление об успехе
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.innerHTML = `
            <div class="success-content">
                <span class="success-icon">✅</span>
                <span class="success-message">${message}</span>
            </div>
        `;
        
        // Добавляем стили для уведомления
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--success);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            font-size: 14px;
            font-weight: 500;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Анимация появления
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Автоматическое скрытие через 3 секунды
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // Quick add field functionality
    addQuickField() {
        console.log('addQuickField called'); // Debug log
        
        const categorySelect = document.getElementById('quickFieldCategory');
        const customBlockInput = document.getElementById('customBlockName');
        const fieldName = document.getElementById('quickFieldName').value.trim();
        const fieldValue = document.getElementById('quickFieldValue').value.trim();
        
        console.log('Values:', { categorySelect: categorySelect.value, fieldName, fieldValue }); // Debug log
        
        if (!fieldName) {
            this.showError('Пожалуйста, введите название поля');
            return;
        }
        
        if (!fieldValue) {
            this.showError('Пожалуйста, введите значение поля');
            return;
        }
        
        // Определяем категорию
        let category = categorySelect.value;
        if (category === 'custom') {
            const customBlockName = customBlockInput.value.trim();
            if (!customBlockName) {
                this.showError('Пожалуйста, введите название нового блока');
                return;
            }
            category = this.createCustomCategory(customBlockName);
        }
        
        // Обрабатываем списки (обязанности и преимущества)
        if (category === 'responsibilities' || category === 'benefits') {
            if (!this.structuredData[category]) {
                this.structuredData[category] = [];
            }
            this.structuredData[category].push(fieldValue);
            this.updateListDisplay(category);
            this.showSuccess(`Элемент добавлен в "${this.getCategoryName(category)}"`);
        } else {
            // Добавляем поле в соответствующую секцию
            if (!this.structuredData[category]) {
                this.structuredData[category] = {};
            }
            this.structuredData[category][fieldName] = fieldValue;
            
            // Обновляем отображение соответствующей секции
            this.updateDataGrid(category);
            this.showSuccess(`Поле "${fieldName}" добавлено в блок "${this.getCategoryName(category)}"`);
        }
        
        // Очищаем форму
        this.clearQuickFieldForm();
    }
    
    handleCategoryChange() {
        const categorySelect = document.getElementById('quickFieldCategory');
        const customBlockInput = document.getElementById('customBlockName');
        
        if (categorySelect.value === 'custom') {
            customBlockInput.style.display = 'block';
            customBlockInput.focus();
        } else {
            customBlockInput.style.display = 'none';
            this.updateQuickFieldSuggestions();
        }
    }
    
    createCustomCategory(customName) {
        // Создаем уникальный ключ для нового блока
        const timestamp = Date.now();
        const customKey = `custom_${timestamp}`;
        
        // Сохраняем название блока для отображения
        if (!this.customCategories) {
            this.customCategories = {};
        }
        this.customCategories[customKey] = customName;
        
        return customKey;
    }
    
    clearQuickFieldForm() {
        document.getElementById('quickFieldName').value = '';
        document.getElementById('quickFieldValue').value = '';
        document.getElementById('customBlockName').value = '';
        document.getElementById('customBlockName').style.display = 'none';
        document.getElementById('quickFieldCategory').value = 'requirements';
        this.hideQuickFieldSuggestions();
    }
    
    updateQuickFieldSuggestions() {
        const category = document.getElementById('quickFieldCategory').value;
        const suggestions = this.getFieldSuggestions(category);
        this.showQuickFieldSuggestions('', suggestions);
    }
    
    showQuickFieldSuggestions(input, suggestions = null) {
        const suggestionsContainer = document.getElementById('quickFieldSuggestions');
        const category = document.getElementById('quickFieldCategory').value;
        
        if (!suggestions) {
            suggestions = this.getFieldSuggestions(category);
        }
        
        if (!input || input.length < 1) {
            this.hideQuickFieldSuggestions();
            return;
        }
        
        const filteredSuggestions = suggestions.filter(suggestion => 
            suggestion.toLowerCase().includes(input.toLowerCase())
        );
        
        if (filteredSuggestions.length === 0) {
            this.hideQuickFieldSuggestions();
            return;
        }
        
        suggestionsContainer.innerHTML = '';
        filteredSuggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'field-suggestion';
            item.textContent = suggestion;
            item.addEventListener('click', () => {
                document.getElementById('quickFieldName').value = suggestion;
                this.hideQuickFieldSuggestions();
            });
            suggestionsContainer.appendChild(item);
        });
        
        suggestionsContainer.style.display = 'block';
    }
    
    hideQuickFieldSuggestions() {
        document.getElementById('quickFieldSuggestions').style.display = 'none';
    }
    
    openAddFieldModal() {
        document.getElementById('addFieldModal').style.display = 'flex';
        this.updateFieldSuggestions();
        document.getElementById('fieldName').focus();
    }
    
    closeAddFieldModal() {
        document.getElementById('addFieldModal').style.display = 'none';
        this.clearAddFieldForm();
    }
    
    clearAddFieldForm() {
        document.getElementById('fieldCategory').value = 'requirements';
        document.getElementById('fieldName').value = '';
        document.getElementById('fieldValue').value = '';
        this.hideFieldSuggestions();
    }
    
    updateFieldSuggestions() {
        const category = document.getElementById('fieldCategory').value;
        const suggestions = this.getFieldSuggestions(category);
        this.showFieldSuggestions('', suggestions);
    }
    
    getFieldSuggestions(category) {
        const suggestions = {
            'job_info': [
                'Название должности', 'Компания', 'Тип занятости', 'График работы', 
                'Местоположение', 'Уровень', 'Опыт работы', 'Образование', 'Отдел',
                'Руководитель', 'Дата начала работы', 'Испытательный срок'
            ],
            'salary': [
                'Зарплата от', 'Зарплата до', 'Валюта', 'Тип оплаты', 'Бонусы',
                'Форма оплаты', 'Премии', 'Компенсации', 'Социальный пакет',
                'Страховка', 'Отпуск', 'Больничный'
            ],
            'requirements': [
                'Опыт работы', 'Образование', 'Технические навыки', 'Языки программирования',
                'Инструменты', 'Иностранные языки', 'Личные качества', 'Сертификаты',
                'Возраст', 'Пол', 'Водительские права', 'Готовность к командировкам'
            ],
            'company_info': [
                'Описание компании', 'Сфера деятельности', 'Размер компании', 'Стадия развития',
                'Год основания', 'Количество сотрудников', 'Офисы', 'Клиенты',
                'Продукты', 'Технологии', 'Культура компании'
            ],
            'contact_info': [
                'Контактное лицо', 'Email', 'Телефон', 'Сайт', 'LinkedIn',
                'Адрес офиса', 'Метро', 'Время работы', 'Как добраться'
            ],
            'additional_info': [
                'Процесс отбора', 'Дополнительные требования', 'Сроки', 'Примечания',
                'Бонусы', 'Льготы', 'Обучение', 'Карьерный рост', 'Команда',
                'Проекты', 'Технологический стек'
            ]
        };
        
        return suggestions[category] || [];
    }
    
    showFieldSuggestions(input, suggestions = null) {
        const suggestionsContainer = document.getElementById('fieldSuggestions');
        const category = document.getElementById('fieldCategory').value;
        
        if (!suggestions) {
            suggestions = this.getFieldSuggestions(category);
        }
        
        if (!input || input.length < 1) {
            this.hideFieldSuggestions();
            return;
        }
        
        const filteredSuggestions = suggestions.filter(suggestion => 
            suggestion.toLowerCase().includes(input.toLowerCase())
        );
        
        if (filteredSuggestions.length === 0) {
            this.hideFieldSuggestions();
            return;
        }
        
        suggestionsContainer.innerHTML = '';
        filteredSuggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'field-suggestion';
            item.textContent = suggestion;
            item.addEventListener('click', () => {
                document.getElementById('fieldName').value = suggestion;
                this.hideFieldSuggestions();
            });
            suggestionsContainer.appendChild(item);
        });
        
        suggestionsContainer.style.display = 'block';
    }
    
    hideFieldSuggestions() {
        document.getElementById('fieldSuggestions').style.display = 'none';
    }
    
    addNewFieldFromModal() {
        const category = document.getElementById('fieldCategory').value;
        const fieldName = document.getElementById('fieldName').value.trim();
        const fieldValue = document.getElementById('fieldValue').value.trim();
        
        if (!fieldName) {
            this.showError('Пожалуйста, введите название поля');
            return;
        }
        
        if (!fieldValue) {
            this.showError('Пожалуйста, введите значение поля');
            return;
        }
        
        // Добавляем поле в соответствующую секцию
        if (!this.structuredData[category]) {
            this.structuredData[category] = {};
        }
        this.structuredData[category][fieldName] = fieldValue;
        
        // Обновляем отображение соответствующей секции
        this.updateDataGrid(category);
        
        this.closeAddFieldModal();
        this.showSuccess(`Поле "${fieldName}" добавлено в блок "${this.getCategoryName(category)}"`);
    }
    
    getCategoryName(category) {
        const names = {
            'job_info': 'Информация о вакансии',
            'salary': 'Зарплата',
            'requirements': 'Требования',
            'company_info': 'Информация о компании',
            'contact_info': 'Контактная информация',
            'additional_info': 'Дополнительная информация',
            'responsibilities': 'Обязанности',
            'benefits': 'Преимущества'
        };
        
        // Проверяем пользовательские категории
        if (this.customCategories && this.customCategories[category]) {
            return this.customCategories[category];
        }
        
        return names[category] || category;
    }
    
    updateListDisplay(category) {
        const containerMap = {
            'responsibilities': 'responsibilitiesList',
            'benefits': 'benefitsList'
        };
        
        const containerId = containerMap[category];
        if (containerId) {
            const itemClass = this.getItemClass(containerId);
            this.displayList(containerId, this.structuredData[category], itemClass);
        }
    }
    
    updateDataGrid(category) {
        const gridMapping = {
            'job_info': 'jobInfoGrid',
            'salary': 'salaryGrid',
            'requirements': 'requirementsGrid'
        };
        
        const gridId = gridMapping[category];
        if (gridId) {
            this.displayDataGrid(gridId, this.structuredData[category]);
        } else {
            // Для пользовательских категорий создаем новую секцию
            this.createCustomDataSection(category);
        }
    }
    
    createCustomDataSection(category) {
        const dataSections = document.getElementById('dataSections');
        const categoryName = this.getCategoryName(category);
        
        // Проверяем, не существует ли уже такая секция
        const existingSection = document.getElementById(`custom_${category}`);
        if (existingSection) {
            // Обновляем существующую секцию
            const grid = existingSection.querySelector('.data-grid');
            this.displayDataGrid(grid.id, this.structuredData[category]);
            return;
        }
        
        // Создаем новую секцию
        const section = document.createElement('div');
        section.className = 'data-section';
        section.id = `custom_${category}`;
        
        const gridId = `customGrid_${category}`;
        section.innerHTML = `
            <h3>${categoryName.toUpperCase()}</h3>
            <div class="data-grid" id="${gridId}"></div>
        `;
        
        // Добавляем секцию в конец
        dataSections.appendChild(section);
        
        // Отображаем данные
        this.displayDataGrid(gridId, this.structuredData[category]);
    }
    
    // Field editing methods
    editField(button) {
        const item = button.closest('.data-item');
        const label = item.querySelector('.data-label').textContent;
        const value = item.querySelector('.data-value').textContent;
        
        const newValue = prompt(`Редактировать "${label}":`, value);
        if (newValue !== null && newValue.trim() !== '') {
            // Находим категорию и обновляем данные
            const grid = item.closest('.data-grid');
            const category = this.findCategoryByGridId(grid.id);
            
            if (category && this.structuredData[category]) {
                this.structuredData[category][label] = newValue.trim();
                this.displayDataGrid(grid.id, this.structuredData[category]);
                this.showSuccess(`Поле "${label}" обновлено`);
            }
        }
    }
    
    deleteField(button) {
        const item = button.closest('.data-item');
        const label = item.querySelector('.data-label').textContent;
        
        if (confirm(`Удалить поле "${label}"?`)) {
            // Находим категорию и удаляем данные
            const grid = item.closest('.data-grid');
            const category = this.findCategoryByGridId(grid.id);
            
            if (category && this.structuredData[category]) {
                delete this.structuredData[category][label];
                this.displayDataGrid(grid.id, this.structuredData[category]);
                this.showSuccess(`Поле "${label}" удалено`);
            }
        }
    }
    
    findCategoryByGridId(gridId) {
        const gridIdMap = {
            'jobInfoGrid': 'job_info',
            'salaryGrid': 'salary',
            'requirementsGrid': 'requirements'
        };
        
        // Проверяем стандартные категории
        if (gridIdMap[gridId]) {
            return gridIdMap[gridId];
        }
        
        // Проверяем пользовательские категории
        if (gridId.startsWith('customGrid_')) {
            return gridId.replace('customGrid_', '');
        }
        
        return null;
    }
    
    // List editing methods
    editListItem(button, containerId, index) {
        const item = button.closest('.editable');
        const textElement = item.querySelector('.list-item-text');
        const currentText = textElement.textContent;
        
        const newText = prompt(`Редактировать элемент:`, currentText);
        if (newText !== null && newText.trim() !== '') {
            // Находим категорию и обновляем данные
            const category = this.findCategoryByContainerId(containerId);
            
            if (category && this.structuredData[category]) {
                this.structuredData[category][index] = newText.trim();
                this.displayList(containerId, this.structuredData[category], this.getItemClass(containerId));
                this.showSuccess(`Элемент обновлен`);
            }
        }
    }
    
    deleteListItem(button, containerId, index) {
        const item = button.closest('.editable');
        const textElement = item.querySelector('.list-item-text');
        const itemText = textElement.textContent;
        
        if (confirm(`Удалить элемент "${itemText}"?`)) {
            // Находим категорию и удаляем данные
            const category = this.findCategoryByContainerId(containerId);
            
            if (category && this.structuredData[category]) {
                this.structuredData[category].splice(index, 1);
                this.displayList(containerId, this.structuredData[category], this.getItemClass(containerId));
                this.showSuccess(`Элемент удален`);
            }
        }
    }
    
    addNewItemButton(containerId, itemClass) {
        const container = document.getElementById(containerId);
        const addButton = document.createElement('div');
        addButton.className = 'add-item-button';
        addButton.innerHTML = `
            <button class="btn-add" onclick="app.addNewListItem('${containerId}')">
                + Добавить новый элемент
            </button>
        `;
        container.appendChild(addButton);
    }
    
    addNewListItem(containerId) {
        const newText = prompt('Введите новый элемент:');
        if (newText !== null && newText.trim() !== '') {
            // Находим категорию и добавляем данные
            const category = this.findCategoryByContainerId(containerId);
            
            if (category) {
                if (!this.structuredData[category]) {
                    this.structuredData[category] = [];
                }
                this.structuredData[category].push(newText.trim());
                this.displayList(containerId, this.structuredData[category], this.getItemClass(containerId));
                this.showSuccess(`Новый элемент добавлен`);
            }
        }
    }
    
    findCategoryByContainerId(containerId) {
        const containerMap = {
            'responsibilitiesList': 'responsibilities',
            'benefitsList': 'benefits'
        };
        
        return containerMap[containerId] || null;
    }
    
    getItemClass(containerId) {
        const classMap = {
            'responsibilitiesList': 'responsibility-item',
            'benefitsList': 'benefit-item'
        };
        
        return classMap[containerId] || 'list-item';
    }

    // Enhanced analysis display with skills scoring
    displayAnalysisResult() {
        if (!this.analysisData) return;
        
        // По просьбе пользователя убираем вывод подробного блока анализа на шаге 4
        // Оставляем только включение кнопки Далее для перехода к распределению баллов (шаг 5)
        const analysisResult = document.getElementById('analysisResult');
        if (analysisResult) {
            analysisResult.style.display = 'none';
            analysisResult.innerHTML = '';
        }
        const nextBtn = document.getElementById('nextStep4Btn');
        if (nextBtn) nextBtn.disabled = false;
        
        // Скрываем область загрузки
        const processingArea = document.querySelector('#step4 .processing-area');
        if (processingArea) {
            processingArea.style.display = 'none';
        }
    }
    
    displayAIAnalysisSummary() {
        // Создаем или обновляем блок с анализом ИИ
        let aiSummary = document.getElementById('aiAnalysisSummary');
        if (!aiSummary) {
            aiSummary = document.createElement('div');
            aiSummary.id = 'aiAnalysisSummary';
            aiSummary.className = 'ai-analysis-summary';
            
            // Добавляем в analysisResult
            const analysisResult = document.getElementById('analysisResult');
            if (analysisResult) {
                analysisResult.appendChild(aiSummary);
            }
        }
        
        if (this.analysisData.skill_scoring && this.analysisData.skill_scoring.analysis_summary) {
            aiSummary.innerHTML = `
                <h3>Анализ требований ИИ (на основе O*NET)</h3>
                <div class="analysis-content">
                    <p><strong>Сводка анализа:</strong> ${this.analysisData.skill_scoring.analysis_summary}</p>
                    <p><strong>Общая сумма баллов:</strong> ${this.analysisData.skill_scoring.total_score || 200}</p>
                    <div class="skills-preview">
                        <h4>Предварительное распределение баллов:</h4>
                        <div class="skills-categories">
                            ${this.analysisData.skill_scoring.technical_skills ? 
                                `<div class="category">
                                    <strong>Технические навыки:</strong>
                                    ${Object.entries(this.analysisData.skill_scoring.technical_skills).map(([skill, score]) => 
                                        `<span class="skill-preview">${skill}: ${score}</span>`
                                    ).join(', ')}
                                </div>` : ''
                            }
                            ${this.analysisData.skill_scoring.programming_languages ? 
                                `<div class="category">
                                    <strong>Языки программирования:</strong>
                                    ${Object.entries(this.analysisData.skill_scoring.programming_languages).map(([skill, score]) => 
                                        `<span class="skill-preview">${skill}: ${score}</span>`
                                    ).join(', ')}
                                </div>` : ''
                            }
                            ${this.analysisData.skill_scoring.tools ? 
                                `<div class="category">
                                    <strong>Инструменты:</strong>
                                    ${Object.entries(this.analysisData.skill_scoring.tools).map(([skill, score]) => 
                                        `<span class="skill-preview">${skill}: ${score}</span>`
                                    ).join(', ')}
                                </div>` : ''
                            }
                        </div>
                    </div>
                </div>
            `;
        } else {
            aiSummary.innerHTML = `
                <h3>Анализ требований ИИ</h3>
                <div class="analysis-content">
                    <p>Анализ требований на основе O*NET будет выполнен на следующем шаге.</p>
                </div>
            `;
        }
    }
    
    displaySkillsAnalysis() {
        const technicalSkills = document.getElementById('technicalSkills');
        const programmingLanguages = document.getElementById('programmingLanguages');
        const tools = document.getElementById('tools');
        
        // Очищаем контейнеры
        technicalSkills.innerHTML = '';
        programmingLanguages.innerHTML = '';
        tools.innerHTML = '';
        
        // Создаем систему баллов на основе структурированных данных
        const scores = this.calculateScores();
        
        // Отображаем технические навыки
        scores.technical_skills.forEach(skill => {
            const item = this.createSkillItem(skill.name, skill.score, skill.level);
            technicalSkills.appendChild(item);
        });
        
        // Отображаем языки программирования
        scores.programming_languages.forEach(skill => {
            const item = this.createSkillItem(skill.name, skill.score, skill.level);
            programmingLanguages.appendChild(item);
        });
        
        // Отображаем инструменты
        scores.tools.forEach(skill => {
            const item = this.createSkillItem(skill.name, skill.score, skill.level);
            tools.appendChild(item);
        });
        
        // Общая сумма баллов
        this.displayTotalScore(scores.total);
    }
    
    analyzeSkillsFromData() {
        const skills = {
            technical: [],
            programming: [],
            tools: []
        };
        
        if (this.structuredData.requirements) {
            const requirements = this.structuredData.requirements;
            
            // Анализируем технические навыки
            if (requirements['Технические навыки']) {
                const techSkills = requirements['Технические навыки'].split(',').map(s => s.trim());
                techSkills.forEach(skill => {
                    skills.technical.push({
                        name: skill,
                        score: this.calculateSkillScore(skill, 'technical'),
                        level: this.getSkillLevel(skill, 'technical')
                    });
                });
            }
            
            // Анализируем языки программирования
            if (requirements['Языки программирования']) {
                const progLanguages = requirements['Языки программирования'].split(',').map(s => s.trim());
                progLanguages.forEach(lang => {
                    skills.programming.push({
                        name: lang,
                        score: this.calculateSkillScore(lang, 'programming'),
                        level: this.getSkillLevel(lang, 'programming')
                    });
                });
            }
            
            // Анализируем инструменты
            if (requirements['Инструменты']) {
                const toolsList = requirements['Инструменты'].split(',').map(s => s.trim());
                toolsList.forEach(tool => {
                    skills.tools.push({
                        name: tool,
                        score: this.calculateSkillScore(tool, 'tools'),
                        level: this.getSkillLevel(tool, 'tools')
                    });
                });
            }
        }
        
        return skills;
    }
    
    calculateScores() {
        const scores = {
            technical_skills: [],
            programming_languages: [],
            tools: [],
            job_info_score: 0,
            salary_score: 0,
            requirements_score: 0,
            company_info_score: 0,
            contact_info_score: 0,
            additional_info_score: 0,
            total: 0
        };
        
        // Базовые категории с весами
        const categories = {
            'job_info': 40,      // Информация о вакансии - 40 баллов
            'salary': 30,        // Зарплата - 30 баллов
            'requirements': 50,  // Требования - 50 баллов
            'company_info': 20,  // Информация о компании - 20 баллов
            'contact_info': 15,  // Контактная информация - 15 баллов
            'additional_info': 25 // Дополнительная информация - 25 баллов
        };
        
        let totalScore = 0;
        
        // Проходим по всем категориям
        Object.entries(categories).forEach(([category, maxPoints]) => {
            if (this.structuredData[category]) {
                const fields = Object.keys(this.structuredData[category]).length;
                const pointsPerField = maxPoints / Math.max(fields, 1);
                let categoryScore = 0;
                
                Object.entries(this.structuredData[category]).forEach(([key, value]) => {
                    if (value && value !== 'Не указано') {
                        const score = Math.round(pointsPerField);
                        const level = this.getSkillLevel(score);
                        
                        if (this.isTechnicalSkill(key)) {
                            scores.technical_skills.push({ name: key, score, level });
                        } else if (this.isProgrammingLanguage(key)) {
                            scores.programming_languages.push({ name: key, score, level });
                        } else if (this.isTool(key)) {
                            scores.tools.push({ name: key, score, level });
                        }
                        
                        categoryScore += score;
                        totalScore += score;
                    }
                });
                
                // Сохраняем баллы по категориям
                scores[`${category}_score`] = categoryScore;
            }
        });
        
        // Проверяем пользовательские категории
        Object.keys(this.structuredData).forEach(category => {
            if (!categories[category] && this.structuredData[category]) {
                const fields = Object.keys(this.structuredData[category]).length;
                const pointsPerField = 20 / Math.max(fields, 1); // 20 баллов на пользовательскую категорию
                
                Object.entries(this.structuredData[category]).forEach(([key, value]) => {
                    if (value && value !== 'Не указано') {
                        const score = Math.round(pointsPerField);
                        const level = this.getSkillLevel(score);
                        
                        if (this.isTechnicalSkill(key)) {
                            scores.technical_skills.push({ name: key, score, level });
                        } else if (this.isProgrammingLanguage(key)) {
                            scores.programming_languages.push({ name: key, score, level });
                        } else if (this.isTool(key)) {
                            scores.tools.push({ name: key, score, level });
                        }
                        
                        totalScore += score;
                    }
                });
            }
        });
        
        // Нормализуем до 200 баллов
        if (totalScore > 0) {
            const multiplier = 200 / totalScore;
            scores.technical_skills.forEach(skill => skill.score = Math.round(skill.score * multiplier));
            scores.programming_languages.forEach(skill => skill.score = Math.round(skill.score * multiplier));
            scores.tools.forEach(skill => skill.score = Math.round(skill.score * multiplier));
            
            // Нормализуем баллы по категориям
            scores.job_info_score = Math.round(scores.job_info_score * multiplier);
            scores.salary_score = Math.round(scores.salary_score * multiplier);
            scores.requirements_score = Math.round(scores.requirements_score * multiplier);
            scores.company_info_score = Math.round(scores.company_info_score * multiplier);
            scores.contact_info_score = Math.round(scores.contact_info_score * multiplier);
            scores.additional_info_score = Math.round(scores.additional_info_score * multiplier);
            
            scores.total = 200;
        }
        
        return scores;
    }
    
    displayTotalScore(total) {
        // Создаем или обновляем отображение общей суммы
        let totalDisplay = document.getElementById('totalScore');
        if (!totalDisplay) {
            totalDisplay = document.createElement('div');
            totalDisplay.id = 'totalScore';
            totalDisplay.className = 'total-score';
            document.querySelector('.skills-analysis').appendChild(totalDisplay);
        }
        
        totalDisplay.innerHTML = `
            <div class="total-score-content">
                <h4>Общая сумма баллов</h4>
                <div class="total-score-value">${total}/200</div>
                <div class="total-score-bar">
                    <div class="total-score-fill" style="width: ${(total/200)*100}%"></div>
                </div>
            </div>
        `;
    }
    
    calculateSkillScore(skillName, category) {
        // Простая логика оценки навыков (можно улучшить)
        const skillLevels = {
            'Python': 85, 'Java': 80, 'JavaScript': 75, 'React': 70, 'Vue': 65,
            'Django': 80, 'Flask': 75, 'Spring': 70, 'Git': 90, 'Docker': 60,
            'PostgreSQL': 70, 'MySQL': 75, 'MongoDB': 65, 'Redis': 60
        };
        
        return skillLevels[skillName] || Math.floor(Math.random() * 40) + 30; // 30-70 для неизвестных
    }
    
    getSkillLevel(score) {
        if (score >= 70) return 'high';
        if (score >= 40) return 'medium';
        return 'low';
    }
    
    isTechnicalSkill(key) {
        const technicalKeywords = [
            'технические навыки', 'навыки', 'технологии', 'фреймворки',
            'базы данных', 'api', 'rest', 'graphql', 'microservices',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'devops',
            'ci/cd', 'git', 'agile', 'scrum', 'тестирование', 'qa'
        ];
        
        const lowerKey = key.toLowerCase();
        return technicalKeywords.some(keyword => lowerKey.includes(keyword));
    }
    
    isProgrammingLanguage(key) {
        const programmingKeywords = [
            'языки программирования', 'программирование', 'python', 'java',
            'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby',
            'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab'
        ];
        
        const lowerKey = key.toLowerCase();
        return programmingKeywords.some(keyword => lowerKey.includes(keyword));
    }
    
    isTool(key) {
        const toolKeywords = [
            'инструменты', 'ide', 'редакторы', 'vs code', 'intellij',
            'eclipse', 'sublime', 'vim', 'emacs', 'postman', 'insomnia',
            'jira', 'confluence', 'slack', 'teams', 'notion', 'figma',
            'sketch', 'adobe', 'photoshop', 'illustrator'
        ];
        
        const lowerKey = key.toLowerCase();
        return toolKeywords.some(keyword => lowerKey.includes(keyword));
    }
    
    createSkillItem(name, score, level) {
        const item = document.createElement('div');
        item.className = 'skill-item';
        item.innerHTML = `
            <span class="skill-name">${name}</span>
            <div class="skill-score">
                <span class="score-badge ${level}">${score}</span>
            </div>
        `;
        return item;
    }
    
    displaySkillRecommendations() {
        const container = document.getElementById('skillRecommendations');
        container.innerHTML = '';
        
        const recommendations = this.generateSkillRecommendations();
        
        recommendations.forEach(rec => {
            const item = document.createElement('div');
            item.className = 'recommendation-item';
            item.innerHTML = `
                <div class="recommendation-icon">💡</div>
                <div class="recommendation-content">
                    <div class="recommendation-title">${rec.title}</div>
                    <div class="recommendation-description">${rec.description}</div>
                </div>
            `;
            container.appendChild(item);
        });
    }
    
    generateSkillRecommendations() {
        const recommendations = [];
        const skills = this.analyzeSkillsFromData();
        
        // Анализируем низкие навыки и предлагаем улучшения
        const allSkills = [...skills.technical, ...skills.programming, ...skills.tools];
        const lowSkills = allSkills.filter(skill => skill.level === 'low');
        
        if (lowSkills.length > 0) {
            recommendations.push({
                title: 'Развитие слабых навыков',
                description: `Рекомендуем изучить: ${lowSkills.map(s => s.name).join(', ')}. Эти навыки помогут повысить вашу конкурентоспособность.`
            });
        }
        
        // Общие рекомендации
        recommendations.push({
            title: 'Современные технологии',
            description: 'Рассмотрите изучение современных фреймворков и инструментов: React, Vue.js, Docker, Kubernetes.'
        });
        
        recommendations.push({
            title: 'Практический опыт',
            description: 'Создайте несколько проектов на GitHub, чтобы продемонстрировать свои навыки на практике.'
        });
        
        return recommendations;
    }

    resetProcess() {
        this.currentStep = 1;
        this.selectedFile = null;
        this.extractedData = null;
        this.structuredData = null;
        this.originalStructuredData = null;
        this.analysisData = null;
        this.vacancyId = null;
        this.isEditMode = false;
        this.editingTemplateId = null;
        this.skillScores = {};
        
        // Reset UI
        this.removeFile();
        this.updateProgress();
        this.showStep(1);
        
        // Hide all result panels
        document.getElementById('extractionResult').style.display = 'none';
        document.getElementById('aiResult').style.display = 'none';
        document.getElementById('analysisResult').style.display = 'none';
        document.getElementById('saveResult').style.display = 'none';
        
        // Show all processing areas
        const processingAreas = document.querySelectorAll('.processing-area');
        processingAreas.forEach(area => {
            area.style.display = 'block';
        });
        
        // Reset form
        document.getElementById('applicationDeadline').value = '';
        document.getElementById('positionsCount').value = '';
        document.getElementById('region').value = '';
        
        // Reset buttons
        document.getElementById('nextStep2Btn').disabled = true;
        document.getElementById('nextStep3Btn').disabled = true;
        document.getElementById('nextStep4Btn').disabled = true;
        
        // Reset step 3 button text
        const nextStep3Btn = document.getElementById('nextStep3Btn');
        if (nextStep3Btn) {
            nextStep3Btn.textContent = 'Далее';
        }
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new VacancyProcessor();
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (window.app) {
        window.app.showError('Произошла неожиданная ошибка. Пожалуйста, попробуйте еще раз.');
    }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    if (window.app) {
        window.app.showError('Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз.');
    }
});

