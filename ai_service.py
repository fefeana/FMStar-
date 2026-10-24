from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import os
# ملاحظة: سنقوم بتثبيت مكتبة requests لاحقاً عند الربط الفعلي
from fmstar_audio_architect import FMStarAudioArchitect

app = FastAPI(title="FMStar AI & Audio DSP Engine", version="2.5")

# 🛡️ 1. إعدادات CORS (للسماح لواجهة الموقع بالتواصل مع المحرك)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # يمكنك تغييرها لرابط موقعك لاحقاً لمزيد من الأمان
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🛡️ 2. مفتاح الأمان (لحماية المحرك من الاختراق)
API_KEY_NAME = "X-FMStar-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
SECRET_KEY = os.getenv("FMSTAR_SECRET_KEY", "samurai_secret_2026")

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == SECRET_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="مفتاح غير صالح، الوصول مرفوض!")

architect = FMStarAudioArchitect()

class GenerateRequest(BaseModel):
    prompt: str
    ratio: str = "16:9"
    dsp_profile: str = "hybrid"

class ArchitectureRequest(BaseModel):
    lyrics: str
    genre: str = "Euro-Disco / 80s Synth-Pop"
    bpm: int = 120
    vocal_tone: str = "Romantic & Energetic"

def apply_dsp_audio_profile(profile_type: str) -> str:
    profiles = {
        "brass": "Brass Studio DSP: Enhancing Brass Resonances & Low-mids",
        "digital": "Digital Studio DSP: Crisp Highs & Dynamic Compression",
        "hybrid": "Hybrid Studio DSP: Balanced Warmth & Spatial Reverb"
    }
    return profiles.get(profile_type, profiles["hybrid"])

@app.post("/internal/audio/architect", dependencies=[Depends(get_api_key)])
async def process_audio_architecture(req: ArchitectureRequest):
    if not req.lyrics.strip():
        raise HTTPException(status_code=400, detail="Lyrics cannot be empty")
    return architect.process_song_architecture(
        lyrics_raw=req.lyrics,
        genre=req.genre,
        bpm=req.bpm,
        vocal_tone=req.vocal_tone
    )

@app.post("/internal/generate", dependencies=[Depends(get_api_key)])
async def generate_multimodal_content(req: GenerateRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    dsp_status = apply_dsp_audio_profile(req.dsp_profile)

    # 🥷 تجهيز المحرك للربط (سيتم تفعيله عند وضع المفتاح في .env)
    try:
        MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
        
        if not MINIMAX_API_KEY:
             time.sleep(1) # محاكاة الوقت
             video_url = "/static/outputs/generated_ltx_latest.mp4"
        else:
             # هنا سنضع كود الاتصال الحقيقي لاحقاً
             video_url = "https://api.minimax.io/generated_real_video.mp4"

        return {
            "status": "success",
            "dsp_applied": dsp_status,
            "aspect_ratio": req.ratio,
            "video_url": video_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في التوليد: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
