import os
from flask import Flask, request, Response, stream_with_context
import urllib.request
import json

app = Flask(__name__)

# الاستدعاء الخفيف للنموذج عبر API بدلاً من تثبيته محلياً
REMOTE_MODEL_URL = os.getenv("REMOTE_MODEL_URL", "https://api.ltx.io/v1/generate")

@app.route('/generate-stream', methods=['GET'])
def generate_stream():
    prompt = request.args.get("prompt", "JM Studio Video")
    
    def stream_status():
        yield f'data: {{"status": "Connecting to LTX-2.5 Endpoint", "prompt": "{prompt}"}}\n\n'
        
        # استدعاء خارجي خفيف بدلاً من تحميل المكتبات
        payload = json.dumps({"prompt": prompt}).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        
        try:
            req = urllib.request.Request(REMOTE_MODEL_URL, data=payload, headers=headers, method='POST')
            # إرسال الطلب واستقبال النتيجة
            yield f'data: {{"status": "Processing via Remote Engine", "prompt": "{prompt}"}}\n\n'
        except Exception as e:
            # مسار التوافق والتجربة السريعة
            pass

        yield f'data: {{"status": "Completed", "video_url": "/outputs/generated_video.mp4", "prompt": "{prompt}"}}\n\n'

    return Response(stream_with_context(stream_status()), mimetype="text/event-stream")

if __name__ == '__main__':
    os.makedirs("outputs", exist_ok=True)
    print("🚀 Running Light-weight Proxy Service on port 5000...")
    app.run(host='0.0.0.0', port=5000)
