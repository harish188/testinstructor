import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from loguru import logger

from models import KnowledgeBase
from database import get_db

class KnowledgeBaseService:
    def __init__(self):
        self.ensure_default_knowledge_base()
    
    def ensure_default_knowledge_base(self):
        """Ensure default knowledge base exists in database"""
        db = next(get_db())
        try:
            # Check if knowledge base is empty
            count = db.query(KnowledgeBase).count()
            if count == 0:
                logger.info("Initializing default knowledge base...")
                self.load_default_knowledge_base(db)
        finally:
            db.close()
    
    def load_default_knowledge_base(self, db: Session):
        """Load default knowledge base into database"""
        default_kb = [
            {
                "category": "Platform Issues",
                "team": "Product/Tech",
                "keywords": ["platform", "system", "technical", "bug", "error", "crash", "server", "database", "api", "integration", "system down", "technical issue"],
                "description": "Technical issues with the platform infrastructure",
                "weight": 1.0
            },
            {
                "category": "Facilities",
                "team": "Facilities",
                "keywords": ["facilities", "room", "equipment", "hardware", "projector", "wifi", "internet", "network", "venue", "location", "building", "classroom"],
                "description": "Physical facilities and equipment issues",
                "weight": 1.0
            },
            {
                "category": "Session Timing Issues",
                "team": "Curriculum/Content",
                "keywords": ["timing", "schedule", "delay", "late", "early", "reschedule", "time", "duration", "session time", "timing issue"],
                "description": "Issues related to session timing and scheduling",
                "weight": 1.0
            },
            {
                "category": "Tech QA Report Issue",
                "team": "Product/Tech",
                "keywords": ["qa", "quality", "testing", "report", "bug report", "defect", "issue report", "technical report", "quality assurance"],
                "description": "Quality assurance and technical reporting issues",
                "weight": 1.0
            },
            {
                "category": "Other On-Ground Issues",
                "team": "Facilities",
                "keywords": ["on-ground", "physical", "venue", "location", "setup", "arrangement", "logistics", "on-site"],
                "description": "Other physical or logistical issues",
                "weight": 1.0
            },
            {
                "category": "Student Portal",
                "team": "Product/Tech",
                "keywords": ["student portal", "student login", "student access", "student dashboard", "student account", "student interface"],
                "description": "Issues specific to student portal access and functionality",
                "weight": 1.0
            },
            {
                "category": "Scheduling Issue",
                "team": "Curriculum/Content",
                "keywords": ["scheduling", "calendar", "appointment", "booking", "slot", "availability", "reschedule", "schedule conflict"],
                "description": "General scheduling and calendar issues",
                "weight": 1.0
            },
            {
                "category": "Session Handling Issues",
                "team": "Instructor",
                "keywords": ["session handling", "instructor", "teaching", "class management", "session conduct", "classroom management"],
                "description": "Issues related to how sessions are conducted by instructors",
                "weight": 1.0
            },
            {
                "category": "Learning Portal Issues",
                "team": "Product/Tech",
                "keywords": ["learning portal", "portal", "login", "access", "authentication", "password", "account", "portal access"],
                "description": "General learning portal access and functionality issues",
                "weight": 1.0
            },
            {
                "category": "Feature Flags / Roles Adding",
                "team": "Product/Tech",
                "keywords": ["feature flag", "role", "permission", "access level", "user role", "admin", "privileges", "feature toggle"],
                "description": "Adding or modifying user roles and feature flags",
                "weight": 1.0
            },
            {
                "category": "Content Access",
                "team": "Curriculum/Content",
                "keywords": ["content access", "material", "resource", "document", "video", "lesson", "module", "learning material"],
                "description": "Issues accessing learning content and materials",
                "weight": 1.0
            },
            {
                "category": "Portal Access",
                "team": "Product/Tech",
                "keywords": ["portal access", "login", "authentication", "password reset", "account locked", "access denied"],
                "description": "General portal access and login issues",
                "weight": 1.0
            },
            {
                "category": "Content Bundle",
                "team": "Curriculum/Content",
                "keywords": ["content bundle", "curriculum", "course", "bundle", "package", "learning path", "course material"],
                "description": "Issues with content bundles and curriculum packages",
                "weight": 1.0
            },
            {
                "category": "Quiz Issues",
                "team": "Curriculum/Content",
                "keywords": ["quiz", "assessment", "test", "exam", "evaluation", "score", "grading", "marks", "question", "answer"],
                "description": "Issues related to quizzes and assessments",
                "weight": 1.0
            },
            {
                "category": "Instructor Categories Adding",
                "team": "Instructor",
                "keywords": ["instructor category", "instructor role", "teacher", "mentor", "faculty", "instructor permissions", "teaching role"],
                "description": "Adding or managing instructor categories and permissions",
                "weight": 1.0
            },
            {
                "category": "Units Unlock",
                "team": "Curriculum/Content",
                "keywords": ["units unlock", "unlock", "locked", "progression", "next unit", "module unlock", "course progression"],
                "description": "Issues with unlocking units or course progression",
                "weight": 1.0
            },
            {
                "category": "Data mismatching in lookers studio",
                "team": "DA Team",
                "keywords": ["data mismatch", "looker", "studio", "analytics", "reporting", "dashboard", "data inconsistency", "looker studio"],
                "description": "Data inconsistencies in Looker Studio reports",
                "weight": 1.0
            }
        ]
        
        for kb_entry in default_kb:
            kb_record = KnowledgeBase(
                category=kb_entry["category"],
                team=kb_entry["team"],
                keywords=json.dumps(kb_entry["keywords"]),
                description=kb_entry["description"],
                weight=kb_entry["weight"]
            )
            db.add(kb_record)
        
        db.commit()
        logger.info(f"Loaded {len(default_kb)} default knowledge base entries")
    
    def add_knowledge_base_entries(self, entries: List[Dict]) -> bool:
        """Add multiple knowledge base entries"""
        db = next(get_db())
        try:
            for entry in entries:
                # Check if category already exists
                existing = db.query(KnowledgeBase).filter(
                    KnowledgeBase.category == entry["category"]
                ).first()
                
                if existing:
                    # Update existing entry
                    existing.team = entry["team"]
                    existing.keywords = json.dumps(entry["keywords"])
                    existing.description = entry.get("description", "")
                    existing.weight = entry.get("weight", 1.0)
                    existing.is_active = entry.get("is_active", True)
                else:
                    # Create new entry
                    kb_record = KnowledgeBase(
                        category=entry["category"],
                        team=entry["team"],
                        keywords=json.dumps(entry["keywords"]),
                        description=entry.get("description", ""),
                        weight=entry.get("weight", 1.0),
                        is_active=entry.get("is_active", True)
                    )
                    db.add(kb_record)
            
            db.commit()
            logger.info(f"Added/updated {len(entries)} knowledge base entries")
            return True
            
        except Exception as e:
            logger.error(f"Error adding knowledge base entries: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_all_knowledge_base(self) -> List[Dict]:
        """Get all active knowledge base entries"""
        db = next(get_db())
        try:
            entries = db.query(KnowledgeBase).filter(
                KnowledgeBase.is_active == True
            ).all()
            
            result = []
            for entry in entries:
                result.append({
                    "id": entry.id,
                    "category": entry.category,
                    "team": entry.team,
                    "keywords": json.loads(entry.keywords),
                    "description": entry.description,
                    "weight": entry.weight,
                    "is_active": entry.is_active
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting knowledge base: {str(e)}")
            return []
        finally:
            db.close()
    
    def get_categorization_rules(self) -> Dict[str, Dict]:
        """Get categorization rules for the categorization service"""
        kb_entries = self.get_all_knowledge_base()
        rules = {}
        
        for entry in kb_entries:
            category = entry["category"]
            keywords = entry["keywords"]
            weight = entry["weight"]
            
            # Create rules with different weights based on keyword specificity
            category_rules = []
            
            # High weight for multi-word keywords
            multi_word_keywords = [kw for kw in keywords if len(kw.split()) > 1]
            if multi_word_keywords:
                category_rules.append({
                    "patterns": multi_word_keywords,
                    "weight": int(15 * weight)
                })
            
            # Medium weight for single keywords
            single_word_keywords = [kw for kw in keywords if len(kw.split()) == 1]
            if single_word_keywords:
                category_rules.append({
                    "patterns": single_word_keywords,
                    "weight": int(10 * weight)
                })
            
            rules[category] = {
                "rules": category_rules,
                "team": entry["team"]
            }
        
        return rules
    
    def update_knowledge_base_from_data(self, kb_data: List[Dict]) -> bool:
        """Update entire knowledge base from provided data"""
        db = next(get_db())
        try:
            # Deactivate all existing entries
            db.query(KnowledgeBase).update({"is_active": False})
            
            # Add new entries
            for entry in kb_data:
                kb_record = KnowledgeBase(
                    category=entry["category"],
                    team=entry["team"],
                    keywords=json.dumps(entry["keywords"]),
                    description=entry.get("description", ""),
                    weight=entry.get("weight", 1.0),
                    is_active=True
                )
                db.add(kb_record)
            
            db.commit()
            logger.info(f"Updated knowledge base with {len(kb_data)} entries")
            return True
            
        except Exception as e:
            logger.error(f"Error updating knowledge base: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_team_for_category(self, category: str) -> str:
        """Get team assignment for a category"""
        db = next(get_db())
        try:
            entry = db.query(KnowledgeBase).filter(
                KnowledgeBase.category == category,
                KnowledgeBase.is_active == True
            ).first()
            
            if entry:
                return entry.team
            else:
                return "Product/Tech"  # Default team
                
        except Exception as e:
            logger.error(f"Error getting team for category {category}: {str(e)}")
            return "Product/Tech"
        finally:
            db.close()
    
    def get_knowledge_base_summary(self) -> List[Dict]:
        """Get summary of current knowledge base"""
        kb_entries = self.get_all_knowledge_base()
        
        summary = []
        for entry in kb_entries:
            summary.append({
                "category": entry["category"],
                "team": entry["team"],
                "keyword_count": len(entry["keywords"]),
                "description": entry["description"][:100] + "..." if len(entry["description"]) > 100 else entry["description"]
            })
        
        return summary