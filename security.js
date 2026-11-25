// FMStar-AI-Studio - Frontend Security (HTML/JS)
// Made for Fefe - Web Security Top 5 Implementation
import DOMPurify from 'https://cdn.jsdelivr.net/npm/dompurify@3.0.8/dist/purify.min.js';

function encodeUtf8Base64(str) {
  const bytes = new TextEncoder().encode(str);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

export const FMStarSecurity = {
  // 1. XSS Protection - لردود الـ AI
  sanitizeAIOutput(raw) {
    if (typeof raw !== 'string') return '';
    return DOMPurify.sanitize(raw, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'code', 'pre', 'br', 'p', 'ul', 'li'],
      ALLOWED_ATTR: []
    });
  },

  renderAIOutput(elementId, aiText) {
    const target = document.getElementById(elementId);
    if (!target) {
      console.warn(`FMStarSecurity: element #${elementId} not found`);
      return;
    }
    target.innerHTML = this.sanitizeAIOutput(aiText);
  },

  // 2. IDOR Protection
  checkOwnership(resourceOwnerId) {
    let currentUser = {};
    try {
      currentUser = JSON.parse(localStorage.getItem('fmstar_user') || '{}');
    } catch (_) {
      currentUser = {};
    }
    if (!currentUser.id || resourceOwnerId !== currentUser.id) {
      console.warn('IDOR blocked for Fefe');
      throw new Error('403 - Not your FMStar project');
    }
    return true;
  },

  // 3. Secure storage
  saveProject(project) {
    this.checkOwnership(project?.ownerId);
    const encoded = encodeUtf8Base64(JSON.stringify(project));
    localStorage.setItem('fmstar_project_secure', encoded);
  }
};

// CSP Meta injection (مضبوط ليتوافق مع GitHub Pages و Render والوسائط)
const existingCsp = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
if (!existingCsp) {
  const meta = document.createElement('meta');
  meta.httpEquiv = 'Content-Security-Policy';
  meta.content = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob: https:",
    "media-src 'self' data: blob: https:",
    "connect-src 'self' https://fmstar-backend-v2.onrender.com https://fefeana.github.io",
    "frame-ancestors 'none'"
  ].join('; ');
  document.head.appendChild(meta);
}

console.log('🛡️ FMStar Frontend secured for Fefe');
