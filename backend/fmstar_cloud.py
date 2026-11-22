import os
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import server_config

app = FastAPI(
    title=server_config.APP_NAME,
    description="FMStar Backend Server",
    version=server_config.APP_VERSION
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=server_config.ALLOWED_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

@app.get("/")
async def root():
    return {
        "name": server_config.APP_NAME,
        "version": server_config.APP_VERSION,
        "status": "online",
        "environment": server_config.ENVIRONMENT,
        "agent": os.getenv("AGENT_NAME", "Claude"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get(server_config.HEALTH_ENDPOINT)
async def health():
    return {
        "status": "healthy",
        "service": "fmstar-backend"
    }

@app.get(f"{server_config.API_PREFIX}/providers")
async def providers():
    return {
        "providers": [
            {"name": "Claude", "status": "browser_session_ready"},
            {"name": "Gemini", "status": "configured" if server_config.GEMINI_API_KEY else "not_configured"},
            {"name": "OmniRoute", "status": "configured" if server_config.OMNIROUTE_API_KEY else "not_configured"}
        ]
    }

@app.get(f"{server_config.API_PREFIX}/models")
async def models():
    return {
        "models": ["claude-free-session"]
    }

@app.get(f"{server_config.API_PREFIX}/files")
async def list_files():
    files = [
        str(p.relative_to(PROJECT_ROOT))
        for p in PROJECT_ROOT.rglob("*")
        if p.is_file() and ".git" not in p.parts
    ]
    return {"files": files}

@app.get(f"{server_config.API_PREFIX}/files/read")
async def read_file(path: str):
    target = (PROJECT_ROOT / path).resolve()
    if not str(target).startswith(str(PROJECT_ROOT)) or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return {
        "path": path,
        "content": target.read_text(encoding="utf-8", errors="replace")
    }
