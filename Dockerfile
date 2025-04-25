FROM python:3.13-slim
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY src src
