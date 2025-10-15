from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/api/status':
            self.serve_status()
        elif path == '/api/categories':
            self.serve_categories()
        elif path == '/api/teams':
            self.serve_teams()
        elif path == '/health':
            self.serve_health()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/categorize':
            self.handle_categorize()
        else:
            self.send_error(404, "Not Found")
    
    def serve_dashboard(self):
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
                
                <div style="text-align: center; margin-top: 30px;">
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
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_status(self):
        data = {
            "status": "online",
            "platform": "vercel",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "message": "Zoho-ClickUp automation system is running"
        }
        self.send_json_response(data)
    
    def serve_categories(self):
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
        self.send_json_response(data)
    
    def serve_teams(self):
        data = {
            "teams": [
                "Product/Tech",
                "Facilities",
                "Curriculum/Content", 
                "Instructor"
            ]
        }
        self.send_json_response(data)
    
    def serve_health(self):
        data = {"status": "healthy", "timestamp": datetime.now().isoformat()}
        self.send_json_response(data)
    
    def handle_categorize(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            tickets = json.loads(post_data.decode('utf-8'))
            
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
            
            data = {"categorized_tickets": categorized}
            self.send_json_response(data)
            
        except Exception as e:
            self.send_error(400, f"Bad Request: {str(e)}")
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())