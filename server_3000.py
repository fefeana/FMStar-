import os
import time
import uuid
import requests
import subprocess
import imageio_ffmpeg
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import Field, BaseModel
from typing import Optional

app = FastAPI(title="FMStar Studio AI | JM Studio Backend")

# السماح للواجهة بالاتصال بالسيرفر من أي رابط (مثل GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# إعدادات البيئة والربط التلقائي
# ==========================================
MINIMAX_BASE_URL = os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_GROUP_ID = os.environ.get("MINIMAX_GROUP_ID", "")
SECRET_KEY = os.environ.get("SECRET_KEY", "samurai_secret_2026")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://onrender.com")

TEMP_DIR = "/tmp/fmstar_media"
os.makedirs(TEMP_DIR, exist_ok=True)


# ==========================================
# مسارات الترحيب المباشر وفحص حالة السيرفر
# ==========================================
@app.get("/")
@app.get("/hello")
@app.get("/hi")
async def welcome_root():
    return JSONResponse(
        status_code=200,
        content={
            "status": "online",
            "welcome": "أهلين ومرحباً بكِ يا FMStar ✨ | Hello & Hi from JM Studio AI Server!",
            "studio": "استوديو جيمي وميرا (FMStar Studio AI)",
            "features": [
                "MiniMax Music & Voice Library (مكتبة الأصوات والأغاني)",
                "Hailuo Video Engine (توليد المشاهد والفيديو)",
                "FFmpeg Auto-Merge (دمج الصوت والصورة تلقائياً)"
            ]
        }
    )


# ==========================================
# نماذج البيانات والأمان
# ==========================================
class SmartStudioRequest(BaseModel):
    prompt: str = Field(..., description="وصف المستخدم الحر (أغنية، شعر، لحن، أو فيديو كليب)")
    style: str = Field(default="Arabic Pop, Emotional", description="النمط الموسيقي والآلات")
    dsp_profile: str = Field(default="hybrid", description="هندسة الصوت ومعالجته")
    image_base64: Optional[str] = Field(default=None, description="صورة اختيارية لتحريكها في الفيديو")
    voice_preset: Optional[str] = Field(default="Alhan", description="مكتبة الصوت أو الطابع الصوتي للأغاني")


def verify_api_key(x_fmstar_key: Optional[str] = Header(default=None)):
    if SECRET_KEY and x_fmstar_key and x_fmstar_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="مفتاح الحماية غير صحيح (Invalid X-FMStar-Key)")
    return True


def sanitize_prompt(text: str) -> str:
    return text.strip()


# ==========================================
# تحليل نية المستخدم وتوجيه الإنتاج
# ==========================================
def detect_user_intent(prompt: str, has_image: bool) -> str:
    text = prompt.lower()
    audio_keywords = ["أغنية", "اغنية", "شعر", "قصيدة", "لحن", "موسيقى", "موسيقي", "غناء", "صوت", "song", "music", "lyrics", "melody", "beat"]
    video_keywords = ["فيديو", "مشهد", "تصوير", "كاميرا", "لقطة", "تحريك", "كليب", "video", "scene", "cinematic", "camera", "clip"]

    wants_audio = any(word in text for word in audio_keywords)
    wants_video = any(word in text for word in video_keywords) or has_image

    if wants_audio and wants_video:
        return "full_studio"
    elif wants_video:
        return "video"
    elif wants_audio:
        return "audio"
    else:
        return "full_studio"


# ==========================================
# محرك الصوت والأغاني (MiniMax Music Library)
# ==========================================
def generate_minimax_audio(prompt: str, style: str, dsp: str, voice_preset: str, headers: dict) -> str:
    url = f"{MINIMAX_BASE_URL}/music_generation"
    if MINIMAX_GROUP_ID:
        url += f"?GroupId={MINIMAX_GROUP_ID}"

    payload = {
        "model": "music-01",
        "prompt": f"Style: {style}, DSP Profile: {dsp}, Voice Vibe: {voice_preset}",
        "lyrics": prompt,
        "audio_setting": {
            "sample_rate": 44100,
            "bitrate": 256000,
            "format": "mp3"
        }
    }

    res = requests.post(url, json=payload, headers=headers, timeout=120)
    res.raise_for_status()
    data = res.json()

    audio_url = data.get("data", {}).get("audio_file") or data.get("audio_file", "")
    if not audio_url:
        file_id = data.get("file_id") or data.get("data", {}).get("file_id")
        if file_id:
            file_res = requests.get(
                f"{MINIMAX_BASE_URL}/files/retrieve",
                headers=headers,
                params={"file_id": file_id},
                timeout=30
            ).json()
            audio_url = file_res.get("file", {}).get("download_url", "")

    if not audio_url:
        raise Exception(f"فشل توليد الصوت من مكتبة MiniMax: {data}")

    return audio_url


# ==========================================
# محرك الفيديو السينمائي (Hailuo Video)
# ==========================================
def generate_hailuo_video(prompt: str, image_b64: Optional[str], headers: dict) -> str:
    create_url = f"{MINIMAX_BASE_URL}/video_generation"
    payload = {
        "model": "MiniMax-Hailuo-02",
        "prompt": prompt,
        "prompt_optimizer": True
    }
    if image_b64:
        payload["first_frame_image"] = image_b64

    create_res = requests.post(create_url, json=payload, headers=headers, timeout=60)
    create_res.raise_for_status()
    task_id = create_res.json().get("task_id")
    if not task_id:
        raise Exception(f"فشل بدء مهمة الفيديو: {create_res.json()}")

    query_url = f"{MINIMAX_BASE_URL}/query/video_generation"
    file_id = None
    for _ in range(30):
        time.sleep(10)
        status_data = requests.get(query_url, headers=headers, params={"task_id": task_id}, timeout=30).json()
        status = status_data.get("status")
        if status == "Success":
            file_id = status_data.get("file_id")
            break
        elif status == "Fail":
            raise Exception(f"فشل توليد الفيديو: {status_data}")

    if not file_id:
        raise Exception("انتهت مهلة انتظار الفيديو.")

    file_url = f"{MINIMAX_BASE_URL}/files/retrieve"
    file_data = requests.get(file_url, headers=headers, params={"file_id": file_id}, timeout=30).json()
    video_url = file_data.get("file", {}).get("download_url")
    if not video_url:
        raise Exception("تعذر استخراج رابط الفيديو.")
    return video_url


# ==========================================
# دمج الصوت والفيديو عبر FFmpeg
# ==========================================
def merge_audio_and_video(video_url: str, audio_url: str) -> str:
    uid = uuid.uuid4().hex[:8]
    vid_path = os.path.join(TEMP_DIR, f"vid_{uid}.mp4")
    aud_path = os.path.join(TEMP_DIR, f"aud_{uid}.mp3")
    out_filename = f"JM_Studio_Clip_{uid}.mp4"
    out_path = os.path.join(TEMP_DIR, out_filename)

    with open(vid_path, "wb") as f:
        f.write(requests.get(video_url, timeout=60).content)
    with open(aud_path, "wb") as f:
        f.write(requests.get(audio_url, timeout=60).content)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y",
        "-stream_loop", "-1", "-i", vid_path,
        "-i", aud_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(vid_path)
    os.remove(aud_path)
    return out_filename


# ==========================================
# نقاط النهاية للإنتاج وتقديم الملفات
# ==========================================
@app.get("/media/{filename}")
async def serve_merged_media(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="الملف غير موجود")
    return FileResponse(file_path, media_type="video/mp4")


@app.post("/v1/studio/smart-generate", dependencies=[Depends(verify_api_key)])
async def smart_generate(req: SmartStudioRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="يرجى كتابة وصف للعمل المطلوب.")
    if not MINIMAX_API_KEY:
        raise HTTPException(status_code=500, detail="مفتاح MINIMAX_API_KEY غير مضاف في بيئة التشغيل.")

    safe_prompt = sanitize_prompt(req.prompt)
    headers = {"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"}
    intent = detect_user_intent(safe_prompt, bool(req.image_base64))

    try:
        if intent == "audio":
            audio_url = generate_minimax_audio(safe_prompt, req.style, req.dsp_profile, req.voice_preset, headers)
            return {
                "status": "success",
                "type": "audio",
                "model_used": "MiniMax Music Engine (صوت وأغاني)",
                "media_url": audio_url
            }

        elif intent == "video":
            video_url = generate_hailuo_video(safe_prompt, req.image_base64, headers)
            return {
                "status": "success",
                "type": "video",
                "model_used": "Hailuo Video Engine (فيديو فقط)",
                "media_url": video_url
            }

        else:
            audio_url = generate_minimax_audio(safe_prompt, req.style, req.dsp_profile, req.voice_preset, headers)
            video_url = generate_hailuo_video(safe_prompt, req.image_base64, headers)
            merged_filename = merge_audio_and_video(video_url, audio_url)
            base_url = RENDER_EXTERNAL_URL.rstrip("/")
            merged_url = f"{base_url}/media/{merged_filename}"
            return {
                "status": "success",
                "type": "video",
                "model_used": "JM Studio AI Full Clip (فيديو + أغنية مدمجة)",
                "media_url": merged_url
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ أثناء الإنتاج في الاستوديو: {str(e)}")


# ==========================================
# تشغيل الخادم المباشر
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
