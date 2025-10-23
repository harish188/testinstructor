from firebase_functions import https_fn
from firebase_admin import initialize_app
import json
from datetime import datetime

# Initialize Firebase Admin
initialize_app()

@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    """Firebase Cloud Function for API endpoints"""
    
    # Enable CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Handle preflight requests
    if req.method == 'OPTIONS':
        return https_fn.Response('', status=200, headers=headers)
    
    # Get the path from the request
    path = req.path
    method = req.method
    
    try:
        # Route the requests
        if path == '/api/status' and method == 'GET':
            data = {
                "status": "online",
                "platform": "firebase",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "message": "Zoho-ClickUp automation system running on Firebase"
            }
            headers['Content-Type'] = 'application/json'
            return https_fn.Response(json.dumps(data), status=200, headers=headers)
        
        elif path == '/api/categories' and method == 'GET':
            data = {
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
            headers['Content-Type'] = 'application/json'
            return https_fn.Response(json.dumps(data), status=200, headers=headers)
        
        elif path == '/api/teams' and method == 'GET':
            data = {
                "teams": [
                    "Product/Tech",
                    "Facilities",
                    "Curriculum/Content", 
                    "Instructor"
                ]
            }
            headers['Content-Type'] = 'application/json'
            return https_fn.Response(json.dumps(data), status=200, headers=headers)
        
        elif path == '/api/categorize' and method == 'POST':
            # Get request body
            request_json = req.get_json(silent=True)
            tickets = request_json if request_json else []
            
            categorized = []
            for ticket in tickets:
                subject = str(ticket.get("subject", "")).lower()
                description = str(ticket.get("description", "")).lower()
                
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
                
                categorized.append({
                    **ticket,
                    "category": category,
                    "team": team,
                    "confidence": 0.85
                })
            
            data = {"categorized_tickets": categorized}
            headers['Content-Type'] = 'application/json'
            return https_fn.Response(json.dumps(data), status=200, headers=headers)
        
        elif path == '/api/health' and method == 'GET':
            data = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            headers['Content-Type'] = 'application/json'
            return https_fn.Response(json.dumps(data), status=200, headers=headers)
        
        else:
            data = {"error": "Not Found", "path": path, "method": method}
            headers['Content-Type'] = 'application/json'
            return https_fn.Response(json.dumps(data), status=404, headers=headers)
            
    except Exception as e:
        data = {"error": "Internal Server Error", "message": str(e)}
        headers['Content-Type'] = 'application/json'
        return https_fn.Response(json.dumps(data), status=500, headers=headers)