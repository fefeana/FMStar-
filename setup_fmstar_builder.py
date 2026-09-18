cat << 'EOF' > setup_fmstar_builder.py
import os
import sys
import subprocess

# 1. التثبيت التلقائي للمكتبات الأساسية
def install_requirements():
    packages = ["google-genai"]
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"🔄 جاري تثبيت {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

install_requirements()

from google import genai

# 2. بناء الهيكل الشامل لمنصة FMStar
def orchestrate_fmstar():
    try:
        client = genai.Client()
    except Exception as e:
        print("\n❌ خطأ: لم يتم العثور على GEMINI_API_KEY!")
        print("💡 يُرجى التأكد من تشغيل: export GEMINI_API_KEY='your_key'")
        return

    print("\n🌟 ✨ بدء مهندس بناء منصة FMStar عبر Claude & Gemini...")

    prompt_task = """
    أنت مهندس معمارية برمجية قائد لمنصة FMStar (AI Audio & Video Studio).
    قم بتوليد كود Python تنفيذي ممتاز يقوم بإنشاء الملفات والهياكل التالية فوراً:
    1. مجلد backend يحتوي على app.py (FastAPI سريح لمعالجة الصوتيات وربط API) و config.py.
    2. مجلد frontend يحتوي على مكونات React / Three.js الأساسية للواجهة الصوتية.
    3. ملف claude_automation.sh لتنفيذ أوامر Claude CLI تلقائياً وبناء الوحدات البرمجية الصعبة.
    4. ملف README.md مفصل يوضح كيفية التشغيل والتكامل.
    اكتب الكود بالكامل بدون مقدمات وبصيغة جاهزة للتنفيذ.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_task
        )

        code_output = response.text
        print("\n--- ✅ تم توليد كود البناء بنجاح ---")

        with open("build_fmstar.py", "w", encoding="utf-8") as f:
            f.write(code_output)

        print("\n✅ تم حفظ السكريبت الرئيسي في 'build_fmstar.py'")
        print("🚀 لتطبيق وتوليد كامل ملفات المشروع الآن، قم بتشغيل:")
        print("   python build_fmstar.py")

    except Exception as e:
        print(f"\n❌ حدث خطأ أثناء الاتصال بالنموذج: {e}")

if __name__ == "__main__":
    orchestrate_fmstar()
EOF

python setup_fmstar_builder.py