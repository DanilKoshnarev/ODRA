.PHONY: help install dev test lint build clean docker-up docker-down generate-data

help:
	@echo "ODRA - Outcome-Driven RAG Auditor"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make dev            - Run in development mode"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Lint code"
	@echo "  make build          - Build Docker images"
	@echo "  make docker-up      - Start Docker Compose"
	@echo "  make docker-down    - Stop Docker Compose"
	@echo "  make generate-data  - Generate sample data (1000 docs)"
	@echo "  make clean          - Clean up generated files"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting backend and frontend..."
	cd backend && python -m uvicorn app.main:app --reload &
	cd frontend && npm run dev

test:
	cd backend && pytest tests/ -v

lint:
	cd backend && black app/ tests/ && ruff check app/ tests/
	cd frontend && npm run lint || true

build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

generate-data:
	cd backend && python ../scripts/generate_sample_data.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/odra.db
	rm -rf frontend/dist
	rm -rf frontend/node_modules
