# 🔧 HƯỚNG DẪN CẤU HÌNH TIMEOUT

## 📋 Tổng quan
Tất cả các thông số timeout đã được tập trung hóa vào file `app/core/config.py` và có thể điều chỉnh thông qua environment variables.

## 🎯 Các thông số có thể cấu hình

### 1. Nginx Timeout Settings
```bash
NGINX_PROXY_CONNECT_TIMEOUT=300    # 5 phút
NGINX_PROXY_SEND_TIMEOUT=300       # 5 phút  
NGINX_PROXY_READ_TIMEOUT=300       # 5 phút
```

### 2. AI Provider Timeout Settings
```bash
AI_PROVIDER_TIMEOUT=300            # 5 phút
AI_PROVIDER_RETRY_ATTEMPTS=3       # Số lần retry
AI_PROVIDER_RETRY_MIN_WAIT=2       # Thời gian chờ tối thiểu (giây)
AI_PROVIDER_RETRY_MAX_WAIT=10      # Thời gian chờ tối đa (giây)
```

### 3. Redis Timeout Settings
```bash
REDIS_LOCK_TIMEOUT=300             # 5 phút
REDIS_CACHE_WAIT_TIMEOUT=300       # 5 phút
REDIS_CACHE_TTL=600                # 10 phút
REDIS_BLOCKING_TIMEOUT=0.1         # 100ms
```

### 4. Signal Service Timeout Settings
```bash
SIGNAL_SERVICE_LOCK_TIMEOUT=300    # 5 phút
SIGNAL_SERVICE_CACHE_WAIT_TIMEOUT=300  # 5 phút
SIGNAL_SERVICE_CACHE_TTL=600       # 10 phút
```

## 🚀 Cách sử dụng

### 1. Tạo file .env
```bash
cp env.example .env
```

### 2. Chỉnh sửa các giá trị trong .env
```bash
# Ví dụ: Tăng timeout lên 10 phút
AI_PROVIDER_TIMEOUT=600
NGINX_PROXY_READ_TIMEOUT=600
```

### 3. Restart services
```bash
docker-compose down
docker-compose up -d --build
```

## 📊 Timeout Chain
```
Client Request → Nginx (NGINX_PROXY_READ_TIMEOUT) → FastAPI → AI Provider (AI_PROVIDER_TIMEOUT) → Redis (REDIS_LOCK_TIMEOUT)
```

## ⚡ Tối ưu hóa theo môi trường

### Development (Nhanh hơn)
```bash
AI_PROVIDER_TIMEOUT=60
NGINX_PROXY_READ_TIMEOUT=60
REDIS_LOCK_TIMEOUT=60
```

### Production (Ổn định hơn)
```bash
AI_PROVIDER_TIMEOUT=300
NGINX_PROXY_READ_TIMEOUT=300
REDIS_LOCK_TIMEOUT=300
```

### High Load (Tăng cường)
```bash
AI_PROVIDER_TIMEOUT=600
NGINX_PROXY_READ_TIMEOUT=600
REDIS_LOCK_TIMEOUT=600
REDIS_CACHE_TTL=1200
```

## 🔍 Monitoring
- Kiểm tra logs: `docker-compose logs -f fastapi`
- Monitor timeout errors trong logs
- Điều chỉnh timeout dựa trên thực tế sử dụng

## ⚠️ Lưu ý
- Tất cả timeout phải đồng bộ với nhau
- Nginx timeout phải >= AI Provider timeout
- Redis timeout phải >= Signal Service timeout
- Test kỹ sau khi thay đổi timeout
