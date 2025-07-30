import React, { useState, useEffect } from 'react';
import { ArticleGenerationForm } from './components/ArticleGenerationForm';
import { ArticleView } from './components/ArticleView';
import { ArticleHistory } from './components/ArticleHistory';
import { Button } from './components/ui/button';
import { Card, CardContent } from './components/ui/card';
import { 
  Sparkles, 
  History, 
  FileText,
  Github,
  Heart,
  CheckCircle,
  Clock
} from 'lucide-react';
import { GenerationResponse, Article, HealthResponse, AsyncGenerationResponse } from './types/api';
import { articleApi } from './services/api';
import './index.css';

type ViewMode = 'form' | 'article' | 'history';

function App() {
  const [currentView, setCurrentView] = useState<ViewMode>('form');
  const [currentArticle, setCurrentArticle] = useState<GenerationResponse | null>(null);
  const [viewingArticleId, setViewingArticleId] = useState<string | null>(null);
  const [asyncGenerationNotification, setAsyncGenerationNotification] = useState<{
    show: boolean;
    message: string;
    articleId?: string;
  }>({ show: false, message: '' });

  // Load app version on component mount
  useEffect(() => {
    const loadVersion = async () => {
      try {
        const healthData: HealthResponse = await articleApi.healthCheck();
        const versionElement = document.getElementById('app-version');
        if (versionElement) {
          versionElement.textContent = `v${healthData.version}`;
        }
        
        // Принудительно обновляем кэш браузера
        if ('caches' in window) {
          try {
            const cacheNames = await caches.keys();
            await Promise.all(
              cacheNames.map(cacheName => caches.delete(cacheName))
            );
            console.log('Browser cache cleared');
          } catch (error) {
            console.warn('Failed to clear cache:', error);
          }
        }
      } catch (error) {
        console.error('Failed to load version:', error);
        // Keep default version
      }
    };

    loadVersion();
  }, []);

  const handleArticleGenerated = (article: GenerationResponse) => {
    setCurrentArticle(article);
    setCurrentView('article');
  };

  const handleAsyncGenerationStarted = (response: AsyncGenerationResponse) => {
    // Показываем уведомление об успешном запуске генерации
    setAsyncGenerationNotification({
      show: true,
      message: `Генерация статьи "${response.article_id}" запущена! Проверьте прогресс в истории статей.`,
      articleId: response.article_id
    });

    // Переходим к истории статей, чтобы пользователь мог следить за прогрессом
    setCurrentView('history');

    // Скрываем уведомление через 10 секунд
    setTimeout(() => {
      setAsyncGenerationNotification({ show: false, message: '' });
    }, 10000);
  };

  const handleViewHistoryArticle = async (articleId: string) => {
    try {
      console.log('Загружаем статью с ID:', articleId);
      
      const article = await articleApi.getArticle(articleId);
      console.log('Статья загружена с сервера:', article);
      
      // Проверяем, что все необходимые поля существуют
      if (!article) {
        throw new Error('Статья не найдена');
      }
      
      // Дополнительная проверка критических полей
      if (!article.article_id || !article.topic) {
        throw new Error('Статья содержит некорректные данные');
      }

      // Проверяем статус статьи
      if (article.status !== 'completed') {
        // Если статья не завершена, показываем сообщение
        if (article.status === 'pending') {
          alert('Статья ожидает начала генерации. Пожалуйста, подождите.');
        } else if (article.status === 'generating') {
          alert('Статья генерируется. Пожалуйста, подождите завершения процесса.');
        } else if (article.status === 'failed') {
          alert(`Ошибка при генерации статьи: ${article.error_message || 'Неизвестная ошибка'}`);
        }
        return;
      }
      
      console.log('Отображаем статью:', article);
      console.log('App: article.usage:', article.usage);
      console.log('App: article.usage?.model:', article.usage?.model);
      console.log('App: article.model_used:', article.model_used);
      
      // Дополнительная проверка usage объекта
      if (!article.usage) {
        console.warn('App: Usage объект отсутствует, создаем дефолтный');
        article.usage = {
          id: '',
          article_id: article.article_id || '',
          model: article.model_used || 'unknown',
          prompt_tokens: 0,
          completion_tokens: 0,
          total_tokens: 0,
          cost_usd: '0.00',
          created_at: article.created_at || new Date().toISOString()
        };
      }
      
      // Проверяем, что usage.model существует
      if (!article.usage.model) {
        console.warn('App: Usage.model отсутствует, устанавливаем дефолтное значение');
        article.usage.model = article.model_used || 'unknown';
      }
      
      console.log('App: Финальный article.usage:', article.usage);
      console.log('App: Финальный article.usage.model:', article.usage.model);
      
      setCurrentArticle(article);
      setCurrentView('article');
    } catch (error) {
      console.error('Общая ошибка при загрузке статьи:', error);
      alert('Не удалось загрузить статью');
    }
  };

  const handleBackToForm = () => {
    setCurrentView('form');
    setCurrentArticle(null);
    setViewingArticleId(null);
  };

  const handleBackToHistory = () => {
    setCurrentView('history');
    setCurrentArticle(null);
    setViewingArticleId(null);
  };

  const dismissNotification = () => {
    setAsyncGenerationNotification({ show: false, message: '' });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Уведомление об асинхронной генерации */}
      {asyncGenerationNotification.show && (
        <div className="bg-green-500 text-white px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            <span className="text-sm font-medium">{asyncGenerationNotification.message}</span>
          </div>
          <button
            onClick={dismissNotification}
            className="text-white hover:text-green-200 ml-4"
          >
            ✕
          </button>
        </div>
      )}

      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="px-2 sm:px-4 md:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 py-4 sm:py-0 sm:h-16">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="p-1.5 sm:p-2 bg-primary rounded-lg">
                <FileText className="h-5 w-5 sm:h-6 sm:w-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg sm:text-xl font-bold text-gray-900">
                  SEO Article Generator
                </h1>
                <p className="text-xs sm:text-sm text-gray-600">
                  Генерация качественных SEO-статей с помощью ИИ
                </p>
              </div>
            </div>

            <nav className="flex items-center gap-1 sm:gap-2 w-full sm:w-auto">
              <Button
                variant={currentView === 'form' ? 'default' : 'ghost'}
                onClick={handleBackToForm}
                className="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm px-2 sm:px-3 py-1.5 sm:py-2"
              >
                <Sparkles className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">Создать статью</span>
                <span className="sm:hidden">Создать</span>
              </Button>
              
              <Button
                variant={currentView === 'history' ? 'default' : 'ghost'}
                onClick={() => setCurrentView('history')}
                className="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm px-2 sm:px-3 py-1.5 sm:py-2"
              >
                <History className="h-3 w-3 sm:h-4 sm:w-4" />
                История
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 px-0 sm:px-1 md:px-2 py-1 sm:py-2 md:py-3">
        {currentView === 'form' && (
          <div className="space-y-2 sm:space-y-3 md:space-y-4">
            <div className="text-center">
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-1 sm:mb-2 md:mb-4">
                Создайте качественную SEO-статью за минуты
              </h2>
              <p className="text-sm sm:text-base md:text-lg text-gray-600 max-w-2xl mx-auto px-0 sm:px-1">
                Используйте мощь искусственного интеллекта для генерации 
                оптимизированных статей с автоматическим анализом ключевых слов 
                и SEO-оценкой
              </p>
            </div>
            
            <ArticleGenerationForm 
              onArticleGenerated={handleArticleGenerated}
              onAsyncGenerationStarted={handleAsyncGenerationStarted}
            />
            
            {/* Features */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 md:gap-6 mt-4 sm:mt-6 md:mt-8">
              <Card>
                <CardContent className="p-4 sm:p-6 text-center">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3 sm:mb-4">
                    <Sparkles className="h-5 w-5 sm:h-6 sm:w-6 text-blue-600" />
                  </div>
                  <h3 className="font-semibold mb-2 text-sm sm:text-base">ИИ-генерация</h3>
                  <p className="text-xs sm:text-sm text-gray-600">
                    Используем GPT-4 и Claude для создания качественного контента
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4 sm:p-6 text-center">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3 sm:mb-4">
                    <FileText className="h-5 w-5 sm:h-6 sm:w-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold mb-2 text-sm sm:text-base">SEO-оптимизация</h3>
                  <p className="text-xs sm:text-sm text-gray-600">
                    Автоматический анализ ключевых слов и оценка SEO-качества
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4 sm:p-6 text-center">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3 sm:mb-4">
                    <Clock className="h-5 w-5 sm:h-6 sm:w-6 text-purple-600" />
                  </div>
                  <h3 className="font-semibold mb-2 text-sm sm:text-base">Асинхронная генерация</h3>
                  <p className="text-xs sm:text-sm text-gray-600">
                    Запускайте генерацию в фоне и следите за прогрессом в реальном времени
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {currentView === 'article' && currentArticle && (
          <ArticleView 
            article={currentArticle} 
            onBack={handleBackToForm}
          />
        )}

        {currentView === 'history' && (
          <ArticleHistory onViewArticle={handleViewHistoryArticle} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto py-2 sm:py-3 md:py-4">
        <div className="px-0 sm:px-1 md:px-2">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-1 sm:gap-2 text-xs sm:text-sm text-gray-600">
            <div className="flex items-center gap-1 sm:gap-2">
              <span>Создано с</span>
              <Heart className="h-3 w-3 sm:h-4 sm:w-4 text-red-500" />
              <span>используя FastAPI и React</span>
            </div>
            <div>
              <span id="app-version">v0.1.0</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App; 