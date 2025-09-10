#!/usr/bin/env python3
"""
Simple test script for API /signal
Quick test để verify API hoạt động và cache mechanism
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
SIGNAL_ENDPOINT = f"{API_BASE_URL}/api/v1/signal"

# Simplified test data
TEST_DATA = {
    "cache_key": {
        "timezone": "GMT+3.0",
        "timeframe": "H2",
        "symbol": "EURUSD"
    },
    "symbol": "EURUSD",
    "timeframe": "H2",
    "account_info": {
        "balance": 423.81,
        "equity": 423.81,
        "currency": "USD"
    },
    "balance_config": {
        "max_position": 3,
        "max_risk": 2.0,
        "total_max_risk": 6
    },
    "max_positions": 3,
    "active_orders_summary": "total_active_orders: 0",
    "pending_orders_summary": "total_pending_orders: 0",
    "portfolio_exposure": {
        "active_positions": [],
        "pending_orders": [],
        "summary": {
            "total_active_positions": 0,
            "total_pending_orders": 0,
            "total_potential_loss_from_portfolio_usd": 0.0,
            "total_margin_used_from_portfolio_usd": 0.0
        }
    },
    "account_type_details": {
        "name": "STANDARD",
        "multiplier": 100000,
        "pip_value": 10.0
    },
    "symbol_info": {
        "ask": 1.17417,
        "bid": 1.17417,
        "digits": 5,
        "volume_min": 0.01,
        "volume_max": 200.0,
        "volume_step": 0.01
    },
    "multi_timeframes": {
        "H2": {
            "indicators": {
                "rsi": 57.67,
                "macd": [0.00145, 0.00188, -0.00043],
                "bollinger_bands": [1.1745, 1.1785, 1.1705],
                "atr": 0.00173,
                "adx": [43.81, 22.70, 22.54],
                "sma_100": 1.1689,
                "sma_200": 1.1670,
                "volume_sma_250": 4993.6
            },
            "analyze_price_action": {
                "current_price_context": {
                    "price": 1.17417,
                    "position_relative_to_levels": "Price is approaching resistance at 1.17426."
                }
            }
        }
    }
}

def make_request(request_id, data):
    """Make request to API /signal"""
    print(f"📤 Request {request_id}: Sending to {SIGNAL_ENDPOINT}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            SIGNAL_ENDPOINT,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"   ✅ Success: {response_data.get('success', False)}")
            print(f"   Error Code: {response_data.get('errorCode', 'N/A')}")
            
            if response_data.get('success') and 'data' in response_data:
                data = response_data['data']
                print(f"   Signal: {data.get('signal', 'N/A')}")
                print(f"   Entry Price: {data.get('entry_price', 'N/A')}")
                print(f"   Cache Key: {data.get('cache_key', 'N/A')}")
            
            return {
                "success": True,
                "response_time": response_time,
                "data": response_data
            }
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return {
                "success": False,
                "response_time": response_time,
                "error": response.text
            }
            
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"   ❌ Exception: {str(e)}")
        return {
            "success": False,
            "response_time": response_time,
            "error": str(e)
        }

def main():
    """Main test function"""
    print("🚀 Simple API /signal Test")
    print("=" * 50)
    
    # Test 1: First request (should be cache miss)
    print("\n🔍 Test 1: First Request (Cache Miss)")
    result1 = make_request(1, TEST_DATA)
    
    # Wait a bit
    print("\n⏳ Waiting 2 seconds...")
    time.sleep(2)
    
    # Test 2: Second request (should be cache hit)
    print("\n🔍 Test 2: Second Request (Cache Hit)")
    result2 = make_request(2, TEST_DATA)
    
    # Analysis
    print("\n📊 Analysis:")
    print("=" * 50)
    
    if result1["success"] and result2["success"]:
        print("✅ Both requests successful")
        
        # Check response time improvement
        if result2["response_time"] < result1["response_time"]:
            improvement = result1["response_time"] - result2["response_time"]
            print(f"🎯 Cache working! Time improvement: {improvement:.3f}s")
        else:
            print("⚠️  Cache may not be working (no time improvement)")
        
        # Check response consistency
        if ("data" in result1["data"] and "data" in result2["data"] and
            result1["data"]["data"] == result2["data"]["data"]):
            print("✅ Response consistency: PASSED")
        else:
            print("⚠️  Response consistency: NEEDS CHECK")
            
    else:
        print("❌ Some requests failed")
        if not result1["success"]:
            print(f"   Request 1 error: {result1.get('error', 'Unknown')}")
        if not result2["success"]:
            print(f"   Request 2 error: {result2.get('error', 'Unknown')}")
    
    print(f"\n💾 Test completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
