export interface GenerationRequest {
  topic: string;
  thesis: string;
  style_examples?: string;
  character_count?: number;
  model: string;
}

export interface OpenAIUsage {
  id: string;
  article_id: string;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  cost_usd: string;
  created_at: string;
}

// Типы статусов статей
export type ArticleStatus = 'pending' | 'generating' | 'completed' | 'failed';

export interface GenerationResponse {
  article_id: string;
  topic: string;
  thesis: string;
  style_examples?: string;
  character_count?: number;
  keywords?: string[] | null;  // Может быть null до завершения генерации
  structure?: string | null;   // Может быть null до завершения генерации
  article?: string | null;     // Может быть null до завершения генерации
  seo_score?: number | null;   // Может быть null до завершения генерации
  model_used: string;
  status: ArticleStatus;       // Новое поле статуса
  error_message?: string | null; // Новое поле для сообщений об ошибках
  usage?: OpenAIUsage | null;  // Может быть null до завершения генерации
}

export interface Article {
  id: string;
  topic: string;
  thesis: string;
  style_examples?: string;
  character_count?: number;
  keywords?: string[] | null;  // Может быть null до завершения генерации
  structure?: string | null;   // Может быть null до завершения генерации
  article?: string | null;     // Может быть null до завершения генерации
  seo_score?: number | null;   // Может быть null до завершения генерации
  model_used: string;
  status: ArticleStatus;       // Новое поле статуса
  error_message?: string | null; // Новое поле для сообщений об ошибках
  created_at: string;
  updated_at?: string | null;  // Новое поле времени обновления
}

export interface ArticleListItem {
  id: string;
  topic: string;
  thesis: string;
  style_examples?: string;
  character_count?: number;
  seo_score?: number | null;   // Может быть null до завершения генерации
  model_used: string;
  status: ArticleStatus;       // Новое поле статуса
  error_message?: string | null; // Новое поле для сообщений об ошибках
  created_at: string;
  updated_at?: string | null;  // Новое поле времени обновления
}

// Новые типы для асинхронной генерации
export interface AsyncGenerationResponse {
  article_id: string;
  status: ArticleStatus;
  message: string;
  estimated_time?: number;     // Примерное время генерации в секундах
}

export interface ArticleStatusResponse {
  article_id: string;
  status: ArticleStatus;
  progress?: string | null;    // Описание текущего этапа
  error_message?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface SEORecommendations {
  article_id: string;
  seo_score: number;
  recommendations: string[];
}

// Новые типы для моделей
export interface ModelInfo {
  id: string;
  name: string;
  description: string;
  category: string;
  pricing: {
    input: number;
    output: number;
  };
}

export interface ModelsResponse {
  models: ModelInfo[];
}

export interface HealthResponse {
  status: string;
  message: string;
  version: string;
  database: boolean;
  services: boolean;
} 