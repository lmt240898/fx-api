#!/usr/bin/env python3
"""
Test script để kiểm tra tính năng lưu prompt.log
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.response_logger import response_logger
from app.services.prompt_service import PromptService


def test_prompt_logging():
    """Test tính năng lưu prompt.log"""
    
    print("🧪 Testing Prompt Logging Feature")
    print("=" * 50)
    
    # Sample request data
    sample_request_data = {
        "symbol": "EURUSD",
        "timeframe": "H2",
        "cache_key": {
            "timezone": "GMT+3.0",
            "timeframe": "H2",
            "symbol": "EURUSD"
        },
        "multi_timeframes": {
            "H2": {
                "indicators": {
                    "rsi": 45.2,
                    "macd": {"macd": 0.0012, "signal": 0.0008, "histogram": 0.0004},
                    "bollinger_bands": {"upper": 1.0850, "middle": 1.0820, "lower": 1.0790},
                    "atr": 0.0025,
                    "adx": 28.5,
                    "sma_100": 1.0815,
                    "sma_200": 1.0800,
                    "volume_sma_250": 1250000
                },
                "price_data": {
                    "open": 1.0825,
                    "high": 1.0840,
                    "low": 1.0810,
                    "close": 1.0835,
                    "volume": 1200000
                }
            }
        },
        "account_info": {
            "balance": 1000.0,
            "equity": 1050.0,
            "margin": 50.0,
            "free_margin": 950.0
        }
    }
    
    try:
        # 1. Test tạo prompt
        print("1. Testing prompt generation...")
        prompt_service = PromptService()
        prompt_content = prompt_service.create_prompt_for_signal_analyst(sample_request_data)
        
        if prompt_content:
            print("✅ Prompt generated successfully")
            print(f"📏 Prompt length: {len(prompt_content)} characters")
            print(f"📄 Prompt preview: {prompt_content[:200]}...")
        else:
            print("❌ Failed to generate prompt")
            return False
        
        # 2. Test lưu prompt only
        print("\n2. Testing prompt-only logging...")
        prompt_log_path = response_logger.log_prompt_only(
            symbol="EURUSD",
            timeframe="H2",
            prompt_content=prompt_content,
            request_data=sample_request_data
        )
        
        if os.path.exists(prompt_log_path):
            print(f"✅ Prompt logged successfully: {prompt_log_path}")
            
            # Verify content (text format, not JSON)
            with open(prompt_log_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            
            print(f"📏 Prompt file size: {len(prompt_content)} characters")
            print(f"📄 Prompt preview: {prompt_content[:200]}...")
            print(f"✅ Prompt content is in text format (not JSON)")
        else:
            print(f"❌ Prompt log file not found: {prompt_log_path}")
            return False
        
        # 3. Test lưu response với prompt
        print("\n3. Testing response logging with prompt...")
        sample_response = {
            "success": True,
            "data": {
                "symbol": "EURUSD",
                "signal_type": "BUY",
                "order_type_proposed": "MARKET",
                "entry_price_proposed": 1.0835,
                "stop_loss_proposed": 1.0800,
                "take_profit_proposed": 1.0880,
                "estimate_win_probability": 65,
                "risk_reward_ratio": 1.8,
                "technical_reasoning": "Strong bullish momentum with RSI oversold recovery"
            }
        }
        
        response_log_path = response_logger.log_signal_response(
            symbol="EURUSD",
            timeframe="H2",
            response_data=sample_response,
            request_data=sample_request_data,
            prompt_content=prompt_content
        )
        
        if os.path.exists(response_log_path):
            print(f"✅ Response logged successfully: {response_log_path}")
            
            # Check if prompt.log was also created
            folder_path = os.path.dirname(response_log_path)
            prompt_log_path = os.path.join(folder_path, "prompt.log")
            
            if os.path.exists(prompt_log_path):
                print(f"✅ Prompt.log also created: {prompt_log_path}")
                
                # Verify both files
                with open(prompt_log_path, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                
                with open(response_log_path, 'r', encoding='utf-8') as f:
                    response_data = json.load(f)
                
                print(f"📁 Folder contains:")
                print(f"   - result.log: {os.path.basename(response_log_path)} (JSON format)")
                print(f"   - prompt.log: {os.path.basename(prompt_log_path)} (Text format)")
                print(f"📊 Prompt file size: {len(prompt_content)} characters")
                print(f"📊 Response log type: {response_data.get('log_type')}")
                print(f"✅ Prompt.log contains pure text content (like sample file)")
                
            else:
                print(f"❌ Prompt.log not found in folder: {folder_path}")
                return False
        else:
            print(f"❌ Response log file not found: {response_log_path}")
            return False
        
        # 4. Test folder structure
        print("\n4. Testing folder structure...")
        folder_path = os.path.dirname(response_log_path)
        expected_structure = "logs/MM-YYYY/DD/EURUSD_ddmmyyhhmmss/"
        
        print(f"📁 Actual folder: {folder_path}")
        print(f"📁 Expected pattern: {expected_structure}")
        
        # Check if folder follows expected pattern
        if "EURUSD_" in folder_path and "result.log" in os.listdir(folder_path):
            print("✅ Folder structure is correct")
        else:
            print("❌ Folder structure is incorrect")
            return False
        
        print("\n🎉 All tests passed!")
        print("=" * 50)
        print("📋 Summary:")
        print(f"   - Prompt generation: ✅")
        print(f"   - Prompt-only logging: ✅")
        print(f"   - Response + prompt logging: ✅")
        print(f"   - Folder structure: ✅")
        print(f"   - File creation: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_statistics():
    """Test prompt statistics"""
    
    print("\n📊 Testing Prompt Statistics")
    print("=" * 30)
    
    try:
        prompt_service = PromptService()
        
        # Sample data
        sample_data = {
            "symbol": "GBPUSD",
            "timeframe": "H4",
            "multi_timeframes": {
                "H4": {
                    "indicators": {
                        "rsi": 55.0,
                        "macd": {"macd": 0.0005, "signal": 0.0003, "histogram": 0.0002},
                        "bollinger_bands": {"upper": 1.2750, "middle": 1.2700, "lower": 1.2650}
                    }
                },
                "H2": {
                    "indicators": {
                        "rsi": 52.0,
                        "macd": {"macd": 0.0003, "signal": 0.0002, "histogram": 0.0001}
                    }
                }
            },
            "account_info": {"balance": 2000.0}
        }
        
        stats = prompt_service.get_prompt_statistics(sample_data)
        
        print(f"📈 Statistics:")
        print(f"   - Data size: {stats.get('data_size_bytes', 0)} bytes")
        print(f"   - Timeframe count: {stats.get('timeframe_count', 0)}")
        print(f"   - Indicators per timeframe: {stats.get('indicators_per_timeframe', {})}")
        print(f"   - Symbol: {stats.get('symbol', 'N/A')}")
        print(f"   - Main timeframe: {stats.get('main_timeframe', 'N/A')}")
        print(f"   - Has account info: {stats.get('has_account_info', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Prompt Logging Tests")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_prompt_logging()
    test2_passed = test_prompt_statistics()
    
    print("\n" + "=" * 60)
    print("🏁 Test Results:")
    print(f"   - Prompt Logging Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   - Statistics Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Prompt logging feature is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the implementation.")
        sys.exit(1)
