class Router {
    constructor() {
        this.routes = {};
        this.currentHash = null;
        
        window.addEventListener('hashchange', () => this.handleRoute());
        window.addEventListener('load', () => this.handleRoute());
    }

    addRoute(hash, component) {
        this.routes[hash] = component;
    }

    async handleRoute() {
        const hash = window.location.hash || '#/login';
        
        console.log('Router: handling route:', hash);
        
        // Предотвращаем повторную загрузку той же страницы
        if (this.currentHash === hash) {
            console.log('Router: same hash, skipping');
            return;
        }
        
        this.currentHash = hash;
        
        const component = this.routes[hash];
        
        if (!component) {
            console.log('Router: component not found, redirecting to login');
            window.location.hash = '#/login';
            return;
        }

        // Проверка аутентификации
        const token = localStorage.getItem('token');
        const isAuthPage = hash === '#/login' || hash === '#/register';
        
        console.log('Router: token exists:', !!token, 'isAuthPage:', isAuthPage);
        
        if (!isAuthPage && !token) {
            console.log('Router: not authenticated, redirecting to login');
            window.location.hash = '#/login';
            return;
        }

        if (isAuthPage && token) {
            console.log('Router: already authenticated, redirecting to dashboard');
            window.location.hash = '#/dashboard';
            return;
        }

        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.classList.remove('hidden');
        }
        
        try {
            const app = document.getElementById('app');
            const content = await component();
            app.innerHTML = content;
            console.log('Router: page loaded successfully');
        } catch (error) {
            console.error('Router: error loading page:', error);
            const app = document.getElementById('app');
            app.innerHTML = `
                <div class="auth-container">
                    <div class="auth-card">
                        <h1>Ошибка загрузки</h1>
                        <p>${error.message}</p>
                        <button class="btn btn-primary" onclick="window.location.hash='#/login'">
                            Вернуться на страницу входа
                        </button>
                    </div>
                </div>
            `;
        } finally {
            if (loadingScreen) {
                loadingScreen.classList.add('hidden');
            }
        }
    }
}

const router = new Router();