# FX API - Multi-Version FastAPI với Docker Stack

Dự án FastAPI hoàn chỉnh với **Multi-Version API support**, MongoDB, Redis và Nginx reverse proxy được containerized bằng Docker.

## 🏗️ Kiến trúc

- **FastAPI**: Multi-version web framework cho Python API
  - **API V1**: Backward compatible - Simple CRUD operations
  - **API V2**: Enhanced features - Caching, pagination, filtering
- **MongoDB**: Database chính cho persistent data
- **Redis**: Cache và session storage cho performance
- **Nginx**: Reverse proxy và load balancer

## 🔄 API Versioning Strategy

### API V1 (Backward Compatible)
- **Prefix**: `/api/v1`
- **Features**: Basic CRUD, Simple responses
- **Use case**: Legacy clients, simple operations
- **Endpoints**:
  - `POST /api/v1/items/` - Create item
  - `GET /api/v1/items/{id}` - Read item
  - `GET /api/v1/health` - Health check

### API V2 (Enhanced Features)  
- **Prefix**: `/api/v2`
- **Features**: 
  - Redis caching for performance
  - Pagination support
  - Advanced filtering (category, tags)
  - Enhanced data models (tags, metadata, priority)
  - Detailed responses with meta information
- **Use case**: New applications requiring advanced features
- **Endpoints**:
  - `POST /api/v2/items/` - Create enhanced item
  - `GET /api/v2/items/{id}` - Read item (cached)
  - `PUT /api/v2/items/{id}` - Update item
  - `DELETE /api/v2/items/{id}` - Delete item
  - `GET /api/v2/items/` - List items (paginated + filtered)
  - `GET /api/v2/health/detailed` - Detailed health check

## 🚀 Cách chạy

### 1. Production Mode
```bash
# Build và chạy tất cả services
docker-compose up -d --build

# Kiểm tra logs
docker-compose logs -f

# Dừng services
docker-compose down
```

### 2. Development Mode
```bash
# Chạy với hot reload
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d --build

# Xem logs real-time
docker-compose logs -f fastapi
```

## 🧪 Testing

### Test toàn bộ stack
```bash
# Cài đặt requests (nếu chưa có)
pip install requests

# Chạy test script
python test_stack.py
```

### Manual testing

#### Global endpoints
```bash
# Global health check
curl http://localhost:8080/health

# API documentation
curl http://localhost:8080/
```

#### API V1 (Backward Compatible)
```bash
# V1 Health check
curl http://localhost:8080/api/v1/health

# V1 Create item (simple)
curl -X POST "http://localhost:8080/api/v1/items/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Item V1", "description": "Simple description"}'

# V1 Read item
curl http://localhost:8080/api/v1/items/{id}
```

#### API V2 (Enhanced Features)
```bash
# V2 Detailed health check
curl http://localhost:8080/api/v2/health/detailed

# V2 Create enhanced item
curl -X POST "http://localhost:8080/api/v2/items/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Enhanced Item V2",
       "description": "Advanced description",
       "tags": ["api", "v2", "enhanced"],
       "category": "development",
       "priority": 3,
       "metadata": {"source": "manual_test"}
     }'

# V2 Read item (with caching)
curl http://localhost:8080/api/v2/items/{id}

# V2 Update item
curl -X PUT "http://localhost:8080/api/v2/items/{id}" \
     -H "Content-Type: application/json" \
     -d '{"priority": 5, "tags": ["updated", "v2"]}'

# V2 List items with filtering
curl "http://localhost:8080/api/v2/items/?page=1&per_page=10&category=development&tags=api"

# V2 Delete item
curl -X DELETE "http://localhost:8080/api/v2/items/{id}"
```

#### Legacy endpoints (backward compatibility)
```bash
# Legacy Redis test
curl http://localhost:8080/redis/

# Direct FastAPI access (bypass Nginx)
curl http://localhost:8001/health
```

## 🔧 Configuration

### Ports
- **8080**: Nginx (external access)
- **8001**: FastAPI (external access, optional)
- **27019**: MongoDB (external access)
- **6381**: Redis (external access)

### Internal Ports (trong Docker network)
- **80**: Nginx (internal)
- **8000**: FastAPI (internal, qua Nginx)
- **27017**: MongoDB (internal)
- **6379**: Redis (internal)

### Environment Variables
```bash
MONGO_URI=mongodb://mongo:27017
REDIS_URI=redis://redis:6379
```

## 📁 Cấu trúc dự án

```
fx-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/              # Pydantic models
│   ├── routers/             # API routes
│   └── services/            # Business logic
├── nginx/
│   └── nginx.conf           # Nginx configuration
├── docker-compose.yml       # Production compose
├── docker-compose.override.yml # Development overrides
├── Dockerfile               # FastAPI container
├── requirements.txt         # Python dependencies
├── test_stack.py           # Testing script
└── README.md               # This file
```

## 🔍 Monitoring

### Health Checks
- **API Health**: `GET http://localhost:8080/health` (qua Nginx)
- **Direct API**: `GET http://localhost:8001/health` (direct FastAPI)
- **Nginx Health**: `GET http://localhost:8080/health` (custom endpoint)

### Logs
```bash
# Xem logs của tất cả services
docker-compose logs

# Xem logs của service cụ thể
docker-compose logs fastapi
docker-compose logs mongo
docker-compose logs redis
docker-compose logs nginx
```

## 🛠️ Development

### Rebuild after code changes
```bash
# Rebuild FastAPI container
docker-compose up -d --build fastapi
```

### Database Operations
```bash
# Connect to MongoDB
docker exec -it mongo_db mongosh

# Connect to Redis
docker exec -it redis_cache redis-cli
```

## 🚧 Troubleshooting

### Common Issues

1. **Port conflicts**: Đảm bảo ports 8080, 8001, 27019, 6381 không bị sử dụng
2. **Build failures**: Xóa images cũ: `docker-compose down --rmi all`
3. **Database connection**: Kiểm tra logs: `docker-compose logs mongo redis`

### External Database Access
```bash
# MongoDB connection string (external)
mongodb://localhost:27019

# Redis connection (external)
redis://localhost:6381

# Connect to MongoDB shell
docker exec -it mongo_db mongosh mongodb://localhost:27017

# Connect to Redis CLI
docker exec -it redis_cache redis-cli
```

### Reset toàn bộ stack
```bash
# Dừng và xóa tất cả
docker-compose down -v --rmi all

# Rebuild từ đầu
docker-compose up -d --build
```
