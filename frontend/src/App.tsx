import React, { useState } from 'react';
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
  Heart
} from 'lucide-react';
import { GenerationResponse, Article } from './types/api';
import { articleApi } from './services/api';
import './index.css';

type ViewMode = 'form' | 'article' | 'history';

function App() {
  const [currentView, setCurrentView] = useState<ViewMode>('form');
  const [currentArticle, setCurrentArticle] = useState<GenerationResponse | null>(null);
  const [viewingArticleId, setViewingArticleId] = useState<string | null>(null);

  const handleArticleGenerated = (article: GenerationResponse) => {
    setCurrentArticle(article);
    setCurrentView('article');
  };

  const handleViewHistoryArticle = async (articleId: string) => {
    try {
      const article = await articleApi.getArticle(articleId);
      // Преобразуем Article в GenerationResponse для совместимости
      const generationResponse: GenerationResponse = {
        article_id: article.id,
        topic: article.topic,
        thesis: article.thesis,
        keywords: article.keywords,
        structure: article.structure,
        article: article.article,
        seo_score: article.seo_score,
        model_used: article.model_used,
        usage: {
          id: '',
          article_id: article.id,
          model: article.model_used,
          prompt_tokens: 0,
          completion_tokens: 0,
          total_tokens: 0,
          cost_usd: '0.00',
          created_at: article.created_at
        }
      };
      setCurrentArticle(generationResponse);
      setCurrentView('article');
    } catch (error) {
      console.error('Failed to load article:', error);
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary rounded-lg">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  SEO Article Generator
                </h1>
                <p className="text-sm text-gray-600">
                  Генерация качественных SEO-статей с помощью ИИ
                </p>
              </div>
            </div>

            <nav className="flex items-center gap-2">
              <Button
                variant={currentView === 'form' ? 'default' : 'ghost'}
                onClick={handleBackToForm}
                className="flex items-center gap-2"
              >
                <Sparkles className="h-4 w-4" />
                Создать статью
              </Button>
              
              <Button
                variant={currentView === 'history' ? 'default' : 'ghost'}
                onClick={() => setCurrentView('history')}
                className="flex items-center gap-2"
              >
                <History className="h-4 w-4" />
                История
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'form' && (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Создайте качественную SEO-статью за минуты
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Используйте мощь искусственного интеллекта для генерации 
                оптимизированных статей с автоматическим анализом ключевых слов 
                и SEO-оценкой
              </p>
            </div>
            
            <ArticleGenerationForm onArticleGenerated={handleArticleGenerated} />
            
            {/* Features */}
            <div className="grid md:grid-cols-3 gap-6 mt-12">
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Sparkles className="h-6 w-6 text-blue-600" />
                  </div>
                  <h3 className="font-semibold mb-2">ИИ-генерация</h3>
                  <p className="text-sm text-gray-600">
                    Используем GPT-3.5 и GPT-4 для создания качественного контента
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <FileText className="h-6 w-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold mb-2">SEO-оптимизация</h3>
                  <p className="text-sm text-gray-600">
                    Автоматический анализ ключевых слов и оценка SEO-качества
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <History className="h-6 w-6 text-purple-600" />
                  </div>
                  <h3 className="font-semibold mb-2">История статей</h3>
                  <p className="text-sm text-gray-600">
                    Сохранение и управление всеми созданными статьями
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
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
            <span>Создано с</span>
            <Heart className="h-4 w-4 text-red-500" />
            <span>используя FastAPI и React</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App; 