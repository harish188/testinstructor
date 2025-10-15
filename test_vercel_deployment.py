#!/usr/bin/env python3
"""
Test script to verify Vercel deployment compatibility
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_simple_api_import():
    """Test that the simple API can be imported"""
    try:
        from api_simple import app
        print("✅ Simple API imported successfully")
        return True
    except Exception as e:
        print(f"❌ Simple API import failed: {e}")
        return False

def test_app_entry_point():
    """Test that the app.py entry point works"""
    try:
        from app import handler
        print("✅ App entry point imported successfully")
        return True
    except Exception as e:
        print(f"❌ App entry point failed: {e}")
        return False

def test_basic_endpoints():
    """Test basic endpoints"""
    try:
        from api_simple import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        print("✅ Health endpoint working")
        
        # Test status endpoint
        response = client.get("/api/status")
        assert response.status_code == 200
        print("✅ Status endpoint working")
        
        # Test categories endpoint
        response = client.get("/api/categories")
        assert response.status_code == 200
        print("✅ Categories endpoint working")
        
        return True
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Vercel Deployment Compatibility")
    print("=" * 50)
    
    tests = [
        test_simple_api_import,
        test_app_entry_point,
        test_basic_endpoints
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Deployment should work.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        sys.exit(1)