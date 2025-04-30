FROM python:3.13-slim
RUN apt-get update && \
	apt-get install -y --no-install-recommends git gcc libpq-dev curl && \
	rm -rf /var/lib/apt/lists/*
ENV PYTHONPATH=/app/src
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY src src
