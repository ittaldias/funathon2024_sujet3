# Use an official Python runtime as a parent image, allowing version to be parameterized
ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

# Set the working directory in the container
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file, to cache the pip install step separately
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY even_better_app/ .

# Inform Docker that the container listens on the specified port at runtime.
EXPOSE 5000

# Define a healthcheck for checking the availability of the service
HEALTHCHECK CMD curl --fail http://localhost:5000/health || exit 1

# Define the command to run the app using Python
ENTRYPOINT ["python", "main.py"]
