#!/usr/bin/env python3
"""
Demo script to showcase the Zoho to ClickUp automation system
"""

import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns

# Add current directory to path
sys.path.append('.')

from models import ZohoTicket, TicketCategory
from services.categorization_service import CategorizationService
from config import settings

console = Console()

def create_sample_tickets():
    """Create sample tickets for demonstration"""
    return [
        ZohoTicket(
            id="TICKET-001",
            subject="Quiz not loading properly",
            description="Students are unable to access the quiz module. Getting error when clicking on quiz section.",
            status="Open",
            priority="High",
            created_time=datetime.now(),
            modified_time=datetime.now(),
            email="student@example.com"
        ),
        ZohoTicket(
            id="TICKET-002", 
            subject="Cannot login to portal",
            description="User cannot access the learning portal. Getting authentication error on login page.",
            status="Open",
            priority="High",
            created_time=datetime.now(),
            modified_time=datetime.now(),
            email="user@example.com"
        ),
        ZohoTicket(
            id="TICKET-003",
            subject="Content bundle missing",
            description="The new curriculum bundle is not showing up in my course materials section.",
            status="Open", 
            priority="Medium",
            created_time=datetime.now(),
            modified_time=datetime.now(),
            email="learner@example.com"
        ),
        ZohoTicket(
            id="TICKET-004",
            subject="Need instructor role added",
            description="Please add instructor permissions to my account so I can access the teaching dashboard.",
            status="Open",
            priority="Medium", 
            created_time=datetime.now(),
            modified_time=datetime.now(),
            email="teacher@example.com"
        ),
        ZohoTicket(
            id="TICKET-005",
            subject="Units are locked",
            description="I completed the previous module but the next units are still locked and unavailable.",
            status="Open",
            priority="Medium",
            created_time=datetime.now(), 
            modified_time=datetime.now(),
            email="student2@example.com"
        ),
        ZohoTicket(
            id="TICKET-006",
            subject="Feedback grooming needed",
            description="The submitted assignment needs feedback grooming and quality review check.",
            status="Open",
            priority="Low",
            created_time=datetime.now(),
            modified_time=datetime.now(), 
            email="instructor@example.com"
        )
    ]

def demo_categorization():
    """Demonstrate the categorization system"""
    console.print(Panel.fit("🤖 Zoho to ClickUp Automation Demo", style="bold blue"))
    
    # Create sample tickets
    tickets = create_sample_tickets()
    console.print(f"\n📋 Created {len(tickets)} sample tickets for demonstration\n")
    
    # Initialize categorization service
    categorization_service = CategorizationService()
    
    # Categorize tickets
    categorizations = categorization_service.batch_categorize(tickets)
    
    # Create results table
    table = Table(title="🎯 Categorization Results")
    table.add_column("Ticket ID", style="cyan", no_wrap=True)
    table.add_column("Subject", style="white", max_width=30)
    table.add_column("Category", style="green", no_wrap=True)
    table.add_column("Team", style="yellow", no_wrap=True)
    table.add_column("ClickUp List", style="magenta", no_wrap=True)
    
    for ticket in tickets:
        category = categorizations[ticket.id]
        team = settings.category_to_team_mapping[category]
        clickup_list = settings.category_to_list_mapping[category]
        
        table.add_row(
            ticket.id,
            ticket.subject,
            category,
            team,
            clickup_list
        )
    
    console.print(table)
    
    # Show team distribution
    console.print("\n")
    team_counts = {}
    for category in categorizations.values():
        team = settings.category_to_team_mapping[category]
        team_counts[team] = team_counts.get(team, 0) + 1
    
    team_panels = []
    for team, count in team_counts.items():
        panel = Panel(
            f"[bold]{count}[/bold] tickets",
            title=f"👥 {team}",
            border_style="blue"
        )
        team_panels.append(panel)
    
    console.print(Columns(team_panels))
    
    # Show category mappings
    console.print("\n")
    mapping_table = Table(title="🗺️  Category to Team Mappings")
    mapping_table.add_column("Category", style="cyan")
    mapping_table.add_column("Team", style="yellow") 
    mapping_table.add_column("ClickUp List ID", style="magenta")
    
    for category, team in settings.category_to_team_mapping.items():
        list_id = settings.category_to_list_mapping[category]
        mapping_table.add_row(category, team, list_id)
    
    console.print(mapping_table)

def demo_duplicate_detection():
    """Demonstrate duplicate detection"""
    console.print(Panel.fit("🔍 Duplicate Detection Demo", style="bold green"))
    
    # Create tickets with duplicates
    tickets_with_duplicates = [
        ZohoTicket(
            id="TICKET-007",
            subject="Quiz not working",
            description="Quiz module is broken",
            status="Open",
            priority="High", 
            created_time=datetime.now(),
            modified_time=datetime.now(),
            email="user1@example.com"
        ),
        ZohoTicket(
            id="TICKET-008", 
            subject="Quiz not working",
            description="Quiz section not loading",
            status="Open",
            priority="High",
            created_time=datetime.now(),
            modified_time=datetime.now(),
            email="user1@example.com"  # Same user
        ),
        ZohoTicket(
            id="TICKET-009",
            subject="Portal login issue", 
            description="Cannot access portal",
            status="Open",
            priority="Medium",
            created_time=datetime.now(),
            modified_time=datetime.now(),
            email="user2@example.com"
        )
    ]
    
    categorization_service = CategorizationService()
    similar_groups = categorization_service.get_similar_tickets(tickets_with_duplicates)
    
    if similar_groups:
        console.print("🔍 Found similar ticket groups:")
        for i, group in enumerate(similar_groups, 1):
            console.print(f"\n📦 Group {i}:")
            for ticket in group:
                console.print(f"  • {ticket.id}: {ticket.subject} ({ticket.email})")
    else:
        console.print("✅ No duplicate tickets found")

if __name__ == "__main__":
    try:
        demo_categorization()
        console.print("\n" + "="*80 + "\n")
        demo_duplicate_detection()
        
        console.print(f"\n🎉 Demo completed successfully!")
        console.print(f"💡 To run the full system:")
        console.print(f"   1. Configure your API credentials in .env")
        console.print(f"   2. Run: python main.py server")
        console.print(f"   3. Open: http://localhost:8000")
        
    except Exception as e:
        console.print(f"❌ Demo failed: {str(e)}", style="red")
        sys.exit(1)