# 🚀 Deployment Guide

## Quick Start (Development)

```bash
# 1. Clone and setup
cd backend-god-level
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements/dev.txt

# 3. Install system dependencies
brew install tesseract poppler  # macOS
python -m spacy download en_core_web_sm

# 4. Configure environment
cp .env.example .env
# Edit .env and add GEMINI_API_KEY

# 5. Run server
python -m app.main
# Or: uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

---

## Production Deployment

### Option 1: Docker (Recommended)

#### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements/prod.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application
COPY app/ app/
COPY .env .env

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/antigravity
      - REDIS_URL=redis://redis:6379/0
      - USE_REDIS=true
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=antigravity
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  celery_worker:
    build: .
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/antigravity
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - redis
      - db
    restart: unless-stopped

volumes:
  postgres_data:
```

#### 3. Deploy

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Scale workers
docker-compose up -d --scale celery_worker=4
```

---

### Option 2: AWS Deployment

#### Architecture

```
Internet
    │
    ▼
Application Load Balancer (ALB)
    │
    ├─> ECS Fargate (FastAPI)
    │   ├─ Task 1
    │   ├─ Task 2
    │   └─ Task N
    │
    ├─> RDS PostgreSQL
    │
    ├─> ElastiCache Redis
    │
    └─> S3 (Resume storage)
```

#### 1. Create ECS Task Definition

```json
{
  "family": "antigravity-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-ecr-repo/antigravity:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql+asyncpg://..."
        },
        {
          "name": "REDIS_URL",
          "value": "redis://..."
        }
      ],
      "secrets": [
        {
          "name": "GEMINI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:..."
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/antigravity",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

#### 2. Deploy to ECS

```bash
# Build and push image
docker build -t antigravity:latest .
docker tag antigravity:latest your-ecr-repo/antigravity:latest
docker push your-ecr-repo/antigravity:latest

# Update ECS service
aws ecs update-service \
  --cluster antigravity-cluster \
  --service antigravity-backend \
  --force-new-deployment
```

---

### Option 3: Kubernetes

#### 1. Create Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: antigravity-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: antigravity
  template:
    metadata:
      labels:
        app: antigravity
    spec:
      containers:
      - name: backend
        image: your-registry/antigravity:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: antigravity-secrets
              key: gemini-api-key
        - name: DATABASE_URL
          value: "postgresql+asyncpg://..."
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 2. Create Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: antigravity-service
spec:
  type: LoadBalancer
  selector:
    app: antigravity
  ports:
  - port: 80
    targetPort: 8000
```

#### 3. Deploy

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check status
kubectl get pods
kubectl logs -f deployment/antigravity-backend
```

---

## Environment Configuration

### Production .env

```bash
# API Configuration
DEBUG=False
CORS_ORIGINS=https://yourdomain.com

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/antigravity

# AI Configuration
GEMINI_API_KEY=your_production_key
GEMINI_MODEL=gemini-2.0-flash-exp

# Redis
REDIS_URL=redis://redis-host:6379/0
USE_REDIS=True

# Celery
CELERY_BROKER_URL=redis://redis-host:6379/1
CELERY_RESULT_BACKEND=redis://redis-host:6379/2

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/app/uploads

# OCR
OCR_CONFIDENCE_THRESHOLD=30
OCR_DPI=200
```

---

## Database Setup

### PostgreSQL Migration

```bash
# 1. Install PostgreSQL
brew install postgresql  # macOS
# sudo apt-get install postgresql  # Ubuntu

# 2. Create database
createdb antigravity

# 3. Update .env
DATABASE_URL=postgresql+asyncpg://localhost/antigravity

# 4. Run migrations (if using Alembic)
alembic upgrade head
```

### Schema

```sql
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    raw_text TEXT,
    skills_extracted JSONB,
    skills_matched JSONB,
    skills_missing JSONB,
    ats_score INTEGER,
    experience_years FLOAT,
    hire_signal VARCHAR(50),
    summary TEXT,
    stage INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE job_descriptions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    required_skills JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_candidates_score ON candidates(ats_score DESC);
CREATE INDEX idx_candidates_stage ON candidates(stage);
```

---

## Monitoring Setup

### Prometheus Metrics

```python
# Add to app/main.py
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
resume_parsed_total = Counter('resume_parsed_total', 'Total resumes parsed')
resume_scored_total = Counter('resume_scored_total', 'Total resumes scored')
parsing_duration = Histogram('parsing_duration_seconds', 'PDF parsing duration')
scoring_duration = Histogram('scoring_duration_seconds', 'Scoring duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "AntiGravity Metrics",
    "panels": [
      {
        "title": "Resumes Processed",
        "targets": [
          {
            "expr": "rate(resume_parsed_total[5m])"
          }
        ]
      },
      {
        "title": "Average Parsing Time",
        "targets": [
          {
            "expr": "rate(parsing_duration_seconds_sum[5m]) / rate(parsing_duration_seconds_count[5m])"
          }
        ]
      }
    ]
  }
}
```

---

## Performance Tuning

### 1. Gunicorn Configuration

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4  # 2 * CPU cores + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
```

Run with:
```bash
gunicorn app.main:app -c gunicorn.conf.py
```

### 2. Redis Caching

```python
# Add to app/services/cache_service.py
import aioredis
from app.config.settings import settings

redis = aioredis.from_url(settings.REDIS_URL)

async def cache_skill_extraction(text_hash: str, result: dict):
    await redis.setex(
        f"skills:{text_hash}",
        settings.CACHE_TTL,
        json.dumps(result)
    )

async def get_cached_skills(text_hash: str):
    cached = await redis.get(f"skills:{text_hash}")
    return json.loads(cached) if cached else None
```

### 3. Database Connection Pooling

```python
# app/db/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

---

## Security Checklist

- [ ] **HTTPS only** - Use SSL/TLS certificates
- [ ] **API rate limiting** - Prevent abuse
- [ ] **Input validation** - Sanitize all inputs
- [ ] **File size limits** - Max 10MB per file
- [ ] **File type validation** - Check MIME types
- [ ] **Executable detection** - Block .exe, .sh files
- [ ] **SQL injection prevention** - Use parameterized queries
- [ ] **XSS prevention** - Escape HTML in responses
- [ ] **CORS configuration** - Whitelist allowed origins
- [ ] **Secret management** - Use environment variables or AWS Secrets Manager
- [ ] **Logging** - Log all security events
- [ ] **Monitoring** - Alert on suspicious activity

---

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump antigravity > /backups/antigravity_$DATE.sql
gzip /backups/antigravity_$DATE.sql

# Keep last 30 days
find /backups -name "antigravity_*.sql.gz" -mtime +30 -delete
```

### Resume Storage

```bash
# Sync uploads to S3
aws s3 sync /app/uploads s3://antigravity-resumes/ --delete
```

---

## Troubleshooting

### Common Issues

#### 1. Tesseract not found
```bash
# Install Tesseract
brew install tesseract poppler  # macOS
sudo apt-get install tesseract-ocr poppler-utils  # Ubuntu
```

#### 2. spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

#### 3. Gemini API rate limit
```bash
# Check error logs
# Increase retry delays in settings.py
GEMINI_RETRY_DELAYS = [20, 40, 80, 160]
```

#### 4. Out of memory
```bash
# Increase container memory
# Or reduce batch size
BATCH_SIZE=50  # Instead of 100
```

---

## Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
from locust import HttpUser, task, between

class ResumeUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def score_resume(self):
        with open("test_resume.pdf", "rb") as f:
            self.client.post(
                "/api/score-resume",
                files={"file": f},
                data={"job_description": "Python developer"}
            )

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

---

## Rollback Plan

```bash
# Docker rollback
docker-compose down
docker-compose up -d --build --force-recreate

# Kubernetes rollback
kubectl rollout undo deployment/antigravity-backend

# ECS rollback
aws ecs update-service \
  --cluster antigravity-cluster \
  --service antigravity-backend \
  --task-definition antigravity-backend:previous-version
```

---

## Support

For deployment issues:
- Check logs: `docker-compose logs -f`
- Health endpoint: `curl http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

---

**Last Updated:** 2026-05-05  
**Version:** 2.0.0
