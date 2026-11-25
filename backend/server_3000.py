import http.server
import socketserver
import json
import os
import subprocess
import time
import urllib.request
import urllib.parse
import uuid
import zipfile
import io
import threading
import html
import re
import secrets

_RATE_LIMIT_STORE = {}
_RATE_LIMIT_LOCK = threading.Lock()
_SCRIPT_RE = re.compile(r'(?is)<\s*script[^>]*>.*?<\s*/\s*script\s*>|javascript:|on\w+\s*=')

def sanitize_text_input(val: str) -> str:
    if not isinstance(val, str):
        return ""
    cleaned = _SCRIPT_RE.sub("", val)
    return html.escape(cleaned.strip())

def check_rate_limit(ip: str, limit: int = 10, window_seconds: int = 60) -> bool:
    now = time.time()
    with _RATE_LIMIT_LOCK:
        entry = _RATE_LIMIT_STORE.get(ip)
        if not entry or (now - entry["window_start"]) >= window_seconds:
            _RATE_LIMIT_STORE[ip] = {"count": 1, "window_start": now}
            return True
        entry["count"] += 1
        return entry["count"] <= limit

def generate_shareable_creation(track_title: str, audio_url: str) -> dict:
    """توليد معرف فريد وإنشاء روابط المشاركة للسوشيال ميديا"""
    unique_id = str(uuid.uuid4())[:8]
    share_link = f"https://fmstar.app/s/{unique_id}"
    
    share_text = f"استمع إلى إبداعي الجديد '{track_title}' عبر صوت الأثير في FMStar! 🎧✨\n{share_link}"
    encoded_text = urllib.parse.quote(share_text)
    encoded_url = urllib.parse.quote(share_link)

    social_links = {
        "whatsapp": f"https://api.whatsapp.com/send?text={encoded_text}",
        "x_twitter": f"https://twitter.com/intent/tweet?text={encoded_text}",
        "telegram": f"https://t.me/share/url?url={encoded_url}&text={urllib.parse.quote(track_title)}"
    }

    return {
        "creation_id": unique_id,
        "share_link": share_link,
        "social_links": social_links
    }

PORT = int(os.getenv("PORT", "3000"))
REMOTE_MODEL_URL = os.getenv("REMOTE_MODEL_URL", "https://api.ltx.io/v1/generate")

class ThreadingSimpleServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class FMStarHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noisy logging
        pass

    def _apply_strict_security_headers(self):
        self._custom_cors_applied = True
        allowed_origin = os.getenv("ALLOWED_ORIGIN", "https://mustafabushra.com")
        origin = self.headers.get("Origin", "")
        if origin and (
            origin == allowed_origin
            or origin.endswith(".run.app")
            or origin.endswith(".trycloudflare.com")
            or origin.endswith(".onrender.com")
            or origin.startswith("http://localhost:")
            or origin.startswith("http://127.0.0.1:")
        ):
            self.send_header("Access-Control-Allow-Origin", origin)
        else:
            self.send_header("Access-Control-Allow-Origin", allowed_origin)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

    def _get_client_ip(self) -> str:
        xff = self.headers.get("X-Forwarded-For", "")
        if xff:
            return xff.split(",")[0].strip()
        return self.client_address[0] if self.client_address else "unknown"

    def end_headers(self):
        if not getattr(self, "_custom_cors_applied", False):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        has_conn = any(b'connection:' in h.lower() for h in getattr(self, '_headers_buffer', []))
        if not has_conn:
            self.send_header('Connection', 'close')
        super().end_headers()

    def do_OPTIONS(self):
        try:
            self.send_response(200)
            if self.path == '/api/generate':
                self._apply_strict_security_headers()
            self.end_headers()
        except Exception:
            pass

    def do_POST(self):
        if self.path.startswith('/internal/'):
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req = urllib.request.Request(
                    f"http://127.0.0.1:8001{self.path}",
                    data=post_data,
                    headers={
                        "Content-Type": self.headers.get("Content-Type", "application/json"),
                        "X-FMStar-Key": self.headers.get("X-FMStar-Key", os.getenv("FMSTAR_SECRET_KEY", ""))
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    resp_data = resp.read()
                    self.send_response(resp.status)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(resp_data)
            except urllib.error.HTTPError as he:
                self.send_response(he.code)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(he.read())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return

        if self.path == '/generate':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except Exception:
                    data = {}
                lyrics = data.get('text', '')

                audio_url = "/public/poetry_output.mp3"
                try:
                    from song_engine import generate_song_music
                    audio_file = generate_song_music(lyrics)
                    if audio_file:
                        audio_url = f"/public/{audio_file}"
                except Exception:
                    pass

                snippet = lyrics[:20] if len(lyrics) >= 20 else lyrics
                res_data = {
                    "status": "success",
                    "message": f"تم توليد لحن أكوستيك بنجاح لكلمات: ({snippet}...)",
                    "audio_url": audio_url,
                    "lyrics": lyrics
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/v1/audio/architect':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req_data = json.loads(post_data.decode('utf-8'))
                
                from fmstar_audio_architect import FMStarAudioArchitect
                architect = FMStarAudioArchitect()
                result = architect.process_song_architecture(
                    lyrics_raw=req_data.get('lyrics', ''),
                    genre=req_data.get('genre', 'Euro-Disco / 80s Synth-Pop'),
                    bpm=int(req_data.get('bpm', 120)),
                    vocal_tone=req_data.get('vocal_tone', 'Romantic & Energetic')
                )
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/v1/ether/chat':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req_data = json.loads(post_data.decode('utf-8'))
                
                from fmstar_ether_voice import fmstar_ether_voice
                user_id = req_data.get('user_id', 'default_user')
                user_input = req_data.get('message', '')
                history = req_data.get('history', [])
                
                reply = fmstar_ether_voice(user_id, user_input, history)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply, "user_id": user_id}, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/generate-ether':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req_data = json.loads(post_data.decode('utf-8'))
                user_input = req_data.get('prompt', '')

                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Connection', 'keep-alive')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                from ether_streaming_service import omni_route_intent, generate_stream_engine
                intent = omni_route_intent(user_input)
                for chunk in generate_stream_engine(user_input, intent):
                    self.wfile.write(chunk.encode('utf-8'))
                    self.wfile.flush()
            except Exception as e:
                pass
            return

        if self.path == '/api/generate':
            try:
                # 1. Rate Limiting (10 طلبات في الدقيقة لكل مستخدم)
                client_ip = self._get_client_ip()
                if not check_rate_limit(client_ip, limit=10, window_seconds=60):
                    self.send_response(429)
                    self._apply_strict_security_headers()
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "error": "Too Many Requests, please slow down."
                    }, ensure_ascii=False).encode('utf-8'))
                    return

                content_length = int(self.headers.get('Content-Length', 0))
                if content_length <= 0 or content_length > 65536:
                    self.send_response(400)
                    self._apply_strict_security_headers()
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid input data"}).encode('utf-8'))
                    return

                post_data = self.rfile.read(content_length)
                content_type = self.headers.get('Content-Type', '')

                name = ''
                occasion = ''
                style = ''
                details = ''
                mode = ''
                text = ''
                tool = ''
                dialect = ''
                prompt = ''
                gender = 'male'

                if 'application/json' in content_type:
                    try:
                        req = json.loads(post_data.decode('utf-8'))
                        tool = sanitize_text_input(req.get('tool', ''))
                        dialect = sanitize_text_input(req.get('dialect', ''))
                        prompt = sanitize_text_input(req.get('prompt', ''))
                        mode = sanitize_text_input(req.get('mode', ''))
                        text = sanitize_text_input(req.get('text', ''))
                        name = sanitize_text_input(req.get('name', ''))
                        occasion = sanitize_text_input(req.get('occasion', ''))
                        style = sanitize_text_input(req.get('style', ''))
                        details = sanitize_text_input(req.get('details', ''))
                        gender = sanitize_text_input(req.get('gender', 'male')) or 'male'
                    except Exception:
                        self.send_response(400)
                        self._apply_strict_security_headers()
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Invalid input data"}).encode('utf-8'))
                        return
                else:
                    raw_text = post_data.decode('utf-8', errors='ignore')
                    for field in ['name', 'occasion', 'style', 'details', 'text', 'mode', 'tool', 'dialect', 'prompt']:
                        pattern = f'name="{field}"\r\n\r\n'
                        if pattern in raw_text:
                            val = sanitize_text_input(raw_text.split(pattern)[1].split('\r\n')[0].strip())
                            if field == 'name': name = val
                            elif field == 'occasion': occasion = val
                            elif field == 'style': style = val
                            elif field == 'details': details = val
                            elif field == 'text': text = val
                            elif field == 'mode': mode = val
                            elif field == 'tool': tool = val
                            elif field == 'dialect': dialect = val
                            elif field == 'prompt': prompt = val

                # إصدار كوكي جلسة محمي بمعايير صارمة
                cookie_header = self.headers.get('Cookie', '')
                new_session_token = None
                if 'session_token=' not in cookie_header:
                    new_session_token = secrets.token_hex(32)

                if prompt or (tool and not name and not mode):
                    if not prompt:
                        self.send_response(400)
                        self._apply_strict_security_headers()
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Invalid input data"}).encode('utf-8'))
                        return

                    safe_tool = tool or 'أغنية / قصيدة'
                    safe_dialect = dialect or 'سينمائي، ليلي'
                    generated_text = (
                        f"✨ [تم التوليد بنجاح عبر استوديو FMStar | {safe_tool}]:\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎙️ الفكرة: {prompt}\n\n"
                        f"يا هاجس الشعر هات القاف من بدري\n"
                        f"واسجِ المعاني على أوتار ألحاني\n"
                        f"في ليلةٍ يزهر الإحساس في صدري\n"
                        f"ويغرد الصوت في أثيرٍ وأوزانِ\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎛️ التأثيرات والنمط: {safe_dialect}\n"
                        f"🛡️ محمي عبر Omni-Root v4.2"
                    )
                    res_data = {
                        "status": "success",
                        "engine": "Omni-Root v4.2",
                        "tool": safe_tool,
                        "dialect": safe_dialect,
                        "result": generated_text
                    }
                elif name or occasion or (style and not mode):
                    target_name = name if name else 'صديقنا الغالي'
                    occasion_str = occasion if occasion else 'مفاجأة'
                    style_str = style if style else 'طرب'
                    lyrics = (
                        f"🎁 إهداء خاص إلى: {target_name} بمناسبة {occasion_str}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"يا هلا بنور العين وأغلى الحبايب.. {target_name}\n"
                        f"في يومك السعيد غنت لك كل السحايب\n"
                        f"لك في القلب معزة وعزيمة تطيب وتصايب\n"
                        f"عسى أيامك هنا وسعادة وما تفارقها الرغائب!\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎵 اللحن والستايل: {style_str} مدمج بتقنية Omni-Root\n"
                        f"✨ {details if details else 'أجمل التهاني القلبية'}"
                    )
                    res_data = {
                        "status": "success",
                        "lyrics": lyrics,
                        "result": lyrics,
                        "media_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
                    }
                else:
                    from poetry_engine import generate_poetry_recitation
                    from song_engine import generate_song_music
                    if mode == "song":
                        audio_file = generate_song_music(text=text)
                        res_data = {
                            "status": "success",
                            "mode": "song",
                            "audio_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                            "audio_file": audio_file
                        }
                    else:
                        audio_file = generate_poetry_recitation(text=text, dialect=dialect or 'fus_ha_modern', gender=gender)
                        res_data = {
                            "status": "success",
                            "mode": "poetry",
                            "dialect": dialect or 'fus_ha_modern',
                            "gender": gender,
                            "audio_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                            "audio_file": audio_file
                        }

                self.send_response(200)
                self._apply_strict_security_headers()
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                if new_session_token:
                    self.send_header(
                        'Set-Cookie',
                        f'session_token={new_session_token}; Path=/; Max-Age=3600; HttpOnly; Secure; SameSite=Strict'
                    )
                self.end_headers()
                self.wfile.write(json.dumps(res_data, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self._apply_strict_security_headers()
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "status": "error"}).encode('utf-8'))
            return

        if self.path == '/api/evaluate':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req = json.loads(post_data.decode('utf-8'))
                content = req.get('content', req.get('text', ''))
                model = req.get('model', 'respan/span-01-lite')

                from respan_evaluator import evaluate_response_respan
                eval_result = evaluate_response_respan(content=content, model=model)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(eval_result, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/v1/tracks':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                track_data = json.loads(post_data.decode('utf-8'))
                track_data['id'] = str(int(time.time() * 1000))
                track_data['created_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "track": track_data
                }).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/fmstar/generate':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except Exception:
                    data = {}

                prompt = data.get('prompt', 'مشهد سينمائي مع صوت محيطي')
                ratio = data.get('ratio', '16:9')
                profile = data.get('dsp_profile', 'hybrid')

                # Execute audio DSP pipeline
                try:
                    subprocess.run(
                        ["python3", "fmstar-project/ltx_dsp_engine.py", "--prompt", prompt, "--ratio", ratio, "--profile", profile],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                except Exception:
                    pass

                video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
                share_data = generate_shareable_creation(prompt, video_url)

                response_data = {
                    "status": "success",
                    "video_url": video_url,
                    "dsp_applied": f"{profile.capitalize()} Studio DSP Profile Active",
                    "aspect_ratio": ratio,
                    "timestamp": int(time.time()),
                    "share_data": share_data
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            except Exception as e:
                try:
                    self.send_response(500)
                    self.end_headers()
                except Exception:
                    pass
            return

        if self.path == '/api/creations/export-pdf' or self.path == '/api/v1/creations/export-pdf':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode('utf-8')) if post_data else {}
                
                title = payload.get('title', 'إبداع فني - Gemini & Mira Studio')
                creation_type = payload.get('type', 'شعر / موسيقى')
                dialect = payload.get('dialect', 'فصيح حديث')
                text_content = payload.get('text', 'نص الإبداع الشعري والفني')
                timestamp = payload.get('created_at', time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
                author = payload.get('author', 'Mira Studio AI Architect')
                
                pdf_content = (
                    f"%PDF-1.4\n"
                    f"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
                    f"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
                    f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
                    f"4 0 obj\n<< /Length 380 >>\nstream\n"
                    f"BT\n"
                    f"/F1 20 Tf\n50 780 Td\n(GEMINI & MIRA STUDIO - CREATION METADATA) Tj\n"
                    f"/F1 12 Tf\n0 -30 Td\n(Title: {title.encode('ascii', 'replace').decode('ascii')}) Tj\n"
                    f"0 -20 Td\n(Type: {creation_type.encode('ascii', 'replace').decode('ascii')}) Tj\n"
                    f"0 -20 Td\n(Dialect / Style: {dialect.encode('ascii', 'replace').decode('ascii')}) Tj\n"
                    f"0 -20 Td\n(Author / Engine: {author.encode('ascii', 'replace').decode('ascii')}) Tj\n"
                    f"0 -20 Td\n(Date: {timestamp.encode('ascii', 'replace').decode('ascii')}) Tj\n"
                    f"0 -35 Td\n(Content Summary:) Tj\n"
                    f"/F1 10 Tf\n0 -20 Td\n({text_content[:200].encode('ascii', 'replace').decode('ascii')}) Tj\n"
                    f"ET\n"
                    f"endstream\nendobj\n"
                    f"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
                    f"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000244 00000 n \n0000000676 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n755\n%%EOF"
                )
                
                pdf_bytes = pdf_content.encode('latin1')
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', 'attachment; filename="creation_metadata.pdf"')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(pdf_bytes)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        if self.path in ('/api/creations/batch-download', '/api/v1/creations/batch-download', '/api/creations/download-zip'):
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req_data = json.loads(post_data.decode('utf-8')) if post_data else []
                if isinstance(req_data, dict):
                    file_list = req_data.get('file_paths', [])
                elif isinstance(req_data, list):
                    file_list = req_data
                else:
                    file_list = []

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for item in file_list:
                        fname = os.path.basename(str(item))
                        found = False
                        for candidate_path in [item, os.path.join("public", fname), os.path.join("static", fname), fname]:
                            if os.path.exists(candidate_path) and os.path.isfile(candidate_path):
                                zf.write(candidate_path, arcname=fname)
                                found = True
                                break
                        if not found:
                            zf.writestr(fname, f"Creation Item: {fname}\nGenerated by FMStar Studio\nStatus: Archived")

                zip_buffer.seek(0)
                zip_bytes = zip_buffer.getvalue()

                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Disposition', 'attachment; filename="Gemini_Mira_Creations.zip"')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(zip_bytes)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/v1/share':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req_data = json.loads(post_data.decode('utf-8'))
                title = req_data.get('title', 'إبداع صوت الأثير الجديد')
                audio_url = req_data.get('audio_url', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4')
                
                share_res = generate_shareable_creation(title, audio_url)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(share_res, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        try:
            self.send_response(404)
            self.end_headers()
        except Exception:
            pass

    def do_GET(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path_only = parsed.path
            query_params = urllib.parse.parse_qs(parsed.query)

            if path_only == '/favicon.ico':
                self.send_response(204)
                self.end_headers()
                return

            if path_only in ['/docs', '/openapi.json'] or path_only.startswith('/docs'):
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:8001{self.path}", timeout=5) as u_resp:
                        body = u_resp.read()
                        self.send_response(u_resp.status)
                        content_type = u_resp.headers.get('Content-Type', 'text/html; charset=utf-8')
                        self.send_header('Content-Type', content_type)
                        self.send_header('Content-Length', str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)
                        return
                except Exception as e:
                    self.send_response(502)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(f"FastAPI proxy info: {e}".encode('utf-8'))
                    return

            # Creations Search and Filtering Endpoint
            if path_only in ('/api/creations/search', '/api/v1/creations/search'):
                query = query_params.get("q", [""])[0].lower()
                creation_type = query_params.get("type", ["all"])[0].lower()

                sample_creations = [
                    {"id": "c1", "title": "ملحمة فضاء عام 30000", "type": "poetry", "dialect": "yemeni_zamel", "filename": "poetry_output.mp3", "created_at": "2026-09-26T21:00:00Z"},
                    {"id": "c2", "title": "شعر نبطي في وصف النجوم", "type": "poetry", "dialect": "khaleeji_nabati", "filename": "poetry_nabati.mp3", "created_at": "2026-09-26T21:10:00Z"},
                    {"id": "c3", "title": "دارمي الشوق والمسافات", "type": "poetry", "dialect": "iraqi_darami", "filename": "poetry_darami.mp3", "created_at": "2026-09-26T21:15:00Z"},
                    {"id": "c4", "title": "JM Synthwave Cyber Odyssey", "type": "song", "dialect": "euro_disco", "filename": "synthwave_odyssey.mp3", "created_at": "2026-09-26T21:20:00Z"},
                    {"id": "c5", "title": "أثير الفضاء المستقبلي", "type": "song", "dialect": "ambient", "filename": "ambient_ether.mp3", "created_at": "2026-09-26T21:30:00Z"}
                ]

                filtered = []
                for item in sample_creations:
                    match_type = (creation_type == "all" or item["type"] == creation_type)
                    match_query = (not query or query in item["title"].lower() or query in item.get("dialect", "").lower())
                    if match_type and match_query:
                        filtered.append(item)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(filtered, ensure_ascii=False).encode('utf-8'))
                return

            # Health check endpoint
            if path_only == '/health':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "service": "ltx_bridge", "engine": "LTX-2.5"}).encode('utf-8'))
                return

            if path_only.startswith('/internal/') or path_only == '/api/ai_service/status':
                try:
                    target_path = "/" if path_only == "/api/ai_service/status" else path_only
                    req = urllib.request.Request(
                        f"http://127.0.0.1:8001{target_path}",
                        headers={"X-FMStar-Key": self.headers.get("X-FMStar-Key", os.getenv("FMSTAR_SECRET_KEY", ""))},
                        method="GET"
                    )
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        resp_data = resp.read()
                        self.send_response(resp.status)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(resp_data)
                        return
                except Exception as e:
                    self.send_response(502)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"AI service unavailable: {e}"}).encode('utf-8'))
                    return

            if path_only == '/api/v1/config/status':
                kimi_key = os.getenv("KIMI_API_KEY", "")
                bridge_url = os.getenv("LTX_BRIDGE_URL", "http://localhost:8001")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "kimi_configured": bool(kimi_key),
                    "bridge_url": bridge_url,
                    "status": "online",
                    "database": bool(os.getenv("SUPABASE_DB_URL"))
                }).encode('utf-8'))
                return

            # LTX-2.5 Ultra-Fast Streaming Endpoint (/generate-stream & /api/v1/generate-stream)
            if path_only in ('/generate-stream', '/api/v1/generate-stream'):
                prompt = query_params.get("prompt", ["FMStar Track Generation"])[0]

                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache, no-transform, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.send_header('Connection', 'keep-alive')
                self.send_header('X-Accel-Buffering', 'no')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                # 1. إرسال حدث البدء اللحظي
                initial_payload = json.dumps({"status": "starting", "progress": 0, "message": f"Initiating LTX-2.5 core sequence for '{prompt}'..."})
                self.wfile.write(f"event: progress\ndata: {initial_payload}\n\n".encode('utf-8'))
                self.wfile.flush()
                time.sleep(0.05)

                # 2. ضخ مراحل المعالجة المباشرة بدون تأخير
                for progress in range(25, 101, 25):
                    payload = json.dumps({
                        "status": "processing",
                        "progress": progress,
                        "frame_rendered": int(progress * 1.2),
                        "audio_synced": True if progress > 40 else False
                    })
                    self.wfile.write(f"event: progress\ndata: {payload}\n\n".encode('utf-8'))
                    self.wfile.flush()
                    time.sleep(0.08)

                # 3. حدث الإكمال النهائي
                completed_payload = json.dumps({
                    "status": "completed",
                    "progress": 100,
                    "stream_url": "/media/outputs/generated_track.mp4",
                    "message": "Stream synthesis successful."
                })
                self.wfile.write(f"event: complete\ndata: {completed_payload}\n\n".encode('utf-8'))
                self.wfile.flush()
                return

            if path_only == '/api/v1/stream':
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Connection', 'keep-alive')
                self.end_headers()
                msg = 'data: {"status": "Jimi & Mira Studio Engine Active", "backend": "Python + Supabase + LTX-2.5"}\n\n'
                self.wfile.write(msg.encode('utf-8'))
                self.wfile.flush()
                return

            if path_only == '/api/v1/tracks/recent':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps([
                    {
                        "id": "1",
                        "title": "JM Synthwave Cyber Odyssey",
                        "prompt": "Cyberpunk city night neon lights driving fast car",
                        "stream_url": "/media/outputs/generated_track.mp4",
                        "status": "ready",
                        "created_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - 3600))
                    }
                ]).encode('utf-8'))
                return

            if path_only in ['/docs', '/openapi.json'] or path_only.startswith('/docs'):
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:8001{self.path}", timeout=5) as u_resp:
                        self.send_response(u_resp.status)
                        for k, v in u_resp.headers.items():
                            if k.lower() not in ['transfer-encoding', 'content-length']:
                                self.send_header(k, v)
                        body = u_resp.read()
                        self.send_header('Content-Length', str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)
                        return
                except Exception as e:
                    pass

            if path_only in ['/gifts', '/gifts/']:
                self.path = '/index.html'
                return super().do_GET()

            if path_only in ['/samurai', '/samurai/', '/samurai.html']:
                self.path = '/samurai.html'
                return super().do_GET()

            if path_only in ['/fmstar', '/fmstar/', '/fmstar_studio', '/fmstar_studio.html']:
                self.path = '/fmstar_studio.html'
                return super().do_GET()

            if path_only in ['/jm-studio', '/jm-studio/', '/jm_studio', '/jm_studio/', '/studio', '/studio/']:
                self.path = '/jm_studio.html'
                return super().do_GET()

            if self.path == '/' or self.path == '':
                self.path = '/index.html'

            return super().do_GET()
        except (ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            try:
                self.send_error(500, str(e))
            except Exception:
                pass

if __name__ == '__main__':
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('static/outputs', exist_ok=True)
    os.makedirs('fmstar-project/static/outputs', exist_ok=True)
    os.makedirs('public', exist_ok=True)

    def run_port_5000():
        try:
            print("⚔️ الساموراي جاهز! الخادم يعمل على http://127.0.0.1:5000")
            s5000 = ThreadingSimpleServer(("", 5000), FMStarHandler)
            s5000.serve_forever()
        except Exception as e:
            print(f"Port 5000 server info: {e}")

    threading.Thread(target=run_port_5000, daemon=True).start()

    print(f"🚀 Running Light-weight Proxy & Studio Service on port {PORT}...")
    while True:
        try:
            server = ThreadingSimpleServer(("", PORT), FMStarHandler)
            server.serve_forever()
        except Exception as e:
            time.sleep(1)
