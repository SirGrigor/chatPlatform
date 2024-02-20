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

ENV PYTHONUNBUFFERED=1
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-dev --no-interaction --no-ansi
COPY . .
RUN chmod +x entrypoint.sh
EXPOSE 8000

# Specify the command to run the application
CMD ["/entrypoint.sh"]
