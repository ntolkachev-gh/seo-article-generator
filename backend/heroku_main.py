#!/usr/bin/env python3
"""
Entry point for Heroku deployment
"""

import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import the FastAPI app
from main import app
from database import engine
from models import Base

if __name__ == "__main__":
    import uvicorn
    
    # Create tables when starting the app
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 