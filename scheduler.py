from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from loguru import logger
from services.automation_service import AutomationService
from config import settings

class SyncScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.automation_service = AutomationService()
        self.is_running = False
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Add scheduled job
        self.scheduler.add_job(
            func=self._scheduled_sync,
            trigger=IntervalTrigger(hours=settings.sync_interval_hours),
            id='sync_job',
            name='Zoho to ClickUp Sync',
            replace_existing=True,
            next_run_time=datetime.now()  # Run immediately on start
        )
        
        # Add daily cleanup job
        self.scheduler.add_job(
            func=self._cleanup_old_logs,
            trigger=CronTrigger(hour=2, minute=0),  # Run at 2 AM daily
            id='cleanup_job',
            name='Database Cleanup',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info(f"Scheduler started - sync every {settings.sync_interval_hours} hours")
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")
    
    async def _scheduled_sync(self):
        """Scheduled sync job"""
        try:
            logger.info("Starting scheduled sync...")
            result = await self.automation_service.run_sync()
            logger.info(f"Scheduled sync completed: {result.success} success, {result.errors} errors")
        except Exception as e:
            logger.error(f"Scheduled sync failed: {str(e)}")
    
    async def _cleanup_old_logs(self):
        """Clean up old log entries (keep last 1000)"""
        try:
            from database import get_db
            from models import SyncLog
            
            db = next(get_db())
            
            # Keep only the most recent 1000 entries
            total_count = db.query(SyncLog).count()
            if total_count > 1000:
                # Get IDs of old entries to delete
                old_entries = db.query(SyncLog.id).order_by(SyncLog.created_at.desc()).offset(1000).all()
                old_ids = [entry.id for entry in old_entries]
                
                # Delete old entries
                db.query(SyncLog).filter(SyncLog.id.in_(old_ids)).delete(synchronize_session=False)
                db.commit()
                
                deleted_count = len(old_ids)
                logger.info(f"Cleaned up {deleted_count} old log entries")
            
            db.close()
            
        except Exception as e:
            logger.error(f"Cleanup job failed: {str(e)}")
    
    async def trigger_manual_sync(self) -> dict:
        """Trigger manual sync and return result"""
        try:
            logger.info("Manual sync triggered")
            result = await self.automation_service.run_sync()
            return {
                "success": True,
                "result": result.dict(),
                "message": f"Sync completed: {result.success} success, {result.errors} errors"
            }
        except Exception as e:
            logger.error(f"Manual sync failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Sync failed"
            }
    
    def get_job_status(self) -> dict:
        """Get current job status"""
        if not self.is_running:
            return {"status": "stopped", "next_run": None}
        
        job = self.scheduler.get_job('sync_job')
        if job:
            return {
                "status": "running",
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "interval_hours": settings.sync_interval_hours
            }
        
        return {"status": "error", "next_run": None}