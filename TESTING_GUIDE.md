# 🧪 ODRA System Testing Guide

## 🚀 Quick Start

### 1. Запуск Системы

**Автоматический запуск (рекомендуется):**
```bash
cd "/Users/danikosnarev/Desktop/ODRA 2"
source .venv/bin/activate
./START_SYSTEM.sh
```

**Или запустить компоненты отдельно:**

**Terminal 1 - Backend API:**
```bash
cd "/Users/danikosnarev/Desktop/ODRA 2/backend"
source ../.venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend Dev Server:**
```bash
cd "/Users/danikosnarev/Desktop/ODRA 2/frontend"
npm run dev
```

---

## 🧪 Testing Scenarios

### Test 1: Backend Health Check
```bash
curl http://localhost:8000/health | jq .
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "embeddings": "ready",
  "task_queue": "ready",
  "timestamp": "2026-02-08T21:00:00.000000"
}
```

---

### Test 2: API Documentation
Access interactive API docs:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

### Test 3: Ingest Documents

**Upload a single document:**
```bash
curl -X POST http://localhost:8000/ingest/batch \
  -H "X-API-Key: dev-key-change-in-production" \
  -F "files=@test_document.txt"
```

**Example test file content:**
```
Financial Report Q1 2024
Total Revenue: 5000000
Total Expenses: 3000000
Net Profit: 2000000
Transaction Count: 15
```

**Expected Response:**
```json
{
  "total_files": 1,
  "queued": 1,
  "results": [
    {
      "task_id": "ingest_xxxxx",
      "filename": "test_document.txt",
      "status": "queued"
    }
  ]
}
```

---

### Test 4: Start Audit Job

**Create audit job:**
```bash
curl -X POST http://localhost:8000/audit/run \
  -H "X-API-Key: dev-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Verify financial accuracy",
    "scope": "finance",
    "priority": 9
  }'
```

**Expected Response:**
```json
{
  "job_id": "job_xxxxx",
  "status": "pending",
  "created_at": "2026-02-08T21:00:00.000000"
}
```

---

### Test 5: Get Audit Status

**Check audit progress:**
```bash
curl http://localhost:8000/audit/status/job_xxxxx | jq .
```

**Expected Response:**
```json
{
  "job_id": "job_xxxxx",
  "status": "processing",
  "progress_percent": 25,
  "total_documents": 10,
  "processed_documents": 3,
  "metrics": {
    "precision": 0.85,
    "recall": 0.80
  },
  "current_iteration": 1
}
```

---

### Test 6: Get Audit Report

**Get final audit report:**
```bash
curl http://localhost:8000/audit/report/job_xxxxx | jq .
```

---

### Test 7: Submit Feedback

**Provide feedback on evidence:**
```bash
curl -X POST http://localhost:8000/audit/feedback/job_xxxxx \
  -H "X-API-Key: dev-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "doc_123",
    "feedback": "relevant",
    "comment": "This document contains critical evidence"
  }'
```

---

## 🔑 API Keys

**Development API Key:** `dev-key-change-in-production`

> ⚠️ **IMPORTANT:** Change this in production! See `backend/app/config.py`

---

## 📊 Running Integration Tests

```bash
cd "/Users/danikosnarev/Desktop/ODRA 2"
source .venv/bin/activate
python test_integration.py
```

**What it tests:**
- ✅ Backend API health
- ✅ Document ingestion
- ✅ Audit job creation
- ✅ Status retrieval
- ✅ Database connectivity

---

## 🎨 Frontend Interface

Access the web UI at: **http://localhost:5173**

**Features:**
- 📤 Upload documents
- 🔍 View audit jobs
- 📊 Track progress
- 📋 View audit reports
- 💬 Submit feedback

---

## 🐛 Troubleshooting

### Backend not starting?
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process if needed
kill -9 <PID>
```

### Frontend not starting?
```bash
# Check if port 5173 is in use
lsof -i :5173

# Clear npm cache
npm cache clean --force
rm -rf node_modules
npm install
```

### Database errors?
```bash
# Reinitialize database
rm odra.db
python init_db.py
```

### Import errors?
```bash
# Verify PYTHONPATH
export PYTHONPATH="/Users/danikosnarev/Desktop/ODRA 2/backend:/Users/danikosnarev/Desktop/ODRA 2/workers"

# Reinstall dependencies
pip install -r backend/requirements.txt
```

---

## 📈 Performance Testing

**Load test with multiple documents:**
```bash
# Create 10 test documents
for i in {1..10}; do
  echo "Document $i - Total: $((i*1000)), Sum: $((i*500))" > test_doc_$i.txt
  curl -X POST http://localhost:8000/ingest/batch \
    -H "X-API-Key: dev-key-change-in-production" \
    -F "files=@test_doc_$i.txt"
done
```

---

## 🔄 Background Worker

The worker processes documents asynchronously:

**Check worker logs:**
```bash
tail -f nohup.out
```

**Manually run worker:**
```bash
cd "/Users/danikosnarev/Desktop/ODRA 2"
source .venv/bin/activate
PYTHONPATH="backend:workers" python workers/processor.py
```

---

## 📝 Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/ingest/batch` | Upload documents |
| GET | `/ingest/status/{task_id}` | Check ingestion status |
| POST | `/audit/run` | Start audit job |
| GET | `/audit/status/{job_id}` | Check audit progress |
| GET | `/audit/report/{job_id}` | Get audit report |
| POST | `/audit/feedback/{job_id}` | Submit feedback |

---

## 🎯 Next Steps

1. **Access the system:** http://localhost:5173
2. **Upload test documents** via the web UI
3. **Start an audit** with your criteria
4. **Monitor progress** in real-time
5. **Review reports** when complete

---

## 📞 Support

- Backend API Docs: http://localhost:8000/docs
- Check logs for detailed errors
- Verify all services are running: `ps aux | grep -E "(uvicorn|npm)"`

