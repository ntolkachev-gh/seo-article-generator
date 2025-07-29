# 🚀 Quick Deploy Guide

Быстрое развертывание SEO Article Generator с поддержкой всех моделей OpenAI и Anthropic.

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL (или SQLite для тестирования)
- OpenAI API ключ (для GPT моделей)
- Anthropic API ключ (для Claude моделей)

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd seo-article-generator
```

### 2. Backend Setup
```bash
cd backend

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cat > .env << EOF
# OpenAI API (для GPT моделей)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API (для Claude моделей)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/seo_articles
# Или для SQLite:
# DATABASE_URL=sqlite:///./seo_articles.db

# Frontend URL
FRONTEND_URL=http://localhost:3000
EOF

# Запуск миграций
alembic upgrade head

# Запуск сервера
python run_backend.py
```

### 3. Frontend Setup
```bash
cd frontend

# Установка зависимостей
npm install

# Запуск приложения
npm start
```

## 🤖 Available AI Models

### Fast & Cost-Effective
- **GPT-4o Mini** (OpenAI) - $0.00015/1K input, $0.0006/1K output
- **GPT-3.5 Turbo** (OpenAI) - $0.0015/1K input, $0.002/1K output
- **Claude 3.5 Haiku** (Anthropic) - $0.00025/1K input, $0.00125/1K output

### Balanced
- **GPT-4o** (OpenAI) - $0.005/1K input, $0.015/1K output
- **GPT-4 Turbo** (OpenAI) - $0.01/1K input, $0.03/1K output
- **Claude 3.5 Sonnet** (Anthropic) - $0.003/1K input, $0.015/1K output

### High Quality
- **GPT-4** (OpenAI) - $0.03/1K input, $0.06/1K output
- **Claude 3 Sonnet** (Anthropic) - $0.003/1K input, $0.015/1K output

### Premium
- **Claude 3 Opus** (Anthropic) - $0.015/1K input, $0.075/1K output
- **GPT-4 32K** (OpenAI) - $0.06/1K input, $0.12/1K output

## 🎯 Usage Tips

### Cost Optimization
1. **Drafts**: Use GPT-4o Mini or Claude 3.5 Haiku for quick drafts
2. **Final Content**: Use GPT-4o or Claude 3.5 Sonnet for balanced quality
3. **Premium Content**: Use Claude 3 Opus for best results

### Model Selection
- **Fast**: For quick iterations and testing
- **Balanced**: For production content
- **Quality**: For important articles
- **Premium**: For flagship content

### Provider Benefits
- **OpenAI**: Wide model variety, good for creative content
- **Anthropic**: Excellent reasoning, good for analytical content

## 🔧 Configuration

### Environment Variables
```bash
# Required (at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database (choose one)
DATABASE_URL=postgresql://user:pass@localhost:5432/db
DATABASE_URL=sqlite:///./seo_articles.db

# Optional
SERP_API_KEY=your_serp_api_key
FRONTEND_URL=http://localhost:3000
```

### API Endpoints
- `POST /api/articles/generate` - Generate article
- `GET /api/models` - List available models
- `GET /api/articles` - List articles
- `GET /api/health` - Health check

## 🚀 Production Deployment

### Heroku
```bash
# Backend
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
heroku config:set ANTHROPIC_API_KEY=your_key
heroku config:set DATABASE_URL=your_postgres_url
git push heroku main

# Frontend
cd frontend
npm run build
# Deploy build folder to your hosting
```

### Docker
```bash
docker-compose up -d
```

### Vercel
```bash
vercel --prod
```

## 📊 Monitoring

### Cost Tracking
- All API calls are logged with token usage
- Cost calculation per model and provider
- Usage history in database
- Separate tracking for OpenAI and Anthropic

### Performance
- Async request processing
- Optimized prompts for each model
- Caching for repeated requests
- Automatic provider selection

## 🆘 Troubleshooting

### Common Issues
1. **API Key Error**: Check OPENAI_API_KEY and ANTHROPIC_API_KEY in .env
2. **Database Error**: Verify DATABASE_URL format
3. **CORS Error**: Check FRONTEND_URL setting
4. **Model Not Found**: Ensure model name is correct
5. **Provider Error**: Check if API key is set for the selected provider

### Debug Mode
```bash
# Backend
DEBUG=1 python run_backend.py

# Frontend
REACT_APP_DEBUG=1 npm start
```

### Testing
```bash
# Test configuration
python3 test_anthropic.py
```

## 📈 Scaling

### Database
- Use PostgreSQL for production
- Enable connection pooling
- Regular backups

### API
- Rate limiting per user
- Caching layer (Redis)
- Load balancing

### Monitoring
- Log aggregation
- Performance metrics
- Cost alerts
- Provider availability monitoring

## 🔒 Security

### API Keys
- Never commit .env files
- Use environment variables
- Rotate keys regularly
- Separate keys for different providers

### Database
- Use strong passwords
- Enable SSL connections
- Regular security updates

### Frontend
- Input validation
- XSS protection
- HTTPS only

## 📞 Support

- GitHub Issues: [Create Issue](https://github.com/your-repo/issues)
- Documentation: `/docs` folder
- Examples: `/examples` folder

## 🔄 Recent Updates

- ✅ Added Claude 3.5 Haiku and Sonnet models
- ✅ Automatic provider selection (OpenAI/Anthropic)
- ✅ Separate pricing for each provider
- ✅ Fallback mechanisms for API failures
- ✅ Enhanced model selection interface

---

**Ready to generate amazing SEO content with the best AI models! 🎉** 