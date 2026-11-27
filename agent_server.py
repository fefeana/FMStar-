import os
import subprocess
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="FMStar Cloud Agent Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fefeana.github.io",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


class AgentTaskRequest(BaseModel):
    prompt: str
    target: str | None = None


@app.get("/")
def root():
    return {
        "status": "live",
        "service": "claude-agent-server",
        "project": "FMStar-",
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "anthropic_base_url_configured": bool(os.getenv("ANTHROPIC_BASE_URL")),
        "anthropic_api_key_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
    }


@app.post("/agent/task")
def agent_task(req: AgentTaskRequest):
    workdir = Path(req.target or os.getenv("FMSTAR_TARGET", "/workspace/FMStar-")).resolve()
    if not workdir.exists():
        raise HTTPException(status_code=400, detail=f"Target directory not found: {workdir}")

    try:
        result = subprocess.run(
            ["claude", "-p", req.prompt],
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=300,
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "output": result.stdout[-4000:],
            "error": result.stderr[-2000:] if result.returncode != 0 else "",
        }
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Claude CLI is not installed in this container.")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Claude task timed out.")
