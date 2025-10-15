def handler(request, context):
    """Ultra-simple Vercel handler"""
    
    # Get the path from the request
    path = request.get('path', '/')
    method = request.get('httpMethod', 'GET')
    
    # Simple routing
    if path == '/' and method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': '''
            <!DOCTYPE html>
            <html>
            <head><title>Zoho-ClickUp Automation</title></head>
            <body style="font-family: Arial; margin: 40px;">
                <h1>🚀 Zoho-ClickUp Automation System</h1>
                <div style="background: #e8f5e8; padding: 15px; border-radius: 5px;">
                    <h3>✅ System Status: Online</h3>
                    <p>Successfully deployed on Vercel!</p>
                </div>
                <h3>API Endpoints:</h3>
                <ul>
                    <li><a href="/api/status">/api/status</a> - System status</li>
                    <li><a href="/api/categories">/api/categories</a> - Categories</li>
                    <li><a href="/api/teams">/api/teams</a> - Teams</li>
                </ul>
            </body>
            </html>
            '''
        }
    
    elif path == '/api/status':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"status": "online", "platform": "vercel", "message": "Working!"}'
        }
    
    elif path == '/api/categories':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"categories": ["Platform Issues", "Facilities", "Session Timing Issues", "Tech QA Report Issue", "Student Portal", "Session Handling Issues"]}'
        }
    
    elif path == '/api/teams':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"teams": ["Product/Tech", "Facilities", "Curriculum/Content", "Instructor"]}'
        }
    
    elif path == '/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"status": "healthy"}'
        }
    
    else:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': '{"error": "Not Found"}'
        }