from pydantic_settings import BaseSettings
from typing import Dict, Optional
import os

class Settings(BaseSettings):
    # Zoho Configuration
    zoho_client_id: str
    zoho_client_secret: str
    zoho_refresh_token: str
    zoho_organization_id: str
    
    # ClickUp Configuration
    clickup_api_token: str
    clickup_team_id: str
    
    # ClickUp List IDs
    learning_portal_list_id: str
    feature_flags_list_id: str
    content_access_list_id: str
    portal_access_list_id: str
    content_bundle_list_id: str
    quiz_issues_list_id: str
    units_unlock_list_id: str
    instructor_list_id: str
    grooming_check_list_id: str
    
    # Application Settings
    database_url: str = "sqlite:///./automation.db"
    log_level: str = "INFO"
    sync_interval_hours: int = 1
    max_retries: int = 3
    
    class Config:
        env_file = ".env"
    
    @property
    def category_to_list_mapping(self) -> Dict[str, str]:
        return {
            "Platform Issues": self.learning_portal_list_id,
            "Facilities": self.feature_flags_list_id,
            "Session Timing Issues": self.content_access_list_id,
            "Tech QA Report Issue": self.portal_access_list_id,
            "Other On-Ground Issues": self.content_bundle_list_id,
            "Student Portal": self.quiz_issues_list_id,
            "Scheduling Issue": self.units_unlock_list_id,
            "Session Handling Issues": self.instructor_list_id,
            "Learning Portal Issues": self.grooming_check_list_id,
            "Feature Flags / Roles Adding": self.learning_portal_list_id,
            "Content Access": self.feature_flags_list_id,
            "Portal Access": self.content_access_list_id,
            "Content Bundle": self.portal_access_list_id,
            "Quiz Issues": self.content_bundle_list_id,
            "Instructor Categories Adding": self.quiz_issues_list_id,
            "Units Unlock": self.units_unlock_list_id,
            "Data mismatching in lookers studio": self.instructor_list_id,
        }
    
    @property
    def category_to_team_mapping(self) -> Dict[str, str]:
        return {
            "Platform Issues": "Product/Tech",
            "Facilities": "Facilities",
            "Session Timing Issues": "Curriculum/Content",
            "Tech QA Report Issue": "Product/Tech",
            "Other On-Ground Issues": "Facilities",
            "Student Portal": "Product/Tech",
            "Scheduling Issue": "Curriculum/Content",
            "Session Handling Issues": "Instructor",
            "Learning Portal Issues": "Product/Tech",
            "Feature Flags / Roles Adding": "Product/Tech",
            "Content Access": "Curriculum/Content",
            "Portal Access": "Product/Tech",
            "Content Bundle": "Curriculum/Content",
            "Quiz Issues": "Curriculum/Content",
            "Instructor Categories Adding": "Instructor",
            "Units Unlock": "Curriculum/Content",
            "Data mismatching in lookers studio": "DA Team",
        }

settings = Settings()