from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from datetime import datetime

from services.automation_service import AutomationService
from scheduler import SyncScheduler
from database import create_tables
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Zoho to ClickUp Automation",
    description="Automated ticket routing from Zoho Desk to ClickUp",
    version="1.0.0"
)

# Initialize services
automation_service = AutomationService()
scheduler = SyncScheduler()

# Request/Response models
class ManualSyncRequest(BaseModel):
    hours_back: Optional[int] = 24

class SyncResponse(BaseModel):
    success: bool
    message: str
    result: Optional[dict] = None
    error: Optional[str] = None

# Startup event - Modified for serverless compatibility
@app.on_event("startup")
async def startup_event():
    # Create database tables (safe for serverless)
    try:
        create_tables()
    except Exception as e:
        print(f"Database initialization warning: {e}")
    
    # Skip scheduler in serverless environment
    if not os.getenv("VERCEL"):
        scheduler.start()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    if not os.getenv("VERCEL"):
        scheduler.stop()

# API Routes
@app.get("/")
async def root():
    """Serve the dashboard"""
    return FileResponse("static/index.html")

@app.get("/api/status")
async def get_status():
    """Get system status"""
    job_status = scheduler.get_job_status()
    stats = await automation_service.get_stats()
    
    return {
        "system_status": "running" if scheduler.is_running else "stopped",
        "scheduler": job_status,
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/sync", response_model=SyncResponse)
async def trigger_manual_sync(request: ManualSyncRequest, background_tasks: BackgroundTasks):
    """Trigger manual synchronization"""
    try:
        result = await scheduler.trigger_manual_sync()
        return SyncResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_sync_history(limit: int = 50):
    """Get synchronization history"""
    try:
        history = await automation_service.get_sync_history(limit)
        return {
            "history": [
                {
                    "id": log.id,
                    "zoho_ticket_id": log.zoho_ticket_id,
                    "clickup_task_id": log.clickup_task_id,
                    "category": log.category,
                    "team": log.team,
                    "status": log.status,
                    "error_message": log.error_message,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """Get available categories and team mappings"""
    return {
        "categories": list(settings.category_to_list_mapping.keys()),
        "team_mappings": settings.category_to_team_mapping,
        "list_mappings": settings.category_to_list_mapping
    }

@app.post("/api/scheduler/start")
async def start_scheduler():
    """Start the scheduler"""
    try:
        scheduler.start()
        return {"message": "Scheduler started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scheduler/stop")
async def stop_scheduler():
    """Stop the scheduler"""
    try:
        scheduler.stop()
        return {"message": "Scheduler stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tickets/fetch")
async def fetch_tickets(request: Dict):
    """Fetch tickets from Zoho Desk"""
    try:
        hours_back = request.get('hours_back', 24)
        
        # Use automation service to fetch tickets
        tickets = await automation_service.zoho_service.fetch_recent_tickets(hours_back)
        
        # Convert to dict format for JSON response
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                "id": ticket.id,
                "subject": ticket.subject,
                "description": ticket.description,
                "status": ticket.status,
                "priority": ticket.priority,
                "created_time": ticket.created_time.isoformat(),
                "modified_time": ticket.modified_time.isoformat(),
                "contact_id": ticket.contact_id,
                "email": ticket.email
            })
        
        return {
            "success": True,
            "tickets": tickets_data,
            "count": len(tickets_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync-tickets")
async def sync_tickets_to_clickup(request: Dict):
    """Sync selected tickets to ClickUp"""
    try:
        tickets_data = request.get('tickets', [])
        
        if not tickets_data:
            raise HTTPException(status_code=400, detail="No tickets provided")
        
        results = []
        
        for ticket_data in tickets_data:
            try:
                # Create ClickUp task
                task_id = await automation_service.clickup_service.create_task_from_data(ticket_data)
                
                # Log the sync
                await automation_service._log_sync_result(
                    ticket_data['id'], 
                    task_id, 
                    ticket_data['predicted_category'], 
                    ticket_data['team'], 
                    'success'
                )
                
                results.append({
                    "ticket_id": ticket_data['id'],
                    "success": True,
                    "task_id": task_id
                })
                
            except Exception as e:
                # Log the failure
                await automation_service._log_sync_result(
                    ticket_data['id'], 
                    None, 
                    ticket_data['predicted_category'], 
                    ticket_data['team'], 
                    'failed',
                    str(e)
                )
                
                results.append({
                    "ticket_id": ticket_data['id'],
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r['success'])
        
        return {
            "success": True,
            "results": results,
            "summary": {
                "total": len(results),
                "successful": successful,
                "failed": len(results) - successful
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge-base")
async def get_knowledge_base():
    """Get current knowledge base summary"""
    try:
        kb_summary = automation_service.categorization_service.get_knowledge_base_summary()
        return {
            "success": True,
            "knowledge_base": kb_summary,
            "count": len(kb_summary)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/knowledge-base/add")
async def add_knowledge_base_entries(entries: List[Dict]):
    """Add knowledge base entries directly"""
    try:
        success = automation_service.categorization_service.add_knowledge_base_entries(entries)
        
        if success:
            kb_summary = automation_service.categorization_service.get_knowledge_base_summary()
            return {
                "success": True,
                "message": f"Added {len(entries)} knowledge base entries successfully",
                "categories_count": len(kb_summary)
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to add knowledge base entries")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/knowledge-base/upload")
async def upload_knowledge_base(file: UploadFile = File(...)):
    """Upload and update knowledge base from CSV file"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV and convert to knowledge base format
        import csv
        import io
        
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        kb_entries = []
        
        for row in csv_reader:
            kb_entries.append({
                "category": row["category"],
                "team": row["team"],
                "keywords": [kw.strip().lower() for kw in row["keywords"].split(",")],
                "description": row.get("description", ""),
                "weight": float(row.get("weight", 1.0))
            })
        
        # Update knowledge base
        success = automation_service.categorization_service.update_knowledge_base_from_data(kb_entries)
        
        if success:
            kb_summary = automation_service.categorization_service.get_knowledge_base_summary()
            return {
                "success": True,
                "message": "Knowledge base updated successfully",
                "categories_count": len(kb_summary)
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update knowledge base")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/categorize-tickets")
async def categorize_tickets(request: Dict):
    """Categorize tickets using the knowledge base"""
    try:
        tickets_data = request.get('tickets', [])
        
        if not tickets_data:
            raise HTTPException(status_code=400, detail="No tickets provided")
        
        categorized_tickets = []
        
        for ticket_data in tickets_data:
            # Convert to ZohoTicket object
            from models import ZohoTicket
            from datetime import datetime
            
            ticket = ZohoTicket(
                id=ticket_data['id'],
                subject=ticket_data['subject'],
                description=ticket_data['description'],
                status=ticket_data.get('status', 'Open'),
                priority=ticket_data.get('priority', 'Medium'),
                created_time=datetime.fromisoformat(ticket_data['created_time'].replace('Z', '+00:00')),
                modified_time=datetime.fromisoformat(ticket_data['modified_time'].replace('Z', '+00:00')),
                contact_id=ticket_data.get('contact_id'),
                email=ticket_data.get('email')
            )
            
            # Categorize using the knowledge base
            category = automation_service.categorization_service.categorize_ticket(ticket)
            team = automation_service.categorization_service.get_team_for_category(category)
            
            # Add categorization to ticket data
            categorized_ticket = {
                **ticket_data,
                'predicted_category': category,
                'team': team
            }
            
            categorized_tickets.append(categorized_ticket)
        
        return {
            "success": True,
            "categorized_tickets": categorized_tickets,
            "count": len(categorized_tickets)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)