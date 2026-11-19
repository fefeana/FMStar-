import os
import json
import re

competitors = [
    {"name": "Talkwedd Studio", "url": "https://talkweddstudio.business.site"},
    {"name": "Time Freeze Studios", "url": "https://timefreezestudios.com/photography/"},
    {"name": "Harshit Digital Studio", "url": "https://harshit-digital-studio.business.site/"},
    {"name": "Memories Mirror", "url": "http://www.memoriesmirror.com/"},
    {"name": "The Exposure Photography", "url": "https://the-exposure-photography.odoo.com/"},
    {"name": "Jclas Albums", "url": "https://www.jclasalbums.com/"},
]

print("🚀 بدأ سحب أسعار استديوهات Lucknow...")

# سحب المفتاح بأمان من متغيرات البيئة في النظام
gemini_key = os.getenv("GEMINI_API_KEY")

try:
    from scrapegraphai.graphs import SmartScraperGraph
    CONFIG = {"llm": {"model": "gemini/gemini-1.5-flash", "api_key": gemini_key}}
    
    for s in competitors:
        print(f"🔍 {s['name']}")
        try:
            g = SmartScraperGraph(prompt="Extract photography packages and prices as JSON", source=s["url"], config=CONFIG)
            print(g.run())
        except Exception as e: 
            print(f"⚠️ {e}")
except Exception as e:
    print(f"⚠️ خطأ في التشغيل: {e}")

print("✅ خلص - جاهز لتطبيق الاستديو 🎸")
