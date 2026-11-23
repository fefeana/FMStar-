import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="FMStar Cloud Agent Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    return {
        "received": True,
        "prompt": req.prompt,
        "target": req.target,
    }
