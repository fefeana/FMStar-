from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

# 🛡️ استيراد درع الحماية
from secure_brain import sanitize_prompt

app = FastAPI(title="FMStar AI Engine with OmniRoute", version="8.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_NAME = "X-FMStar-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
SECRET_KEY = "samurai_secret_2026"

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == SECRET_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="مفتاح غير صالح")

class GenerateRequest(BaseModel):
    prompt: str
    ratio: str = "16:9"
    dsp_profile: str = "hybrid"

# 🌐 إعدادات OmniRoute
# ⚠️ استبدلي هذا الرابط برابط OmniRoute الخاص بكِ (سحابي أو محلي)
OMNIROUTE_URL = "https://cloud.omniroute.online/v1/chat/completions"
# ⚠️ ضعي هنا مفتاح البوابة الذي نسختيه من لوحة التحكم
OMNIROUTE_API_KEY = "sk-ضعي_مفتاح_البوابة_هنا"

@app.post("/internal/generate", dependencies=[Depends(get_api_key)])
async def generate_multimodal_content(req: GenerateRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="الرجاء كتابة وصف المشهد.")

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
        response = requests.post(OMNIROUTE_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        ai_data = response.json()
        optimized_prompt = ai_data['choices'][0]['message']['content']
        
        return {
            "status": "success",
            "model_used": ai_data.get('model', 'OmniRoute Auto'),
            "optimized_prompt": optimized_prompt,
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ: {str(e)}")
