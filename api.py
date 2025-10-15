from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_html()
        elif self.path == '/api/status':
            self.send_json({
                "status": "online",
                "platform": "vercel", 
                "timestamp": datetime.now().isoformat()
            })
        elif self.path == '/api/categories':
            self.send_json({
                "categories": [
                    "Platform Issues",
                    "Facilities",
                    "Session Timing Issues", 
                    "Tech QA Report Issue",
                    "Student Portal",
                    "Session Handling Issues"
                ]
            })
        elif self.path == '/api/teams':
            self.send_json({
                "teams": [
                    "Product/Tech",
                    "Facilities", 
                    "Curriculum/Content",
                    "Instructor"
                ]
            })
        elif self.path == '/health':
            self.send_json({"status": "healthy"})
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/categorize':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    tickets = json.loads(post_data.decode('utf-8'))
                else:
                    tickets = []
                
                categorized = []
                for ticket in tickets:
                    subject = str(ticket.get("subject", "")).lower()
                    
                    if "platform" in subject or "system" in subject:
                        category = "Platform Issues"
                        team = "Product/Tech"
                    elif "facility" in subject or "room" in subject:
                        category = "Facilities" 
                        team = "Facilities"
                    elif "session" in subject or "timing" in subject:
                        category = "Session Timing Issues"
                        team = "Curriculum/Content"
                    else:
                        category = "Platform Issues"
                        team = "Product/Tech"
                    
                    categorized.append({
                        **ticket,
                        "category": category,
                        "team": team
                    })
                
                self.send_json({"categorized_tickets": categorized})
            except:
                self.send_error(400)
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_html(self):
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Zoho-ClickUp Automation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Zoho-ClickUp Automation</h1>
        <div class="status">
            <h3>✅ System Online</h3>
            <p>Deployed successfully on Vercel</p>
        </div>
        <h3>Available Endpoints:</h3>
        <ul>
            <li><strong>GET /api/status</strong> - System status</li>
            <li><strong>GET /api/categories</strong> - Ticket categories</li>
            <li><strong>GET /api/teams</strong> - Available teams</li>
            <li><strong>POST /api/categorize</strong> - Categorize tickets</li>
        </ul>
        <button class="button" onclick="testAPI()">Test API</button>
        <div id="result"></div>
    </div>
    <script>
        async function testAPI() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('result').innerHTML = 
                    '<div class="status"><h4>Test Result:</h4><pre>' + 
                    JSON.stringify(data, null, 2) + '</pre></div>';
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    '<div style="background: #ffe6e6; padding: 15px;">Error: ' + error.message + '</div>';
            }
        }
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())