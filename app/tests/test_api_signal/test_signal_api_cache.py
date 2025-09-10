#!/usr/bin/env python3
"""
Test script for API /signal với cache mechanism
Kiểm tra 2 requests liên tiếp để verify cache hoạt động đúng
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8000"
SIGNAL_ENDPOINT = f"{API_BASE_URL}/api/v1/signal"

# Sample data từ signal.mdc
SAMPLE_SIGNAL_DATA = {
    "cache_key": {
        "timezone": "GMT+3.0",
        "timeframe": "H2",
        "symbol": "EURUSD"
    },
    "symbol": "EURUSD",
    "timeframe": "H2",
    "account_info": {
        "leverage": 500,
        "limit_orders": 200,
        "balance": 423.81,
        "profit": 0.0,
        "equity": 423.81,
        "margin_free": 423.81,
        "margin_level": 0.0,
        "margin_so_call": 100.0,
        "commission_blocked": 0.0,
        "currency": "USD",
        "server": "ICMarketsSC-Demo",
        "company": "Raw Trading Ltd"
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
        "description": "Standard Account (1 lot = 100,000 units)",
        "pip_value": 10.0
    },
    "symbol_info": {
        "ask": 1.17417,
        "bid": 1.17417,
        "spread": 0,
        "swap_long": -11.7304,
        "swap_short": 3.3992,
        "digits": 5,
        "point": 1e-05,
        "trade_tick_size": 1e-05,
        "trade_tick_value": 1.0,
        "volume_min": 0.01,
        "volume_max": 200.0,
        "volume_step": 0.01,
        "currency_profit": "USD",
        "currency_base": "EUR",
        "currency_margin": "EUR",
        "current_usdjpy_rate": 146.809,
        "trade_contract_size": 100000.0
    },
    "multi_timeframes": {
        "D1": {
            "indicators": {
                "rsi": 57.71891344693777,
                "macd": [
                    0.00225054401526803,
                    0.0014285578449930493,
                    0.0008219861702749808
                ],
                "bollinger_bands": [
                    1.1674545,
                    1.1759146890610175,
                    1.1589943109389826
                ],
                "atr": 0.008099999999999996,
                "adx": [
                    17.117202908412903,
                    24.594356261022714,
                    11.216931216931279
                ],
                "sma_100": 1.1533198,
                "sma_200": 1.10758665,
                "volume_sma_250": 67065.192
            },
            "analyze_price_action": {
                "time_context": {
                    "start_time": "2024-09-23 00:00:00 UTC",
                    "end_time": "2025-09-09 00:00:00 UTC",
                    "total_candles": 250
                },
                "key_levels": {
                    "period_high": {
                        "price": 1.18298,
                        "time": "2025-07-01 00:00:00"
                    },
                    "period_low": {
                        "price": 1.01773,
                        "time": "2025-01-13 00:00:00"
                    },
                    "resistance": [
                        {
                            "price": 1.17426,
                            "type": "swing_high",
                            "time": "2025-08-22 00:00:00",
                            "recency": "recent"
                        }
                    ],
                    "support": [
                        {
                            "price": 1.17,
                            "type": "round_number",
                            "time": None,
                            "recency": "historic"
                        }
                    ]
                },
                "price_patterns": {
                    "all_detected_on_last": ["Bearish SHORTLINE"],
                    "last_single_candle_pattern": "N/A",
                    "last_multi_candle_pattern": "Bearish SHORTLINE"
                },
                "volume_context": {
                    "status": "Below Average",
                    "interpretation": "Low volume suggests lack of interest or conviction."
                },
                "current_price_context": {
                    "price": 1.17417,
                    "position_relative_to_levels": "Price is approaching resistance at 1.17426.",
                    "nearest_resistance": {
                        "price": 1.17426,
                        "type": "swing_high",
                        "time": "2025-08-22 00:00:00",
                        "recency": "recent"
                    },
                    "nearest_support": {
                        "price": 1.17,
                        "type": "round_number",
                        "time": None,
                        "recency": "historic"
                    }
                }
            }
        },
        "H2": {
            "indicators": {
                "rsi": 57.66990291262113,
                "macd": [
                    0.0014547684447987486,
                    0.001883383703712072,
                    -0.00042861525891332354
                ],
                "bollinger_bands": [
                    1.1745285,
                    1.1785181776020646,
                    1.1705388223979356
                ],
                "atr": 0.001727142857142816,
                "adx": [
                    43.81346151806095,
                    22.70471464019995,
                    22.539288668321277
                ],
                "sma_100": 1.1688821999999999,
                "sma_200": 1.1669578,
                "volume_sma_250": 4993.596
            },
            "analyze_price_action": {
                "time_context": {
                    "start_time": "2025-08-11 22:00:00 UTC",
                    "end_time": "2025-09-09 16:00:00 UTC",
                    "total_candles": 250
                },
                "key_levels": {
                    "period_high": {
                        "price": 1.17801,
                        "time": "2025-09-09 08:00:00"
                    },
                    "period_low": {
                        "price": 1.1574,
                        "time": "2025-08-27 14:00:00"
                    },
                    "resistance": [
                        {
                            "price": 1.17426,
                            "type": "swing_high",
                            "time": "2025-08-22 20:00:00",
                            "recency": "intermediate"
                        }
                    ],
                    "support": [
                        {
                            "price": 1.17,
                            "type": "round_number",
                            "time": None,
                            "recency": "historic"
                        }
                    ]
                },
                "price_patterns": {
                    "all_detected_on_last": ["Bullish HARAMI", "Bullish SHORTLINE"],
                    "last_single_candle_pattern": "N/A",
                    "last_multi_candle_pattern": "Bullish HARAMI"
                },
                "volume_context": {
                    "status": "Below Average",
                    "interpretation": "Low volume suggests lack of interest or conviction."
                },
                "current_price_context": {
                    "price": 1.17417,
                    "position_relative_to_levels": "Price is approaching resistance at 1.17426.",
                    "nearest_resistance": {
                        "price": 1.17426,
                        "type": "swing_high",
                        "time": "2025-08-22 20:00:00",
                        "recency": "intermediate"
                    },
                    "nearest_support": {
                        "price": 1.17,
                        "type": "round_number",
                        "time": None,
                        "recency": "historic"
                    }
                }
            }
        },
        "M30": {
            "indicators": {
                "rsi": 30.551181102362662,
                "macd": [
                    -0.0005084525791709815,
                    -0.00016341554207555928,
                    -0.00034503703709542224
                ],
                "bollinger_bands": [
                    1.1759325,
                    1.1783788926181673,
                    1.1734861073818328
                ],
                "atr": 0.0010707142857143057,
                "adx": [
                    34.483872427306785,
                    12.074716477650657,
                    41.9613075383575
                ],
                "sma_100": 1.1740137,
                "sma_200": 1.1699221,
                "volume_sma_250": 1330.444
            },
            "analyze_price_action": {
                "time_context": {
                    "start_time": "2025-09-01 10:30:00 UTC",
                    "end_time": "2025-09-09 16:00:00 UTC",
                    "total_candles": 300
                },
                "key_levels": {
                    "period_high": {
                        "price": 1.17801,
                        "time": "2025-09-09 08:30:00"
                    },
                    "period_low": {
                        "price": 1.1608,
                        "time": "2025-09-03 10:00:00"
                    },
                    "resistance": [
                        {
                            "price": 1.17429,
                            "type": "swing_high",
                            "time": "2025-09-08 11:00:00",
                            "recency": "intermediate"
                        }
                    ],
                    "support": [
                        {
                            "price": 1.1735,
                            "type": "swing_low",
                            "time": "2025-09-08 20:00:00",
                            "recency": "recent"
                        }
                    ]
                },
                "price_patterns": {
                    "all_detected_on_last": [],
                    "last_single_candle_pattern": "N/A",
                    "last_multi_candle_pattern": "N/A"
                },
                "volume_context": {
                    "status": "Normal",
                    "interpretation": "Volume is at an average level."
                },
                "current_price_context": {
                    "price": 1.17417,
                    "position_relative_to_levels": "Price is approaching resistance at 1.17429.",
                    "nearest_resistance": {
                        "price": 1.17429,
                        "type": "swing_high",
                        "time": "2025-09-08 11:00:00",
                        "recency": "intermediate"
                    },
                    "nearest_support": {
                        "price": 1.1735,
                        "type": "swing_low",
                        "time": "2025-09-08 20:00:00",
                        "recency": "recent"
                    }
                }
            }
        }
    }
}

class SignalAPITester:
    """Test class cho API /signal với cache mechanism"""
    
    def __init__(self):
        self.session = None
        self.results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, request_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Thực hiện request đến API /signal"""
        start_time = time.time()
        
        try:
            async with self.session.post(
                SIGNAL_ENDPOINT,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                response_data = await response.json()
                
                return {
                    "request_id": request_id,
                    "status_code": response.status,
                    "response_time": response_time,
                    "response_data": response_data,
                    "timestamp": datetime.now().isoformat(),
                    "success": response.status == 200
                }
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "request_id": request_id,
                "status_code": 0,
                "response_time": response_time,
                "response_data": {"error": str(e)},
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def validate_response_format(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response format theo chuẩn response_format.mdc"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Kiểm tra structure cơ bản
        required_fields = ["success", "errorMsg", "errorCode", "data"]
        for field in required_fields:
            if field not in response_data:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
        
        # Kiểm tra data structure nếu success = true
        if response_data.get("success") and "data" in response_data:
            data = response_data["data"]
            expected_data_fields = [
                "signal", "entry_price", "stop_loss", "take_profit", 
                "confidence", "timestamp", "cache_key"
            ]
            
            for field in expected_data_fields:
                if field not in data:
                    validation_result["warnings"].append(f"Missing expected data field: {field}")
        
        return validation_result
    
    def analyze_cache_behavior(self, results: list) -> Dict[str, Any]:
        """Phân tích cache behavior từ 2 requests"""
        if len(results) < 2:
            return {"error": "Need at least 2 requests to analyze cache behavior"}
        
        first_request = results[0]
        second_request = results[1]
        
        analysis = {
            "cache_working": False,
            "response_time_improvement": 0,
            "response_consistency": False,
            "details": {}
        }
        
        # Kiểm tra response time improvement (cache hit nên nhanh hơn)
        if (first_request["success"] and second_request["success"] and 
            second_request["response_time"] < first_request["response_time"]):
            analysis["cache_working"] = True
            analysis["response_time_improvement"] = (
                first_request["response_time"] - second_request["response_time"]
            )
        
        # Kiểm tra response consistency (cùng cache key nên cùng response)
        if (first_request["success"] and second_request["success"] and
            "data" in first_request["response_data"] and 
            "data" in second_request["response_data"]):
            
            first_data = first_request["response_data"]["data"]
            second_data = second_request["response_data"]["data"]
            
            # So sánh các field quan trọng
            key_fields = ["signal", "entry_price", "stop_loss", "take_profit"]
            consistent_fields = []
            
            for field in key_fields:
                if (field in first_data and field in second_data and
                    first_data[field] == second_data[field]):
                    consistent_fields.append(field)
            
            analysis["response_consistency"] = len(consistent_fields) == len(key_fields)
            analysis["details"]["consistent_fields"] = consistent_fields
        
        analysis["details"]["first_request_time"] = first_request["response_time"]
        analysis["details"]["second_request_time"] = second_request["response_time"]
        
        return analysis
    
    async def run_test(self):
        """Chạy test với 2 requests liên tiếp"""
        print("🚀 Bắt đầu test API /signal với cache mechanism")
        print("=" * 60)
        
        # Test 1: Request đầu tiên (cache miss)
        print("📤 Request 1: Cache miss (lần đầu)")
        result1 = await self.make_request(1, SAMPLE_SIGNAL_DATA)
        self.results.append(result1)
        
        print(f"   Status: {result1['status_code']}")
        print(f"   Response Time: {result1['response_time']:.3f}s")
        print(f"   Success: {result1['success']}")
        
        if result1["success"]:
            validation1 = self.validate_response_format(result1["response_data"])
            print(f"   Response Valid: {validation1['valid']}")
            if validation1["errors"]:
                print(f"   Errors: {validation1['errors']}")
            if validation1["warnings"]:
                print(f"   Warnings: {validation1['warnings']}")
        
        print()
        
        # Đợi 1 giây để đảm bảo cache đã được lưu
        await asyncio.sleep(1)
        
        # Test 2: Request thứ hai (cache hit)
        print("📤 Request 2: Cache hit (lần thứ hai)")
        result2 = await self.make_request(2, SAMPLE_SIGNAL_DATA)
        self.results.append(result2)
        
        print(f"   Status: {result2['status_code']}")
        print(f"   Response Time: {result2['response_time']:.3f}s")
        print(f"   Success: {result2['success']}")
        
        if result2["success"]:
            validation2 = self.validate_response_format(result2["response_data"])
            print(f"   Response Valid: {validation2['valid']}")
            if validation2["errors"]:
                print(f"   Errors: {validation2['errors']}")
            if validation2["warnings"]:
                print(f"   Warnings: {validation2['warnings']}")
        
        print()
        
        # Phân tích cache behavior
        print("🔍 Phân tích Cache Behavior:")
        cache_analysis = self.analyze_cache_behavior(self.results)
        
        if "error" in cache_analysis:
            print(f"   ❌ {cache_analysis['error']}")
        else:
            print(f"   Cache Working: {'✅' if cache_analysis['cache_working'] else '❌'}")
            print(f"   Response Consistency: {'✅' if cache_analysis['response_consistency'] else '❌'}")
            print(f"   Time Improvement: {cache_analysis['response_time_improvement']:.3f}s")
            
            if cache_analysis["details"]["consistent_fields"]:
                print(f"   Consistent Fields: {cache_analysis['details']['consistent_fields']}")
        
        print()
        
        # Tổng kết
        print("📊 TỔNG KẾT TEST:")
        print("=" * 60)
        
        successful_requests = sum(1 for r in self.results if r["success"])
        print(f"✅ Successful Requests: {successful_requests}/2")
        
        if successful_requests == 2:
            avg_response_time = sum(r["response_time"] for r in self.results) / len(self.results)
            print(f"⏱️  Average Response Time: {avg_response_time:.3f}s")
            
            if cache_analysis.get("cache_working"):
                print("🎯 Cache Mechanism: WORKING CORRECTLY")
            else:
                print("⚠️  Cache Mechanism: NEEDS INVESTIGATION")
        else:
            print("❌ Some requests failed - check API status")
        
        return self.results

async def main():
    """Main function để chạy test"""
    async with SignalAPITester() as tester:
        results = await tester.run_test()
        
        # Lưu kết quả vào file
        with open("tests/signal_api_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to: tests/signal_api_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())
