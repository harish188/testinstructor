#!/usr/bin/env python3
"""
Vercel-compatible entry point for the Zoho to ClickUp Automation System
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Use simple API for Vercel deployment
try:
    from api_simple import app
    print("Using simplified API for Vercel deployment")
except ImportError:
    # Fallback to full API
    from api import app
    print("Using full API")

# This is the ASGI application that Vercel will use
handler = app

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)