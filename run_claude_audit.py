import os
import requests

AGENT_SERVER_URL = os.environ.get("AGENT_SERVER_URL", "http://localhost:8000").rstrip("/")
AGENT_API_KEY = os.environ.get("AGENT_API_KEY", "")
TARGET_DIR = os.environ.get("FMSTAR_TARGET", "/workspace/FMStar-")

TASK_PROMPT = """
أنت Claude Code وتعمل على تطوير مشروع FMStar AI Studio في المستودع https://github.com/fefeana/FMStar-
اقرأ أولاً ملف FMSTAR_AUDIT.md الموجود في جذر المستودع، والتزم بجميع نتائجه.

قواعد إلزامية لا تهاون فيها:
1. لا تغيّر الهوية البصرية لـ index.html أو تحذف أي ميزة أو صفحة أو زر.
2. لا تضع أي مفاتيح حقيقية أو أسرار افتراضية في الكود أو المستودع أو الاختبارات.
3. المفاتيح الحقيقية الشغالة حالياً في بيئة الخادم هي مفتاح Gemini (GEMINI_API_KEY) ومفتاح Samurai فقط عبر متغيرات البيئة؛ بينما تبقى طبقة OmniRoute قابلة للتفعيل عند ضبط OMNIROUTE_BASE_URL و OMNIROUTE_API_KEY دون إسقاط النظام.

نفّذ الآن المرحلتين B و C فقط بالترتيب:

[المرحلة B — المخطط المعماري]
- أنشئ ملف FMSTAR_ARCHITECTURE.md باللغة العربية يوثق المعمارية الهجينة الموحدة (/api/v1/ + التوافق مع /api/generate لـ index.html)، وفصل موصلات OmniRoute و Gemini و Media Adapters، ونظام المهام والتخزين الآمن، وخطة التعديلات خطوة بخطوة.

[المرحلة C — إصلاح الأسرار وتوحيد التشغيل]
1. أزل تماماً الأسرار الافتراضية المكشوفة ("samurai_secret_2026" و "sk-omniroute-free-key" و "change-me") من جميع ملفات HTML و Python واجعلها تُقرأ حصراً من متغيرات البيئة (بدون قيم افتراضية سرية).
2. حدّث .gitignore ليشمل .env و debug.keystore وأي ملفات مؤقتة، وحدّث .env.example بقيم وهمية آمنة فقط.
3. وحّد نقطة الدخول بين Dockerfile و Procfile و render.yaml لتعمل جميعها على خادم واحد مستقر يقرأ PORT، وأزل الـ Cron من render.yaml لمطابقة الخطة المجانية دون بطاقة.
4. أصلح أخطاء التشغيل الفورية (نقص import os في media-engine/main.py و backend/gemini_mira_backend.py، والكتابة في /public داخل backend/song_engine.py، وثغرة Path Traversal في main.go).
5. قّيد إعدادات CORS بالنطاقات المطلوبة (https://fefeana.github.io و localhost) وأصلح نشر GitHub Pages حتى لا ينشر ملفات الخادم أو debug.keystore علناً.
6. أنشئ ملفي SECURITY_AUDIT.md (مع التنبيه الصريح بضرورة تدوير الأسرار التي ظهرت في تاريخ Git) و ENVIRONMENT_VARIABLES.md بجدول كامل لجميع متغيرات البيئة.

بعد الانتهاء، قدّم تقريراً بالملفات التي أُنشئت أو عُدّلت، ونتيجة التحقق من عدم وجود أي سر مكشوف في الملفات.
"""

headers = {"Content-Type": "application/json"}
if AGENT_API_KEY:
    headers["Authorization"] = f"Bearer {AGENT_API_KEY}"

resp = requests.post(
    f"{AGENT_SERVER_URL}/agent/task",
    json={"prompt": TASK_PROMPT, "target": TARGET_DIR},
    headers=headers,
    timeout=300,
)

print("Status:", resp.status_code)
print(resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text)
