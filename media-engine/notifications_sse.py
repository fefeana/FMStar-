from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI(title="FMStar Studio - SSE Notifications")

class EventBus:
    def __init__(self):
        self.listeners = []

    async def connect(self):
        queue = asyncio.Queue()
        self.listeners.append(queue)
        return queue

    def disconnect(self, queue):
        if queue in self.listeners:
            self.listeners.remove(queue)

    async def notify_user(self, event_data: dict):
        for queue in self.listeners:
            await queue.put(event_data)

bus = EventBus()

@app.get("/api/v2/notifications/stream")
async def sse_notifications(user_id: str = "current_user"):
    queue = await bus.connect()
    
    async def event_generator():
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        except asyncio.CancelledError:
            bus.disconnect(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/v2/creations/complete")
async def creation_completed(title: str, creation_type: str):
    notification_payload = {
        "type": "CREATION_COMPLETE",
        "title": title,
        "category": creation_type,
        "message": f"تم الانتهاء من توليد '{title}' بنجاح!"
    }
    await bus.notify_user(notification_payload)
    return {"status": "sent"}
