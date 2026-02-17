#!/bin/bash
echo "Starting FastAPI Server..."
conda run -n oura-env uvicorn main:app --reload --port 8000
