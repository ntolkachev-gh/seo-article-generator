export interface GenerationRequest {
  topic: string;
  thesis: string;
  model: string; // Изменено с union type на string для поддержки всех моделей
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

export interface GenerationResponse {
  article_id: string;
  topic: string;
  thesis: string;
  keywords: string[];
  structure: string;
  article: string;
  seo_score: number;
  model_used: string;
  usage: OpenAIUsage;
}

export interface Article {
  id: string;
  topic: string;
  thesis: string;
  keywords: string[];
  structure: string;
  article: string;
  seo_score: number;
  model_used: string;
  created_at: string;
}

export interface ArticleListItem {
  id: string;
  topic: string;
  seo_score: number;
  model_used: string;
  created_at: string;
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