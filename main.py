#!/usr/bin/env python3
"""
Zoho to ClickUp Automation System
Main entry point for the application
"""

import asyncio
import sys
from pathlib import Path
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from services.automation_service import AutomationService
from scheduler import SyncScheduler
from database import create_tables
from config import settings

console = Console()

async def run_single_sync():
    """Run a single synchronization"""
    console.print(Panel.fit("🚀 Starting Zoho to ClickUp Sync", style="bold blue"))
    
    automation_service = AutomationService()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Synchronizing tickets...", total=None)
        
        try:
            result = await automation_service.run_sync()
            
            # Display results
            table = Table(title="Sync Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="magenta")
            
            table.add_row("Total Tickets", str(result.total_tickets))
            table.add_row("Processed", str(result.processed))
            table.add_row("Successful", str(result.success))
            table.add_row("Errors", str(result.errors))
            table.add_row("Duplicates", str(result.duplicates))
            table.add_row("Execution Time", f"{result.execution_time:.2f}s")
            
            console.print(table)
            
            if result.errors > 0:
                console.print(f"⚠️  {result.errors} tickets failed to process", style="yellow")
            
            console.print(f"✅ Sync completed successfully!", style="green")
            
        except Exception as e:
            console.print(f"❌ Sync failed: {str(e)}", style="red")
            sys.exit(1)

async def run_server():
    """Run the web server with scheduler"""
    console.print(Panel.fit("🌐 Starting Web Server", style="bold green"))
    
    # Create database tables
    create_tables()
    
    # Import and run the FastAPI app
    import uvicorn
    from api import app
    
    console.print("Server starting at http://localhost:8000")
    console.print("Dashboard available at http://localhost:8000")
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower()
    )
    server = uvicorn.Server(config)
    await server.serve()

def show_help():
    """Show help information"""
    help_text = """
🔧 Zoho to ClickUp Automation System

Usage:
    python main.py [command]

Commands:
    sync        Run a single synchronization
    server      Start the web server with scheduler (default)
    help        Show this help message

Examples:
    python main.py sync          # Run one-time sync
    python main.py server        # Start web server
    python main.py               # Start web server (default)

Configuration:
    Copy .env.example to .env and configure your API credentials.
    
Web Dashboard:
    When running in server mode, access the dashboard at:
    http://localhost:8000
    """
    console.print(help_text)

async def main():
    """Main entry point"""
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file logging
    logger.add(
        "logs/automation.log",
        rotation="1 day",
        retention="30 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Parse command line arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "server"
    
    if command == "sync":
        await run_single_sync()
    elif command == "server":
        await run_server()
    elif command == "help":
        show_help()
    else:
        console.print(f"❌ Unknown command: {command}", style="red")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="yellow")
    except Exception as e:
        console.print(f"❌ Fatal error: {str(e)}", style="red")
        sys.exit(1)