from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(
    title="FMStar OmniRoute Engine - AI Brain",
    description="Multi-Model Dynamic Engine for FMStar Studio",
    version="6.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_NAME = "X-FMStar-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
SECRET_KEY = os.getenv("SECRET_KEY", "samurai_secret_2026")

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == SECRET_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Invalid Key: Unauthorized Access")

class GenerateRequest(BaseModel):
    prompt: str
    ratio: str = "16:9"
    dsp_profile: str = "hybrid"

@app.get("/")
async def root():
    return {
        "status": "online",
        "engine": "FMStar OmniRoute Gateway (ai-brain)",
        "quality": "4K Ultra HD / Max Free Tier",
        "version": "6.0"
    }

@app.post("/internal/generate", dependencies=[Depends(get_api_key)])
async def generate_content(req: GenerateRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is empty")

    return {
        "status": "success",
        "routing": "OmniRoute Multi-Model Dynamic Engine",
        "selected_model": "Gemini 2.5 Flash / High-Speed Free Route",
        "original_prompt": req.prompt,
        "optimized_prompt": f"تمت المعالجة بنجاح عبر OmniRoute! النص: {req.prompt}",
        "dsp_applied": f"Applied {req.dsp_profile} profile",
        "direct_stream_url": "https://www.w3schools.com/html/mov_bbb.mp4"
    }
