import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  History, 
  Eye, 
  Trash2, 
  Star, 
  Calendar,
  Zap,
  RefreshCw,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  Loader2
} from 'lucide-react';
import { ArticleListItem, ArticleStatus } from '../types/api';
import { articleApi } from '../services/api';

interface ArticleHistoryProps {
  onViewArticle: (articleId: string) => void;
}

export const ArticleHistory: React.FC<ArticleHistoryProps> = ({ onViewArticle }) => {
  const [articles, setArticles] = useState<ArticleListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchArticles = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await articleApi.getArticles();
      setArticles(data);
    } catch (err: any) {
      console.error('Error fetching articles:', err);
      setError('Не удалось загрузить статьи. Проверьте подключение к серверу.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
    
    // Автоматическое обновление каждые 5 секунд для отслеживания статуса генерации
    const interval = setInterval(() => {
      // Обновляем только если есть статьи в процессе генерации
      const hasGeneratingArticles = articles.some(article => 
        article.status === 'pending' || article.status === 'generating'
      );
      
      if (hasGeneratingArticles) {
        fetchArticles();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [articles]);

  const handleDeleteArticle = async (articleId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!window.confirm('Вы уверены, что хотите удалить эту статью? Это действие нельзя отменить.')) {
      return;
    }

    try {
      await articleApi.deleteArticle(articleId);
      setArticles(articles.filter(article => article.id !== articleId));
    } catch (err: any) {
      console.error('Error deleting article:', err);
      alert('Не удалось удалить статью. Попробуйте еще раз.');
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'Дата неизвестна';
    }
  };

  const getSEOScoreColor = (score: number | null | undefined) => {
    if (!score) return 'text-gray-600 bg-gray-100 border-gray-200';
    if (score >= 8) return 'text-green-600 bg-green-100 border-green-200';
    if (score >= 6) return 'text-yellow-600 bg-yellow-100 border-yellow-200';
    return 'text-red-600 bg-red-100 border-red-200';
  };

  const getSEOScoreText = (score: number | null | undefined) => {
    if (!score) return 'Не рассчитан';
    if (score >= 8) return 'Отличный';
    if (score >= 6) return 'Хороший';
    return 'Требует доработки';
  };

  const getStatusInfo = (status: ArticleStatus) => {
    switch (status) {
      case 'pending':
        return {
          icon: <Clock className="h-4 w-4" />,
          text: 'Ожидает генерации',
          color: 'text-blue-600 bg-blue-100 border-blue-200'
        };
      case 'generating':
        return {
          icon: <Loader2 className="h-4 w-4 animate-spin" />,
          text: 'Генерируется...',
          color: 'text-orange-600 bg-orange-100 border-orange-200'
        };
      case 'completed':
        return {
          icon: <CheckCircle className="h-4 w-4" />,
          text: 'Завершена',
          color: 'text-green-600 bg-green-100 border-green-200'
        };
      case 'failed':
        return {
          icon: <XCircle className="h-4 w-4" />,
          text: 'Ошибка',
          color: 'text-red-600 bg-red-100 border-red-200'
        };
      default:
        return {
          icon: <Clock className="h-4 w-4" />,
          text: 'Неизвестно',
          color: 'text-gray-600 bg-gray-100 border-gray-200'
        };
    }
  };

  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const canViewArticle = (article: ArticleListItem) => {
    return article.status === 'completed';
  };

  if (isLoading) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-8">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin mr-2" />
            Загружаю статьи...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-8">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchArticles} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Попробовать снова
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold">История статей</h1>
          {articles.length > 0 && (
            <Badge variant="secondary" className="ml-2">
              {articles.length} {articles.length === 1 ? 'статья' : articles.length < 5 ? 'статьи' : 'статей'}
            </Badge>
          )}
        </div>
        <Button onClick={fetchArticles} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Обновить
        </Button>
      </div>

      {articles.length === 0 ? (
        <Card>
          <CardContent className="p-8">
            <div className="text-center text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg mb-2">Пока нет сгенерированных статей</p>
              <p>Создайте свою первую SEO-статью, чтобы увидеть её здесь</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {articles.map((article) => {
            const statusInfo = getStatusInfo(article.status);
            const canView = canViewArticle(article);
            
            return (
              <Card 
                key={article.id} 
                className={`hover:shadow-md transition-shadow border-l-4 border-l-primary/20 ${
                  canView ? 'cursor-pointer' : ''
                }`}
                onClick={canView ? () => onViewArticle(article.id) : undefined}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 flex-1">
                          {article.topic}
                        </h3>
                        <Badge className={`${statusInfo.color} border flex items-center gap-1 shrink-0`}>
                          {statusInfo.icon}
                          {statusInfo.text}
                        </Badge>
                      </div>
                      
                      {article.thesis && (
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                          {truncateText(article.thesis, 150)}
                        </p>
                      )}
                      
                      {article.error_message && article.status === 'failed' && (
                        <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded-md">
                          <p className="text-sm text-red-600">
                            <strong>Ошибка:</strong> {article.error_message}
                          </p>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {formatDate(article.created_at)}
                        </div>
                        
                        <div className="flex items-center gap-1">
                          <Zap className="h-4 w-4" />
                          {article.model_used || 'unknown'}
                        </div>

                        {article.character_count && (
                          <div className="flex items-center gap-1">
                            <FileText className="h-4 w-4" />
                            {article.character_count.toLocaleString()} знаков
                          </div>
                        )}
                      </div>

                      {article.status === 'completed' && article.seo_score !== null && (
                        <div className="flex items-center gap-2">
                          <Star className="h-4 w-4 text-primary" />
                          <span className="text-sm font-medium">SEO-оценка:</span>
                          <Badge className={`${getSEOScoreColor(article.seo_score)} border`}>
                            {article.seo_score.toFixed(1)} - {getSEOScoreText(article.seo_score)}
                          </Badge>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      {canView && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onViewArticle(article.id);
                          }}
                          className="flex items-center gap-1"
                        >
                          <Eye className="h-4 w-4" />
                          Посмотреть
                        </Button>
                      )}
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => handleDeleteArticle(article.id, e)}
                        className="flex items-center gap-1 text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                        Удалить
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}; 