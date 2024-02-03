# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install netcat and other necessary system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.in
RUN pip install --no-cache-dir -r requirements.in

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Copy and set the entrypoint script
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Run the application
CMD ["./entrypoint.sh"]
