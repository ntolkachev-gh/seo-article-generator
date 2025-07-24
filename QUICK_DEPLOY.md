# ⚡ Быстрый деплой фронтенда

## 🎯 Самый простой способ - GitHub Pages

### Шаг 1: Настройка GitHub Pages
1. Перейдите в ваш репозиторий: https://github.com/ntolkachev-gh/seo-article-generator
2. Нажмите на вкладку "Settings"
3. В левом меню найдите "Pages"
4. В разделе "Source" выберите "Deploy from a branch"
5. Выберите ветку `main` и папку `/docs`
6. Нажмите "Save"

### Шаг 2: Проверка
Через несколько минут ваш сайт будет доступен по адресу:
**https://ntolkachev-gh.github.io/seo-article-generator/**

## 🚀 Альтернатива - Vercel (еще проще)

1. Перейдите на https://vercel.com
2. Нажмите "New Project"
3. Подключите ваш GitHub аккаунт
4. Выберите репозиторий `seo-article-generator`
5. Нажмите "Deploy"

Vercel автоматически обнаружит конфигурацию и задеплоит сайт!

## 🧪 Локальный тест

Если хотите протестировать локально:
```bash
cd frontend
python -m http.server 3000
```

Затем откройте http://localhost:3000

## ✅ Что получится

После деплоя у вас будет полнофункциональное веб-приложение:
- ✅ Форма генерации статей
- ✅ История всех статей
- ✅ Просмотр деталей статей
- ✅ SEO-оценка
- ✅ Интеграция с Heroku API

## 🔧 Настройка OpenAI API

Для полной функциональности добавьте API ключ:
```bash
heroku config:set OPENAI_API_KEY=your_openai_api_key_here
``` 