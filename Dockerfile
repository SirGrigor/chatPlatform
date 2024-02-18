# Start with a Python 3.9 slim image as the base
FROM python:3.9-slim as base

# Set working directory in the container
WORKDIR /app

# Install system dependencies required for the runtime and any additional packages
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    curl && \
    rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Install Poetry in a single layer and configure it to not create a virtual environment
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s $HOME/.local/bin/poetry /usr/local/bin/poetry && \
    poetry config virtualenvs.create false

# Set environment variable to ensure Python output is directed straight to terminal without being first buffered
ENV PYTHONUNBUFFERED=1

# Copy only the files necessary for installing Python dependencies
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies without dev dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Set the entrypoint script with proper permissions
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Specify the command to run the application
CMD ["/entrypoint.sh"]
