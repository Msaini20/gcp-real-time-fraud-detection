#!/usr/bin/env bash
set -e
echo "🔄 Starting Streamlit server on port 8080..."
pkill -f streamlit || true
sleep 1
nohup streamlit run app.py \
  --server.port=8080 \
  --server.address=0.0.0.0 \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --server.headless=true > streamlit_run.log 2>&1 &
echo "🚀 Operations Command Center is LIVE on Port 8080!"
