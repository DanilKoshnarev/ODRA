# ODRA - Outcome-Driven RAG Auditor

**Status:** MVP (v0.1.0) - Working end-to-end flow with fallback mode support

A semantic document processing system that uses Retrieval-Augmented Generation (RAG) to analyze large document batches and generate audit reports with evidence. Built for compliance, trust, and security.

## 🚀 Features

- **Semantic Sharding**: Documents are automatically sharded based on metadata and embeddings for parallel processing
- **Parallel Document Processing**: Process 100+ documents simultaneously with async workers
- **Vector Search**: Cosine similarity-based search on stored embeddings
- **RAG Synthesis**: LLM-powered report generation with evidence links
- **Audit Jobs**: Track job progress and retrieve final reports with evidence
- **Human Feedback**: Submit feedback on evidence for future retraining
- **Observability**: Prometheus metrics and health checks built-in
- **Compliance-Ready**: API key authentication, PII redaction stub, audit trails

## 📋 Tech Stack

### Backend
- **Framework**: FastAPI + Uvicorn
- **Database**: SQLite (fallback) or ClickHouse (production)
- **Embeddings**: Sentence-Transformers (local) with Anthropic/OpenAI abstraction
- **Task Queue**: In-process queue (fallback) or Celery+Redis (production)
- **Python**: 3.11+

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Observability**: Prometheus metrics

## 🏃 Quick Start (Fallback Mode - No External Dependencies)

### Prerequisites
- Docker & Docker Compose
- OR: Python 3.11, Node.js 18 (for local development)

### Option 1: Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd ODRA

# Start all services (backend, frontend, Redis - no ClickHouse/Temporal needed)
docker-compose up -d

# Wait for services to be ready
sleep 10

# Check health
curl http://localhost:8000/health

# Frontend available at http://localhost:5173
# Backend API at http://localhost:8000
```

### Option 2: Local Development (Fallback Mode)

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Set environment variables
cat > .env << 'ENV'
API_KEY=dev-key-change-in-production
DATABASE_URL=sqlite:///./odra.db
USE_CLICKHOUSE=False
USE_CELERY=False
LLM_PROVIDER=mock
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
ENV

# Start backend
python -m uvicorn app.main:app --reload

# In another terminal - Frontend setup
cd frontend
npm install
npm run dev  # Frontend at http://localhost:5173
```

## 🔧 Configuration

### Environment Variables

**Backend** (`backend/.env`):
```
# API Security
API_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Database (SQLite for local, ClickHouse for production)
DATABASE_URL=sqlite:///./odra.db
USE_CLICKHOUSE=False
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_DB=odra

# Task Queue (in-process for local, Celery+Redis for production)
REDIS_URL=redis://localhost:6379/0
USE_CELERY=False

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# LLM (mock, anthropic, openai)
LLM_PROVIDER=mock
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx

# Processing
MAX_WORKERS=4
CHUNK_SIZE=1000
OVERLAP=100

# Audit Parameters
TARGET_PRECISION=0.85
MAX_ITERATIONS=5
PRECISION_WEIGHT=0.7
RECALL_WEIGHT=0.2
COST_WEIGHT=0.1
```

**Frontend** (`frontend/.env`):
```
VITE_API_URL=http://localhost:8000
```

## 📖 Usage

### 1. Start an Audit Job

```bash
curl -X POST http://localhost:8000/audit/run \
  -H "X-API-Key: dev-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Find suspicious purchases in 2024",
    "scope": "Finance Department",
    "priority": 8
  }'

# Response:
# {
#   "job_id": "job_a1b2c3d4e5f6",
#   "status": "pending",
#   "created_at": "2024-02-06T10:30:00Z"
# }
```

### 2. Check Job Status

```bash
curl http://localhost:8000/audit/status/job_a1b2c3d4e5f6 \
  -H "X-API-Key: dev-key-change-in-production"

# Response includes: progress_percent, processed_documents, metrics (precision, recall)
```

### 3. Get Audit Report

```bash
curl http://localhost:8000/audit/report/job_a1b2c3d4e5f6 \
  -H "X-API-Key: dev-key-change-in-production"

# Response includes: evidence array with doc_id, snippet, relevance_score, summary, recommendations
```

### 4. Ingest Documents

```bash
curl -X POST http://localhost:8000/ingest/batch \
  -H "X-API-Key: dev-key-change-in-production" \
  -F "files=@document1.txt" \
  -F "files=@document2.pdf"
```

### 5. Submit Human Feedback

```bash
curl -X POST http://localhost:8000/audit/feedback/job_a1b2c3d4e5f6 \
  -H "X-API-Key: dev-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "doc_xyz",
    "feedback": "relevant",
    "comment": "This is clearly suspicious"
  }'
```

## 📊 Web UI

Access the frontend at `http://localhost:5173`:

- **Home**: Submit audit goals and track job IDs
- **Job Status**: Real-time progress monitoring with metrics
- **Report**: View evidence with relevance scores and download JSON
- **Admin**: System health, feature status, configuration

## 🛠️ Production Mode Setup

### Enable ClickHouse

```bash
# Set in backend/.env or environment:
USE_CLICKHOUSE=True
CLICKHOUSE_HOST=clickhouse-server.example.com
CLICKHOUSE_PORT=9000
CLICKHOUSE_DB=odra

# Run ClickHouse migrations:
# (Already included in docker-compose - init.sql will auto-run)
```

### Enable Celery + Redis for Workers

```bash
# Set in backend/.env:
USE_CELERY=True
REDIS_URL=redis://redis-prod.example.com:6379/0

# The worker service will automatically pick up tasks from the queue
```

### Integrate with Anthropic/OpenAI

```bash
# Set LLM provider:
LLM_PROVIDER=anthropic  # or "openai"
ANTHROPIC_API_KEY=sk-ant-xxxxx

# The auditor will now use Claude for report synthesis instead of mock LLM
```

## �� Testing

### Run Backend Tests

```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v
```

### Generate Sample Data

```bash
cd scripts
python generate_sample_data.py

# Generates 1000 synthetic audit-ready documents
# Ingests them into SQLite (fallback) or ClickHouse (if enabled)
```

### E2E Test Stub (Playwright)

```bash
cd frontend
npm install @playwright/test
npx playwright test

# Basic e2e test to verify UI navigation
```

## 📊 Observability

### Prometheus Metrics

```bash
# Metrics endpoint:
curl http://localhost:8000/metrics

# Includes:
# - API request counts and latencies
# - Task queue depth
# - Document processing statistics
# - Audit job metrics
```

### Health Check

```bash
curl http://localhost:8000/health

# Response includes:
# {
#   "status": "healthy",
#   "database": "connected",
#   "embeddings": "ready",
#   "task_queue": "ready"
# }
```

## ��️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (React)                        │
│                    http://localhost:5173                      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    FastAPI Backend                           │
│  POST /audit/run, /ingest/batch, GET /audit/report/{id}   │
│              http://localhost:8000                           │
└────────┬───────────────────┬───────────────────┬────────────┘
         │                   │                   │
    ┌────▼─────┐        ┌────▼─────┐      ┌─────▼────┐
    │  SQLite  │        │   Redis  │      │ Sentence │
    │   (DB)   │        │  (Queue) │      │Transform │
    │Fallback  │        │ Optional │      │  (LLM)   │
    └──────────┘        └──────────┘      └──────────┘
         │                   │
         └───────────────────┴─────── ClickHouse (Optional)
                              │
                         ┌────▼─────┐
                         │  Celery  │
                         │ Workers  │
                         └──────────┘
```

## 🔐 Security Considerations

### Implemented
- ✅ API Key authentication on sensitive endpoints
- ✅ CORS policy configuration
- ✅ Input validation (Pydantic models)
- ✅ Database connection security

### TODO (Production Hardening)
- [ ] Rate limiting on public endpoints
- [ ] PII redaction in logs and storage
- [ ] Encryption at rest for embeddings
- [ ] JWT-based session tokens
- [ ] Request signing for audit trails
- [ ] Database connection pooling limits
- [ ] Cost control per user/job

## 📈 Scaling Considerations

### Current Limits (Fallback Mode)
- Max workers: 4 (configurable)
- Max documents per batch: 1000s
- Max embedding dimension: 384
- Typical processing: ~100 docs/min per worker

### Production Scaling
- **Horizontal**: Scale workers via Celery task distribution
- **Vertical**: Increase worker resources and batch sizes
- **Storage**: Partition ClickHouse by date, use HNSW indexes for vector search
- **Caching**: Use Redis for embedding cache and search results
- **Optimization**: Implement async document parsing, batch embeddings

## 🚦 Reward Function (Stub Implementation)

The auditor uses a simple reward function to decide when to stop iterating:

```
reward = precision_weight * precision + recall_weight * recall - cost_weight * cost

Stop condition: precision >= target_precision OR iterations >= max_iterations
```

### Current Weights
- `PRECISION_WEIGHT=0.7` (70% importance)
- `RECALL_WEIGHT=0.2` (20% importance)  
- `COST_WEIGHT=0.1` (10% cost penalty)

Tune these in `.env` based on your use case.

## 📝 Project Structure

```
ODRA/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── config.py          # Configuration
│   │   ├── models.py          # Pydantic schemas
│   │   ├── db.py              # Database models
│   │   ├── security.py        # Auth utilities
│   │   ├── api/               # Route handlers
│   │   │   ├── audit.py       # Audit endpoints
│   │   │   ├── ingest.py      # Ingest endpoints
│   │   │   └── health.py      # Health check
│   │   └── services/          # Business logic
│   │       ├── embeddings.py  # LLM abstraction
│   │       ├── ingest.py      # Document processing
│   │       ├── auditor.py     # RAG synthesis
│   │       └── task_queue.py  # Task orchestration
│   ├── tests/
│   │   ├── test_ingest.py
│   │   └── test_auditor.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React application
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── api/               # API client
│   │   ├── App.tsx            # Root component
│   │   └── index.css          # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── workers/                    # Background processors
│   ├── processor.py           # Worker logic
│   └── Dockerfile
├── clickhouse/                # Database schema
│   └── init.sql              # DDL statements
├── scripts/
│   └── generate_sample_data.py # 1000 doc generator
├── docker-compose.yml         # Local infrastructure
├── .github/workflows/ci.yml    # GitHub Actions CI/CD
└── README.md                  # This file
```

## 🎯 Next Steps - PoC Roadmap

### Phase 1: Validation ✅ (Current)
- [x] End-to-end flow (ingest → audit → report)
- [x] Fallback mode (SQLite + in-process queue)
- [x] Basic UI (home, job, report, admin)
- [x] Sample data generator (1000 docs)

### Phase 2: Scale Test (Next Sprint)
- [ ] **Scale Test 100K Documents**
  - Benchmark ingestion throughput
  - Test vector search latency
  - Optimize embedding batch sizes
  - Monitor memory/CPU usage
  
- [ ] **Worker Pool Optimization**
  - Add Celery workers for parallel processing
  - Implement retry logic with exponential backoff
  - Add checkpoint/resume capability
  
- [ ] **Vector Index Optimization**
  - Enable HNSW index in ClickHouse
  - Benchmark search performance
  - Implement approximate nearest neighbor search

### Phase 3: Human Review (Q2)
- [ ] **Human Feedback UI**
  - Evidence annotation interface
  - Batch labeling tools
  - Feedback aggregation and analytics
  
- [ ] **Active Learning Loop**
  - Retrain embeddings with human feedback
  - Implement confidence scoring
  - Add uncertainty sampling

### Phase 4: Production Integration (Q2)
- [ ] **Anthropic/OpenAI Integration**
  - Replace mock LLM with Claude 3 / GPT-4
  - Implement prompt templates for audit context
  - Add cost tracking and budget alerts
  
- [ ] **Advanced Auditor**
  - Multi-step reasoning with sub-queries
  - Chain-of-thought prompts
  - Evidence confidence scoring
  
- [ ] **Compliance & Security**
  - PII redaction pipeline (using nlp-privacy)
  - Audit trail logging
  - Access control (RBAC)
  - Data retention policies

### Phase 5: Enterprise Features (Q3)
- [ ] **Advanced Observability**
  - Full Grafana dashboard
  - Custom metrics and alerts
  - Audit log visualization
  
- [ ] **Multi-Tenant Support**
  - Workspace isolation
  - Custom branding
  - Usage quotas and billing
  
- [ ] **API Enhancements**
  - Webhook notifications
  - Async job polling with websockets
  - Export formats (PDF, Excel)

## 📚 Additional Resources

- **Embeddings**: [Sentence-Transformers Docs](https://www.sbert.net/)
- **ClickHouse**: [Documentation](https://clickhouse.com/docs)
- **FastAPI**: [Official Guide](https://fastapi.tiangolo.com/)
- **RAG Pattern**: [LangChain RAG Docs](https://python.langchain.com/docs/use_cases/question_answering/)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/audit-improvements`
2. Make changes and add tests
3. Run tests: `pytest tests/ -v`
4. Push and create a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🐛 Known Issues & Limitations

- **Mock LLM**: Currently returns template responses. Integrate Anthropic/OpenAI for real synthesis.
- **Single-Node**: In-process queue doesn't scale. Use Celery for multi-node deployments.
- **Search Accuracy**: Cosine similarity is basic. HNSW index in ClickHouse recommended for 100K+ docs.
- **Cost Tracking**: Not implemented. Add cost logging when using paid LLM APIs.
- **PII Redaction**: Stub only. Implement with spacy or transformer-based NER.

## 💬 Support

For questions or issues:
1. Check existing GitHub issues
2. Create a new issue with reproduction steps
3. Include logs from `backend/logs/` and `frontend/console` output

---

**Last Updated**: 2024-02-06 | **Version**: 0.1.0-alpha
