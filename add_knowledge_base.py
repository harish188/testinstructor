#!/usr/bin/env python3
"""
Script to add knowledge base entries directly to the database
Usage: python add_knowledge_base.py
"""

import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add current directory to path
sys.path.append('.')

from services.knowledge_base_service import KnowledgeBaseService
from database import create_tables

console = Console()

def add_knowledge_base_entries():
    """Add your knowledge base entries here"""
    
    # Your comprehensive knowledge base
    knowledge_base_entries = [
        {
            "category": "Platform Issues",
            "team": "Product/Tech",
            "keywords": ["platform", "system", "technical", "bug", "error", "crash", "server", "database", "api", "integration", "system down", "technical issue", "platform crash", "system failure"],
            "description": "Technical issues with the platform infrastructure",
            "weight": 1.2
        },
        {
            "category": "Facilities",
            "team": "Facilities",
            "keywords": ["facilities", "room", "equipment", "hardware", "projector", "wifi", "internet", "network", "venue", "location", "building", "classroom", "room booking", "equipment failure"],
            "description": "Physical facilities and equipment issues",
            "weight": 1.0
        },
        {
            "category": "Session Timing Issues",
            "team": "Curriculum/Content",
            "keywords": ["timing", "schedule", "delay", "late", "early", "reschedule", "time", "duration", "session time", "timing issue", "session delay", "schedule conflict"],
            "description": "Issues related to session timing and scheduling",
            "weight": 1.1
        },
        {
            "category": "Tech QA Report Issue",
            "team": "Product/Tech",
            "keywords": ["qa", "quality", "testing", "report", "bug report", "defect", "issue report", "technical report", "quality assurance", "test results", "qa testing"],
            "description": "Quality assurance and technical reporting issues",
            "weight": 1.0
        },
        {
            "category": "Other On-Ground Issues",
            "team": "Facilities",
            "keywords": ["on-ground", "physical", "venue", "location", "setup", "arrangement", "logistics", "on-site", "ground support", "physical setup"],
            "description": "Other physical or logistical issues",
            "weight": 1.0
        },
        {
            "category": "Student Portal",
            "team": "Product/Tech",
            "keywords": ["student portal", "student login", "student access", "student dashboard", "student account", "student interface", "student platform"],
            "description": "Issues specific to student portal access and functionality",
            "weight": 1.1
        },
        {
            "category": "Scheduling Issue",
            "team": "Curriculum/Content",
            "keywords": ["scheduling", "calendar", "appointment", "booking", "slot", "availability", "reschedule", "schedule conflict", "calendar issue", "booking problem"],
            "description": "General scheduling and calendar issues",
            "weight": 1.0
        },
        {
            "category": "Session Handling Issues",
            "team": "Instructor",
            "keywords": ["session handling", "instructor", "teaching", "class management", "session conduct", "classroom management", "instructor support", "teaching issue"],
            "description": "Issues related to how sessions are conducted by instructors",
            "weight": 1.0
        },
        {
            "category": "Learning Portal Issues",
            "team": "Product/Tech",
            "keywords": ["learning portal", "portal", "login", "access", "authentication", "password", "account", "portal access", "portal login", "learning platform"],
            "description": "General learning portal access and functionality issues",
            "weight": 1.0
        },
        {
            "category": "Feature Flags / Roles Adding",
            "team": "Product/Tech",
            "keywords": ["feature flag", "role", "permission", "access level", "user role", "admin", "privileges", "feature toggle", "role assignment", "permission issue"],
            "description": "Adding or modifying user roles and feature flags",
            "weight": 1.0
        },
        {
            "category": "Content Access",
            "team": "Curriculum/Content",
            "keywords": ["content access", "material", "resource", "document", "video", "lesson", "module", "learning material", "content issue", "material access"],
            "description": "Issues accessing learning content and materials",
            "weight": 1.0
        },
        {
            "category": "Portal Access",
            "team": "Product/Tech",
            "keywords": ["portal access", "login", "authentication", "password reset", "account locked", "access denied", "login issue", "authentication error"],
            "description": "General portal access and login issues",
            "weight": 1.0
        },
        {
            "category": "Content Bundle",
            "team": "Curriculum/Content",
            "keywords": ["content bundle", "curriculum", "course", "bundle", "package", "learning path", "course material", "curriculum package", "content package"],
            "description": "Issues with content bundles and curriculum packages",
            "weight": 1.0
        },
        {
            "category": "Quiz Issues",
            "team": "Curriculum/Content",
            "keywords": ["quiz", "assessment", "test", "exam", "evaluation", "score", "grading", "marks", "question", "answer", "quiz problem", "assessment issue"],
            "description": "Issues related to quizzes and assessments",
            "weight": 1.1
        },
        {
            "category": "Instructor Categories Adding",
            "team": "Instructor",
            "keywords": ["instructor category", "instructor role", "teacher", "mentor", "faculty", "instructor permissions", "teaching role", "instructor access"],
            "description": "Adding or managing instructor categories and permissions",
            "weight": 1.0
        },
        {
            "category": "Units Unlock",
            "team": "Curriculum/Content",
            "keywords": ["units unlock", "unlock", "locked", "progression", "next unit", "module unlock", "course progression", "unit access", "locked content"],
            "description": "Issues with unlocking units or course progression",
            "weight": 1.0
        },
        {
            "category": "Data mismatching in lookers studio",
            "team": "DA Team",
            "keywords": ["data mismatch", "looker", "studio", "analytics", "reporting", "dashboard", "data inconsistency", "looker studio", "data issue", "report problem"],
            "description": "Data inconsistencies in Looker Studio reports",
            "weight": 1.0
        }
    ]
    
    return knowledge_base_entries

def main():
    console.print(Panel.fit("📚 Knowledge Base Setup", style="bold blue"))
    
    # Create database tables
    create_tables()
    
    # Initialize knowledge base service
    kb_service = KnowledgeBaseService()
    
    # Get knowledge base entries
    entries = add_knowledge_base_entries()
    
    console.print(f"📝 Adding {len(entries)} knowledge base entries...")
    
    # Add entries to database
    success = kb_service.update_knowledge_base_from_data(entries)
    
    if success:
        console.print("✅ Knowledge base entries added successfully!", style="green")
        
        # Display summary
        summary = kb_service.get_knowledge_base_summary()
        
        table = Table(title="📊 Knowledge Base Summary")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Team", style="yellow", no_wrap=True)
        table.add_column("Keywords", style="green")
        table.add_column("Description", style="white", max_width=40)
        
        for entry in summary:
            table.add_row(
                entry["category"],
                entry["team"],
                f"{entry['keyword_count']} keywords",
                entry["description"]
            )
        
        console.print(table)
        
        # Show team distribution
        team_counts = {}
        for entry in summary:
            team = entry["team"]
            team_counts[team] = team_counts.get(team, 0) + 1
        
        console.print("\n📊 Team Distribution:")
        for team, count in team_counts.items():
            console.print(f"  • {team}: {count} categories")
        
        console.print(f"\n🎯 Total: {len(summary)} categories across {len(team_counts)} teams")
        console.print("\n🚀 Knowledge base is ready! Start the server with: python main.py server")
        
    else:
        console.print("❌ Failed to add knowledge base entries", style="red")
        sys.exit(1)

if __name__ == "__main__":
    main()