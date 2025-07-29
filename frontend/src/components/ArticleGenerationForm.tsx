import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Loader2, Sparkles, Zap, Star, Crown } from 'lucide-react';
import { GenerationRequest, GenerationResponse, ModelInfo } from '../types/api';
import { articleApi } from '../services/api';

interface ArticleGenerationFormProps {
  onArticleGenerated: (article: GenerationResponse) => void;
}

export const ArticleGenerationForm: React.FC<ArticleGenerationFormProps> = ({ onArticleGenerated }) => {
  const [formData, setFormData] = useState<GenerationRequest>({
    topic: '',
    thesis: '',
    style_examples: '',
    character_count: 5000,
    model: 'gpt-4o-mini'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [modelsLoading, setModelsLoading] = useState(true);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await articleApi.getAvailableModels();
      setModels(response.models);
    } catch (err) {
      console.error('Failed to load models:', err);
      // Fallback to basic models
      setModels([
        // Fast and cost-effective
        { id: 'gpt-4o-mini', name: 'GPT-4o Mini', description: 'Самый быстрый и дешевый', category: 'fast', pricing: { input: 0.00015, output: 0.0006 } },
        { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Быстрый и экономичный', category: 'fast', pricing: { input: 0.0015, output: 0.002 } },
        { id: 'claude-3-5-haiku-20241022', name: 'Claude 3.5 Haiku', description: 'Быстрый и дешевый', category: 'fast', pricing: { input: 0.00025, output: 0.00125 } },
        
        // Balanced
        { id: 'gpt-4o', name: 'GPT-4o', description: 'Оптимальное качество и скорость', category: 'balanced', pricing: { input: 0.005, output: 0.015 } },
        { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', description: 'Высокое качество', category: 'balanced', pricing: { input: 0.01, output: 0.03 } },
        { id: 'claude-3-5-sonnet-20241022', name: 'Claude 3.5 Sonnet', description: 'Сбалансированное качество', category: 'balanced', pricing: { input: 0.003, output: 0.015 } },
        
        // High quality
        { id: 'gpt-4', name: 'GPT-4', description: 'Максимальное качество', category: 'quality', pricing: { input: 0.03, output: 0.06 } },
        { id: 'claude-3-sonnet-20240229', name: 'Claude 3 Sonnet', description: 'Альтернатива GPT-4', category: 'quality', pricing: { input: 0.003, output: 0.015 } },
        
        // Premium
        { id: 'claude-3-opus-20240229', name: 'Claude 3 Opus', description: 'Премиум качество', category: 'premium', pricing: { input: 0.015, output: 0.075 } },
        { id: 'gpt-4-32k', name: 'GPT-4 32K', description: 'Длинные контексты', category: 'premium', pricing: { input: 0.06, output: 0.12 } },
      ]);
    } finally {
      setModelsLoading(false);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'fast':
        return <Zap className="h-4 w-4 text-green-500" />;
      case 'balanced':
        return <Sparkles className="h-4 w-4 text-blue-500" />;
      case 'quality':
        return <Star className="h-4 w-4 text-yellow-500" />;
      case 'premium':
        return <Crown className="h-4 w-4 text-purple-500" />;
      default:
        return <Sparkles className="h-4 w-4" />;
    }
  };

  const getCategoryName = (category: string) => {
    switch (category) {
      case 'fast':
        return 'Быстрые';
      case 'balanced':
        return 'Сбалансированные';
      case 'quality':
        return 'Высокое качество';
      case 'premium':
        return 'Премиум';
      default:
        return category;
    }
  };

  const formatPrice = (price: number) => {
    return `$${(price * 1000).toFixed(2)}/1K токенов`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.topic.trim() || !formData.thesis.trim() || !formData.style_examples?.trim()) {
      setError('Пожалуйста, заполните все обязательные поля');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await articleApi.generateArticle(formData);
      onArticleGenerated(response);
      
      // Очищаем форму после успешной генерации
      setFormData({
        topic: '',
        thesis: '',
        style_examples: '',
        character_count: 5000,
        model: 'gpt-4o-mini'
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Произошла ошибка при генерации статьи');
    } finally {
      setIsLoading(false);
    }
  };

  // Группируем модели по категориям
  const groupedModels = models.reduce((acc, model) => {
    if (!acc[model.category]) {
      acc[model.category] = [];
    }
    acc[model.category].push(model);
    return acc;
  }, {} as Record<string, ModelInfo[]>);

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-primary" />
          Генерация SEO-статьи
        </CardTitle>
        <CardDescription>
          Заполните форму ниже, чтобы сгенерировать качественную SEO-статью с помощью ИИ
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="topic" className="text-sm font-medium">
              Тема статьи *
            </label>
            <Input
              id="topic"
              placeholder="Например: Как похудеть без диет за 30 дней"
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="thesis" className="text-sm font-medium">
              Тезисы и ключевые идеи *
            </label>
            <Textarea
              id="thesis"
              placeholder="Опишите основные идеи, которые должны быть раскрыты в статье..."
              value={formData.thesis}
              onChange={(e) => setFormData({ ...formData, thesis: e.target.value })}
              disabled={isLoading}
              className="min-h-[120px]"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="style_examples" className="text-sm font-medium">
              Примеры стиля письма *
            </label>
            <Textarea
              id="style_examples"
              placeholder="Вставьте примеры текстов в том стиле, в котором должна быть написана статья. Это поможет ИИ понять нужный тон и манеру изложения..."
              value={formData.style_examples}
              onChange={(e) => setFormData({ ...formData, style_examples: e.target.value })}
              disabled={isLoading}
              className="min-h-[150px]"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="character_count" className="text-sm font-medium">
              Размер статьи (знаков)
            </label>
            <Select
              value={formData.character_count?.toString()}
              onValueChange={(value: string) => 
                setFormData({ ...formData, character_count: parseInt(value) })
              }
              disabled={isLoading}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="3000">3 000 знаков (короткая)</SelectItem>
                <SelectItem value="5000">5 000 знаков (средняя)</SelectItem>
                <SelectItem value="7000">7 000 знаков (длинная)</SelectItem>
                <SelectItem value="10000">10 000 знаков (очень длинная)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label htmlFor="model" className="text-sm font-medium">
              Модель ИИ
            </label>
            {modelsLoading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Загрузка моделей...
              </div>
            ) : (
              <Select
                value={formData.model}
                onValueChange={(value: string) => 
                  setFormData({ ...formData, model: value })
                }
                disabled={isLoading}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(groupedModels).map(([category, categoryModels]) => (
                    <div key={category}>
                      <div className="px-2 py-1.5 text-sm font-semibold text-muted-foreground flex items-center gap-2">
                        {getCategoryIcon(category)}
                        {getCategoryName(category)}
                      </div>
                      {categoryModels.map((model) => (
                        <SelectItem key={model.id} value={model.id}>
                          <div className="flex flex-col">
                            <div className="font-medium">{model.name}</div>
                            <div className="text-xs text-muted-foreground">
                              {model.description} • {formatPrice(model.pricing.input)}
                            </div>
                          </div>
                        </SelectItem>
                      ))}
                    </div>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          {error && (
            <div className="p-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
              {error}
            </div>
          )}

          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading}
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Генерирую статью...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Сгенерировать статью
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}; 