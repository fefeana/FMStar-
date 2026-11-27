import os
import requests

AGENT_SERVER_URL = os.environ.get("AGENT_SERVER_URL", "http://localhost:8000").rstrip("/")
AGENT_API_KEY = os.environ.get("AGENT_API_KEY", "")
TARGET_DIR = os.environ.get("FMSTAR_TARGET", "/workspace/FMStar-")

AUDIT_PROMPT = """
أنت Claude Code وتعمل على تطوير مشروع FMStar AI Studio إلى نظام هجين متكامل.
المستودع: https://github.com/fefeana/FMStar-
الواجهة المنشورة: https://fefeana.github.io/FMStar-/

قواعد إلزامية:
1. لا تغيّر الهوية البصرية لـ FMStar أو تحذف أي ميزة أو صفحة أو زر أو مسار موجود.
2. لا تضع أو تطبع أي مفاتيح API أو أسرار في الكود أو السجلات أو الواجهة الأمامية أو ملفات الاختبار.
3. لا تدّعِ نجاح أي اختبار أو نشر أو اتصال دون دليل فعلي.

واقع المفاتيح والمزوّدات:
- المفاتيح الحقيقية الشغالة حالياً في البيئة هي مفتاح Gemini ومفتاح Samurai فقط (تحقق من أسماء المتغيرات في الكود والبيئة دون طباعة أي قيمة).
- أي مفاتيح أخرى ليست مفعّلة حالياً؛ أبقِ موصل OmniRoute وبقية الموصلات جاهزة وتُظهر حالتها بوضوح دون تعطيل النظام.

نفّذ المرحلة A فقط:
- افحص جميع ملفات ومجلدات المشروع (الواجهة، server_3000.py، app.py، render.yaml، Docker، إن وجدت).
- أنشئ تقرير "FMSTAR_AUDIT.md" باللغة العربية مع إبقاء أسماء الملفات والأوامر والمتغيرات بالإنجليزية.
- حدّد التعارضات (مثل تعدد نقاط التشغيل، مسار 127.0.0.1:8001، تخزين المهام في الذاكرة، وقيم CORS/REMOTE_MODEL_URL).
"""

headers = {"Content-Type": "application/json"}
if AGENT_API_KEY:
    headers["Authorization"] = f"Bearer {AGENT_API_KEY}"

resp = requests.post(
    f"{AGENT_SERVER_URL}/agent/task",
    json={"prompt": AUDIT_PROMPT, "target": TARGET_DIR},
    headers=headers,
    timeout=120,
)

print("Status:", resp.status_code)
print(resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text)
