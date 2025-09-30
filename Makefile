# Makefile for TTS Service

.PHONY: help install dev test lint format build run clean docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run in development mode"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  build       - Build for production"
	@echo "  run         - Run production server"
	@echo "  clean       - Clean temporary files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run  - Run with Docker Compose"

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Development server
dev:
	python main.py --reload --debug

# Run tests
test:
	pytest -v --cov=src --cov-report=html --cov-report=term

# Lint code
lint:
	python -m flake8 src/ tests/ main.py
	python -m mypy src/ main.py --ignore-missing-imports

# Format code
format:
	python -m black src/ tests/ main.py
	python -m isort src/ tests/ main.py

# Production build
build:
	pip install --upgrade pip
	pip install -r requirements.txt --no-dev

# Run production server
run:
	python main.py

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/

# Docker build
docker-build:
	docker build -t tts-service .

# Docker run with compose
docker-run:
	docker-compose up --build

# Docker run in production mode
docker-prod:
	docker-compose --profile production up --build -d