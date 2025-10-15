#!/usr/bin/env python3
"""
Add knowledge base entries via API (for when server is running)
"""

import requests
import json
from rich.console import Console

console = Console()

def add_knowledge_base_via_api():
    """Add knowledge base entries via API call"""
    
    # Your knowledge base entries
    kb_entries = [
        {
            "category": "Platform Issues",
            "team": "Product/Tech",
            "keywords": ["platform", "system", "technical", "bug", "error", "crash", "server", "database", "api", "integration"],
            "description": "Technical issues with the platform infrastructure",
            "weight": 1.2
        },
        {
            "category": "Facilities",
            "team": "Facilities", 
            "keywords": ["facilities", "room", "equipment", "projector", "wifi", "venue", "location"],
            "description": "Physical facilities and equipment issues",
            "weight": 1.0
        }
        # Add more entries as needed
    ]
    
    try:
        response = requests.post(
            "http://localhost:8000/api/knowledge-base/add",
            json=kb_entries,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            console.print(f"✅ {result['message']}", style="green")
            console.print(f"📊 Total categories: {result['categories_count']}")
        else:
            console.print(f"❌ Error: {response.status_code} - {response.text}", style="red")
            
    except requests.exceptions.ConnectionError:
        console.print("❌ Server not running. Start with: python main.py server", style="red")
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")

if __name__ == "__main__":
    console.print("📚 Adding Knowledge Base via API")
    add_knowledge_base_via_api()