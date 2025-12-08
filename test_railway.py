#!/usr/bin/env python
"""
Test script to verify minimal Railway deployment works
"""
import os
import sys
import django
from django.conf import settings
from django.test.client import Client
from django.core.management import execute_from_command_line

# Set minimal settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rejlers_api.minimal_settings')

def test_deployment():
    print("🧪 Testing minimal Railway deployment...")
    
    try:
        # Setup Django
        django.setup()
        print("✅ Django setup successful")
        
        # Test client
        client = Client()
        
        # Test all health endpoints
        endpoints = ['/', '/health/', '/api/v1/health/', '/api/v1/ready/', '/ping/']
        
        for endpoint in endpoints:
            try:
                response = client.get(endpoint)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - Status: {response.status_code}")
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
        
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = test_deployment()
    sys.exit(0 if success else 1)