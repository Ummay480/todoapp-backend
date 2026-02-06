#!/bin/bash

# Start the FastAPI application with uvicorn
echo "Starting Todo API server..."

# Check if .env file exists and source it
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Run the application
exec uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-7860} --workers ${WORKERS:-1}