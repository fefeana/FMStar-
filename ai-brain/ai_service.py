from fastapi import FastAPI, HTTPException, Security, Depends, Request, status, Header
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
import os
import uuid
import bleach # مكتبة الحماية

# 🛡️ استيراد درع الحماية مدمج هنا عشان نلغي مشكلة secure_brain
def sanitize_prompt(user_input: str) -> str:
    clean = bleach.clean(user_input, tags=[], attributes={}, strip=True)
    return clean[:4000]

app = FastAPI(title="FMStar AI Engine v1.5", version="1.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🛡️ Error Handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": exc.detail,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": request.url.path
        },
        media_type="application/problem+json"
    )

API_KEY_NAME = "X-FMStar-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
SECRET_KEY = "samurai_secret_2026"

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == SECRET_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Invalid API Key")

class AudioGenerationRequest(BaseModel):
    prompt: str = Field(..., description="وصف المشهد أو النص المطلوب")
    ratio: str = Field(default="16:9", description="أبعاد الفيديو")
    dsp_profile: str = Field(default="hybrid", description="ملف تأثير الصوت")

OMNIROUTE_CLOUD_URL = "https://cloud.omniroute.online/v1/chat/completions"
OMNIROUTE_API_KEY = "sk-omniroute-free-key"

@app.post("/v1/audio/generations", dependencies=[Depends(get_api_key)])
async def create_audio_generation(
    req: AudioGenerationRequest, 
    request: Request,
    idempotency_key: str = Header(None, alias="Idempotency-Key") 
):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    
    safe_prompt = sanitize_prompt(req.prompt)

    headers = {
        "Authorization": f"Bearer {OMNIROUTE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "auto", 
        "messages": [
            {"role": "system", "content": "You are an expert AI prompt engineer."},
            {"role": "user", "content": safe_prompt}
        ]
    }

    try:
        response = requests.post(OMNIROUTE_CLOUD_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        ai_data = response.json()
        optimized_prompt = ai_data['choices'][0]['message']['content']
        
        return {
            "status": "success",
            "id": str(uuid.uuid4()),
            "model_used": ai_data.get('model', 'OmniRoute Auto'),
            "optimized_prompt": optimized_prompt,
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to connect to OmniRoute: {str(e)}"
        )
