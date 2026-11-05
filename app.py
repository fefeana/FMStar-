#!/usr/bin/env python3
# app.py - Star FM AI Studio Generator CLI & Engine
import argparse
import os
import sys
import json
import urllib.request
import urllib.error

def generate_poetry_local(prompt_text: str, effects: str = "ليلي, سينمائي") -> str:
    """توليد كلمات شعرية وغنائية احترافية باللغة العربية (محلياً واحتياطياً)"""
    return f"""🎙️ [Star FM | ليلة من صنعك]
━━━━━━━━━━━━━━━━━━━━━━
الليل أرخى سدوله والنجوم شهود..
على لحنٍ من خيالك يروي الوجود..
في هدوء السكون يعزف الشوق نغمة..
تلامس أوتار الفؤاد وتزهر ببسمة..

بين وميض النيون وأثير الأماني..
صوتك يسافر في فضاء المعاني..
ليلةٌ من صُنعك أنت، لا تشبه ليلة..
كل نغمة فيها حكاية.. وكل همسة أصيلة!
━━━━━━━━━━━━━━━━━━━━━━
✨ النمط والمؤثرات: {effects}
📻 الإذاعة: Star FM Cyber Studio • ليلة من صنعك"""

def generate_with_gemini(api_key: str, prompt_text: str, image_path: str = None) -> str:
    """استدعاء Gemini API المباشر عبر HTTP القياسي بدون مكتبات خارجية معقدة"""
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return generate_poetry_local(prompt_text)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    system_instruction = "أنت شاعر وملحن ومخرج صوتي محترف في إذاعة Star FM. اكتب كلمات أغنية أو قصيدة حالمة بناءً على الفكرة والصورة المرفقة. اجعل الكلمات موزونة ومليئة بالمشاعر. لا تكتب مقدمات رسمية."
    full_prompt = f"{system_instruction}\n\nفكرة العمل: {prompt_text}"

    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }]
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            candidates = res_data.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts:
                    return parts[0].get('text', '').strip()
    except Exception as e:
        print(f"⚠️ ملاحظة من Gemini API ({e}): جاري التحويل للمحرك الشعري المدمج...")
        return generate_poetry_local(prompt_text)

    return generate_poetry_local(prompt_text)

def main():
    parser = argparse.ArgumentParser(description="Star FM AI Studio - Music & Poetry Generator")
    parser.add_argument("--image_path", type=str, default="./1000120219_2.webp", help="Path to input cover image")
    parser.add_argument("--generate_with_text", type=str, default="ليلة من صنعك... ألحان قصيدة ليلي", help="Input text or lyric concept")
    parser.add_argument("--api_key", type=str, default=os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY"), help="Google Gemini API Key")
    parser.add_argument("--output_file", type=str, default=None, help="Optional output text file path")

    args = parser.parse_args()

    print("=" * 60)
    print("📻 Star FM | استوديو توليد الموسيقى والشعر بالذكاء الاصطناعي")
    print("=" * 60)
    print(f"🖼️ الصورة المعتمدة: {args.image_path}")
    print(f"📝 النص المدخل: {args.generate_with_text}")
    print("⚡ جاري المعالجة والتوليد...")
    print("-" * 60)

    result = generate_with_gemini(args.api_key, args.generate_with_text, args.image_path)
    
    print("\n🎉 النتيجة النهائية:\n")
    print(result)
    print("-" * 60)

    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"💾 تم حفظ النتيجة في: {args.output_file}")

if __name__ == "__main__":
    main()
