# SEO Article Generator

AI-powered SEO article generator with support for multiple OpenAI and Anthropic models and style customization.

## 🚀 Features

### 🤖 Multiple AI Models Support
- **Fast Models**: GPT-4o Mini, GPT-3.5 Turbo, Claude 3.5 Haiku - для быстрой и экономичной генерации
- **Balanced Models**: GPT-4o, GPT-4 Turbo, Claude 3.5 Sonnet - оптимальное соотношение качества и скорости
- **Quality Models**: GPT-4, Claude 3 Sonnet - максимальное качество контента
- **Premium Models**: Claude 3 Opus, GPT-4 32K - премиум качество и длинные контексты

### 📝 Article Generation
- SEO-оптимизированные статьи с естественным включением ключевых слов
- Автоматический анализ SERP для определения популярных вопросов
- Генерация структуры и полного текста статьи
- Поддержка стилевых примеров для кастомизации тона и стиля
- **Автоматический выбор провайдера** (OpenAI/Anthropic) в зависимости от модели

### 💰 Cost Tracking
- Отслеживание использования токенов для каждой модели
- Расчет стоимости генерации в реальном времени
- История использования с детальной статистикой
- **Поддержка разных тарифов** для OpenAI и Anthropic

### 🎨 Style Customization
- Загрузка примеров текстов для копирования стиля
- Настройка объема статьи (количество символов)
- Сохранение стилевых предпочтений

## 🛠️ Technology Stack

### Backend
- **FastAPI** - современный веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - основная база данных
- **Alembic** - миграции базы данных
- **OpenAI API** - интеграция с различными моделями ИИ
- **Anthropic API** - интеграция с Claude моделями

### Frontend
- **React** с TypeScript
- **Tailwind CSS** - стилизация
- **Axios** - HTTP клиент
- **Lucide React** - иконки

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл с вашими API ключами

# Запуск миграций
alembic upgrade head

# Запуск сервера
python run_backend.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI API (обязательно для GPT моделей)
OPENAI_API_KEY=your_openai_api_key

# Anthropic API (обязательно для Claude моделей)
ANTHROPIC_API_KEY=your_anthropic_api_key

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/seo_articles

# SERP API (опционально)
SERP_API_KEY=your_serp_api_key

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### Available Models

| Model | Provider | Category | Description | Input Cost | Output Cost |
|-------|----------|----------|-------------|------------|-------------|
| GPT-4o Mini | OpenAI | Fast | Самый быстрый и дешевый | $0.00015/1K | $0.0006/1K |
| GPT-3.5 Turbo | OpenAI | Fast | Быстрый и экономичный | $0.0015/1K | $0.002/1K |
| Claude 3.5 Haiku | Anthropic | Fast | Быстрый и дешевый | $0.00025/1K | $0.00125/1K |
| GPT-4o | OpenAI | Balanced | Оптимальное качество и скорость | $0.005/1K | $0.015/1K |
| GPT-4 Turbo | OpenAI | Balanced | Высокое качество | $0.01/1K | $0.03/1K |
| Claude 3.5 Sonnet | Anthropic | Balanced | Сбалансированное качество | $0.003/1K | $0.015/1K |
| GPT-4 | OpenAI | Quality | Максимальное качество | $0.03/1K | $0.06/1K |
| Claude 3 Sonnet | Anthropic | Quality | Альтернатива GPT-4 | $0.003/1K | $0.015/1K |
| Claude 3 Opus | Anthropic | Premium | Премиум качество | $0.015/1K | $0.075/1K |
| GPT-4 32K | OpenAI | Premium | Длинные контексты | $0.06/1K | $0.12/1K |

## 🚀 Usage

### Basic Article Generation
1. Откройте приложение в браузере
2. Введите тему статьи
3. Добавьте тезисы и ключевые идеи
4. Выберите подходящую модель ИИ (OpenAI или Claude)
5. Нажмите "Сгенерировать статью"

### Style Customization
1. В разделе "Стиль письма" добавьте примеры текстов
2. Укажите желаемый объем статьи
3. Генерируйте статьи в выбранном стиле

### Cost Optimization
- **Быстрые черновики**: GPT-4o Mini или Claude 3.5 Haiku
- **Финальные версии**: GPT-4o или Claude 3.5 Sonnet
- **Премиум контент**: Claude 3 Opus
- **Длинные статьи**: GPT-4 32K

### Provider Selection
- **Автоматический выбор**: Система сама определяет провайдера по модели
- **OpenAI**: Все модели GPT (gpt-3.5-turbo, gpt-4, gpt-4o, etc.)
- **Anthropic**: Все модели Claude (claude-3-5-haiku, claude-3-sonnet, etc.)

## 📊 API Endpoints

### Articles
- `POST /api/articles/generate` - Генерация новой статьи
- `GET /api/articles` - Список всех статей
- `GET /api/articles/{id}` - Получение статьи по ID
- `DELETE /api/articles/{id}` - Удаление статьи

### Models
- `GET /api/models` - Список доступных моделей с ценами

### Health
- `GET /api/health` - Проверка состояния сервиса

## 🎯 SEO Features

- Автоматический анализ поисковых запросов
- Генерация релевантных ключевых слов
- SEO-оценка готовых статей
- Рекомендации по улучшению

## 🔒 Security

- Валидация входных данных
- Ограничение размера запросов
- Безопасное хранение API ключей
- CORS настройки

## 📈 Performance

- Асинхронная обработка запросов
- Кэширование результатов
- Оптимизированные промпты
- Мониторинг использования токенов
- **Автоматический fallback** при недоступности одного из провайдеров

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Создайте Issue в GitHub
- Проверьте документацию в `/docs`
- Обратитесь к руководству по развертыванию

## 🔄 Updates

### Latest Updates
- ✅ Добавлена поддержка GPT-4o и GPT-4o Mini
- ✅ Интеграция с Claude 3 и Claude 3.5 моделями
- ✅ Автоматический выбор провайдера (OpenAI/Anthropic)
- ✅ Улучшенный интерфейс выбора моделей
- ✅ Детальное отслеживание стоимости для всех провайдеров
- ✅ Поддержка стилевых примеров
- ✅ Fallback механизмы при недоступности API