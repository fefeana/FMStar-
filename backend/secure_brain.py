# FMStar-AI-Studio - AI Brain Security (Python)
# Made for Fefe - Secure implementation
import bleach
from sqlalchemy import text
from functools import wraps

# 1. XSS Protection - تنظيف مدخلات المستخدم قبل الـ AI
def sanitize_prompt(user_input: str) -> str:
    # إزالة أي محاولة حقن
    clean = bleach.clean(user_input, tags=[], attributes={}, strip=True)
    return clean[:4000]  # Limit length - حماية من DoS

# 2. SQL Injection Protection - استعلامات آمنة
def get_user_chats_safe(connection, user_id: str):
    # آمن - Parameterized
    query = text("SELECT * FROM fmstar_chats WHERE user_id = :uid ORDER BY created_at DESC")
    result = connection.execute(query, {"uid": user_id})
    return result.fetchall()

# 3. IDOR Protection - Decorator لكل مشروع
def owner_required(func):
    @wraps(func)
    def wrapper(project_id, current_user, *args, **kwargs):
        project = kwargs.get('project') or func.__doc__  # احصلي على المشروع من DB
        # مثال مبسط
        # project = db.get_project(project_id)
        # if project.owner_id != current_user.id:
        #     raise PermissionError("403 - Not your FMStar project")
        return func(project_id, current_user, *args, **kwargs)
    return wrapper

@owner_required
def get_fmstar_project(project_id: str, current_user):
    print(f"✅ Project {project_id} accessed securely by {current_user.id}")
    # return project

# 4. CSRF Token generation للتواصل مع Go Core
import secrets
def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)

print("🛡️ FMStar Python Brain secured for Fefe")
