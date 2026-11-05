# 🥷 FMStarAI Studio - Master Project Plan

## 🎯 الهدف
بناء منصة FMStarAI Studio (استوديو صوتي ذكي) لإنشاء الأصوات والموسيقى.

## 🛠️ التقنيات (Tech Stack)
- الواجهة الأمامية: Next.js / React (داخل مجلد frontend).
- محرك الذكاء الاصطناعي: Python / FastAPI (ملف ai_service.py).
- واجهة الأندرويد: Jetpack Compose.
- DevOps: GitHub Actions.

## ⚡ نماذج الذكاء الاصطناعي المعتمدة (الوقود المجاني)
- MiniMax H3 (لتوليد الصوت والفيديو).
- OmniRoute (مزود APIs مجاني).

## 🛡️ قواعد الأمان الصارمة (Security Rules)
1. تحديث Node.js إلى الإصدار v22 أو أحدث في ملفات GitHub Actions (تجنب ثغرات v20).
2. عدم كتابة أي مفاتيح API داخل الأكواد (استخدام ملف .env فقط).
3. حماية محرك Python باستخدام CORS و API Key.
4. التحقق من صحة جميع المدخلات (Input Validation).
