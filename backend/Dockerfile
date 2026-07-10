FROM python:3.12-slim AS build

ENV POETRY_VERSION=1.8.3
ENV POETRY_NO_INTERACTION=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

COPY pyproject.toml ./
COPY src ./src
COPY tests ./tests

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN useradd --create-home --shell /bin/bash appuser

COPY --from=build /usr/local /usr/local
COPY --from=build /app /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]