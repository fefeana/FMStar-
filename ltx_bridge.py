import asyncio
import json
import logging
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ltx_bridge")

app = FastAPI(
    title="FMStar Studio - LTX Microservice Bridge",
    description="High-performance async SSE bridge for real-time video/audio generation streams",
    version="2.5.0"
)

# دعم CORS للاتصال السلس مع الواجهات وسيرفر Go
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def ltx_stream_generator(prompt: str, request: Request) -> AsyncGenerator[str, None]:
    """
    مولد البث اللحظي السريع لعمليات LTX Engine.
    يقوم ببث أحداث SSE فور توليدها دون تخزين مؤقت.
    """
    try:
        # إرسال حدث البدء
        initial_payload = json.dumps({"status": "starting", "progress": 0, "message": "Initiating LTX-2.5 core sequence..."})
        yield f"event: progress\ndata: {initial_payload}\n\n"
        await asyncio.sleep(0.1)

        # محاكاة خطوة المعالجة والمكالمة للمحرك
        for progress in range(10, 101, 15):
            # التحقق مما إذا كان العميل قد قطع الاتصال
            if await request.is_disconnected():
                logger.warning("Client disconnected from stream. Aborting LTX pipeline generation.")
                break

            payload = json.dumps({
                "status": "processing",
                "progress": progress,
                "frame_rendered": int(progress * 1.2),
                "audio_synced": True if progress > 40 else False
            })
            
            # صيغة SSE القياسية: event + data + \n\n
            yield f"event: progress\ndata: {payload}\n\n"
            await asyncio.sleep(0.2) # تجديد البث بسرعة ودون إعاقة Event Loop

        # حدث الإكمال النهائي
        completed_payload = json.dumps({
            "status": "completed",
            "progress": 100,
            "stream_url": "/media/outputs/generated_track.mp4",
            "message": "Stream synthesis successful."
        })
        yield f"event: complete\ndata: {completed_payload}\n\n"

    except asyncio.CancelledError:
        logger.info("Stream processing request was cancelled.")
    except Exception as e:
        logger.error(f"Error during LTX stream generation: {str(e)}")
        error_payload = json.dumps({"status": "error", "message": str(e)})
        yield f"event: error\ndata: {error_payload}\n\n"

@app.get("/api/v1/generate-stream")
async def generate_stream(request: Request, prompt: str = "FMStar Track Generation"):
    """
    Endpoint البث اللحظي مع ضبط الرؤوس (Headers) لضمان عدم التخزين المؤقت بأي طبقة بروكسي (Nginx / Cloudflare).
    """
    # الرؤوس الحاسمة لضمان البث اللحظي المباشر منعاً للتخزين المؤقت
    custom_headers = {
        "Cache-Control": "no-cache, no-transform, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "Content-Type": "text/event-stream",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",          # إيقاف التخزين المؤقت في Nginx فوراً
        "X-Content-Type-Options": "nosniff" # منع المتصفح من محاولة تخمين النمط
    }

    return StreamingResponse(
        ltx_stream_generator(prompt, request),
        media_type="text/event-stream",
        headers=custom_headers
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ltx_bridge", "engine": "LTX-2.5"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
