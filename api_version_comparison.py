#!/usr/bin/env python3
"""
Script demo so sánh khả năng của API V1 vs V2
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8080"

def print_header(title):
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def print_response(response, title):
    print(f"\n📄 {title}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
    else:
        print(f"Error: {response.text}")

def compare_api_versions():
    print("🚀 API Version Comparison Demo")
    print(f"Testing Multi-Version API at {BASE_URL}")
    
    # Test Global API Info
    print_header("Global API Information")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "Root endpoint - Available API versions")
    
    # Health Check Comparison
    print_header("Health Check Comparison")
    
    # V1 Health
    response_v1 = requests.get(f"{BASE_URL}/api/v1/health")
    print_response(response_v1, "V1 Health Check (Simple)")
    
    # V2 Health
    response_v2 = requests.get(f"{BASE_URL}/api/v2/health/detailed")
    print_response(response_v2, "V2 Detailed Health Check (Enhanced)")
    
    # Item Creation Comparison
    print_header("Item Creation Comparison")
    
    # V1 Simple Item
    simple_item = {
        "name": "Demo Item V1",
        "description": "Simple item created via API V1"
    }
    
    start_time = time.time()
    response_v1_create = requests.post(f"{BASE_URL}/api/v1/items/", json=simple_item)
    v1_time = round((time.time() - start_time) * 1000, 2)
    print_response(response_v1_create, f"V1 Item Creation (Response time: {v1_time}ms)")
    
    # V2 Enhanced Item
    enhanced_item = {
        "name": "Demo Item V2",
        "description": "Enhanced item created via API V2 with advanced features",
        "tags": ["demo", "v2", "enhanced", "multi-version"],
        "category": "demonstration",
        "priority": 4,
        "metadata": {
            "created_by": "comparison_script",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "features": ["caching", "pagination", "filtering"]
        }
    }
    
    start_time = time.time()
    response_v2_create = requests.post(f"{BASE_URL}/api/v2/items/", json=enhanced_item)
    v2_time = round((time.time() - start_time) * 1000, 2)
    print_response(response_v2_create, f"V2 Enhanced Item Creation (Response time: {v2_time}ms)")
    
    # Item Reading Comparison
    print_header("Item Reading Comparison")
    
    if response_v1_create.status_code == 201:
        v1_item_id = response_v1_create.json().get("data", {}).get("id")
        if v1_item_id:
            response_v1_read = requests.get(f"{BASE_URL}/api/v1/items/{v1_item_id}")
            print_response(response_v1_read, "V1 Item Read (Simple response)")
    
    if response_v2_create.status_code == 201:
        v2_item_id = response_v2_create.json().get("data", {}).get("id")
        if v2_item_id:
            # First read (from database)
            start_time = time.time()
            response_v2_read1 = requests.get(f"{BASE_URL}/api/v2/items/{v2_item_id}")
            read1_time = round((time.time() - start_time) * 1000, 2)
            print_response(response_v2_read1, f"V2 Item Read #1 - From DB (Response time: {read1_time}ms)")
            
            # Second read (from cache)
            start_time = time.time()
            response_v2_read2 = requests.get(f"{BASE_URL}/api/v2/items/{v2_item_id}")
            read2_time = round((time.time() - start_time) * 1000, 2)
            print_response(response_v2_read2, f"V2 Item Read #2 - From Cache (Response time: {read2_time}ms)")
    
    # V2 Advanced Features Demo
    print_header("V2 Advanced Features Demo")
    
    if response_v2_create.status_code == 201:
        v2_item_id = response_v2_create.json().get("data", {}).get("id")
        
        # Update item
        update_data = {
            "priority": 5,
            "tags": ["demo", "v2", "updated", "advanced"],
            "metadata": {
                "updated_by": "comparison_script",
                "update_timestamp": datetime.now().isoformat(),
                "action": "priority_boost"
            }
        }
        
        response_update = requests.put(f"{BASE_URL}/api/v2/items/{v2_item_id}", json=update_data)
        print_response(response_update, "V2 Item Update (Partial update with cache invalidation)")
        
        # List items with filtering
        response_list = requests.get(f"{BASE_URL}/api/v2/items/?page=1&per_page=5&category=demonstration")
        print_response(response_list, "V2 Item List (Paginated + Filtered by category)")
        
        # List items with tag filtering
        response_list_tags = requests.get(f"{BASE_URL}/api/v2/items/?tags=demo&tags=v2")
        print_response(response_list_tags, "V2 Item List (Filtered by tags)")
    
    # Performance Summary
    print_header("Performance Summary")
    print(f"✅ V1 Create Response Time: {v1_time}ms")
    print(f"🚀 V2 Create Response Time: {v2_time}ms")
    if 'read1_time' in locals() and 'read2_time' in locals():
        print(f"📊 V2 Read from DB: {read1_time}ms")
        print(f"⚡ V2 Read from Cache: {read2_time}ms")
        print(f"🎯 Cache Performance Improvement: {round((read1_time - read2_time), 2)}ms ({round((read1_time - read2_time)/read1_time*100, 1)}%)")
    
    # Feature Comparison
    print_header("Feature Comparison Summary")
    print("""
📋 API V1 Features:
  ✅ Basic CRUD operations
  ✅ Simple request/response format
  ✅ Backward compatibility
  ✅ Lightweight and fast
  
🚀 API V2 Features:
  ✅ All V1 features PLUS:
  ✅ Redis caching for performance
  ✅ Enhanced data models (tags, metadata, priority)
  ✅ Pagination support
  ✅ Advanced filtering (category, tags)
  ✅ Full CRUD operations (including UPDATE, DELETE)
  ✅ Detailed response metadata
  ✅ Cache performance metrics
  ✅ Comprehensive error handling
  
🎯 Use Case Recommendations:
  
  📱 Use API V1 when:
    - Legacy client compatibility required
    - Simple CRUD operations sufficient
    - Minimal response overhead needed
    - Quick integration required
  
  🚀 Use API V2 when:
    - Performance optimization needed (caching)
    - Advanced filtering/pagination required
    - Rich metadata and tagging needed
    - Full-featured application development
    - Modern API standards preferred
    """)

if __name__ == "__main__":
    try:
        compare_api_versions()
        print("\n🎉 API Version Comparison completed successfully!")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Cannot connect to {BASE_URL}")
        print("Make sure the Docker stack is running:")
        print("  docker-compose up -d --build")
    except Exception as e:
        print(f"\n❌ Error: {e}")
