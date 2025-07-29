import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { 
  FileText, 
  Star, 
  Clock, 
  DollarSign, 
  Zap, 
  Eye,
  ArrowLeft,
  Lightbulb
} from 'lucide-react';
import { GenerationResponse, SEORecommendations } from '../types/api';
import { articleApi } from '../services/api';

interface ArticleViewProps {
  article: GenerationResponse;
  onBack: () => void;
}

export const ArticleView: React.FC<ArticleViewProps> = ({ article, onBack }) => {
  const [recommendations, setRecommendations] = useState<SEORecommendations | null>(null);
  const [showRecommendations, setShowRecommendations] = useState(false);

  // Проверяем, что article существует
  if (!article) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onBack}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Назад
          </Button>
          <h1 className="text-2xl font-bold text-gray-900">Статья не найдена</h1>
        </div>
        <Card>
          <CardContent className="p-8">
            <div className="text-center text-muted-foreground">
              <p>Не удалось загрузить статью. Попробуйте еще раз.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Убеждаемся, что объект usage существует и все поля безопасны
  const safeUsage = article.usage || {
    id: '',
    article_id: article.article_id || '',
    model: article.model_used || 'unknown',
    prompt_tokens: 0,
    completion_tokens: 0,
    total_tokens: 0,
    cost_usd: '0.00',
    created_at: new Date().toISOString()
  };

  // Убеждаемся, что все поля статьи безопасны
  const safeArticle = {
    ...article,
    topic: article.topic || 'Без названия',
    thesis: article.thesis || '',
    style_examples: article.style_examples || '',
    character_count: article.character_count || 5000,
    keywords: article.keywords || [],
    structure: article.structure || '',
    article: article.article || '',
    seo_score: article.seo_score || 0,
    model_used: article.model_used || 'unknown',
    usage: safeUsage
  };

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const recs = await articleApi.getSEORecommendations(safeArticle.article_id);
        setRecommendations(recs);
      } catch (error) {
        console.error('Failed to fetch SEO recommendations:', error);
      }
    };

    fetchRecommendations();
  }, [safeArticle.article_id]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSEOScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600 bg-green-100';
    if (score >= 6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getSEOScoreText = (score: number) => {
    if (score >= 8) return 'Отличный';
    if (score >= 6) return 'Хороший';
    return 'Требует улучшения';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Заголовок с кнопкой назад */}
      <div className="flex items-center gap-4">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={onBack}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Назад
        </Button>
        <h1 className="text-2xl font-bold text-gray-900">{safeArticle.topic}</h1>
      </div>

      {/* Метрики статьи */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">SEO-оценка</p>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold">{safeArticle.seo_score.toFixed(1)}</span>
                  <Badge className={getSEOScoreColor(safeArticle.seo_score)}>
                    {getSEOScoreText(safeArticle.seo_score)}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Модель</p>
                <p className="text-lg font-semibold">{safeArticle.model_used}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Стоимость</p>
                <p className="text-lg font-semibold">${safeUsage.cost_usd}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Токены</p>
                <p className="text-lg font-semibold">{safeUsage.total_tokens}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* SEO рекомендации */}
      {recommendations && recommendations.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              SEO Рекомендации
            </CardTitle>
            <CardDescription>
              Советы по улучшению SEO-оптимизации статьи
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              onClick={() => setShowRecommendations(!showRecommendations)}
              className="mb-4"
            >
              {showRecommendations ? 'Скрыть' : 'Показать'} рекомендации
            </Button>
            
            {showRecommendations && (
              <ul className="space-y-2">
                {recommendations.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-primary font-semibold">•</span>
                    <span className="text-sm">{rec}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      )}

      {/* Ключевые слова */}
      <Card>
        <CardHeader>
          <CardTitle>Ключевые слова</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {safeArticle.keywords.map((keyword, index) => (
              <Badge key={index} variant="secondary">
                {keyword}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Тезисы */}
      <Card>
        <CardHeader>
          <CardTitle>Тезисы автора</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground whitespace-pre-wrap">{safeArticle.thesis}</p>
        </CardContent>
      </Card>

      {/* Структура статьи */}
      <Card>
        <CardHeader>
          <CardTitle>Структура статьи</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{safeArticle.structure}</ReactMarkdown>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Полная статья */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Готовая статья
          </CardTitle>
          <CardDescription>
            Полный текст сгенерированной SEO-статьи
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="prose prose-lg max-w-none">
            <ReactMarkdown>{safeArticle.article}</ReactMarkdown>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 