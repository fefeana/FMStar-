services:
  - type: web
    name: claude-agent-server
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.fmstar_cloud:app --host 0.0.0.0 --port $PORT
