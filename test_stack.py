#!/usr/bin/env python3
"""
Script để test toàn bộ Docker stack
"""

import requests
import json
import time
import sys

def wait_for_service(url, max_retries=30, delay=2):
    """Chờ service sẵn sàng"""
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Service at {url} is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Waiting for service at {url}... ({i+1}/{max_retries})")
        time.sleep(delay)
    
    print(f"❌ Service at {url} not ready after {max_retries} retries")
    return False

def test_api_endpoints():
    """Test các API endpoints - cả V1 và V2"""
    base_url = "http://localhost:8080"  # Nginx port
    
    print("\n🧪 Testing Multi-Version API endpoints...")
    
    # Test global health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Global health check: {health_data.get('status')}")
            print(f"   Available APIs: {health_data.get('available_apis')}")
        else:
            print(f"❌ Global health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Global health check error: {e}")
    
    # Test API V1 (Backward Compatible)
    print("\n📋 Testing API V1 (Legacy/Backward Compatible)...")
    test_api_v1(base_url)
    
    # Test API V2 (Enhanced Features)
    print("\n🚀 Testing API V2 (Enhanced Features)...")
    test_api_v2(base_url)
    
    # Test Legacy Redis endpoint
    try:
        response = requests.get(f"{base_url}/redis/")
        if response.status_code == 200:
            redis_data = response.json()
            print(f"✅ Legacy Redis test: {redis_data.get('status')}")
        else:
            print(f"❌ Legacy Redis test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Legacy Redis test error: {e}")

def test_api_v1(base_url):
    """Test API V1 endpoints"""
    v1_prefix = "/api/v1"
    
    # V1 Health check
    try:
        response = requests.get(f"{base_url}{v1_prefix}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ V1 health check: {health_data.get('status')}")
        else:
            print(f"❌ V1 health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ V1 health check error: {e}")
    
    # V1 Create and Read item
    try:
        item_data = {"name": "Test Item V1", "description": "Test Description V1"}
        response = requests.post(f"{base_url}{v1_prefix}/items/", json=item_data)
        if response.status_code == 201:
            create_result = response.json()
            print(f"✅ V1 item create: {create_result.get('message')}")
            
            # Test read item
            item_id = create_result.get("data", {}).get("id")
            if item_id:
                response = requests.get(f"{base_url}{v1_prefix}/items/{item_id}")
                if response.status_code == 200:
                    item_data = response.json()
                    print(f"✅ V1 item read: {item_data.get('message')}")
                else:
                    print(f"❌ V1 item read failed: {response.status_code}")
        else:
            print(f"❌ V1 item create failed: {response.status_code}")
    except Exception as e:
        print(f"❌ V1 API test error: {e}")

def test_api_v2(base_url):
    """Test API V2 endpoints"""
    v2_prefix = "/api/v2"
    
    # V2 Detailed health check
    try:
        response = requests.get(f"{base_url}{v2_prefix}/health/detailed")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ V2 detailed health: {health_data.get('status')}")
            print(f"   Response time: {health_data.get('performance', {}).get('response_time_ms')}ms")
        else:
            print(f"❌ V2 detailed health failed: {response.status_code}")
    except Exception as e:
        print(f"❌ V2 health check error: {e}")
    
    # V2 Enhanced item operations
    try:
        # Create enhanced item
        item_data = {
            "name": "Test Item V2",
            "description": "Enhanced Test Description V2",
            "tags": ["test", "v2", "enhanced"],
            "category": "testing",
            "priority": 3,
            "metadata": {"source": "test_script", "version": "2.0"}
        }
        
        response = requests.post(f"{base_url}{v2_prefix}/items/", json=item_data)
        if response.status_code == 201:
            create_result = response.json()
            print(f"✅ V2 enhanced item create: {create_result.get('message')}")
            print(f"   Cached: {create_result.get('meta', {}).get('cached')}")
            
            item_id = create_result.get("data", {}).get("id")
            if item_id:
                # Test read with caching
                response = requests.get(f"{base_url}{v2_prefix}/items/{item_id}")
                if response.status_code == 200:
                    item_data = response.json()
                    print(f"✅ V2 item read: {item_data.get('message')}")
                    print(f"   From cache: {item_data.get('meta', {}).get('cached')}")
                
                # Test update
                update_data = {"priority": 5, "tags": ["test", "v2", "updated"]}
                response = requests.put(f"{base_url}{v2_prefix}/items/{item_id}", json=update_data)
                if response.status_code == 200:
                    update_result = response.json()
                    print(f"✅ V2 item update: {update_result.get('message')}")
                
                # Test list with pagination
                response = requests.get(f"{base_url}{v2_prefix}/items/?page=1&per_page=5&category=testing")
                if response.status_code == 200:
                    list_result = response.json()
                    print(f"✅ V2 item list: {list_result.get('message')}")
                    print(f"   Total items: {list_result.get('meta', {}).get('total')}")
        else:
            print(f"❌ V2 item create failed: {response.status_code}")
    except Exception as e:
        print(f"❌ V2 API test error: {e}")

def main():
    print("🚀 Testing Docker Stack...")
    
    # Chờ Nginx ready
    if not wait_for_service("http://localhost:8080/health"):
        print("❌ Stack not ready!")
        sys.exit(1)
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
