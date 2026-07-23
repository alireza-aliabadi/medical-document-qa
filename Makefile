.PHONY: install dev lint format typecheck test security docker-up docker-down migrate

install:
	poetry install --with dev

dev:
	poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

lint:
	poetry run ruff check backend training
	poetry run ruff format --check backend training

format:
	poetry run ruff check --fix backend training
	poetry run ruff format backend training

typecheck:
	poetry run mypy -p backend

test:
	poetry run pytest backend/tests --cov=backend --cov-report=xml -q

security:
	poetry run bandit -r backend -x backend/tests -ll
	poetry run pip-audit || true

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

migrate:
	poetry run alembic upgrade head

quality: lint typecheck test security
