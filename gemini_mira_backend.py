# gemini_mira_backend.py - FastAPI Service for Gemini & Mira Studio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from poetry_engine import generate_poetry_recitation 
from song_engine import generate_song_music
from voice_profiles import DIALECT_CONFIGS

app = FastAPI(title="Gemini & Mira Studio Audio Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    mode: str       # 'song' أو 'poetry'
    text: str       # نص الكلمات
    dialect: str = "fus_ha_modern"    # لهجة الشعر المختارة
    gender: str = "male"     # نوع الصوت

@app.get("/api/dialects")
async def get_dialects():
    return {"status": "success", "dialects": DIALECT_CONFIGS}

@app.post("/api/generate")
async def handle_generation(req: GenerateRequest):
    if req.mode == "song":
        # توجيه الطلب إلى محرك الألحان والموسيقى (Suno / Music API)
        audio_file = generate_song_music(text=req.text)
        return {"status": "success", "mode": "song", "audio_url": f"https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", "file": audio_file}

    elif req.mode == "poetry":
        # توجيه الطلب إلى محرك الإلقاء الشعري وتحديد اللهجة
        audio_file = generate_poetry_recitation(
            text=req.text, 
            dialect=req.dialect, 
            gender=req.gender
        )
        return {"status": "success", "mode": "poetry", "dialect": req.dialect, "gender": req.gender, "audio_url": f"https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", "file": audio_file}

    else:
        raise HTTPException(status_code=400, detail="نوع الخيار غير معروف")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
