from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

Base = declarative_base()

class SyncLog(Base):
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    zoho_ticket_id = Column(String, unique=True, index=True)
    clickup_task_id = Column(String, nullable=True)
    category = Column(String, nullable=False)
    team = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, success, failed, duplicate
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False, index=True)
    team = Column(String, nullable=False, index=True)
    keywords = Column(Text, nullable=False)  # JSON string of keywords
    description = Column(Text, nullable=True)
    weight = Column(Float, default=1.0)  # Weight for this category
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    DUPLICATE = "duplicate"

class TicketCategory(str, Enum):
    LEARNING_PORTAL = "Learning Portal Issues"
    FEATURE_FLAGS = "Feature Flags / Roles Adding"
    CONTENT_ACCESS = "Content Access"
    PORTAL_ACCESS = "Portal Access"
    CONTENT_BUNDLE = "Content Bundle"
    QUIZ_ISSUES = "Quiz Issues"
    UNITS_UNLOCK = "Units Unlock"
    INSTRUCTOR_CATEGORIES = "Instructor Categories Adding"
    GROOMING_CHECK = "Grooming Check Issues"

class ZohoTicket(BaseModel):
    id: str
    subject: str
    description: str
    status: str
    priority: str
    created_time: datetime
    modified_time: datetime
    contact_id: Optional[str] = None
    email: Optional[str] = None

class ClickUpTask(BaseModel):
    name: str
    description: str
    list_id: str
    priority: Optional[int] = None
    status: str = "Open"
    tags: List[str] = []

class ProcessedTicket(BaseModel):
    zoho_ticket: ZohoTicket
    category: TicketCategory
    team: str
    clickup_task_id: Optional[str] = None
    processing_status: ProcessingStatus
    error_message: Optional[str] = None

class SyncResult(BaseModel):
    total_tickets: int
    processed: int
    duplicates: int
    errors: int
    success: int
    execution_time: float
    timestamp: datetime