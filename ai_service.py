from fastapi import FastAPI, HTTPException, Security, Depends, Request, status, Header
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
import os
import uuid
import bleach  # مكتبة الحماية


# 🛡️ دالة الحماية مدمجة مباشرة لتعقيم المدخلات
def sanitize_prompt(user_input: str) -> str:
    clean = bleach.clean(user_input, tags=[], attributes={}, strip=True)
    return clean[:4000]


app = FastAPI(title="FMStar AI Engine v1.7", version="1.7.0")

# 🛡️ إعداد CORS (السماح لموقعك وبيئة التطوير فقط)
allowed_origins = ["https://fefeana.github.io", "http://localhost:3000"]
extra_origin = os.getenv("ALLOWED_ORIGIN", "").strip()
if extra_origin and extra_origin not in allowed_origins:
    allowed_origins.append(extra_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🛡️ Error Handling (RFC 7807 Problem Details)
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

OMNIROUTE_CLOUD_URL = os.getenv(
    "OMNIROUTE_CLOUD_URL",
    "https://cloud.omniroute.online/v1/chat/completions"
)


def get_api_key(api_key_header: str = Security(api_key_header)):
    secret_key = os.getenv("FMSTAR_SECRET_KEY")
    if not secret_key:
        raise HTTPException(
            status_code=500,
            detail="Missing environment key: FMSTAR_SECRET_KEY"
        )
    if api_key_header == secret_key:
        return api_key_header
    raise HTTPException(status_code=403, detail="Invalid API Key")


class AudioGenerationRequest(BaseModel):
    prompt: str = Field(..., description="وصف المشهد أو النص المطلوب")
    ratio: str = Field(default="16:9", description="أبعاد الفيديو")
    dsp_profile: str = Field(default="hybrid", description="ملف تأثير الصوت")


@app.get("/")
def health_check():
    return {
        "status": "online",
        "engine": "FMStar AI Engine",
        "version": "1.7.0"
    }


@app.post("/v1/audio/generations", dependencies=[Depends(get_api_key)])
def create_audio_generation(
    req: AudioGenerationRequest,
    request: Request,
    idempotency_key: str = Header(None, alias="Idempotency-Key")
):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    omniroute_api_key = os.getenv("OMNIROUTE_API_KEY")
    if not omniroute_api_key:
        raise HTTPException(
            status_code=500,
            detail="Missing environment key: OMNIROUTE_API_KEY"
        )

    safe_prompt = sanitize_prompt(req.prompt)

    headers = {
        "Authorization": f"Bearer {omniroute_api_key}",
        "Content-Type": "application/json"
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    payload = {
        "model": "auto",
        "messages": [
            {"role": "system", "content": "You are an expert AI prompt engineer."},
            {"role": "user", "content": safe_prompt}
        ]
    }

    try:
        # تقليل الـ Timeout لـ 25 ثانية لتفادي حد Render عند 30 ثانية
        response = requests.post(OMNIROUTE_CLOUD_URL, json=payload, headers=headers, timeout=25)
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
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="OmniRoute took too long to respond.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to OmniRoute: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
