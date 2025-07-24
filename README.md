# SEO Article Generator

Полноценное web-приложение для генерации SEO-статей с помощью OpenAI GPT API.

## 🚀 Функциональность

### Frontend (React + shadcn/ui)
- **Форма генерации статьи**: Тема, тезисы, выбор модели (GPT-3.5/GPT-4)
- **Просмотр статьи**: Отображение структуры, готовой статьи, SEO-оценки
- **История статей**: Таблица всех сгенерированных статей с сортировкой
- **SEO-рекомендации**: Советы по улучшению оптимизации статей

### Backend (FastAPI + PostgreSQL)
- **Анализ SERP**: Извлечение ключевых слов из топ-результатов поиска
- **Генерация структуры**: Создание markdown-структуры статьи
- **Генерация текста**: Полный текст статьи по структуре
- **SEO-оценка**: Локальный расчет качества статьи (0-10 баллов)
- **Учет токенов**: Отслеживание использования и стоимости OpenAI API

## 🛠 Технологический стек

### Backend
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - система миграций
- **PostgreSQL** - основная база данных
- **OpenAI API** - генерация контента
- **BeautifulSoup** - парсинг SERP результатов

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - типизированный JavaScript
- **shadcn/ui** - современные UI компоненты
- **Tailwind CSS** - утилитарный CSS фреймворк
- **Axios** - HTTP клиент
- **React Markdown** - рендеринг markdown

## 📊 База данных

### Таблица `articles`
- `id` (UUID) - уникальный идентификатор
- `topic` (TEXT) - тема статьи
- `thesis` (TEXT) - тезисы автора
- `keywords` (JSONB) - массив ключевых слов
- `structure` (TEXT) - структура статьи (markdown)
- `article` (TEXT) - полный текст статьи
- `seo_score` (FLOAT) - SEO-оценка (0-10)
- `model_used` (TEXT) - использованная модель OpenAI
- `created_at` (TIMESTAMP) - дата создания

### Таблица `openai_usage`
- `id` (UUID) - уникальный идентификатор
- `article_id` (UUID) - ссылка на статью
- `model` (TEXT) - название модели
- `prompt_tokens` (INTEGER) - токены в запросе
- `completion_tokens` (INTEGER) - токены в ответе
- `total_tokens` (INTEGER) - общее количество токенов
- `cost_usd` (DECIMAL) - стоимость в долларах
- `created_at` (TIMESTAMP) - дата запроса

## 🚀 Установка и запуск

### Требования
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+

### Backend

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения в `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/seo_articles
OPENAI_API_KEY=your_openai_api_key_here
FRONTEND_URL=http://localhost:3000
```

4. Создайте базу данных и выполните миграции:
```bash
cd backend
alembic upgrade head
```

5. Запустите сервер:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

1. Установите зависимости:
```bash
cd frontend
npm install
```

2. Создайте файл `.env.local`:
```env
REACT_APP_API_URL=http://localhost:8000
```

3. Запустите приложение:
```bash
npm start
```

Приложение будет доступно по адресу: http://localhost:3000

## 🔧 API Endpoints

- `POST /api/articles/generate` - генерация новой статьи
- `GET /api/articles` - получение списка статей
- `GET /api/articles/{id}` - получение статьи по ID
- `DELETE /api/articles/{id}` - удаление статьи
- `GET /api/articles/{id}/seo-recommendations` - SEO-рекомендации
- `GET /api/health` - проверка состояния API

## 📈 SEO-оценка

Система оценивает статьи по следующим критериям:
- **Количество слов** (2000-3000 оптимально)
- **Структура заголовков** (H1, H2, H3)
- **Использование ключевых слов** (плотность 1-3%)
- **Длина заголовков** (30-60 символов)
- **Наличие введения и заключения**
- **Читабельность** (длина предложений)
- **Разнообразие контента** (списки, выделения, ссылки)

## 🎯 Особенности

- **Адаптивный дизайн** - работает на всех устройствах
- **Современный UI** - использование shadcn/ui компонентов
- **Типобезопасность** - полная поддержка TypeScript
- **Обработка ошибок** - корректная обработка всех ошибок API
- **Оптимизация** - ленивая загрузка и кэширование данных

## 📝 Лицензия

Проект создан в образовательных целях.

## 🤝 Вклад в проект

Приветствуются любые улучшения и предложения!