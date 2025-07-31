import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Loader2, Sparkles, Zap, Star, Crown, CheckCircle } from 'lucide-react';
import { GenerationRequest, GenerationResponse, ModelInfo, AsyncGenerationResponse } from '../types/api';
import { articleApi } from '../services/api';

interface ArticleGenerationFormProps {
  onArticleGenerated: (article: GenerationResponse) => void;
  onAsyncGenerationStarted?: (response: AsyncGenerationResponse) => void;
}

export const ArticleGenerationForm: React.FC<ArticleGenerationFormProps> = ({ 
  onArticleGenerated, 
  onAsyncGenerationStarted 
}) => {
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
  const [serviceStatus, setServiceStatus] = useState<{
    services?: {
      openai?: boolean;
      anthropic?: boolean;
    };
  } | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    loadModels();
    checkServiceStatus();
  }, []);

  const checkServiceStatus = async () => {
    try {
      const healthData = await articleApi.healthCheck();
      setServiceStatus(healthData);
      
      // Показываем предупреждение, если нет доступных сервисов
      if (healthData.services && (!healthData.services.openai && !healthData.services.anthropic)) {
        setError('⚠️ Внимание: API ключи не настроены. Генерация статей недоступна. Обратитесь к администратору.');
      }
    } catch (err) {
      console.error('Failed to check service status:', err);
    }
  };

  const loadModels = async () => {
    try {
      const response = await articleApi.getAvailableModels();
      setModels(response.models);
      
      // Если нет доступных моделей, показываем предупреждение
      if (response.models.length === 0) {
        setError('⚠️ Нет доступных моделей ИИ. Проверьте настройки API ключей.');
      }
    } catch (err) {
      console.error('Failed to load models:', err);
      setError('⚠️ Не удалось загрузить модели ИИ. Проверьте подключение к серверу.');
      
      // Fallback модели
      setModels([
        { id: 'gpt-4o-mini', name: 'GPT-4o Mini (Недоступно)', description: 'Требует настройки API ключей', category: 'fallback', pricing: { input: 0, output: 0 } },
        { id: 'claude-3-5-haiku-20241022', name: 'Claude 3.5 Haiku (Недоступно)', description: 'Требует настройки API ключей', category: 'fallback', pricing: { input: 0, output: 0 } },
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
    setShowSuccess(false);

    try {
      // Отправляем запрос на асинхронную генерацию
      const response = await articleApi.generateArticleAsync(formData);
      
      if (onAsyncGenerationStarted) {
        onAsyncGenerationStarted(response);
      }
      
      // Показываем сообщение об успешном запуске генерации
      setShowSuccess(true);
      
      // Очищаем форму после успешной отправки
      setFormData({
        topic: '',
        thesis: '',
        style_examples: '',
        character_count: 5000,
        model: 'gpt-4o-mini'
      });
      
      // Скрываем сообщение об успехе через 5 секунд
      setTimeout(() => setShowSuccess(false), 5000);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Произошла ошибка при отправке запроса');
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
          Создание SEO-статьи
        </CardTitle>
        <CardDescription>
          Заполните форму ниже, чтобы запустить генерацию SEO-статьи
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
            <p className="text-xs text-gray-600">
              ИИ будет строго следить за указанной длиной (±200 знаков)
            </p>
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
                <SelectItem value="2000">2 000 знаков (краткая заметка)</SelectItem>
                <SelectItem value="3000">3 000 знаков (короткая статья)</SelectItem>
                <SelectItem value="5000">5 000 знаков (средняя статья)</SelectItem>
                <SelectItem value="7000">7 000 знаков (подробная статья)</SelectItem>
                <SelectItem value="10000">10 000 знаков (развернутая статья)</SelectItem>
                <SelectItem value="15000">15 000 знаков (длинная статья)</SelectItem>
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

          {showSuccess && (
            <div className="p-4 text-sm text-green-600 bg-green-50 border border-green-200 rounded-md flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              <div>
                <div className="font-medium">Генерация запущена!</div>
                <div>Статья генерируется в фоне. Проверьте статус в разделе "История статей".</div>
              </div>
            </div>
          )}

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
                Запускаю генерацию...
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