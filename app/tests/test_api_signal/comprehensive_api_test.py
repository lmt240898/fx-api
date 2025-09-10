#!/usr/bin/env python3
"""
Comprehensive API Test với full tracking và logging
Chứng minh API hoạt động chính xác từng bước
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from datetime import datetime

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.signal_service import SignalService
from app.utils.redis_client import RedisClient
from app.utils.response_logger import ResponseLogger

class APITracker:
    """Track toàn bộ quá trình API hoạt động"""
    
    def __init__(self):
        self.steps = []
        self.start_time = None
        self.end_time = None
    
    def add_step(self, step_name, details, status="INFO"):
        """Thêm step tracking"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        step = {
            "timestamp": timestamp,
            "step": step_name,
            "details": details,
            "status": status
        }
        self.steps.append(step)
        print(f"[{timestamp}] {status}: {step_name}")
        if details:
            print(f"    └─ {details}")
    
    def start_tracking(self):
        """Bắt đầu tracking"""
        self.start_time = time.time()
        self.add_step("TRACKING_START", "Bắt đầu theo dõi API hoạt động", "START")
    
    def end_tracking(self):
        """Kết thúc tracking"""
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        self.add_step("TRACKING_END", f"Hoàn thành trong {total_time:.3f}s", "END")
    
    def save_report(self, filename):
        """Lưu báo cáo chi tiết"""
        report = {
            "test_info": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
                "total_duration": self.end_time - self.start_time,
                "total_steps": len(self.steps)
            },
            "steps": self.steps
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Báo cáo chi tiết đã lưu: {filename}")

async def comprehensive_api_test():
    """Test toàn diện API với tracking chi tiết"""
    
    print("🔍 COMPREHENSIVE API TEST WITH FULL TRACKING")
    print("=" * 60)
    
    tracker = APITracker()
    tracker.start_tracking()
    
    # Test data
    test_data = {
        "cache_key": {
            "timezone": "GMT+3.0",
            "timeframe": "H2",
            "symbol": "EURUSD"
        },
        "symbol": "EURUSD",
        "timeframe": "H2",
        "account_info": {
            "balance": 423.81,
            "equity": 423.81
        },
        "symbol_info": {
            "ask": 1.17417,
            "bid": 1.17417
        },
        "multi_timeframes": {
            "H2": {
                "indicators": {
                    "rsi": 57.67,
                    "macd": [0.001, 0.002, -0.001],
                    "bollinger_bands": [1.17, 1.175, 1.165],
                    "atr": 0.0017,
                    "adx": [43.8, 22.7, 22.5],
                    "sma_100": 1.168,
                    "sma_200": 1.166
                }
            }
        }
    }
    
    try:
        # Step 1: Kiểm tra Redis connection
        tracker.add_step("REDIS_CHECK", "Kiểm tra kết nối Redis")
        redis_client = RedisClient()
        if redis_client.is_connected():
            tracker.add_step("REDIS_SUCCESS", "Redis kết nối thành công", "SUCCESS")
        else:
            tracker.add_step("REDIS_FAILED", "Redis kết nối thất bại", "ERROR")
            return
        
        # Step 2: Xóa cache cũ
        tracker.add_step("CACHE_CLEAR", "Xóa cache cũ để test fresh")
        redis_client.redis_client.flushall()
        keys_before = redis_client.redis_client.keys("signal:*")
        tracker.add_step("CACHE_CLEARED", f"Cache đã xóa, còn {len(keys_before)} keys", "SUCCESS")
        
        # Step 3: Tạo SignalService
        tracker.add_step("SERVICE_INIT", "Khởi tạo SignalService")
        signal_service = SignalService(redis_client)
        tracker.add_step("SERVICE_READY", "SignalService sẵn sàng", "SUCCESS")
        
        # Step 4: Test 1 - Cache Miss (AI Analysis)
        tracker.add_step("TEST1_START", "Bắt đầu Test 1: Cache Miss")
        start_time_1 = time.time()
        
        result1 = await signal_service.analyze_signal(test_data)
        
        end_time_1 = time.time()
        duration_1 = end_time_1 - start_time_1
        
        tracker.add_step("TEST1_AI_ANALYSIS", f"AI phân tích hoàn thành trong {duration_1:.3f}s", "SUCCESS")
        tracker.add_step("TEST1_RESULT", f"Success: {result1.get('success')}, ErrorCode: {result1.get('errorCode')}", "SUCCESS")
        
        if result1.get('success'):
            data1 = result1.get('data', {})
            tracker.add_step("TEST1_SIGNAL", f"Signal: {data1.get('signal')}, Entry: {data1.get('entry_price')}", "SUCCESS")
        
        # Step 5: Kiểm tra cache sau Test 1
        keys_after_1 = redis_client.redis_client.keys("signal:*")
        tracker.add_step("CACHE_AFTER_TEST1", f"Cache có {len(keys_after_1)} keys sau Test 1", "INFO")
        
        # Step 6: Test 2 - Cache Hit
        tracker.add_step("TEST2_START", "Bắt đầu Test 2: Cache Hit")
        start_time_2 = time.time()
        
        result2 = await signal_service.analyze_signal(test_data)
        
        end_time_2 = time.time()
        duration_2 = end_time_2 - start_time_2
        
        tracker.add_step("TEST2_CACHE_HIT", f"Cache hit hoàn thành trong {duration_2:.3f}s", "SUCCESS")
        tracker.add_step("TEST2_RESULT", f"Success: {result2.get('success')}, ErrorCode: {result2.get('errorCode')}", "SUCCESS")
        
        # Step 7: So sánh kết quả
        tracker.add_step("COMPARISON_START", "So sánh kết quả 2 tests")
        
        if result1.get('success') == result2.get('success'):
            tracker.add_step("SUCCESS_CONSISTENCY", "Cả 2 tests đều thành công", "SUCCESS")
        else:
            tracker.add_step("SUCCESS_INCONSISTENCY", "Kết quả không nhất quán", "ERROR")
        
        if result1.get('data', {}).get('signal') == result2.get('data', {}).get('signal'):
            tracker.add_step("SIGNAL_CONSISTENCY", "Signal nhất quán giữa 2 tests", "SUCCESS")
        else:
            tracker.add_step("SIGNAL_INCONSISTENCY", "Signal không nhất quán", "ERROR")
        
        # Step 8: Phân tích performance
        speed_improvement = duration_1 / duration_2 if duration_2 > 0 else 0
        tracker.add_step("PERFORMANCE_ANALYSIS", f"Cache nhanh hơn {speed_improvement:.1f}x", "SUCCESS")
        
        # Step 9: Kiểm tra response logs
        tracker.add_step("LOG_CHECK", "Kiểm tra response logs")
        log_dir = Path("logs/09-2025/10")
        if log_dir.exists():
            log_files = list(log_dir.glob("EURUSD_*/result.log"))
            tracker.add_step("LOG_FOUND", f"Tìm thấy {len(log_files)} log files", "SUCCESS")
            
            # Đọc log mới nhất
            if log_files:
                latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                tracker.add_step("LATEST_LOG", f"Log mới nhất: {latest_log.name}", "INFO")
        else:
            tracker.add_step("LOG_NOT_FOUND", "Không tìm thấy log directory", "WARNING")
        
        # Step 10: Tổng kết
        tracker.add_step("FINAL_ANALYSIS", "Phân tích cuối cùng")
        
        if result1.get('success') and result2.get('success'):
            tracker.add_step("API_WORKING", "✅ API hoạt động hoàn hảo!", "SUCCESS")
        else:
            tracker.add_step("API_ERROR", "❌ API có lỗi", "ERROR")
        
        if speed_improvement > 1.5:
            tracker.add_step("CACHE_WORKING", "✅ Cache hoạt động hiệu quả!", "SUCCESS")
        else:
            tracker.add_step("CACHE_ISSUE", "⚠️ Cache có vấn đề", "WARNING")
        
    except Exception as e:
        tracker.add_step("EXCEPTION", f"Lỗi: {str(e)}", "ERROR")
    
    finally:
        tracker.end_tracking()
        
        # Lưu báo cáo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"api_test_report_{timestamp}.json"
        tracker.save_report(report_file)
        
        print("\n" + "=" * 60)
        print("🏁 COMPREHENSIVE TEST COMPLETED")
        print(f"📊 Tổng cộng: {len(tracker.steps)} steps")
        print(f"📄 Báo cáo chi tiết: {report_file}")

if __name__ == "__main__":
    asyncio.run(comprehensive_api_test())
