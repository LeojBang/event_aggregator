FROM python:3.11-slim

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN uv sync --frozen --no-dev

EXPOSE 8000

COPY alembic.ini ./
COPY alembic ./alembic

CMD ["sh", "-c", "alembic upgrade head && uvicorn event_aggregator.main:app --host 0.0.0.0 --port 8000"]
