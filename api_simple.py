from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import json
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Zoho to ClickUp Automation",
    description="Automated ticket routing from Zoho Desk to ClickUp",
    version="1.0.0"
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    pass  # Handle case where static directory doesn't exist

# Simple response models
class SyncResponse(BaseModel):
    success: bool
    message: str
    result: Optional[dict] = None

# Basic routes
@app.get("/")
async def root():
    """Serve the dashboard"""
    try:
        return FileResponse("static/index.html")
    except Exception:
        return HTMLResponse("""
        <html>
            <head><title>Zoho-ClickUp Automation</title></head>
            <body>
                <h1>🚀 Zoho-ClickUp Automation System</h1>
                <p>System is running on Vercel!</p>
                <p><a href="/docs">View API Documentation</a></p>
            </body>
        </html>
        """)

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "system_status": "running",
        "platform": "vercel",
        "timestamp": datetime.now().isoformat(),
        "message": "System is operational"
    }

@app.get("/api/categories")
async def get_categories():
    """Get available categories"""
    categories = [
        "Platform Issues",
        "Facilities", 
        "Session Timing Issues",
        "Tech QA Report Issue",
        "Other On-Ground Issues",
        "Student Portal",
        "Scheduling Issue",
        "Session Handling Issues"
    ]
    return {"categories": categories}

@app.get("/api/teams")
async def get_teams():
    """Get available teams"""
    teams = [
        "Product/Tech",
        "Facilities",
        "Curriculum/Content", 
        "Instructor"
    ]
    return {"teams": teams}

@app.get("/api/mock-tickets")
async def get_mock_tickets():
    """Get mock tickets for testing"""
    mock_tickets = [
        {
            "id": "1",
            "subject": "Platform system crash during login",
            "description": "Users unable to access the learning platform",
            "category": "Platform Issues",
            "team": "Product/Tech",
            "priority": "High",
            "status": "Open",
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": "2", 
            "subject": "Projector not working in Room 101",
            "description": "Hardware issue with classroom projector",
            "category": "Facilities",
            "team": "Facilities",
            "priority": "Medium",
            "status": "Open",
            "created_at": "2024-01-15T11:15:00Z"
        },
        {
            "id": "3",
            "subject": "Session timing delay notification",
            "description": "Students not receiving session timing updates",
            "category": "Session Timing Issues", 
            "team": "Curriculum/Content",
            "priority": "Medium",
            "status": "Open",
            "created_at": "2024-01-15T12:00:00Z"
        }
    ]
    return {"tickets": mock_tickets}

@app.post("/api/categorize-tickets")
async def categorize_tickets(tickets: List[dict]):
    """Categorize tickets using simple rules"""
    categorized = []
    
    for ticket in tickets:
        subject = ticket.get("subject", "").lower()
        description = ticket.get("description", "").lower()
        
        # Simple categorization logic
        if any(word in subject + " " + description for word in ["platform", "system", "login", "portal"]):
            category = "Platform Issues"
            team = "Product/Tech"
        elif any(word in subject + " " + description for word in ["projector", "room", "hardware", "facility"]):
            category = "Facilities"
            team = "Facilities"
        elif any(word in subject + " " + description for word in ["session", "timing", "schedule"]):
            category = "Session Timing Issues"
            team = "Curriculum/Content"
        elif any(word in subject + " " + description for word in ["instructor", "teaching"]):
            category = "Session Handling Issues"
            team = "Instructor"
        else:
            category = "Other On-Ground Issues"
            team = "Facilities"
        
        categorized_ticket = {
            **ticket,
            "category": category,
            "team": team,
            "confidence": 0.85
        }
        categorized.append(categorized_ticket)
    
    return {"categorized_tickets": categorized}

@app.post("/api/sync")
async def trigger_sync():
    """Simulate sync operation"""
    return SyncResponse(
        success=True,
        message="Sync completed successfully (Demo Mode)",
        result={
            "processed": 3,
            "successful": 3,
            "errors": 0,
            "execution_time": 2.5
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )