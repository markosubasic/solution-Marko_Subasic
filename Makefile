.PHONY: install migrate run lint test docs docker-build docker-up

install:
	pip install -r requirements.txt -e .

migrate:
	alembic upgrade head

run:
	uvicorn tickethub.main:app --reload

lint:
	ruff check src tests alembic

test:
	pytest -v

docs:
	python scripts/export_openapi.py

docker-build:
	docker build -t tickethub .

docker-up:
	docker compose up --build
