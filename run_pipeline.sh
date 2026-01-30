#!/bin/bash

echo "🚀 Starting Olist Data Pipeline..."

# 1. Pull latest changes (optional, if using git)
# git pull origin main

# 2. Build the Docker image (to catch any code changes)
docker build -t olist-pipeline .

# 3. Run the pipeline
docker run --network="host" --env-file .env -v $(pwd):/app olist-pipeline

echo "✅ Pipeline execution finished!"
