# تقرير التدقيق الهندسي الشامل — FMStar AI Studio (`FMSTAR_AUDIT.md`)

**تاريخ التدقيق:** 2026-11-24  
**المستودع:** `https://github.com/fefeana/FMStar-` (الفرع الرئيسي: `main`)  
**الواجهة المنشورة حالياً:** `https://fefeana.github.io/FMStar-/`  
**نطاق هذه المرحلة (المرحلة A):** فحص فعلي كامل للمستودع وقراءة محتوى الملفات دون إجراء أي تعديل على الشيفرة التشغيلية.

---

## 1. البنية الحالية للمشروع

يحتوي المستودع على مزيج متراكم من عدة طبقات ومجلدات متداخلة (تتضمن نسخاً مكررة بين الجذر ومجلدات فرعية):

| الطبقة / المسار | التقنية | الوصف الفعلي من قراءة الملفات |
| :--- | :--- | :--- |
| **الواجهة الرئيسية المنشورة** (`index.html`, `public/index.html`) | HTML + Tailwind CDN + Vanilla JS + Web Audio API | واجهة **Star FM \| AI Studio** (متطابقة تماماً في الملفين — 411 سطراً)، تدعم المشغّل الإذاعي، توليد نغمات Web Audio، اختيار الأداة والمؤثرات، والنطق الصوتي `speechSynthesis`. |
| **واجهات ويب إضافية** (`fmstar_studio.html`, `FMStar.html`, `jm_studio.html`, `samurai.html`, `music_app/index.html`, `fmstar-project/static/`, `standby_layers/`) | HTML/JS/TS | صفحات استوديو وموسيقى وتجارب بديلة متفرقة بمسارات API غير موحدة. |
| **مكونات React/TSX** (`frontend/src/`) | React / TypeScript (`package.json` بلا سكربت بناء Vite/Next فعلي) | مكون `FMStarStudio.tsx` وخطاف `useStudioNotifications.ts` (`EventSource`). |
| **تطبيق Android** (`app/`) | Kotlin + Jetpack Compose + Room (`FMStarDatabase`) | تطبيق أندرويد كامل الواجهة يعمل حالياً ببيانات محلية ومولّد قوالب `PoetryGenerator.kt` ومولّد صوت `AudioTrack`؛ مكتبات `Retrofit`/`OkHttp`/`Firebase AI` موجودة في `app/build.gradle.kts` لكنها غير مربوطة بأي طلبات شبكة فعلية. |
| **الخادم الأساسي الحالي (Python HTTP)** (`server_3000.py`, `backend/server_3000.py`) | Python `http.server` + `socketserver` | خادم متعدد المسارات (874 سطراً، نسختان متطابقتان في الجذر و`backend/`) يدعم `/api/generate` وتصدير PDF وZIP وبث SSE. |
| **محرك الذكاء الاصطناعي / OmniRoute** (`ai_service.py`, `backend/ai_service.py`, `ai-brain/ai_service.py`) | Python FastAPI | النسخة `v1.7` (في الجذر و`backend/`) تتصل فعلياً بـ `OMNIROUTE_CLOUD_URL` عبر `/v1/audio/generations` مع تعقيم `bleach` وفحص `X-FMStar-Key`. |
| **خدمات Python متفرقة** (`app.py`, `backend/main.py`, `ai-brain/main.py`, `backend/fmstar_cloud.py`, `backend/server.py`, `backend/gemini_mira_backend.py`, `backend/ether_streaming_service.py`, `backend/ltx_service.py`, `ltx_bridge.py`, `proxy_service.py`, `media-engine/main.py`) | FastAPI / Flask / CLI | خدمات متناثرة بين منافذ `3000` و`5000` و`8000` و`8001`؛ بعضها CLI (`app.py`) وبعضها واجهات أولية أو محاكاة. |
| **طبقة التخزين المؤقت الذكي** (`ai-brain/adaptive_cache/`) | Python | وحدات `policy.py` و`l1_local.py` و`manager.py` جاهزة ومختبرة. |
| **خدمات Go** (`main.go`, `backend-go/main.go`, `services/gateway/main.go`, `jm-studio/main.go`, `fmstar-project/main.go`, `Agents/agents.go`) | Go `net/http` + `pgxpool` | عدة نوى Go منفصلة لـ Supabase/PostgreSQL وبوابة `/api/v1/fmstar/*` وتصدير ZIP؛ لا توجد عملية بناء أو نشر موحدة لها حالياً. |
| **البنية التحتية والنشر** (`Dockerfile`, `Procfile`, `render.yaml`, `infrastructure/docker/`, `.github/workflows/`) | Docker / Render / GitHub Actions | 4 ملفات Workflow (`deploy.yml`, `pages.yml`, `claude.yml`, `fmstar-remote.yml`) وإعدادات متعارضة لنقطة التشغيل. |

---

## 2. نقطة تشغيل كل خدمة (Entrypoints)

| ملف التشغيل / التكوين | الأمر الفعلي | المنفذ | الملاحظات والتعارضات |
| :--- | :--- | :--- | :--- |
| `Dockerfile` | `uvicorn ai_service:app --host 0.0.0.0 --port ${PORT:-8080}` | `${PORT:-8080}` | يشغّل `ai_service.py` فقط (لا يخدم `index.html` ولا `/api/generate`). |
| `Procfile` | `uvicorn ai_service:app --host 0.0.0.0 --port $PORT` | `$PORT` | مطابق لـ `Dockerfile`. |
| `render.yaml` (`web`) | `python server_3000.py` | `PORT` (افتراضي `3000`) | **تعارض مباشر** مع `Dockerfile` و`Procfile` (يشغّل خادماً مختلفاً بمسارات مختلفة!). |
| `render.yaml` (`cron`) | `urllib.request.urlopen('https://fmstar-backend-v2.onrender.com/')` | — | **غير متوافق** مع خطة Render المجانية دون بطاقة (الـ Cron Jobs ليست مجانية وتخالف شرط منع التحايل على النوم). |
| `package.json` و`frontend/package.json` | `python3 server_3000.py` | `3000` | يعامل `server_3000.py` كنقطة تشغيل محلية. |
| `app.py` | CLI (`argparse`) | لا يوجد منفذ | **ليس خادم ويب**؛ أداة سطر أوامر تستدعي Gemini أو تعيد قصيدة افتراضية محلية. |
| `backend/main.py` و`ai-brain/main.py` | FastAPI `app` (بلا `__main__`) | يفترض `8001` لـ `server_3000.py` | يستخدمها `server_3000.py` كبروكسي داخلي عبر `http://127.0.0.1:8001/internal/*` الذي لن يعمل في النشر المنفصل على خدمة ويب واحدة! |
| `media-engine/main.py` | `uvicorn` على `PORT` (`8001`) | `8001` | يفشل بـ `NameError: name 'os' is not defined` عند تشغيله مباشرة لأن `os` غير مستورد. |
| `ltx_bridge.py` / `backend/server.py` / `backend/ltx_service.py` / `proxy_service.py` | FastAPI / Flask | `5000` | تضارب منافذ (كلها تحاول حجز المنفذ `5000`). |
| `main.go` | `http.ListenAndServe(":"+port, nil)` | `${PORT:-8080}` | خادم Go مستقل غير مستخدم في `Dockerfile` أو `render.yaml`. |

---

## 3. الميزات الموجودة فعلياً وتقييم حالتها

### أ) ميزات مكتملة وتعمل فعلياً
- **واجهة الويب الرئيسية (`index.html`):** تصميم Neon Glassmorphism متكامل، اختيار الأداة (`أغنية` / `قصيدة` / `فيديو`)، قائمة التأثيرات، عداد الأحرف `0 / 280`، مشغل موسيقى توليدي بـ Web Audio API، والنطق العربي عبر `window.speechSynthesis`.
- **حماية ودعم خادم `server_3000.py`:** Rate Limiting (`10` طلبات/دقيقة لكل IP)، تعقيم مدخلات XSS (`sanitize_text_input`)، كوكي جلسة `HttpOnly; Secure; SameSite=Strict`، تصدير PDF حقيقي (`/api/creations/export-pdf`)، ضغط وتنزيل ملفات ZIP (`/api/creations/batch-download`)، وبحث الأعمال (`/api/creations/search`).
- **اتصال OmniRoute الأساسي (`ai_service.py` v1.7):** التحقق من `X-FMStar-Key` عبر متغير البيئة `FMSTAR_SECRET_KEY`، تعقيم النص بـ `bleach`، إرسال طلب فعلي إلى `OMNIROUTE_CLOUD_URL` مع مهلة 25 ثانية، واستجابات خطأ RFC 7807 (`application/problem+json`).
- **طبقة التخزين المؤقت (`ai-brain/adaptive_cache/`):** سياسات التوجيه والكاش المحلي `L1` مبرمجة وجاهزة لإعادة الاستخدام.
- **تطبيق Android (`app/`):** واجهة Jetpack Compose كاملة + تخزين محلي Room (`FMStarDatabase`) + مؤثرات صوتية محلية (`AudioPlayerManager`).

### ب) ميزات ناقصة أو تعمل بقوالب/بيانات تجريبية (Stubs / Mocks)
- **`POST /api/generate` في `server_3000.py` و`main.go`:** يعيد حالياً **قصيدة ثابتة مكتوبة مسبقاً** (`"يا هاجس الشعر هات القاف من بدري..."`) ورابط فيديو تجريبي `BigBuckBunny.mp4` بدلاً من استدعاء Gemini أو OmniRoute.
- **`POST /v1/audio/generations` في `ai_service.py`:** يحسّن النص فعلياً عبر OmniRoute، لكنه يعيد رابط فيديو ثابتاً (`https://www.w3schools.com/html/mov_bbb.mp4`) وليس توليد فيديو حقيقي.
- **`POST /api/fmstar/generate` في `server_3000.py`:** يعيد رابط `BigBuckBunny.mp4` التجريبي.
- **`backend/poetry_engine.py` و`backend/song_engine.py`:** يكتبان ملفات MP3 وهمية فارغة (رأس `ID3` بطول 10–270 بايت فقط) عند غياب مفتاح ElevenLabs.
- **`backend/ltx_service.py`:** يكتب ملف `outputs/generated_video.mp4` بحجم **0 بايت** عند عدم توفر بطاقة GPU CUDA.
- **تطبيق Android (`CloudRepository.kt` و`PoetryGenerator.kt`):** يولّد قصائد من قوالب ثابتة ويعرض عناوين وسجلات سحابية محاكاة (`35.224.180.92`, `jimi-mira-studio.example.com`) دون اتصال حقيقي بالخلفية.

### ج) ميزات معطلة أو غير مربوطة حالياً
- **الاتصال من GitHub Pages إلى الخلفية:** `index.html` يطلب المسار النسبي `/api/generate`؛ وبما أن GitHub Pages استضافة ملفات ثابتة فقط، فإن التوليد سيفشل على الرابط العام `https://fefeana.github.io/FMStar-/` لعدم وجود عنوان خادم مركزي (`API_BASE_URL`).
- **بروكسي `/internal/*` في `server_3000.py`:** يوجّه إلى `http://127.0.0.1:8001` غير المتاح ما لم تُشغّل خدمة ثانية في نفس الحاوية.
- **`media-engine/main.py` و`backend/gemini_mira_backend.py`:** يحتويان على خطأ `NameError` بسبب استخدام `os.getenv` دون `import os`.
- **`frontend/src/components/viviana-console/FMStarStudio.tsx`:** يطلب `/api/v1/fmstar/generate` و`/api/v1/fmstar/synthesize-speech` الموجودة فقط في `services/gateway/main.go` (المفصول عن `server_3000.py` و`ai_service.py`)، كما لا يملك `frontend/package.json` أداة بناء فعلية.
- **`.github/workflows/fmstar-remote.yml`:** يراقب القضية `#5` (غير موجودة في المستودع؛ الموجود `#1` و`#2`) ويرسل إلى `/api/fmstar/command` غير المُنفَّذ في الخادم.

---

## 4. نقاط الاتصال الحالية بين الواجهة والخلفية

| الواجهة | المسار المستدعى | الحالة الفعلية |
| :--- | :--- | :--- |
| `index.html` / `public/index.html` | `POST /api/generate` (مسار نسبي) | يعمل محلياً مع `server_3000.py` (بقصيدة ثابتة) و**يفشل على GitHub Pages**. |
| `FMStar.html` | `[ضع_رابط_جوجل_كلاود_هنا]/internal/generate` | **معطّل** (نص placeholder + مفتاح سري مكشوف في المتصفح). |
| `fmstar_studio.html` | `/api/fmstar/generate-video`, `/internal/generate`, `/api/fmstar/generate`, `/api/generate-ether`, `/api/creations/export-pdf` | مسارات متفرقة على عدة خوادم + مفتاح `X-FMStar-Key` مكشوف. |
| `frontend/src/...` | `/api/v1/fmstar/generate`, `/api/v1/fmstar/synthesize-speech`, `/api/v2/notifications/stream` | منفصلة عن خادم Python الرئيسي. |
| تطبيق Android (`app/`) | لا يوجد اتصال HTTP فعلي | يعمل محلياً فقط (`Room` + `PoetryGenerator`). |

---

## 5. الخدمات والوحدات القابلة لإعادة الاستخدام بأقل تعديل

1. **`ai_service.py` (v1.7):** نواة FastAPI جاهزة للعمل مع OmniRoute ومتغيرات البيئة وحماية RFC 7807 — مناسبة لتكون قاعدة خدمة الـ API الموحدة تحت `/api/v1/`.
2. **`server_3000.py` (منطق المساعدات):** دوال التصدير (PDF / ZIP)، Rate Limiting، تعقيم المدخلات، وبنية الاستجابة المتوافقة مع `index.html`.
3. **`backend/server_config.py`:** هيكل إعدادات مركزي جيد (يحتاج إزالة القيمة الافتراضية `"change-me"` وإضافة جميع المتغيرات المكتشفة).
4. **`ai-brain/adaptive_cache/`:** جاهزة لتقليل استهلاك الحصص المجانية والطلبات المكررة.
5. **`app.py` (`generate_with_gemini`) و`backend/respan_evaluator.py` و`backend/fmstar_audio_architect.py`:** منطق استدعاء Gemini المباشر، التقييم، وهندسة التوزيع الصوتي يمكن دمجها كموصلات نظيفة في الطبقة الهجينة.
6. **`index.html` (التصميم والوظائف):** جاهز تماماً؛ يحتاج فقط فصل عنوان الـ API إلى إعداد مركزي (`API_BASE_URL`) وإظهار حالة الاتصال/المزود دون أي تغيير بصري.

---

## 6. التعارضات والأخطاء والمخاطر الأمنية الحرجة

### مخاطر أمنية عالية الأولوية
1. **كشف أسرار افتراضية وثابتة في الشيفرة والواجهات العامة:**
   - `"samurai_secret_2026"` ظاهر بشكل صريح في ملفات واجهة عامة: `FMStar.html` (سطر 257)، `fmstar_studio.html` (سطر 1514)، `standby_layers/layer_3_fmstar_audio/index.html` (سطر 1514)، وكذلك كقيمة افتراضية في `server_3000.py` (الأسطر 127، 705)، `backend/main.py` (سطر 23)، `ai-brain/main.py` (سطر 23)، و`ai-brain/ai_service.py` (سطر 44).
   - `"sk-omniroute-free-key"` كقيمة افتراضية في `ai-brain/ai_service.py` (سطر 58)، و`"change-me"` في `backend/server_config.py` (سطر 21).
   - **ملاحظة تدوير الأسرار:** لأن `"samurai_secret_2026"` و`"sk-omniroute-free-key"` مسجّلان بالفعل في تاريخ Git وفي صفحات HTML، يجب عدم استخدامهما مطلقاً في الإنتاج وتدوير أي مفاتيح مرتبطة بهما.
2. **نشر جذر المستودع بالكامل على GitHub Pages (`path: '.'`):**
   - ملفا `.github/workflows/deploy.yml` و`.github/workflows/pages.yml` مكرران وكلاهما ينشر الجذر `.` بالكامل؛ ما يجعل ملفات الخادم الخلفي (`server_3000.py`, `ai_service.py`) وملفات `.claude/` و`debug.keystore` متاحة علناً عبر الويب!
3. **CORS غير مقيد وأصل خاطئ:**
   - استخدام `allow_origins=["*"]` في `backend/main.py`، `ai-brain/main.py`، `backend/fmstar_cloud.py`، `backend/gemini_mira_backend.py`، `ltx_bridge.py`، `services/gateway/main.go`، وبعض مسارات `main.go` و`server_3000.py`.
   - `server_3000.py` (سطر 72) يضبط الأصل الافتراضي إلى `https://mustafabushra.com` بدلاً من `https://fefeana.github.io`.
4. **مخاطر حقن المسار والنظام:**
   - `main.go` (`DownloadBatchZipHandler`, سطر 473) يفتح `filepath.Clean(path)` مباشرة من طلب المستخدم دون حصره داخل مجلد محدد (Path Traversal).
   - `backend/song_engine.py` (سطر 12) يحاول الكتابة في `/public` (مجلد الجذر في النظام) بدلاً من مجلد تخزين مؤقت/محلي آمن.

### أخطاء برمجية وتعارضات تشغيلية
- تكرار ملفات الخادم (`server_3000.py` في 2 مسار، `ai_service.py` في 4 مسارات، `ltx_bridge.py` في 4 مسارات، `main.go` في 5 مسارات).
- تعارض `Dockerfile`/`Procfile` (`ai_service:app`) مع `render.yaml` (`server_3000.py`) و`render.yaml cron` المخالف للخطة المجانية دون بطاقة.
- أخطاء تشغيل فورية: نقص `import os` في `media-engine/main.py` و`backend/gemini_mira_backend.py`.
- نقص تغطية الاختبارات التلقائية للخادم ومسارات OmniRoute والتكامل.

---

## 7. خطة التنفيذ المقترحة دون كسر الوظائف الموجودة

| المرحلة | الهدف | المخرجات الرئيسية |
| :--- | :--- | :--- |
| **B — التصميم المعماري** | توثيق المعمارية الهجينة الموحدة وقائمة الملفات المستهدفة بالتعديل | `FMSTAR_ARCHITECTURE.md` |
| **C — توحيد الخادم والأسرار** | إزالة الأسرار الثابتة من الكود والواجهات، توحيد نقطة الدخول (`Dockerfile`/`Procfile`/`render.yaml` بلا Cron)، إصلاح CORS والنشر في GitHub Pages، وإصلاح `os` و`/public` | `SECURITY_AUDIT.md`, `ENVIRONMENT_VARIABLES.md`, خادم موحد على `/api/v1/` + توافق `/api/generate` |
| **D — API Gateway وOmniRoute والموصلات** | دمج بوابة `/api/v1/` مع دعم OmniRoute القابل للتفعيل/التبديل، وموصلات Gemini / Media Adapters مع Fallback واضح ومصادق عليه | بوابة FastAPI موحدة + محولات المزودين |
| **E — إدارة المهام والتخزين** | طابور مهام (Jobs) غير متزامن مع حالة المهمة وتخزين مؤقت/آمن قابل للاستبدال مع تنظيف دوري وعدم الاعتماد على `/tmp` للبيانات الدائمة | مدير مهام + طبقة تخزين آمنة |
| **F — ربط الواجهة دون تغيير التصميم** | إضافة `API_BASE_URL` مركزي في `index.html` (مع إبقاء التصميم والأدوات 100% كما هي)، وعرض حالة الخادم وOmniRoute والمهل بوضوح | واجهة مرتبطة تعمل محلياً وعبر GitHub Pages |
| **G — الاختبارات الشاملة** | اختبارات تلقائية تغطي البنود الـ 14 (Health, OmniRoute mock/live, غياب المفاتيح, Rate limit, Jobs, CORS, عدم تسريب الأسرار, بناء الواجهة) | `TESTING_REPORT.md` + حزمة `pytest` |
| **H — النشر المجاني دون بطاقة** | مقارنة حية وموثقة من المواقع الرسمية لخيارات الاستضافة المجانية بلا بطاقة بنكية للـ Backend وOmniRoute وتوثيق خطوات Android | `DEPLOYMENT_NO_CARD.md`, `API_DOCUMENTATION.md` |
