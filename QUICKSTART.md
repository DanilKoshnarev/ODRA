# ODRA Quick Start Guide

## 🚀 30-Second Setup

```bash
# Clone and enter directory
git clone <repo> && cd ODRA

# Start all services with Docker Compose
docker-compose up -d

# Wait for services
sleep 10

# Access the application
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Health: http://localhost:8000/health
```

## 📝 First Audit (5 Minutes)

1. **Open Frontend**: http://localhost:5173
2. **Enter Audit Goal**: "Find suspicious purchases in Q4 2024"
3. **Click Start Audit**
4. **Monitor Progress**: Watch real-time metrics
5. **View Report**: Download JSON with evidence

## 🔧 Local Development (No Docker)

### Backend Only
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend Only
```bash
cd frontend
npm install
npm run dev
```

## 📊 Generate Sample Data

```bash
# 1000 synthetic documents (~15 minutes)
python scripts/generate_sample_data.py

# Or via Docker
docker-compose exec backend python ../scripts/generate_sample_data.py
```

## 🧪 Run Tests

```bash
cd backend
pytest tests/ -v
```

## 🔑 API Key

Default development key: `dev-key-change-in-production`

Set in requests:
```bash
curl -H "X-API-Key: dev-key-change-in-production" http://localhost:8000/health
```

## 📈 Enable Production Features

### ClickHouse Instead of SQLite
```bash
# Set in .env or docker-compose.yml
USE_CLICKHOUSE=True
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_PORT=9000
```

### Anthropic LLM
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### Celery + Redis Workers
```bash
USE_CELERY=True
REDIS_URL=redis://redis:6379/0
```

## 🐛 Troubleshooting

**Port already in use?**
```bash
docker-compose down
docker ps -a
```

**Database locked?**
```bash
rm backend/odra.db
docker-compose restart backend
```

**Embeddings slow?**
- First run downloads model (~400MB)
- Subsequent runs are fast

## 📞 Next Steps

1. Read [README.md](./README.md) for full documentation
2. Check [PoC Roadmap](./README.md#-next-steps---poc-roadmap) for features
3. Integrate Anthropic API keys
4. Load your own documents
5. Fine-tune audit parameters

---

For detailed documentation, see [README.md](./README.md)
