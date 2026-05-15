// Global state
let uploadedImages = [];
let currentFullscreenIndex = 0;
let fullscreenImages = [];

// Page Components
async function LoginPage() {
    return `
        <div class="auth-container">
            <div class="auth-card">
                <div class="auth-header">
                    <div class="logo">🎯</div>
                    <h1>Marketplace Ad Generator</h1>
                    <p>Войдите в аккаунт для генерации рекламы</p>
                </div>
                <div id="error-message" class="error-message"></div>
                <form id="login-form" onsubmit="return false;">
                    <div class="form-group">
                        <label>Логин</label>
                        <input type="text" id="username" placeholder="Введите логин" required minlength="3">
                    </div>
                    <div class="form-group">
                        <label>Пароль</label>
                        <input type="password" id="password" placeholder="Введите пароль" required minlength="6">
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-sign-in-alt"></i> Войти
                    </button>
                </form>
                <div class="auth-links">
                    <p>Нет аккаунта? <a onclick="window.location.hash='#/register'">Зарегистрироваться</a></p>
                </div>
            </div>
        </div>
    `;
}

async function RegisterPage() {
    return `
        <div class="auth-container">
            <div class="auth-card">
                <div class="auth-header">
                    <div class="logo">🚀</div>
                    <h1>Создать аккаунт</h1>
                    <p>Начните создавать рекламу для маркетплейсов</p>
                </div>
                <div id="error-message" class="error-message"></div>
                <form id="register-form" onsubmit="return false;">
                    <div class="form-group">
                        <label>Логин</label>
                        <input type="text" id="reg-username" placeholder="Придумайте логин" required minlength="3">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="reg-email" placeholder="Введите email" required>
                    </div>
                    <div class="form-group">
                        <label>Пароль</label>
                        <input type="password" id="reg-password" placeholder="Придумайте пароль" required minlength="6">
                    </div>
                    <div class="form-group">
                        <label>Подтвердите пароль</label>
                        <input type="password" id="reg-password2" placeholder="Повторите пароль" required minlength="6">
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-user-plus"></i> Зарегистрироваться
                    </button>
                </form>
                <div class="auth-links">
                    <p>Уже есть аккаунт? <a onclick="window.location.hash='#/login'">Войти</a></p>
                </div>
            </div>
        </div>
    `;
}

async function DashboardPage() {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    
    return `
        <div class="dashboard">
            <header class="header">
                <div class="header-left">
                    <div class="header-logo">🎯</div>
                    <h1>Marketplace Ad Generator</h1>
                </div>
                <div class="user-menu">
                    <div class="user-info">
                        <div class="user-name">${userData.username || 'Пользователь'}</div>
                    </div>
                    <button class="btn-logout" onclick="handleLogout()">
                        <i class="fas fa-sign-out-alt"></i> Выйти
                    </button>
                </div>
            </header>

            <main class="main-content">
                <div class="tabs">
                    <button class="tab-btn active" onclick="switchTab(event, 'generate')">
                        <i class="fas fa-magic"></i> Генерация
                    </button>
                    <button class="tab-btn" onclick="switchTab(event, 'history')">
                        <i class="fas fa-history"></i> История
                    </button>
                    <button class="tab-btn" onclick="switchTab(event, 'favorites')">
                        <i class="fas fa-star"></i> Избранное
                    </button>
                    <button class="tab-btn" onclick="switchTab(event, 'analytics')">
                        <i class="fas fa-chart-bar"></i> Аналитика
                    </button>
                </div>

                <div id="tab-generate" class="tab-content active">
                    ${GenerateTab()}
                </div>
                <div id="tab-history" class="tab-content">
                    <div id="history-content"></div>
                </div>
                <div id="tab-favorites" class="tab-content">
                    <div id="favorites-content"></div>
                </div>
                <div id="tab-analytics" class="tab-content">
                    ${AnalyticsTab()}
                </div>
            </main>
        </div>
    `;
}

function GenerateTab() {
    return `
        <div class="generation-form">
            <h2>Создать рекламный комплект</h2>
            <form id="generate-form" onsubmit="return false;">
                <div class="form-row">
                    <div class="form-group">
                        <label>Промпт для генерации</label>
                        <textarea 
                            id="prompt" 
                            class="prompt-textarea" 
                            placeholder="Опишите товар, стиль и площадку для рекламы..."
                            required
                        ></textarea>
                    </div>
                    <div class="form-group">
                        <label>Фото товара (до 5 шт.)</label>
                        <div class="image-upload-area" onclick="document.getElementById('product-images').click()">
                            <div class="upload-icon">
                                <i class="fas fa-cloud-upload-alt"></i>
                            </div>
                            <div class="upload-text">Нажмите для загрузки или перетащите файлы</div>
                        </div>
                        <input type="file" id="product-images" accept="image/*" multiple style="display: none" onchange="handleImageUpload(event)">
                        <div class="image-preview" id="image-preview"></div>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary btn-generate" id="generate-btn">
                    <i class="fas fa-wand-magic-sparkles"></i> Сгенерировать рекламу
                </button>
            </form>
        </div>
        <div id="generation-results"></div>
    `;
}

function AnalyticsTab() {
    return `
        <div class="generation-form">
            <h2>Аналитика</h2>
            <div class="form-row">
                <div class="form-group">
                    <label>Начальная дата</label>
                    <input type="date" id="analytics-start" value="${getDateDaysAgo(30)}">
                </div>
                <div class="form-group">
                    <label>Конечная дата</label>
                    <input type="date" id="analytics-end" value="${getDateToday()}">
                </div>
                <div class="form-group">
                    <label>Гранулярность</label>
                    <select id="analytics-granularity">
                        <option value="day">По дням</option>
                        <option value="week">По неделям</option>
                        <option value="month">По месяцам</option>
                    </select>
                </div>
            </div>
            <button class="btn btn-primary" onclick="loadAnalytics()">
                <i class="fas fa-search"></i> Загрузить данные
            </button>
        </div>
        <div id="analytics-results"></div>
    `;
}

// Event Handlers
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username')?.value;
    const password = document.getElementById('password')?.value;
    const errorDiv = document.getElementById('error-message');
    
    if (!username || !password) {
        if (errorDiv) {
            errorDiv.textContent = 'Заполните все поля';
            errorDiv.classList.add('show');
        }
        return;
    }
    
    try {
        const response = await api.login(username, password);
        
        if (response.token) {
            api.setToken(response.token);
            localStorage.setItem('userData', JSON.stringify({
                username: username,
                user_id: response.user_id
            }));
            showToast('Вход выполнен успешно!', 'success');
            window.location.hash = '#/dashboard';
        }
    } catch (error) {
        if (errorDiv) {
            errorDiv.textContent = error.message || 'Ошибка входа';
            errorDiv.classList.add('show');
        }
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('reg-username')?.value;
    const email = document.getElementById('reg-email')?.value;
    const password = document.getElementById('reg-password')?.value;
    const password2 = document.getElementById('reg-password2')?.value;
    const errorDiv = document.getElementById('error-message');
    
    if (password !== password2) {
        if (errorDiv) {
            errorDiv.textContent = 'Пароли не совпадают';
            errorDiv.classList.add('show');
        }
        return;
    }
    
    try {
        const response = await api.register(username, email, password, password2);
        
        if (response.token) {
            api.setToken(response.token);
            localStorage.setItem('userData', JSON.stringify({
                username: username,
                email: email,
                user_id: response.user_id
            }));
            showToast('Регистрация успешна!', 'success');
            window.location.hash = '#/dashboard';
        }
    } catch (error) {
        if (errorDiv) {
            errorDiv.textContent = error.message || 'Ошибка регистрации';
            errorDiv.classList.add('show');
        }
    }
}

async function handleLogout() {
    await api.logout();
    localStorage.removeItem('userData');
    showToast('Вы вышли из системы', 'success');
    window.location.hash = '#/login';
}

async function handleGenerate(event) {
    event.preventDefault();
    
    const prompt = document.getElementById('prompt')?.value;
    const btn = document.getElementById('generate-btn');
    
    if (!prompt) {
        showToast('Введите промпт', 'error');
        return;
    }
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Генерируем рекламу...';
    }
    
    try {
        const response = await api.generateContent(prompt, uploadedImages);
        displayGenerationResult(response);
        showToast('Реклама успешно сгенерирована!', 'success');
        
        const promptEl = document.getElementById('prompt');
        if (promptEl) promptEl.value = '';
        clearImageUpload();
        
    } catch (error) {
        showToast('Ошибка генерации: ' + error.message, 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Сгенерировать рекламу';
        }
    }
}

// Image upload
function handleImageUpload(event) {
    const files = Array.from(event.target.files);
    uploadedImages = [...uploadedImages, ...files].slice(0, 5);
    displayImagePreviews();
}

function displayImagePreviews() {
    const preview = document.getElementById('image-preview');
    if (!preview) return;
    
    preview.innerHTML = uploadedImages.map((file, index) => `
        <div class="preview-item">
            <img src="${URL.createObjectURL(file)}" alt="Preview">
            <button class="preview-remove" onclick="removeImage(${index})">×</button>
        </div>
    `).join('');
}

function removeImage(index) {
    uploadedImages.splice(index, 1);
    displayImagePreviews();
}

function clearImageUpload() {
    uploadedImages = [];
    const preview = document.getElementById('image-preview');
    const input = document.getElementById('product-images');
    if (preview) preview.innerHTML = '';
    if (input) input.value = '';
}

// Display results
function displayGenerationResult(data) {
    const results = document.getElementById('generation-results');
    if (!results) return;
    
    const card = createResultCard(data);
    results.insertAdjacentHTML('afterbegin', card);
}

function createResultCard(data) {
    const images = data.generated_images || [];
    
    let imagesHtml = '';
    if (images.length > 0) {
        imagesHtml = images.map((img, index) => {
            const imgUrl = img.url || `https://via.placeholder.com/300/6366f1/ffffff?text=Image+${index+1}`;
            return `<img src="${imgUrl}" alt="Generated" class="result-image" 
                         onclick="event.stopPropagation(); openFullscreen('${imgUrl}', ${index})"
                         onerror="this.src='https://via.placeholder.com/300/6366f1/ffffff?text=Image'">`;
        }).join('');
    } else {
        for (let i = 0; i < 4; i++) {
            const colors = ['6366f1', '8b5cf6', 'ec4899', 'f59e0b'];
            imagesHtml += `<img src="https://via.placeholder.com/300/${colors[i]}/ffffff?text=Image+${i+1}" alt="Placeholder" class="result-image">`;
        }
    }
    
    const previewText = data.generated_text 
        ? data.generated_text.substring(0, 100) + '...'
        : 'Текст генерируется...';
    
    return `
        <div class="result-card" data-id="${data.id}">
            <div class="result-images" onclick="openGenerationCard('${data.id}')">
                ${imagesHtml}
            </div>
            <div class="result-content">
                <p class="result-text">${previewText}</p>
                <div class="result-actions">
                    <button class="btn-view" onclick="openGenerationCard('${data.id}')">
                        <i class="fas fa-eye"></i> Открыть карточку
                    </button>
                    <button class="btn-icon btn-favorite" onclick="event.stopPropagation(); toggleFavorite('${data.id}')">
                        <i class="far fa-star"></i>
                    </button>
                    <button class="btn-icon btn-delete" onclick="event.stopPropagation(); deleteGeneration('${data.id}')">
                        <i class="far fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Modal functions
async function openGenerationCard(generationId) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Карточка товара</h2>
                <button class="modal-close" onclick="closeModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Загрузка...</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    
    try {
        const data = await api.getImages('history', 1, 100);
        const items = data.results || data.items || [];
        const generation = items.find(item => item.id === generationId);
        
        if (generation) {
            displayGenerationModal(generation);
        } else {
            throw new Error('Генерация не найдена');
        }
    } catch (error) {
        const modalBody = modal.querySelector('.modal-body');
        if (modalBody) {
            modalBody.innerHTML = `<div class="error-message show">Ошибка: ${error.message}</div>`;
        }
    }
}

function displayGenerationModal(data) {
    const modal = document.querySelector('.modal-overlay');
    if (!modal) return;
    
    const images = data.generated_images || [];
    const imageLabels = ['Основной вид', 'Ракурс сбоку', 'В использовании', 'Детали'];
    
    const modalBody = modal.querySelector('.modal-body');
    modalBody.innerHTML = `
        <div class="modal-images-grid">
            ${images.map((img, index) => `
                <div class="modal-image-container" onclick="openFullscreen('${img.url || ''}', ${index})">
                    <img src="${img.url || `https://via.placeholder.com/500/6366f1/ffffff?text=Image+${index+1}`}" 
                         alt="Generated image ${index + 1}"
                         onerror="this.src='https://via.placeholder.com/500/6366f1/ffffff?text=Image+${index+1}'">
                    <span class="image-label">${imageLabels[index] || 'Изображение ' + (index + 1)}</span>
                </div>
            `).join('')}
        </div>
        
        <div class="modal-text">
            <h3>Рекламный текст</h3>
            <div class="modal-text-content">${formatText(data.generated_text || 'Текст не сгенерирован')}</div>
        </div>
        
        <div class="result-actions">
            <button class="btn-icon btn-favorite" onclick="toggleFavorite('${data.id}')">
                <i class="far fa-star"></i> В избранное
            </button>
            <button class="btn-icon btn-delete" onclick="deleteGenerationFromModal('${data.id}')">
                <i class="far fa-trash-alt"></i> Удалить
            </button>
        </div>
    `;
}

function formatText(text) {
    if (!text) return 'Текст не доступен';
    return text.replace(/\n/g, '<br>');
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) modal.remove();
}

async function deleteGenerationFromModal(id) {
    if (!confirm('Удалить эту генерацию?')) return;
    
    try {
        await api.deleteImages([id]);
        showToast('Удалено успешно!', 'success');
        closeModal();
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        showToast('Ошибка: ' + error.message, 'error');
    }
}

// Fullscreen image
function openFullscreen(imageUrl, index) {
    const overlay = document.createElement('div');
    overlay.className = 'fullscreen-overlay';
    overlay.id = 'fullscreen-overlay';
    overlay.innerHTML = `
        <button class="fullscreen-close" onclick="closeFullscreen()">
            <i class="fas fa-times"></i>
        </button>
        <img src="${imageUrl}" alt="Full size">
    `;
    
    document.body.appendChild(overlay);
    
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeFullscreen();
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeFullscreen();
    });
}

function closeFullscreen() {
    const overlay = document.getElementById('fullscreen-overlay');
    if (overlay) overlay.remove();
}

// Tabs
async function switchTab(event, tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        content.style.display = 'none';
    });
    
    if (event && event.target) {
        const btn = event.target.closest('.tab-btn');
        if (btn) btn.classList.add('active');
    }
    
    const tabContent = document.getElementById(`tab-${tab}`);
    if (tabContent) {
        tabContent.classList.add('active');
        tabContent.style.display = 'block';
    }
    
    if (tab === 'history') {
        await loadImages('history', 'history-content');
    } else if (tab === 'favorites') {
        await loadImages('favorites', 'favorites-content');
    }
}

async function loadImages(tab, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Загрузка...</p></div>';
    
    try {
        const data = await api.getImages(tab, 1, 20);
        
        let items = [];
        if (data.results) items = data.results;
        else if (data.items) items = data.items;
        else if (Array.isArray(data)) items = data;
        
        if (items.length > 0) {
            container.innerHTML = `
                <div class="results-grid">
                    ${items.map(item => createResultCard(item)).join('')}
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <h3>Нет изображений</h3>
                    <p>${tab === 'history' ? 'Создайте первую генерацию' : 'Добавьте изображения в избранное'}</p>
                </div>
            `;
        }
    } catch (error) {
        container.innerHTML = `
            <div class="error-message show">
                <p>Ошибка загрузки: ${error.message}</p>
                <button class="btn btn-primary" onclick="loadImages('${tab}', '${containerId}')">Повторить</button>
            </div>
        `;
    }
}

// Analytics
async function loadAnalytics() {
    const start = document.getElementById('analytics-start')?.value;
    const end = document.getElementById('analytics-end')?.value;
    const granularity = document.getElementById('analytics-granularity')?.value;
    const container = document.getElementById('analytics-results');
    
    if (!container) return;
    container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    try {
        const data = await api.getAnalytics(start, end, granularity);
        
        container.innerHTML = `
            <div class="analytics-grid">
                <div class="stat-card">
                    <div class="stat-value">${(data.summary?.total_views || 0).toLocaleString()}</div>
                    <div class="stat-label">Просмотры</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(data.summary?.total_clicks || 0).toLocaleString()}</div>
                    <div class="stat-label">Клики</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${data.summary?.ctr || 0}%</div>
                    <div class="stat-label">CTR</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(data.summary?.conversions || 0).toLocaleString()}</div>
                    <div class="stat-label">Конверсии</div>
                </div>
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<div class="error-message show">Ошибка: ${error.message}</div>`;
    }
}

async function toggleFavorite(imageId) {
    try {
        await api.toggleFavorite(imageId);
        showToast('Статус избранного обновлен!', 'success');
    } catch (error) {
        showToast('Ошибка: ' + error.message, 'error');
    }
}

async function deleteGeneration(id) {
    if (!confirm('Удалить эту генерацию?')) return;
    
    try {
        await api.deleteImages([id]);
        showToast('Удалено успешно!', 'success');
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        showToast('Ошибка: ' + error.message, 'error');
    }
}

// Utilities
function showToast(message, type = 'success') {
    const existingToast = document.querySelector('.toast');
    if (existingToast) existingToast.remove();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function getDateToday() {
    return new Date().toISOString().split('T')[0];
}

function getDateDaysAgo(days) {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return date.toISOString().split('T')[0];
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('App initialized');
    
    router.addRoute('#/login', LoginPage);
    router.addRoute('#/register', RegisterPage);
    router.addRoute('#/dashboard', DashboardPage);
    
    document.addEventListener('submit', (e) => {
        if (e.target.id === 'login-form') handleLogin(e);
        if (e.target.id === 'register-form') handleRegister(e);
        if (e.target.id === 'generate-form') handleGenerate(e);
    });
    
    if (!window.location.hash) {
        window.location.hash = '#/login';
    }
});