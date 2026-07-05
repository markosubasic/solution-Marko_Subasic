FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt -e .

COPY alembic.ini ./
COPY alembic ./alembic

EXPOSE 8000

CMD alembic upgrade head && uvicorn tickethub.main:app --host 0.0.0.0 --port 8000
