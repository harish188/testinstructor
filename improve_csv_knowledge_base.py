#!/usr/bin/env python3
"""
Improved CSV knowledge base loader with better keyword extraction and manual refinement
"""

import sys
import csv
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

sys.path.append('.')

from services.knowledge_base_service import KnowledgeBaseService
from database import create_tables

console = Console()

def create_improved_knowledge_base():
    """Create improved knowledge base with manually curated keywords based on CSV analysis"""
    
    # Manually curated knowledge base based on CSV analysis
    knowledge_base_entries = [
        {
            "category": "Platform Issues",
            "team": "Product/Tech",
            "keywords": [
                "platform", "instructor portal", "portal", "recording", "upload", "submit", "audio recording",
                "video recording", "technical issue", "system", "portal not working", "recording not submitted",
                "recording failed", "upload issue", "platform not responding", "portal glitch", "system down",
                "recording not uploading", "portal issue", "technical problem", "system error", "platform error"
            ],
            "description": "Technical issues with instructor portal, recording, uploading, and platform functionality",
            "weight": 1.2
        },
        {
            "category": "Facilities",
            "team": "Facilities",
            "keywords": [
                "mic", "microphone", "battery", "batteries", "projector", "screen", "tv", "display",
                "wifi", "internet", "network", "connectivity", "power cut", "electricity", "power",
                "classroom", "room", "hall", "equipment", "facilities", "infrastructure", "ac", "air conditioning",
                "fan", "noise", "marker", "duster", "extension board", "chairs", "benches", "broken"
            ],
            "description": "Physical facilities, equipment, infrastructure, and classroom-related issues",
            "weight": 1.1
        },
        {
            "category": "Session Timing Issues", 
            "team": "Curriculum/Content",
            "keywords": [
                "timing", "time", "late", "delay", "delayed", "started late", "ended late", "session timing",
                "duration", "extra time", "overtime", "time management", "session time", "timing issue",
                "page wait", "waiting", "slow", "takes time", "time consuming", "rushed", "hurry"
            ],
            "description": "Issues related to session timing, delays, and time management",
            "weight": 1.0
        },
        {
            "category": "Tech QA Report Issue",
            "team": "Product/Tech", 
            "keywords": [
                "qa report", "report", "evaluation", "feedback", "rating", "score", "assessment",
                "transcript", "report generation", "report not generated", "qa tool", "quality assurance",
                "rubric", "evaluation rubric", "feedback rating", "report issue", "transcript issue",
                "evaluation error", "scoring issue", "report problem", "qa problem"
            ],
            "description": "Issues with QA reports, evaluations, feedback, and assessment tools",
            "weight": 1.0
        },
        {
            "category": "Other On Ground Issues",
            "team": "Facilities",
            "keywords": [
                "on ground", "ground", "physical", "venue", "location", "setup", "arrangement", "logistics",
                "on-site", "ground support", "physical setup", "venue issue", "location problem",
                "logistical issue", "ground level", "physical problem", "site issue"
            ],
            "description": "Other physical, logistical, and on-ground operational issues",
            "weight": 1.0
        },
        {
            "category": "Student Portal",
            "team": "Product/Tech",
            "keywords": [
                "student portal", "learning portal", "portal access", "students access", "portal login",
                "students unable", "portal blocked", "access denied", "login issue", "authentication",
                "student account", "portal problem", "access issue", "login problem", "portal not working",
                "students cannot access", "portal down", "access blocked", "login failed"
            ],
            "description": "Issues with student portal access, login, and authentication",
            "weight": 1.1
        },
        {
            "category": "Scheduling Issue",
            "team": "Curriculum/Content",
            "keywords": [
                "scheduling", "schedule", "scheduled", "not scheduled", "session not scheduled",
                "timetable", "calendar", "appointment", "booking", "slot", "availability",
                "reschedule", "schedule conflict", "scheduling problem", "session scheduling",
                "class scheduling", "schedule issue", "timing conflict", "schedule error"
            ],
            "description": "Issues with session scheduling, timetables, and calendar management",
            "weight": 1.0
        },
        {
            "category": "Session Handling Issues",
            "team": "Instructor",
            "keywords": [
                "session handling", "class management", "student interaction", "students not responding",
                "students playing", "mobile phones", "distraction", "attention", "engagement",
                "classroom management", "student behavior", "discipline", "interaction", "participation",
                "students talking", "noise", "disruption", "classroom control", "teaching issue",
                "students not attentive", "behavioral issue", "class control"
            ],
            "description": "Issues related to managing sessions, student behavior, and classroom control",
            "weight": 1.0
        }
    ]
    
    return knowledge_base_entries

def load_improved_knowledge_base():
    """Load improved knowledge base into database"""
    console.print(Panel.fit("🚀 Loading Improved CSV Knowledge Base", style="bold green"))
    
    # Get improved knowledge base entries
    kb_entries = create_improved_knowledge_base()
    
    # Display preview
    table = Table(title="📊 Improved Knowledge Base Preview")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Team", style="yellow", no_wrap=True)
    table.add_column("Keywords Count", style="green")
    table.add_column("Weight", style="magenta")
    table.add_column("Sample Keywords", style="white", max_width=40)
    
    for entry in kb_entries:
        sample_keywords = ", ".join(entry["keywords"][:5])
        
        table.add_row(
            entry["category"],
            entry["team"],
            str(len(entry["keywords"])),
            str(entry["weight"]),
            sample_keywords
        )
    
    console.print(table)
    
    # Ask for confirmation
    console.print(f"\n🔍 Ready to load {len(kb_entries)} improved categories into database.")
    confirm = input("Do you want to proceed? (y/N): ").lower().strip()
    
    if confirm == 'y' or confirm == 'yes':
        # Create database tables
        create_tables()
        
        # Initialize knowledge base service
        kb_service = KnowledgeBaseService()
        
        # Load entries into database
        success = kb_service.update_knowledge_base_from_data(kb_entries)
        
        if success:
            console.print("✅ Improved knowledge base loaded successfully!", style="green")
            
            # Show team distribution
            team_counts = defaultdict(int)
            for entry in kb_entries:
                team_counts[entry["team"]] += 1
            
            console.print("\n📊 Team Distribution:")
            for team, count in team_counts.items():
                console.print(f"  • {team}: {count} categories")
            
            console.print(f"\n🎯 Total: {len(kb_entries)} categories loaded")
            console.print("\n🚀 Knowledge base is ready! Test with: python test_csv_categorization.py")
            
            return True
        else:
            console.print("❌ Failed to load knowledge base", style="red")
            return False
    else:
        console.print("❌ Operation cancelled", style="yellow")
        return False

def main():
    console.print("🎯 Improved CSV Knowledge Base Loader")
    console.print("=" * 50)
    
    success = load_improved_knowledge_base()
    
    if success:
        console.print("\n🎉 Improved knowledge base loaded successfully!")
        console.print("\n💡 Next steps:")
        console.print("  1. Test accuracy: python test_csv_categorization.py")
        console.print("  2. Start the server: python main.py server")
        console.print("  3. Test with real tickets in the dashboard")
    else:
        console.print("\n❌ Failed to load improved knowledge base")
        sys.exit(1)

if __name__ == "__main__":
    main()