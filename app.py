#!/usr/bin/env python3
"""
Vercel-compatible entry point for the Zoho to ClickUp Automation System
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Create database tables and logs directory
from database import create_tables
Path("logs").mkdir(exist_ok=True)
create_tables()

# Import the FastAPI app
from api import app

# This is the ASGI application that Vercel will use
application = app

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)