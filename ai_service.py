from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
from fmstar_audio_architect import FMStarAudioArchitect

app = FastAPI(title="FMStar AI & Audio DSP Engine", version="2.5")
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

@app.post("/internal/audio/architect")
async def process_audio_architecture(req: ArchitectureRequest):
    if not req.lyrics.strip():
        raise HTTPException(status_code=400, detail="Lyrics cannot be empty")
    return architect.process_song_architecture(
        lyrics_raw=req.lyrics,
        genre=req.genre,
        bpm=req.bpm,
        vocal_tone=req.vocal_tone
    )

@app.post("/internal/generate")
async def generate_multimodal_content(req: GenerateRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    # 1. تطبيق البروفايل الصوتي (DSP)
    dsp_status = apply_dsp_audio_profile(req.dsp_profile)

    # 2. محاكاة التوليد عبر LTX-2.5 والـ GPU
    time.sleep(1.5)

    return {
        "status": "success",
        "dsp_applied": dsp_status,
        "aspect_ratio": req.ratio,
        "video_url": "/static/outputs/generated_ltx_latest.mp4"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
