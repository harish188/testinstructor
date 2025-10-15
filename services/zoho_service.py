import requests
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger
from config import settings
from models import ZohoTicket

class ZohoService:
    def __init__(self):
        self.base_url = f"https://desk.zoho.com/api/v1"
        self.access_token = None
        self.token_expires_at = None
    
    async def get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            "refresh_token": settings.zoho_refresh_token,
            "client_id": settings.zoho_client_id,
            "client_secret": settings.zoho_client_secret,
            "grant_type": "refresh_token"
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
        
        logger.info("Zoho access token refreshed successfully")
        return self.access_token
    
    async def get_headers(self) -> dict:
        """Get headers with valid access token"""
        token = await self.get_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json",
            "orgId": settings.zoho_organization_id
        }
    
    async def fetch_recent_tickets(self, hours_back: int = 24) -> List[ZohoTicket]:
        """Fetch tickets from the last N hours"""
        try:
            headers = await self.get_headers()
            
            # Calculate time filter
            from_time = datetime.now() - timedelta(hours=hours_back)
            from_time_str = from_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            
            url = f"{self.base_url}/tickets"
            params = {
                "limit": 100,
                "sortBy": "modifiedTime",
                "modifiedTime": from_time_str,
                "include": "contacts"
            }
            
            all_tickets = []
            
            while url:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                tickets_data = data.get("data", [])
                
                for ticket_data in tickets_data:
                    ticket = self._parse_ticket(ticket_data)
                    if ticket:
                        all_tickets.append(ticket)
                
                # Check for pagination
                url = data.get("next", None)
                params = None  # Clear params for subsequent requests
                
                logger.info(f"Fetched {len(tickets_data)} tickets from current page")
            
            logger.info(f"Total tickets fetched: {len(all_tickets)}")
            return all_tickets
            
        except Exception as e:
            logger.error(f"Error fetching tickets from Zoho: {str(e)}")
            raise
    
    def _parse_ticket(self, ticket_data: dict) -> Optional[ZohoTicket]:
        """Parse ticket data from Zoho API response"""
        try:
            return ZohoTicket(
                id=ticket_data["id"],
                subject=ticket_data.get("subject", ""),
                description=ticket_data.get("description", ""),
                status=ticket_data.get("status", ""),
                priority=ticket_data.get("priority", ""),
                created_time=datetime.fromisoformat(
                    ticket_data["createdTime"].replace("Z", "+00:00")
                ),
                modified_time=datetime.fromisoformat(
                    ticket_data["modifiedTime"].replace("Z", "+00:00")
                ),
                contact_id=ticket_data.get("contactId"),
                email=ticket_data.get("contact", {}).get("email")
            )
        except Exception as e:
            logger.warning(f"Failed to parse ticket {ticket_data.get('id', 'unknown')}: {str(e)}")
            return None
    
    async def get_ticket_details(self, ticket_id: str) -> Optional[ZohoTicket]:
        """Get detailed information for a specific ticket"""
        try:
            headers = await self.get_headers()
            url = f"{self.base_url}/tickets/{ticket_id}"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            ticket_data = response.json()
            return self._parse_ticket(ticket_data)
            
        except Exception as e:
            logger.error(f"Error fetching ticket {ticket_id}: {str(e)}")
            return None