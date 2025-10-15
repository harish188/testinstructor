#!/usr/bin/env python3
"""
Start server and test the system
"""

import sys
import subprocess
import time
import requests
import json
from rich.console import Console

console = Console()

def test_server_endpoints():
    """Test server endpoints"""
    console.print("🌐 Testing Server Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            console.print("   ✅ Health endpoint working")
        else:
            console.print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        console.print(f"   ❌ Health endpoint error: {str(e)}")
        return False
    
    # Test knowledge base endpoint
    try:
        response = requests.get(f"{base_url}/api/knowledge-base", timeout=5)
        if response.status_code == 200:
            data = response.json()
            console.print(f"   ✅ Knowledge Base API: {data.get('count', 0)} categories")
        else:
            console.print(f"   ❌ Knowledge Base API failed: {response.status_code}")
            return False
    except Exception as e:
        console.print(f"   ❌ Knowledge Base API error: {str(e)}")
        return False
    
    # Test categorization endpoint
    try:
        test_tickets = [{
            "id": "API-TEST-001",
            "subject": "Instructor portal not working",
            "description": "Portal recording and upload issues",
            "status": "Open",
            "priority": "High",
            "created_time": "2024-10-14T10:00:00Z",
            "modified_time": "2024-10-14T10:00:00Z",
            "email": "test@example.com"
        }]
        
        response = requests.post(
            f"{base_url}/api/categorize-tickets",
            json={"tickets": test_tickets},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and len(data.get('categorized_tickets', [])) > 0:
                ticket = data['categorized_tickets'][0]
                console.print(f"   ✅ Categorization API: '{ticket['subject']}' → {ticket['predicted_category']} ({ticket['team']})")
            else:
                console.print("   ❌ Categorization API: No results returned")
                return False
        else:
            console.print(f"   ❌ Categorization API failed: {response.status_code}")
            return False
    except Exception as e:
        console.print(f"   ❌ Categorization API error: {str(e)}")
        return False
    
    console.print("   ✅ All API endpoints working correctly!")
    return True

def main():
    console.print("🚀 Starting Server and Testing System")
    console.print("=" * 50)
    
    console.print("📋 Instructions:")
    console.print("1. This script will show you how to test the system")
    console.print("2. Start the server manually: python main.py server")
    console.print("3. Then run: python test_server_endpoints.py")
    console.print("4. Open dashboard: http://localhost:8000")
    console.print()
    
    console.print("🎯 What to test in the dashboard:")
    console.print("✅ Click 'Fetch Tickets' - Should load 10 tickets")
    console.print("✅ Check categorization - Should use CSV knowledge base")
    console.print("✅ Filter by category - Should show correct tickets")
    console.print("✅ Filter by team - Should show team-specific tickets")
    console.print("✅ Click team stat cards - Should filter by team")
    console.print("✅ Edit category - Should allow manual changes")
    console.print("✅ Select and sync - Should work in preview mode")
    console.print()
    
    console.print("🔧 If something doesn't work:")
    console.print("1. Check browser console for JavaScript errors")
    console.print("2. Check server logs for backend errors")
    console.print("3. Verify knowledge base is loaded: python test_full_system.py")
    console.print("4. Test API endpoints: python test_server_endpoints.py")

if __name__ == "__main__":
    main()