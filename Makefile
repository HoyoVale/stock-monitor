.PHONY: dev test install build

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest tests/ -v

build:
	cd frontend && npm run build
