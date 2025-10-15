import requests
import asyncio
from typing import Optional, List
from loguru import logger
from config import settings
from models import ClickUpTask, ProcessedTicket

class ClickUpService:
    def __init__(self):
        self.base_url = "https://api.clickup.com/api/v2"
        self.headers = {
            "Authorization": settings.clickup_api_token,
            "Content-Type": "application/json"
        }
    
    async def create_task(self, processed_ticket: ProcessedTicket) -> Optional[str]:
        """Create a task in ClickUp and return task ID"""
        try:
            list_id = settings.category_to_list_mapping.get(processed_ticket.category)
            if not list_id:
                raise ValueError(f"No list ID found for category: {processed_ticket.category}")
            
            # Prepare task data
            task_data = {
                "name": f"[{processed_ticket.category}] {processed_ticket.zoho_ticket.subject}",
                "description": self._format_task_description(processed_ticket),
                "status": "Open",
                "priority": self._map_priority(processed_ticket.zoho_ticket.priority),
                "tags": [
                    processed_ticket.team.lower().replace("/", "-"),
                    processed_ticket.category.lower().replace(" ", "-"),
                    "zoho-import"
                ],
                "custom_fields": [
                    {
                        "id": "zoho_ticket_id",
                        "value": processed_ticket.zoho_ticket.id
                    }
                ]
            }
            
            url = f"{self.base_url}/list/{list_id}/task"
            
            response = requests.post(url, json=task_data, headers=self.headers)
            response.raise_for_status()
            
            task_response = response.json()
            task_id = task_response["id"]
            
            logger.info(f"Created ClickUp task {task_id} for Zoho ticket {processed_ticket.zoho_ticket.id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating ClickUp task for ticket {processed_ticket.zoho_ticket.id}: {str(e)}")
            raise
    
    def _format_task_description(self, processed_ticket: ProcessedTicket) -> str:
        """Format task description with ticket details"""
        ticket = processed_ticket.zoho_ticket
        
        description = f"""
**Zoho Ticket Details**
- **Ticket ID**: {ticket.id}
- **Status**: {ticket.status}
- **Priority**: {ticket.priority}
- **Created**: {ticket.created_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Contact Email**: {ticket.email or 'N/A'}

**Category**: {processed_ticket.category}
**Assigned Team**: {processed_ticket.team}

**Original Description**:
{ticket.description}

---
*This task was automatically created from Zoho Desk ticket #{ticket.id}*
        """.strip()
        
        return description
    
    def _map_priority(self, zoho_priority: str) -> int:
        """Map Zoho priority to ClickUp priority"""
        priority_mapping = {
            "High": 1,
            "Normal": 2,
            "Medium": 2,
            "Low": 3,
            "": 2  # Default to normal
        }
        return priority_mapping.get(zoho_priority, 2)
    
    async def get_task(self, task_id: str) -> Optional[dict]:
        """Get task details from ClickUp"""
        try:
            url = f"{self.base_url}/task/{task_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching ClickUp task {task_id}: {str(e)}")
            return None
    
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status in ClickUp"""
        try:
            url = f"{self.base_url}/task/{task_id}"
            data = {"status": status}
            
            response = requests.put(url, json=data, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Updated ClickUp task {task_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating ClickUp task {task_id}: {str(e)}")
            return False
    
    async def add_comment(self, task_id: str, comment: str) -> bool:
        """Add comment to ClickUp task"""
        try:
            url = f"{self.base_url}/task/{task_id}/comment"
            data = {"comment_text": comment}
            
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Added comment to ClickUp task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding comment to ClickUp task {task_id}: {str(e)}")
            return False
    
    async def create_task_from_data(self, ticket_data: dict) -> Optional[str]:
        """Create a task in ClickUp from ticket data dictionary"""
        try:
            category = ticket_data.get('predicted_category', 'Learning Portal Issues')
            list_id = settings.category_to_list_mapping.get(category)
            
            if not list_id:
                raise ValueError(f"No list ID found for category: {category}")
            
            # Prepare task data
            task_data_payload = {
                "name": f"[{category}] {ticket_data.get('subject', 'No Subject')}",
                "description": self._format_task_description_from_data(ticket_data),
                "status": "Open",
                "priority": self._map_priority(ticket_data.get('priority', '')),
                "tags": [
                    ticket_data.get('team', '').lower().replace("/", "-"),
                    category.lower().replace(" ", "-"),
                    "zoho-import"
                ],
                "custom_fields": [
                    {
                        "id": "zoho_ticket_id",
                        "value": ticket_data.get('id', '')
                    }
                ]
            }
            
            url = f"{self.base_url}/list/{list_id}/task"
            
            response = requests.post(url, json=task_data_payload, headers=self.headers)
            response.raise_for_status()
            
            task_response = response.json()
            task_id = task_response["id"]
            
            logger.info(f"Created ClickUp task {task_id} for Zoho ticket {ticket_data.get('id')}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating ClickUp task for ticket {ticket_data.get('id')}: {str(e)}")
            raise

    def _format_task_description_from_data(self, ticket_data: dict) -> str:
        """Format task description from ticket data dictionary"""
        description = f"""
**Zoho Ticket Details**
- **Ticket ID**: {ticket_data.get('id', 'N/A')}
- **Status**: {ticket_data.get('status', 'N/A')}
- **Priority**: {ticket_data.get('priority', 'N/A')}
- **Contact Email**: {ticket_data.get('email', 'N/A')}

**Category**: {ticket_data.get('predicted_category', 'N/A')}
**Assigned Team**: {ticket_data.get('team', 'N/A')}

**Original Description**:
{ticket_data.get('description', 'No description provided')}

---
*This task was automatically created from Zoho Desk ticket #{ticket_data.get('id', 'N/A')}*
        """.strip()
        
        return description

    async def get_lists(self) -> List[dict]:
        """Get all lists in the team"""
        try:
            url = f"{self.base_url}/team/{settings.clickup_team_id}/list"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json().get("lists", [])
            
        except Exception as e:
            logger.error(f"Error fetching ClickUp lists: {str(e)}")
            return []