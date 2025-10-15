import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

from models import ZohoTicket, ProcessedTicket, ProcessingStatus, SyncResult, SyncLog
from services.zoho_service import ZohoService
from services.clickup_service import ClickUpService
from services.categorization_service import CategorizationService
from database import get_db
from config import settings

class AutomationService:
    def __init__(self):
        self.zoho_service = ZohoService()
        self.clickup_service = ClickUpService()
        self.categorization_service = CategorizationService()
    
    async def run_sync(self, hours_back: int = 24) -> SyncResult:
        """Main synchronization process"""
        start_time = datetime.now()
        logger.info(f"Starting sync process for tickets from last {hours_back} hours")
        
        try:
            # Step 1: Fetch tickets from Zoho
            tickets = await self.zoho_service.fetch_recent_tickets(hours_back)
            logger.info(f"Fetched {len(tickets)} tickets from Zoho")
            
            if not tickets:
                logger.info("No tickets to process")
                return SyncResult(
                    total_tickets=0,
                    processed=0,
                    duplicates=0,
                    errors=0,
                    success=0,
                    execution_time=0,
                    timestamp=start_time
                )
            
            # Step 2: Remove duplicates and check already processed
            unique_tickets = await self._filter_duplicates(tickets)
            logger.info(f"After duplicate removal: {len(unique_tickets)} tickets")
            
            # Step 3: Categorize tickets
            categorizations = self.categorization_service.batch_categorize(unique_tickets)
            
            # Step 4: Process each ticket
            results = await self._process_tickets(unique_tickets, categorizations)
            
            # Step 5: Generate summary
            execution_time = (datetime.now() - start_time).total_seconds()
            
            sync_result = SyncResult(
                total_tickets=len(tickets),
                processed=len(results),
                duplicates=len(tickets) - len(unique_tickets),
                errors=sum(1 for r in results if r.processing_status == ProcessingStatus.FAILED),
                success=sum(1 for r in results if r.processing_status == ProcessingStatus.SUCCESS),
                execution_time=execution_time,
                timestamp=start_time
            )
            
            logger.info(f"Sync completed in {execution_time:.2f}s: {sync_result.success} success, {sync_result.errors} errors, {sync_result.duplicates} duplicates")
            return sync_result
            
        except Exception as e:
            logger.error(f"Sync process failed: {str(e)}")
            raise
    
    async def _filter_duplicates(self, tickets: List[ZohoTicket]) -> List[ZohoTicket]:
        """Filter out duplicate and already processed tickets"""
        db = next(get_db())
        
        try:
            # Get already processed ticket IDs
            processed_ids = set(
                log.zoho_ticket_id for log in 
                db.query(SyncLog).filter(
                    SyncLog.status.in_([ProcessingStatus.SUCCESS, ProcessingStatus.DUPLICATE])
                ).all()
            )
            
            # Filter out already processed tickets
            new_tickets = [t for t in tickets if t.id not in processed_ids]
            
            # Find similar tickets within the current batch
            similar_groups = self.categorization_service.get_similar_tickets(new_tickets)
            
            # Keep only the most recent ticket from each similar group
            unique_tickets = []
            processed_in_batch = set()
            
            for group in similar_groups:
                # Sort by modified time, keep the most recent
                latest_ticket = max(group, key=lambda t: t.modified_time)
                unique_tickets.append(latest_ticket)
                
                # Mark others as duplicates in database
                for ticket in group:
                    if ticket.id != latest_ticket.id:
                        processed_in_batch.add(ticket.id)
                        await self._log_duplicate(db, ticket, latest_ticket.id)
            
            # Add tickets that weren't part of any similar group
            for ticket in new_tickets:
                if ticket.id not in processed_in_batch and not any(
                    ticket.id in [t.id for t in group] for group in similar_groups
                ):
                    unique_tickets.append(ticket)
            
            return unique_tickets
            
        finally:
            db.close()
    
    async def _process_tickets(self, tickets: List[ZohoTicket], categorizations: Dict[str, str]) -> List[ProcessedTicket]:
        """Process tickets with retry logic"""
        results = []
        
        for ticket in tickets:
            category = categorizations[ticket.id]
            team = settings.category_to_team_mapping[category]
            
            processed_ticket = ProcessedTicket(
                zoho_ticket=ticket,
                category=category,
                team=team,
                processing_status=ProcessingStatus.PENDING
            )
            
            # Process with retry logic
            success = await self._process_single_ticket_with_retry(processed_ticket)
            
            if success:
                processed_ticket.processing_status = ProcessingStatus.SUCCESS
            else:
                processed_ticket.processing_status = ProcessingStatus.FAILED
            
            results.append(processed_ticket)
            
            # Log to database
            await self._log_processing_result(processed_ticket)
        
        return results
    
    async def _process_single_ticket_with_retry(self, processed_ticket: ProcessedTicket) -> bool:
        """Process a single ticket with retry logic"""
        max_retries = settings.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                # Create ClickUp task
                task_id = await self.clickup_service.create_task(processed_ticket)
                processed_ticket.clickup_task_id = task_id
                
                logger.info(f"Successfully processed ticket {processed_ticket.zoho_ticket.id} -> ClickUp task {task_id}")
                return True
                
            except Exception as e:
                error_msg = str(e)
                processed_ticket.error_message = error_msg
                
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed for ticket {processed_ticket.zoho_ticket.id}: {error_msg}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to process ticket {processed_ticket.zoho_ticket.id} after {max_retries + 1} attempts: {error_msg}")
        
        return False
    
    async def _log_processing_result(self, processed_ticket: ProcessedTicket):
        """Log processing result to database"""
        db = next(get_db())
        
        try:
            log_entry = SyncLog(
                zoho_ticket_id=processed_ticket.zoho_ticket.id,
                clickup_task_id=processed_ticket.clickup_task_id,
                category=processed_ticket.category,
                team=processed_ticket.team,
                status=processed_ticket.processing_status.value,
                error_message=processed_ticket.error_message
            )
            
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log processing result: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    async def _log_duplicate(self, db: Session, duplicate_ticket: ZohoTicket, original_ticket_id: str):
        """Log duplicate ticket"""
        try:
            log_entry = SyncLog(
                zoho_ticket_id=duplicate_ticket.id,
                clickup_task_id=None,
                category="Duplicate",
                team="N/A",
                status=ProcessingStatus.DUPLICATE.value,
                error_message=f"Duplicate of ticket {original_ticket_id}"
            )
            
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log duplicate: {str(e)}")
            db.rollback()
    
    async def get_sync_history(self, limit: int = 50) -> List[SyncLog]:
        """Get recent sync history"""
        db = next(get_db())
        
        try:
            return db.query(SyncLog).order_by(SyncLog.created_at.desc()).limit(limit).all()
        finally:
            db.close()
    
    async def _log_sync_result(self, ticket_id: str, task_id: Optional[str], category: str, team: str, status: str, error_message: Optional[str] = None):
        """Log sync result to database"""
        db = next(get_db())
        
        try:
            log_entry = SyncLog(
                zoho_ticket_id=ticket_id,
                clickup_task_id=task_id,
                category=category,
                team=team,
                status=status,
                error_message=error_message
            )
            
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log sync result: {str(e)}")
            db.rollback()
        finally:
            db.close()

    async def get_stats(self) -> Dict:
        """Get processing statistics"""
        db = next(get_db())
        
        try:
            total_processed = db.query(SyncLog).count()
            successful = db.query(SyncLog).filter(SyncLog.status == ProcessingStatus.SUCCESS.value).count()
            failed = db.query(SyncLog).filter(SyncLog.status == ProcessingStatus.FAILED.value).count()
            duplicates = db.query(SyncLog).filter(SyncLog.status == ProcessingStatus.DUPLICATE.value).count()
            
            # Category breakdown
            category_stats = {}
            for category in settings.category_to_list_mapping.keys():
                count = db.query(SyncLog).filter(SyncLog.category == category).count()
                category_stats[category] = count
            
            return {
                "total_processed": total_processed,
                "successful": successful,
                "failed": failed,
                "duplicates": duplicates,
                "success_rate": (successful / total_processed * 100) if total_processed > 0 else 0,
                "category_breakdown": category_stats
            }
            
        finally:
            db.close()