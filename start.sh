#!/usr/bin/env bash
# Script to launch MCP Bridge in SSE mode (in background) and Open WebUI via docker compose.
set -euo pipefail

cd "$(dirname "$0")"

# Load .env file if it exists
if [ -f .env ]; then
  echo "Loading environment variables from .env"
  set -a
  source .env
  set +a
fi


echo "Starting Clab AI Orchestrator via docker compose..."
if docker compose version >/dev/null 2>&1; then
  docker compose up -d --build
elif command -v docker-compose >/dev/null 2>&1; then
  docker-compose up -d --build
else
  echo "Error: Neither 'docker compose' nor 'docker-compose' found. Please install the docker-compose-v2 package."
  exit 1
fi

echo ""
echo "=========================================================="
echo "✅ Clab AI Orchestrator Started!"
echo "=========================================================="
echo "🔗 Open WebUI: http://nkchan-desktop-1.taila9034f.ts.net:8080"
echo ""
echo "👉 Follow these steps to connect the MCP server in Open WebUI:"
echo "1. Go to Settings (Profile icon) -> Admin Settings -> Connections"
echo "2. Scroll down to MCP Servers, click '+' to add a new server"
echo "3. Transport type: SSE"
echo "4. URL: http://clab-mcp-bridge:9005/sse"
echo "5. Click Connect to register the tools."
echo "=========================================================="
