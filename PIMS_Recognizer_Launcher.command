#!/usr/bin/env bash
# PIMS_AlgoHCP Standalone Launcher & PWA Host
# Automatically launches the python server and opens the PWA Web App in browser.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "   🩺 Starting PIMS_AlgoHCP Recognizer Engine v2.0 PWA"
echo "=========================================================="

IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo "127.0.0.1")

echo "Server listening on:"
echo "  • Local:   http://localhost:8080"
echo "  • Network: http://${IP}:8080"
echo "=========================================================="

python3 server.py &
SERVER_PID=$!

sleep 1
open "http://localhost:8080" 2>/dev/null || xdg-open "http://localhost:8080" 2>/dev/null

echo "Press Ctrl+C to stop the server..."
wait $SERVER_PID
