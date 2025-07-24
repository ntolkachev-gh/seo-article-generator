# 🚀 Быстрый запуск SEO Article Generator

## Предварительные требования

1. **Python 3.9+** установлен
2. **Node.js 16+** установлен (для frontend)
3. **PostgreSQL** установлен и запущен (или используйте SQLite для тестирования)

## 1. Настройка Backend

```bash
# 1. Создайте виртуальное окружение
python -m venv venv

# 2. Активируйте его
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Создайте файл .env в корне проекта
cp .env.example .env

# 5. Отредактируйте .env файл:
# - Добавьте ваш OpenAI API ключ
# - Настройте подключение к базе данных
```

### Пример .env файла:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/seo_articles
OPENAI_API_KEY=sk-your-openai-api-key-here
FRONTEND_URL=http://localhost:3000
```

```bash
# 6. Выполните миграции базы данных
cd backend
alembic upgrade head
cd ..

# 7. Запустите backend сервер
python run_backend.py
```

Backend будет доступен по адресу: http://localhost:8000

## 2. Настройка Frontend

```bash
# 1. Перейдите в директорию frontend
cd frontend

# 2. Установите зависимости (если у вас есть npm)
npm install

# 3. Создайте файл .env.local
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local

# 4. Запустите frontend
npm start
```

Frontend будет доступен по адресу: http://localhost:3000

## 3. Альтернативный запуск (без npm)

Если у вас нет npm, вы можете использовать только backend:

1. Откройте http://localhost:8000/docs для Swagger UI
2. Используйте API напрямую через curl или Postman

### Пример API запроса:

```bash
curl -X POST "http://localhost:8000/api/articles/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Преимущества React в 2024",
    "thesis": "React остается лучшим выбором для фронтенд разработки",
    "model": "gpt-3.5-turbo"
  }'
```

## 🎯 Что дальше?

1. Откройте приложение в браузере: http://localhost:3000
2. Заполните форму генерации статьи
3. Получите готовую SEO-статью с оценкой качества
4. Просмотрите историю созданных статей

## 🔧 Решение проблем

### Ошибка подключения к базе данных
- Убедитесь, что PostgreSQL запущен
- Проверьте правильность DATABASE_URL в .env файле
- Для тестирования можете использовать SQLite: `DATABASE_URL=sqlite:///./seo_articles.db`

### Ошибка OpenAI API
- Проверьте правильность API ключа в .env файле
- Убедитесь, что у вас есть кредиты на OpenAI аккаунте

### Проблемы с frontend
- Убедитесь, что backend запущен на порту 8000
- Проверьте файл .env.local в директории frontend

## 📚 Дополнительная информация

- Полная документация: [README.md](README.md)
- API документация: http://localhost:8000/docs (после запуска backend)
- Swagger UI: http://localhost:8000/redoc 