class API {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
        localStorage.removeItem('userData');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            ...options.headers
        };

        // Не устанавливаем Content-Type для FormData
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const config = {
            ...options,
            headers
        };

        console.log('API Request:', url, config);

        try {
            const response = await fetch(url, config);
            console.log('API Response status:', response.status);
            
            // Проверяем на 401 (неавторизован)
            if (response.status === 401) {
                console.log('Unauthorized, redirecting to login');
                this.clearToken();
                window.location.hash = '#/login';
                throw new Error('Unauthorized');
            }

            // Проверяем есть ли тело ответа
            const contentType = response.headers.get('content-type');
            let data;
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
                console.log('API Response data:', data);
            } else {
                data = await response.text();
                console.log('API Response text:', data);
                data = { message: data };
            }

            if (!response.ok) {
                throw new Error(data.message || data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth endpoints
    async login(username, password) {
        try {
            console.log('Attempting login with:', { username });
            const response = await this.request('/auth/login/', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            console.log('Login response:', response);
            return response;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    async register(username, email, password, password2) {
        try {
            console.log('Attempting register with:', { username, email });
            const response = await this.request('/auth/register/', {
                method: 'POST',
                body: JSON.stringify({ username, email, password, password2 })
            });
            console.log('Register response:', response);
            return response;
        } catch (error) {
            console.error('Register error:', error);
            throw error;
        }
    }

    async logout() {
        try {
            await this.request('/auth/logout/', {
                method: 'POST',
                body: JSON.stringify({ refresh: localStorage.getItem('refreshToken') })
            });
        } catch (error) {
            console.log('Logout error (ignored):', error);
        } finally {
            this.clearToken();
        }
    }

    // Generation endpoint
    async generateContent(prompt, images = []) {
        const formData = new FormData();
        formData.append('prompt', prompt);
        
        if (images && images.length > 0) {
            images.forEach((image, index) => {
                formData.append('product_images', image);
            });
        }

        return fetch(`${this.baseURL}/api/generate/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`
            },
            body: formData
        }).then(async res => {
            const data = await res.json();
            if (!res.ok) throw new Error(data.message || 'Generation failed');
            return data;
        });
    }

    // Images endpoints
    async getImages(tab = 'history', page = 1, limit = 20) {
        return this.request(`/api/images/?tab=${tab}&page=${page}&limit=${limit}`);
    }

    async toggleFavorite(imageId) {
        return this.request(`/api/images/${imageId}/favorite/`, {
            method: 'PATCH'
        });
    }

    async deleteImages(ids) {
        return this.request('/api/images/', {
            method: 'DELETE',
            body: JSON.stringify({ ids })
        });
    }

    // Analytics endpoints
    async getAnalytics(startDate, endDate, granularity = 'day') {
        return this.request(
            `/api/analytics/metrics/?start_date=${startDate}&end_date=${endDate}&granularity=${granularity}`
        );
    }
}

const api = new API();