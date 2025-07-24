#!/usr/bin/env python3
"""
Скрипт для запуска backend сервера SEO Article Generator
"""

import os
import sys
import uvicorn

# Добавляем backend директорию в Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    # Меняем рабочую директорию на backend
    os.chdir(backend_dir)
    
    # Запускаем сервер
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[backend_dir]
    ) 