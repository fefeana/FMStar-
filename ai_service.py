from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import random

app = FastAPI(title="FMStar OmniRoot Engine", version="7.0")

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
    raise HTTPException(status_code=403, detail="Invalid Key")

class GenerateRequest(BaseModel):
    prompt: str
    ratio: str = "16:9"
    dsp_profile: str = "hybrid"

@app.get("/")
async def root():
    return {"status": "online", "engine": "OmniRoot v7.0", "providers": 357}

# 🚀 هنا السحر بتاع OmniRoot
def omni_router_generate(prompt: str, style: str):
    # في الواقع، إحنا هنا بنربط APIs حقيقية. 
    # دلوقتي هنحاكي رد ذكي عشان نغير فيديو الأرنب
    
    providers = ["Gemini 2.5 Flash", "DeepSeek V3", "Groq Llama 3", "MiniMax Audio"]
    selected_provider = random.choice(providers[:3]) # بنختار مزود نصي عشوائي
    
    # محاكاة لتوليد كلمات الأغنية بالذكاء الاصطناعي
    generated_lyrics = f"🎵 [كلمات تم توليدها بواسطة {selected_provider}]\n\n"
    generated_lyrics += f"في عالمٍ من {style}، نبتدي الحكاية\n"
    generated_lyrics += f"عن {prompt}، وكل الحكاية\n"
    generated_lyrics += "ألحان بتعزف، وقلبي بينادي\n"
    generated_lyrics += "على أحلامي اللي جوايا، بتنادي\n\n"
    generated_lyrics += "✨ [النهاية]"
    
    return selected_provider, generated_lyrics

@app.post("/internal/generate", dependencies=[Depends(get_api_key)])
async def generate_content(req: GenerateRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is empty")

    # 1. استخدام OmniRoot لتوليد الكلام
    provider_used, lyrics = omni_router_generate(req.prompt, req.dsp_profile)

    # 2. إرجاع النتيجة (لاحظ إننا شلنا رابط الأرنب وحطينا الكلام)
    return {
        "status": "success",
        "routing": "OmniRoot Multi-Model Dynamic Engine",
        "selected_model": provider_used,
        "original_prompt": req.prompt,
        "lyrics": lyrics, # النص اللي اتولد
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" # رابط صوتي تجريبي (مش بيانو أطفال)
    }
