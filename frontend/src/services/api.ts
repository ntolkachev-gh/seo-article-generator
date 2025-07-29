import axios from 'axios';
import { GenerationRequest, GenerationResponse, Article, ArticleListItem, SEORecommendations, ModelsResponse, HealthResponse } from '../types/api';

// Определяем URL API в зависимости от окружения
const getApiBaseUrl = () => {
  // Если есть переменная окружения, используем её
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Если мы в продакшене (Heroku), используем продакшен URL
  if (window.location.hostname.includes('herokuapp.com') || 
      window.location.hostname.includes('vercel.app')) {
    return 'https://seo-article-generator-app-8a9fa9a58cbb.herokuapp.com';
  }
  
  // По умолчанию используем localhost
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

console.log('API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 секунд таймаут
});

// Добавляем перехватчик для логирования запросов
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Добавляем перехватчик для логирования ответов
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.response?.data, error.config?.url);
    return Promise.reject(error);
  }
);

export const articleApi = {
  // Генерация новой статьи
  generateArticle: async (data: GenerationRequest): Promise<GenerationResponse> => {
    const response = await api.post('/api/articles/generate', data);
    return response.data;
  },

  // Получение всех статей
  getArticles: async (skip = 0, limit = 100): Promise<ArticleListItem[]> => {
    const response = await api.get('/api/articles', {
      params: { skip, limit }
    });
    return response.data;
  },

  // Получение статьи по ID
  getArticle: async (articleId: string): Promise<GenerationResponse> => {
    const response = await api.get(`/api/articles/${articleId}`);
    return response.data;
  },

  // Удаление статьи
  deleteArticle: async (articleId: string): Promise<void> => {
    await api.delete(`/api/articles/${articleId}`);
  },

  // Получение SEO рекомендаций
  getSEORecommendations: async (articleId: string): Promise<SEORecommendations> => {
    const response = await api.get(`/api/articles/${articleId}/seo-recommendations`);
    return response.data;
  },

  // Получение списка доступных моделей
  getAvailableModels: async (): Promise<ModelsResponse> => {
    const response = await api.get('/api/models');
    return response.data;
  },

  // Проверка здоровья API
  healthCheck: async (): Promise<HealthResponse> => {
    const response = await api.get('/api/health');
    return response.data;
  }
};

export default api; 