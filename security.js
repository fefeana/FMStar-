// FMStar-AI-Studio - Frontend Security (HTML/JS)
// Made for Fefe - Web Security Top 5 Implementation
import DOMPurify from 'https://cdn.jsdelivr.net/npm/dompurify@3.0.8/dist/purify.min.js';

export const FMStarSecurity = {
  // 1. XSS Protection - لردود الـ AI
  sanitizeAIOutput(raw) {
    return DOMPurify.sanitize(raw, {
      ALLOWED_TAGS: ['b','i','em','strong','code','pre','br','p','ul','li'],
      ALLOWED_ATTR: []
    });
  },
  
  renderAIOutput(elementId, aiText) {
    const clean = this.sanitizeAIOutput(aiText);
    document.getElementById(elementId).innerHTML = clean;
  },

  // 2. IDOR Protection
  checkOwnership(resourceOwnerId) {
    const currentUser = JSON.parse(localStorage.getItem('fmstar_user') || '{}');
    if (resourceOwnerId !== currentUser.id) {
      console.warn('IDOR blocked for Fefe');
      throw new Error('403 - Not your FMStar project');
    }
    return true;
  },

  // 3. Secure storage
  saveProject(project) {
    this.checkOwnership(project.ownerId);
    const encrypted = btoa(JSON.stringify(project)); // استخدمي crypto حقيقي في الانتاج
    localStorage.setItem('fmstar_project_secure', encrypted);
  }
};

// CSP Meta injection
const meta = document.createElement('meta');
meta.httpEquiv = "Content-Security-Policy";
meta.content = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'";
document.head.appendChild(meta);
console.log('🛡️ FMStar Frontend secured for Fefe');
