#!/usr/bin/env python3
"""
Simplified FastAPI app for Heroku deployment
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SEO Article Generator",
    description="API для генерации SEO-статей с помощью OpenAI",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники для тестирования
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SEO Article Generator API is running!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

@app.get("/api/test")
async def test_endpoint():
    return {"message": "Test endpoint working!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 