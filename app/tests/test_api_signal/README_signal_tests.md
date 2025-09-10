# Signal API Test Suite

Bộ test để kiểm tra API `/signal` với cache mechanism và response format.

## 📁 Files

### 🎯 **Test chính thức (Core Tests):**

#### 1. `simple_signal_test.py`
- **Mục đích:** Test đơn giản, nhanh chóng
- **Tính năng:** 
  - 2 requests liên tiếp với cùng data
  - Kiểm tra cache behavior (response time improvement)
  - Validate response format cơ bản
- **Sử dụng:** `python app/tests/test_api_signal/simple_signal_test.py`

#### 2. `test_signal_api_cache.py`
- **Mục đích:** Test chi tiết và comprehensive
- **Tính năng:**
  - Async requests với aiohttp
  - Detailed response validation
  - Cache behavior analysis
  - Response consistency checking
  - JSON output với kết quả chi tiết
- **Sử dụng:** `python app/tests/test_api_signal/test_signal_api_cache.py`

#### 3. `comprehensive_api_test.py`
- **Mục đích:** Test toàn diện với tracking chi tiết
- **Tính năng:**
  - Full tracking từng bước
  - Redis connection test
  - Cache clear và verification
  - Performance analysis
  - Detailed JSON report
- **Sử dụng:** `python app/tests/test_api_signal/comprehensive_api_test.py`

#### 4. `run_signal_tests.py`
- **Mục đích:** Chạy tất cả tests
- **Tính năng:**
  - Chạy cả 3 test files
  - Summary report
  - Timeout handling
- **Sử dụng:** `python app/tests/test_api_signal/run_signal_tests.py`

### 🔧 **Test hỗ trợ (Support Tests):**

#### 5. `test_prompt_service.py`
- **Mục đích:** Test PromptService riêng biệt
- **Sử dụng:** `python app/tests/test_api_signal/test_prompt_service.py`

#### 6. `test_prompt_generation.py`
- **Mục đích:** Test prompt generation với nhiều sample data
- **Sử dụng:** `python app/tests/test_api_signal/test_prompt_generation.py`

#### 7. `test_prompt_ai_integration.py`
- **Mục đích:** Test tích hợp PromptService + AIService
- **Sử dụng:** `python app/tests/test_api_signal/test_prompt_ai_integration.py`

## 🚀 Cách sử dụng

### Prerequisites
```bash
pip install requests aiohttp
```

### Chạy test đơn giản
```bash
python tests/simple_signal_test.py
```

### Chạy test chi tiết
```bash
python tests/test_signal_api_cache.py
```

### Chạy tất cả tests
```bash
python tests/run_signal_tests.py
```

## 📊 Test Data

Tests sử dụng sample data từ `signal.mdc` với:
- **Symbol:** EURUSD
- **Timeframe:** H2
- **Cache Key:** `signal:GMT+3.0:H2:EURUSD`
- **Multi-timeframe data:** D1, H2, M30 với indicators và price action

## 🔍 Test Scenarios

### Scenario 1: Cache Miss (Request 1)
- Gửi request đầu tiên với sample data
- API sẽ:
  1. Generate prompt từ multi_timeframes data
  2. Call AI service để phân tích
  3. Cache result với TTL 10 phút
  4. Return response

### Scenario 2: Cache Hit (Request 2)
- Gửi request thứ hai với cùng data
- API sẽ:
  1. Check cache với key `signal:GMT+3.0:H2:EURUSD`
  2. Return cached result (nhanh hơn)
  3. Không gọi AI service

## ✅ Expected Results

### Response Format
```json
{
  "success": true,
  "errorMsg": "",
  "errorCode": 0,
  "data": {
    "signal": "BUY/SELL/HOLD",
    "entry_price": 1.17417,
    "stop_loss": 1.16917,
    "take_profit": 1.17917,
    "confidence": 0.85,
    "timestamp": "2025-01-10T08:00:00Z",
    "cache_key": "signal:GMT+3.0:H2:EURUSD"
  }
}
```

### Cache Behavior
- **Request 1:** Response time cao hơn (AI processing)
- **Request 2:** Response time thấp hơn (cache hit)
- **Consistency:** Cùng response data cho cả 2 requests

## 🐛 Troubleshooting

### API không chạy
```bash
# Kiểm tra API status
curl http://localhost:8000/health
```

### Redis connection error
- Đảm bảo Redis server đang chạy
- Check Redis URI trong config

### AI API error
- Check AI_API_KEY trong environment
- Verify OpenRouter endpoint

### Timeout errors
- Tăng timeout trong test scripts
- Check network connectivity

## 📈 Performance Metrics

Tests sẽ track:
- Response time cho mỗi request
- Cache hit/miss ratio
- Response consistency
- Error rates

## 🔧 Configuration

### API Base URL
Mặc định: `http://localhost:8000`
Có thể thay đổi trong test files:
```python
API_BASE_URL = "http://your-api-url:port"
```

### Timeout Settings
```python
timeout=aiohttp.ClientTimeout(total=30)  # 30 seconds
```

## 📝 Output Files

- `signal_api_test_results.json`: Detailed test results
- Console output: Real-time test progress
- Error logs: Captured exceptions và errors
