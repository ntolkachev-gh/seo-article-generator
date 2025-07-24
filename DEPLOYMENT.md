# 🚀 Инструкции по деплою фронтенда

## Вариант 1: GitHub Pages (Бесплатно)

### Автоматический деплой:
1. Перейдите в настройки репозитория на GitHub
2. В разделе "Pages" выберите источник "Deploy from a branch"
3. Выберите ветку `main` и папку `/docs`
4. Нажмите "Save"

### Ручной деплой:
```bash
# Создайте ветку gh-pages
git checkout -b gh-pages

# Скопируйте файлы
cp frontend/public/index.html ./

# Закоммитьте и запушьте
git add .
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

## Вариант 2: Vercel (Рекомендуется)

1. Зарегистрируйтесь на [vercel.com](https://vercel.com)
2. Подключите ваш GitHub репозиторий
3. Vercel автоматически обнаружит конфигурацию в `vercel.json`
4. Нажмите "Deploy"

## Вариант 3: Netlify

1. Зарегистрируйтесь на [netlify.com](https://netlify.com)
2. Подключите ваш GitHub репозиторий
3. Укажите папку `frontend/public` как корневую
4. Нажмите "Deploy"

## Вариант 4: Локальный тест

```bash
cd frontend
python -m http.server 3000
```

Затем откройте http://localhost:3000

## 🔧 Настройка API

Фронтенд уже настроен для работы с Heroku API:
- URL: `https://seo-article-generator-app-8a9fa9a58cbb.herokuapp.com`
- Все endpoints доступны

## 📝 Примечания

- Фронтенд использует CDN для Tailwind CSS, Axios и Marked
- Не требует сборки или Node.js
- Работает сразу после деплоя
- Поддерживает все функции: генерация статей, история, просмотр

## 🌐 Ссылки

- **Backend API**: https://seo-article-generator-app-8a9fa9a58cbb.herokuapp.com
- **API Docs**: https://seo-article-generator-app-8a9fa9a58cbb.herokuapp.com/docs
- **GitHub Repo**: https://github.com/ntolkachev-gh/seo-article-generator 