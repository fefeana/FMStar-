services:
  - type: web
    name: claude-agent-server
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd backend && python FMStar_server.py
