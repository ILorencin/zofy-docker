# Makefile

VENV_NAME = venv
PYTHON = python3
REQ_FILE = requirements.txt
APP_FILE = app.py
STREAMLIT_FILE = frontend.py

.DEFAULT_GOAL := run_backend

.PHONY: install run_backend run_frontend run clean \
        build-backend build-frontend build \
        start-backend start-frontend start \
        stop-backend stop-frontend stop \
        docker-up docker-down

# -------------------------------
# 1) LOCAL DEV (venv) COMMANDS
# -------------------------------
install:
	@if [ ! -d "$(VENV_NAME)" ]; then \
	  $(PYTHON) -m venv $(VENV_NAME); \
	fi
	. $(VENV_NAME)/bin/activate && pip install --upgrade pip
	. $(VENV_NAME)/bin/activate && pip install -r $(REQ_FILE)

run_backend: install
	@echo "Starting FastAPI backend on http://127.0.0.1:8000"
	. $(VENV_NAME)/bin/activate && uvicorn app:app --reload

run_frontend: install
	@echo "Starting Streamlit frontend on http://127.0.0.1:8501"
	. $(VENV_NAME)/bin/activate && streamlit run $(STREAMLIT_FILE)

run: install
	@echo "Running both backend and frontend in parallel (local venv)..."
	. $(VENV_NAME)/bin/activate && uvicorn app:app --reload & \
	. $(VENV_NAME)/bin/activate && streamlit run $(STREAMLIT_FILE)

clean:
	rm -rf $(VENV_NAME)

# --------------------------------------
# 2) DOCKER COMPOSE COMMANDS
# --------------------------------------
docker-up:
	@echo "Starting Docker Compose services..."
	docker compose up --build

docker-down:
	@echo "Stopping Docker Compose services..."
	docker compose down

# --------------------------------------
# 3) INDIVIDUAL DOCKER BUILDS & RUNS
# --------------------------------------

## 3A) Build individual Docker images
build-backend:
	@echo "Building Docker image for BACKEND..."
	# e.g. building from backend/Dockerfile
	docker build -t my-backend:latest -f backend/Dockerfile backend

build-frontend:
	@echo "Building Docker image for FRONTEND..."
	# e.g. building from frontend/Dockerfile
	docker build -t my-frontend:latest -f frontend/Dockerfile frontend

build:
	@echo "Building BOTH Docker images (backend & frontend)..."
	$(MAKE) build-backend
	$(MAKE) build-frontend

## 3B) Run containers individually (without docker-compose)
start-backend:
	@echo "Running BACKEND container on port 8000..."
	# Remove any old container named my_backend first
	docker rm -f my_backend || true
	docker run -d --name my_backend -p 8000:8000 my-backend:latest

start-frontend:
	@echo "Running FRONTEND container on port 8501..."
	# Remove any old container named my_frontend first
	docker rm -f my_frontend || true
	docker run -d --name my_frontend -p 8501:8501 my-frontend:latest

start:
	@echo "Starting BOTH containers (backend & frontend) individually..."
	$(MAKE) start-backend
	$(MAKE) start-frontend

## 3C) Stop individual containers
stop-backend:
	@echo "Stopping BACKEND container..."
	docker rm -f my_backend || true

stop-frontend:
	@echo "Stopping FRONTEND container..."
	docker rm -f my_frontend || true

stop:
	@echo "Stopping BOTH containers..."
	$(MAKE) stop-backend
	$(MAKE) stop-frontend
