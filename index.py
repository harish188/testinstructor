from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
import json
from datetime import datetime

# Create FastAPI app
app = FastAPI(title="Zoho-ClickUp Automation")

@app.get("/")
def read_root():
    """Serve basic dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Zoho-ClickUp Automation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .button:hover { background: #005a87; }
            .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #007cba; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Zoho-ClickUp Automation System</h1>
                <p>Intelligent ticket routing and categorization</p>
            </div>
            
            <div class="status">
                <h3>✅ System Status: Online</h3>
                <p>Deployed on Vercel • Ready for ticket processing</p>
            </div>
            
            <h3>🔧 Available Endpoints:</h3>
            <div class="endpoint">
                <strong>GET /api/status</strong> - System status and health check
            </div>
            <div class="endpoint">
                <strong>GET /api/categories</strong> - Available ticket categories
            </div>
            <div class="endpoint">
                <strong>GET /api/teams</strong> - Available teams
            </div>
            <div class="endpoint">
                <strong>POST /api/categorize</strong> - Categorize tickets
            </div>
            <div class="endpoint">
                <strong>GET /docs</strong> - Interactive API documentation
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <button class="button" onclick="window.open('/docs', '_blank')">View API Docs</button>
                <button class="button" onclick="testAPI()">Test API</button>
            </div>
            
            <div id="result" style="margin-top: 20px;"></div>
        </div>
        
        <script>
            async function testAPI() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    document.getElementById('result').innerHTML = 
                        '<div class="status"><h4>API Test Result:</h4><pre>' + 
                        JSON.stringify(data, null, 2) + '</pre></div>';
                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        '<div style="background: #ffe6e6; padding: 15px; border-radius: 5px;">Error: ' + error.message + '</div>';
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/status")
def get_status():
    """Get system status"""
    return {
        "status": "online",
        "platform": "vercel",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "message": "Zoho-ClickUp automation system is running"
    }

@app.get("/api/categories")
def get_categories():
    """Get available categories"""
    return {
        "categories": [
            "Platform Issues",
            "Facilities", 
            "Session Timing Issues",
            "Tech QA Report Issue",
            "Other On-Ground Issues",
            "Student Portal",
            "Scheduling Issue",
            "Session Handling Issues"
        ]
    }

@app.get("/api/teams")
def get_teams():
    """Get available teams"""
    return {
        "teams": [
            "Product/Tech",
            "Facilities",
            "Curriculum/Content", 
            "Instructor"
        ]
    }

@app.post("/api/categorize")
def categorize_tickets(tickets: list):
    """Categorize tickets"""
    categorized = []
    
    for ticket in tickets:
        subject = str(ticket.get("subject", "")).lower()
        description = str(ticket.get("description", "")).lower()
        
        # Simple categorization
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
        
        categorized.append({
            **ticket,
            "category": category,
            "team": team,
            "confidence": 0.85
        })
    
    return {"categorized_tickets": categorized}

@app.get("/health")
def health_check():
    """Health check"""
    return {"status": "healthy"}

# For Vercel
handler = app