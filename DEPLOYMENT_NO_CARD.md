# دليل التشغيل المجاني بدون بطاقة — FMStar AI Studio

## 1. مسار التشغيل الموحد
- نقطة البدء الموحدة في `render.yaml` و`Dockerfile` و`Procfile` هي:
  `python server_3000.py`
- المنفذ يُقرأ تلقائياً من متغير البيئة `PORT` (والقيمة الافتراضية `3000`).
- لا يُستخدم أي `cron job` مدفوع أو غير متوافق مع الخطة المجانية (`plan: free` في `render.yaml`).

## 2. الواجهة الأمامية والاتصال
- الواجهة المنشورة على GitHub Pages تتصل بالخادم عبر `FMSTAR_API_BASE_URL` / `fmstarApiUrl` وتستفيد من `window.fmstarStudioEngine` للكاش السريع والشفاء الذاتي و`window.fmstarGenerateAndPreview` للمعاينة قبل التنزيل.
- نطاق `https://fefeana.github.io` مُدرج ضمن قائمة `ALLOWED_ORIGINS` لـ CORS في `server_3000.py`.

## 3. المفاتيح والأمان
- مفاتيح `OmniRoute` والأسرار تُضبط في متغيرات بيئة السيرفر فقط (`sync: false` في `render.yaml`) دون تكرارها في مستودع Git أو واجهات HTML العامة.
- عند عدم ضبط المفاتيح الخارجية، تعمل بوابة `/api/v1/studio/generate` بوضع المعاينة المحلية الآمن (`studio-local`) دون تعطل السيرفر.
