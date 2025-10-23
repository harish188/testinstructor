from firebase_functions import https_fn, options
from firebase_admin import initialize_app, firestore
import json
import requests
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
import logging

# Initialize Firebase Admin
initialize_app()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZohoService:
    """Service for Zoho Desk API integration"""
    
    def __init__(self):
        self.client_id = os.environ.get('ZOHO_CLIENT_ID')
        self.client_secret = os.environ.get('ZOHO_CLIENT_SECRET') 
        self.refresh_token = os.environ.get('ZOHO_REFRESH_TOKEN')
        self.org_id = os.environ.get('ZOHO_ORGANIZATION_ID')
        self.access_token = None
        
    def get_access_token(self):
        """Get fresh access token using refresh token"""
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            logger.warning("Zoho credentials not configured")
            return None
            
        url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
                return self.access_token
        except Exception as e:
            logger.error(f"Error getting Zoho access token: {e}")
        return None
    
    def get_tickets(self, hours_back: int = 24) -> List[Dict]:
        """Fetch tickets from Zoho Desk"""
        if not self.get_access_token():
            return []
            
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'orgId': self.org_id
        }
        
        # Calculate date filter
        from_date = (datetime.now() - timedelta(hours=hours_back)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        url = f"https://desk.zoho.com/api/v1/tickets"
        params = {
            'modifiedTime': from_date,
            'limit': 100,
            'sortBy': 'modifiedTime'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Error fetching Zoho tickets: {e}")
        
        return []

class ClickUpService:
    """Service for ClickUp API integration"""
    
    def __init__(self):
        self.api_token = os.environ.get('CLICKUP_API_TOKEN')
        self.team_id = os.environ.get('CLICKUP_TEAM_ID')
        
    def get_headers(self):
        return {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }
    
    def create_task(self, list_id: str, ticket_data: Dict) -> Optional[str]:
        """Create task in ClickUp"""
        if not self.api_token:
            logger.warning("ClickUp API token not configured")
            return None
            
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
        
        task_data = {
            'name': ticket_data.get('subject', 'Untitled Ticket'),
            'description': ticket_data.get('description', ''),
            'status': 'to do',
            'priority': self._map_priority(ticket_data.get('priority')),
            'tags': [ticket_data.get('category', 'general')],
            'custom_fields': [
                {
                    'id': 'zoho_ticket_id',
                    'value': ticket_data.get('id')
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=task_data)
            if response.status_code == 200:
                return response.json().get('id')
        except Exception as e:
            logger.error(f"Error creating ClickUp task: {e}")
        
        return None
    
    def _map_priority(self, zoho_priority: str) -> int:
        """Map Zoho priority to ClickUp priority"""
        priority_map = {
            'High': 1,
            'Medium': 2, 
            'Low': 3,
            'Urgent': 1
        }
        return priority_map.get(zoho_priority, 3)

class CategorizationService:
    """Service for intelligent ticket categorization"""
    
    def __init__(self):
        # Load knowledge base from Firestore or use default
        self.categories = {
            "Platform Issues": {
                "keywords": ["platform", "system", "login", "portal", "access", "authentication"],
                "team": "Product/Tech",
                "list_id": os.environ.get('PLATFORM_LIST_ID', '')
            },
            "Facilities": {
                "keywords": ["projector", "room", "hardware", "facility", "equipment", "maintenance"],
                "team": "Facilities", 
                "list_id": os.environ.get('FACILITIES_LIST_ID', '')
            },
            "Session Timing Issues": {
                "keywords": ["session", "timing", "schedule", "delay", "reschedule"],
                "team": "Curriculum/Content",
                "list_id": os.environ.get('SESSION_LIST_ID', '')
            },
            "Tech QA Report Issue": {
                "keywords": ["qa", "quality", "report", "bug", "testing"],
                "team": "Product/Tech",
                "list_id": os.environ.get('QA_LIST_ID', '')
            },
            "Student Portal": {
                "keywords": ["student", "portal", "enrollment", "profile", "dashboard"],
                "team": "Product/Tech", 
                "list_id": os.environ.get('STUDENT_LIST_ID', '')
            },
            "Session Handling Issues": {
                "keywords": ["instructor", "teaching", "class", "session handling"],
                "team": "Instructor",
                "list_id": os.environ.get('INSTRUCTOR_LIST_ID', '')
            }
        }
    
    def categorize_ticket(self, ticket: Dict) -> Dict:
        """Categorize a single ticket"""
        subject = ticket.get('subject', '').lower()
        description = ticket.get('description', '').lower()
        content = f"{subject} {description}"
        
        best_match = None
        best_score = 0
        
        for category, config in self.categories.items():
            score = sum(1 for keyword in config['keywords'] if keyword in content)
            if score > best_score:
                best_score = score
                best_match = category
        
        if not best_match:
            best_match = "Platform Issues"  # Default category
        
        category_config = self.categories[best_match]
        
        return {
            **ticket,
            'category': best_match,
            'team': category_config['team'],
            'list_id': category_config['list_id'],
            'confidence': min(best_score / len(category_config['keywords']), 1.0)
        }

class AutomationService:
    """Main automation service orchestrating the sync"""
    
    def __init__(self):
        self.zoho = ZohoService()
        self.clickup = ClickUpService()
        self.categorizer = CategorizationService()
        self.db = firestore.client()
    
    def sync_tickets(self, hours_back: int = 24) -> Dict:
        """Main sync operation"""
        logger.info(f"Starting ticket sync for last {hours_back} hours")
        
        result = {
            'total_tickets': 0,
            'processed': 0,
            'successful': 0,
            'errors': 0,
            'duplicates': 0,
            'execution_time': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = datetime.now()
        
        try:
            # Fetch tickets from Zoho
            tickets = self.zoho.get_tickets(hours_back)
            result['total_tickets'] = len(tickets)
            
            for ticket in tickets:
                try:
                    # Check if already processed
                    if self._is_duplicate(ticket['id']):
                        result['duplicates'] += 1
                        continue
                    
                    # Categorize ticket
                    categorized_ticket = self.categorizer.categorize_ticket(ticket)
                    
                    # Create ClickUp task
                    if categorized_ticket['list_id']:
                        task_id = self.clickup.create_task(
                            categorized_ticket['list_id'], 
                            categorized_ticket
                        )
                        
                        if task_id:
                            # Log successful sync
                            self._log_sync(ticket['id'], task_id, categorized_ticket)
                            result['successful'] += 1
                        else:
                            result['errors'] += 1
                    else:
                        logger.warning(f"No list ID configured for category: {categorized_ticket['category']}")
                        result['errors'] += 1
                    
                    result['processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing ticket {ticket.get('id')}: {e}")
                    result['errors'] += 1
            
        except Exception as e:
            logger.error(f"Sync operation failed: {e}")
            result['errors'] += 1
        
        result['execution_time'] = (datetime.now() - start_time).total_seconds()
        logger.info(f"Sync completed: {result}")
        
        return result
    
    def _is_duplicate(self, ticket_id: str) -> bool:
        """Check if ticket already processed"""
        try:
            doc = self.db.collection('sync_logs').document(ticket_id).get()
            return doc.exists
        except:
            return False
    
    def _log_sync(self, ticket_id: str, task_id: str, ticket_data: Dict):
        """Log successful sync to Firestore"""
        try:
            self.db.collection('sync_logs').document(ticket_id).set({
                'zoho_ticket_id': ticket_id,
                'clickup_task_id': task_id,
                'category': ticket_data['category'],
                'team': ticket_data['team'],
                'confidence': ticket_data['confidence'],
                'synced_at': datetime.now(),
                'status': 'success'
            })
        except Exception as e:
            logger.error(f"Error logging sync: {e}")

# Initialize services
automation_service = AutomationService()

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=["*"],
        cors_methods=["GET", "POST", "OPTIONS"]
    )
)
def api(req: https_fn.Request) -> https_fn.Response:
    """Main API endpoint for Firebase Cloud Functions"""
    
    # Handle CORS preflight
    if req.method == 'OPTIONS':
        return https_fn.Response('', status=200)
    
    path = req.path.replace('/api', '')
    method = req.method
    
    try:
        # Status endpoint
        if path == '/status' and method == 'GET':
            return _json_response({
                "status": "online",
                "platform": "firebase",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "message": "Full Zoho-ClickUp automation system running",
                "features": ["zoho_integration", "clickup_integration", "auto_categorization", "real_time_sync"]
            })
        
        # Categories endpoint
        elif path == '/categories' and method == 'GET':
            categories = list(automation_service.categorizer.categories.keys())
            return _json_response({"categories": categories})
        
        # Teams endpoint  
        elif path == '/teams' and method == 'GET':
            teams = list(set(config['team'] for config in automation_service.categorizer.categories.values()))
            return _json_response({"teams": teams})
        
        # Manual sync endpoint
        elif path == '/sync' and method == 'POST':
            request_json = req.get_json(silent=True) or {}
            hours_back = request_json.get('hours_back', 24)
            
            result = automation_service.sync_tickets(hours_back)
            return _json_response({
                "success": True,
                "message": "Sync completed successfully",
                "result": result
            })
        
        # Categorize tickets endpoint
        elif path == '/categorize' and method == 'POST':
            request_json = req.get_json(silent=True) or []
            
            categorized = []
            for ticket in request_json:
                categorized_ticket = automation_service.categorizer.categorize_ticket(ticket)
                categorized.append(categorized_ticket)
            
            return _json_response({"categorized_tickets": categorized})
        
        # Health check
        elif path == '/health' and method == 'GET':
            return _json_response({"status": "healthy", "timestamp": datetime.now().isoformat()})
        
        # Sync history
        elif path == '/history' and method == 'GET':
            try:
                docs = automation_service.db.collection('sync_logs').order_by('synced_at', direction=firestore.Query.DESCENDING).limit(50).stream()
                history = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    history.append(data)
                return _json_response({"history": history})
            except Exception as e:
                return _json_response({"error": str(e)}, 500)
        
        else:
            return _json_response({"error": "Not Found", "path": path, "method": method}, 404)
            
    except Exception as e:
        logger.error(f"API error: {e}")
        return _json_response({"error": "Internal Server Error", "message": str(e)}, 500)

def _json_response(data: Dict, status: int = 200) -> https_fn.Response:
    """Helper to create JSON response with CORS headers"""
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    return https_fn.Response(json.dumps(data), status=status, headers=headers)