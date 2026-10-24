from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import time

app = FastAPI(title="FMStar AI Engine with OmniRoute Cloud", version="4.0")

# 🛡️ إعدادات الأمان (CORS) للسماح للواجهة بالاتصال
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🛡️ مفتاح الحماية للساموراي
API_KEY_NAME = "X-FMStar-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
SECRET_KEY = os.getenv("FMSTAR_SECRET_KEY", "samurai_secret_2026")

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == SECRET_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="مفتاح غير صالح، أنت لست ساموراي!")

class GenerateRequest(BaseModel):
    prompt: str
    ratio: str = "16:9"
    dsp_profile: str = "hybrid"

# 🌐 إعدادات OmniRoute السحابية (بدون مفاتيح)
OMNIROUTE_CLOUD_URL = "http://cloud.omniroute.online/v1/chat/completions"

@app.post("/internal/generate", dependencies=[Depends(get_api_key)])
async def generate_multimodal_content(req: GenerateRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="الرجاء كتابة وصف المشهد.")

    payload = {
        "model": "auto", # OmniRoute سيختار أفضل نموذج مجاني تلقائياً
        "messages": [
            {"role": "system", "content": "You are an expert AI prompt engineer for audio and video generation. Enhance this prompt to make it cinematic and detailed."},
            {"role": "user", "content": req.prompt}
        ]
    }

    try:
        # 🚀 الاتصال بالسحابة
        response = requests.post(OMNIROUTE_CLOUD_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        ai_data = response.json()
        optimized_prompt = ai_data['choices'][0]['message']['content']
        model_used = ai_data.get('model', 'OmniRoute Auto-Selected Model')

        # محاكاة إرجاع الفيديو (لأننا لم نربط محرك التوليد الفعلي بعد)
        return {
            "status": "success",
            "model_used": model_used,
            "original_prompt": req.prompt,
            "optimized_prompt": optimized_prompt,
            "dsp_applied": f"Applied {req.dsp_profile} DSP profile",
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4" # رابط تجريبي للمعاينة
        }

    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail="فشل الاتصال بالسحابة. تأكد من اتصالك بالإنترنت.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في OmniRoute: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # تشغيل المحرك على المنفذ 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
