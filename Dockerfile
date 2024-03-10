FROM python:3.9-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="${PATH}:/root/.local/bin"
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install --no-dev --no-interaction --no-ansi

RUN pip install torch sentence-transformers

COPY . .
RUN chmod +x entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]