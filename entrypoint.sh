#!/bin/bash
# called by Dockerfile, runs DB init and starts api server
set -e

echo "⏳ Waiting for database..."
sleep 2

echo "🔧 Running database initialization..."
python -m app.db.init

echo "🚀 Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
