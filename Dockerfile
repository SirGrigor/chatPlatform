# Use Python 3.9 slim image as the base image
FROM python:3.9-slim as base

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry in a single layer and configure it to not create a virtual environment
ENV PATH="${PATH}:/root/.local/bin"
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

# Avoid Python output buffering
ENV PYTHONUNBUFFERED=1

# Copy the pyproject.toml and poetry.lock files first to leverage Docker caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies without dev dependencies, leveraging Docker's cache mechanism
# This step will only rerun if the pyproject.toml or poetry.lock files change
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy the Alembic configuration and migration scripts before the rest of the application
# This allows Docker to cache the layer if there are no changes to these files
COPY alembic.ini ./alembic.ini
COPY alembic/ ./alembic/

# Optionally, if you use a build argument to control when to install/update Alembic
ARG INSTALL_ALEMBIC=false
RUN if [ "$INSTALL_ALEMBIC" = "true" ]; then \
    poetry run alembic upgrade head; \
    fi

# Copy the rest of the application code
COPY . .

# Set proper permissions for the entrypoint script and ensure it's executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the application port
EXPOSE 8000

# Specify the command to run the application
CMD ["/entrypoint.sh"]
