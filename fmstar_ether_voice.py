import os
import json
from typing import Dict, Any, List

try:
    from google import genai
    from google.genai import types
    client = genai.Client()
    HAS_GENAI = True
except Exception:
    client = None
    types = None
    HAS_GENAI = False

MODEL_ID = "gemini-2.5-flash"

# ---------------------------------------------------------
# 02. claude-mem / Memory System (نظام الذاكرة الممتدة)
# ---------------------------------------------------------
class MemoryManager:
    """تخزين الذاكرة والسياق الخاص بالمستخدم"""
    def __init__(self):
        self.user_profiles: Dict[str, Dict[str, Any]] = {}

    def get_memory(self, user_id: str) -> str:
        profile = self.user_profiles.get(user_id, {})
        if not profile:
            return "لا توجد تفاصيل سابقة مسجلة للمستخدم."
        return f"اسم المستخدم/لقبه: {profile.get('name', 'غير معروف')}، الحالة النفسية السابقة: {profile.get('last_mood', 'عادي')}، الاهتمامات: {profile.get('interests', [])}"

    def update_memory(self, user_id: str, key: str, value: Any):
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        self.user_profiles[user_id][key] = value

memory_db = MemoryManager()

# ---------------------------------------------------------
# 05. Task Observer (نظام الحماية والمراقبة الأخلاقية)
# ---------------------------------------------------------
def task_observer_guardrail(user_input: str) -> bool:
    """فحص الأمان والسلامة للمدخلات قبل المعالجة"""
    danger_keywords = ["انتحار", "إيذاء", "قتل", "تدمير", "سلاح"]
    for word in danger_keywords:
        if word in user_input:
            return False  # العلم بالأخطار للحظر أو توجيه الدعم الطارئ
    return True

# ---------------------------------------------------------
# 03. Headroom (إدارة المساحة الذهنية وتلخيص الحوار)
# ---------------------------------------------------------
def headroom_summarize_context(history: List[Dict[str, str]]) -> str:
    """ضغط وتلخيص المحادثات الطويلة لضمان استجابة سريعة خفيفة"""
    if len(history) <= 4:
        return ""
    
    context_text = "\n".join([f"{h['role']}: {h['content']}" for h in history[:-2]])
    prompt = f"قم بتلخيص النقاط النفسية والعاطفية الأساسية في هذا الحوار باختصار شديد:\n{context_text}"
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        return f"\n[ملخص الجلسة السابقة بواسطة Headroom]: {response.text}\n"
    except Exception as e:
        return f"\n[ملاحظة Headroom]: متابعة الجلسة المباشرة ({str(e)})\n"

# ---------------------------------------------------------
# 01. OmniRoute (موجّه الطلبات والذكاء)
# ---------------------------------------------------------
def omni_route(user_input: str) -> str:
    """تحديد مسار الطلب: (فضفضة/دعم نفسي) أم (شعر وموسيقى)"""
    prompt = f"""
    صنّف طلب المستخدم التالي إلى إحدى الفئتين فقط:
    1. 'THERAPY' (إذا كان يفضفض، يحكي مشكلة، يبحث عن راحة أو دعم نفسي).
    2. 'CREATIVE' (إذا كان يطلب كتابة شعر، تلحين، أو بناء أغنية).
    
    النص: "{user_input}"
    قم بالرد بكلمة واحدة فقط: THERAPY أو CREATIVE.
    """
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        route = response.text.strip().upper()
        return route if route in ["THERAPY", "CREATIVE"] else "THERAPY"
    except Exception:
        # مسار احتياطي ذكي في حالة انقطاع الشبكة
        creative_keywords = ["شعر", "قصيدة", "لحن", "أغنية", "توزيع", "موسيقى", "غناء", "نغم"]
        for kw in creative_keywords:
            if kw in user_input:
                return "CREATIVE"
        return "THERAPY"

# ---------------------------------------------------------
# المحرك الأساسي لتطبيق FMStar (صوت الأثير)
# ---------------------------------------------------------
def fmstar_ether_voice(user_id: str, user_input: str, conversation_history: List[Dict[str, str]]) -> str:
    # 1. مراقبة الأمان (Task Observer)
    if not task_observer_guardrail(user_input):
        return "صوت الأثير يقف معك.. إذا كنت تمر بظرف حرج جداً أو تفكر في إيذاء نفسك، يرجى التواصل فوراً مع خطوط الدعم النفسي المختصة والجهات الرسمية في بلدك لسلامتك."

    # 2. التوجيه الذكي (OmniRoute)
    intent = omni_route(user_input)

    # 3. استرجاع الذاكرة (claude-mem)
    user_memory = memory_db.get_memory(user_id)

    # 4. ضغط الحوار (Headroom)
    headroom_summary = headroom_summarize_context(conversation_history)

    # 5. بناء تعليمات النظام (System Instructions)
    system_instruction = f"""
    أنت 'صوت الأثير' في تطبيق FMStar.
    شخصيتك: مستمع حنون، دافئ، مستشار نفسي واعي، يجمع بين الدعم الإنساني وقواعد علم النفس المعرفي السلوكي (CBT)، بدون أي تمييز.
    
    المسار الحالي المحدد بواسطة OmniRoute: {intent}
    
    معلومات الذاكرة المتاحة:
    {user_memory}
    {headroom_summary}

    إذا كان المسار THERAPY: قدم استماعاً هادئاً، واقترح ترددات صوتية (مثل أصوات الشلالات) وحلول عملية بسيطة.
    إذا كان المسار CREATIVE: حول المشاعر إلى أبيات شعرية أو نصوص فنية دافئة.
    """

    # 6. توليد الاستجابة باستخدام Gemini
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )
        )
        reply = response.text
    except Exception as e:
        if intent == "CREATIVE":
            reply = f"أسمع صدى مشاعرك تتردد في الأثير.. دعنا نصنع منها لحناً دافئاً يضيء العتمة. ({str(e)})"
        else:
            reply = f"أنا هنا بجانبك في صوت الأثير، أستمع لكل نبضة تثقل كاهلك.. خذ نفساً عميقاً، ولنبدأ معاً بترتيب الأفكار خطوة بخطوة."

    # تحديث الذاكرة كنموذج
    memory_db.update_memory(user_id, "last_mood", f"تفاعل مؤخراً عبر مسار {intent}")

    return reply

# ---------------------------------------------------------
# تجربة سريعة للتشغيل (Demo Executable)
# ---------------------------------------------------------
if __name__ == "__main__":
    test_user = "user_101"
    history = []

    print("--- تجربة تشغيل نظام FMStar (صوت الأثير) ---")
    user_msg = "أنا حاسس بضغط كبير ومش قادر أركز من التفكير في المستقبَل.. سرك في بير"
    
    print(f"المستخدم: {user_msg}\n")
    reply = fmstar_ether_voice(test_user, user_msg, history)
    print(f"صوت الأثير (Gemini):\n{reply}")
