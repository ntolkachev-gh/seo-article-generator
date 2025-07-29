import axios from 'axios';
import { GenerationRequest, GenerationResponse, Article, ArticleListItem, SEORecommendations, ModelsResponse } from '../types/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
  getArticle: async (articleId: string): Promise<Article> => {
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
  healthCheck: async (): Promise<{ status: string; message: string }> => {
    const response = await api.get('/api/health');
    return response.data;
  }
};

export default api; 