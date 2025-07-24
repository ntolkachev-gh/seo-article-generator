import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Loader2, Sparkles } from 'lucide-react';
import { GenerationRequest, GenerationResponse } from '../types/api';
import { articleApi } from '../services/api';

interface ArticleGenerationFormProps {
  onArticleGenerated: (article: GenerationResponse) => void;
}

export const ArticleGenerationForm: React.FC<ArticleGenerationFormProps> = ({ onArticleGenerated }) => {
  const [formData, setFormData] = useState<GenerationRequest>({
    topic: '',
    thesis: '',
    model: 'gpt-3.5-turbo'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.topic.trim() || !formData.thesis.trim()) {
      setError('Пожалуйста, заполните все поля');
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
        model: 'gpt-3.5-turbo'
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Произошла ошибка при генерации статьи');
    } finally {
      setIsLoading(false);
    }
  };

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
              placeholder="Например: Преимущества использования React в 2024 году"
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
            <label htmlFor="model" className="text-sm font-medium">
              Модель OpenAI
            </label>
            <Select
              value={formData.model}
              onValueChange={(value: 'gpt-3.5-turbo' | 'gpt-4') => 
                setFormData({ ...formData, model: value })
              }
              disabled={isLoading}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gpt-3.5-turbo">
                  GPT-3.5 Turbo (быстрее, дешевле)
                </SelectItem>
                <SelectItem value="gpt-4">
                  GPT-4 (качественнее, дороже)
                </SelectItem>
              </SelectContent>
            </Select>
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