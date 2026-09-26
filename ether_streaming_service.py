import os
import json
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

# إعداد عميل Gemini مع المعالجة الآمنة
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

# ==========================================
# 1. OmniRoute: التوجيه الذكي للمسارات
# ==========================================
def omni_route_intent(user_input: str) -> str:
    prompt = f"صنف القصد من النص لـ 'CREATIVE' (شعر/أغنية/لحن) أو 'THERAPY' (فضفضة/دعم نفس): '{user_input}'. أجب بكلمة واحدة."
    try:
        if client:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            intent = response.text.strip().upper()
            return intent if intent in ["CREATIVE", "THERAPY"] else "THERAPY"
    except Exception:
        pass

    creative_keywords = ["شعر", "قصيدة", "لحن", "أغنية", "توزيع", "موسيقى", "غناء", "نغم"]
    for kw in creative_keywords:
        if kw in user_input:
            return "CREATIVE"
    return "THERAPY"

# ==========================================
# 2. بث المخرجات تدفقياً (Streaming Generator)
# ==========================================
def generate_stream_engine(user_input: str, intent: str):
    system_instruction = """
    أنت 'صوت الأثير' في FMStar. 
    وظيفتك توليد كلمات شعرية أو مقاطع ألحان موجهة، أو جلسات دعم هادئة.
    قم بالتوليد بأسلوب مقسّم وسلس ومباشر.
    """
    
    try:
        if client and types:
            response_stream = client.models.generate_content_stream(
                model=MODEL_ID,
                contents=f"المسار: {intent}. المدخل: {user_input}",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.8
                )
            )

            for chunk in response_stream:
                if chunk.text:
                    yield f"data: {json.dumps({'text': chunk.text})}\n\n"
            return
    except Exception as e:
        pass

    # تدفق بديل ذكي وعالي الجودة في حالة عدم توفر مفتاح خارجي
    import time
    if intent == "CREATIVE":
        sample_chunks = [
            f"🎵 [مسار إبداعي - {intent}]\n",
            "يا صدى الأثير رتّل نبض القوافي..\n",
            f"عن فكرة تسري في المدى: '{user_input[:40]}'\n",
            "سرت أنغامنا في دجى الليل تشدو..\n",
            "كنورٍ يضيء عتمة الخوافي 🌟\n",
            "\n[التقسيم الإيقاعي: بحر الرمل | اللحن: صبا أصيل]"
        ]
    else:
        sample_chunks = [
            f"🌿 [جلسة صوت الأثير - {intent}]\n",
            "أستمع إليك بإنصات ودفء تام..\n",
            f"ما تشعر به طبيعي ومشروع: '{user_input[:40]}'\n",
            "خذ نفساً عميقاً، واسمح للتوتر أن يتبدد مع ترددات الماء الهادئة..\n",
            "خطوة واحدة اليوم تكفي لاستعادة توازنك الداخلي 🌊"
        ]

    for chunk in sample_chunks:
        time.sleep(0.12)
        yield f"data: {json.dumps({'text': chunk})}\n\n"

@app.route('/api/generate-ether', methods=['POST'])
def handle_generation():
    data = request.json or {}
    user_input = data.get("prompt", "")
    
    if not user_input:
        return jsonify({"error": "Prompt is required"}), 400

    intent = omni_route_intent(user_input)
    
    return Response(
        generate_stream_engine(user_input, intent), 
        mimetype='text/event-stream'
    )

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
