import os
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FMStar AI Studio API",
    description="FMStar Backend Server",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

@app.get("/")
async def root():
    return {
        "name": "FMStar AI Studio",
        "status": "online",
        "agent": os.getenv("AGENT_NAME", "Claude"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "service": "fmstar-backend"
    }

@app.get("/api/v1/providers")
async def providers():
    return {
        "providers": [
            {"name": "Claude", "status": "browser_session_ready"},
            {"name": "Gemini", "status": "not_configured"},
            {"name": "OmniRoute", "status": "not_configured"}
        ]
    }

@app.get("/api/v1/models")
async def models():
    return {
        "models": ["claude-free-session"]
    }

@app.get("/api/v1/files")
async def list_files():
    files = [
        str(p.relative_to(PROJECT_ROOT))
        for p in PROJECT_ROOT.rglob("*")
        if p.is_file() and ".git" not in p.parts
    ]
    return {"files": files}

@app.get("/api/v1/files/read")
async def read_file(path: str):
    target = (PROJECT_ROOT / path).resolve()
    if not str(target).startswith(str(PROJECT_ROOT)) or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return {
        "path": path,
        "content": target.read_text(encoding="utf-8", errors="replace")
}
