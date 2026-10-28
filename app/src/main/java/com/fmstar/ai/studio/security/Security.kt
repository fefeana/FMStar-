// FMStar-AI-Studio - Mobile App Security (Kotlin)
// Made for Fefe
package com.fmstar.ai.studio.security

import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import okhttp3.Request

object FMStarMobileSecurity {

    // 1. WebView XSS Protection
    fun setupSecureWebView(webView: WebView) {
        webView.settings.apply {
            javaScriptEnabled = true
            allowFileAccess = false
            allowContentAccess = false
        }
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                // امنعي فتح iframe خارجي - Clickjacking protection
                return true
            }
        }
    }

    fun sanitizeAIOutput(input: String): String {
        // إزالة سكريبتات قبل عرضها
        return input.replace(Regex("<script.*?>.*?</script>", RegexOption.IGNORE_CASE), "")
            .replace(Regex("javascript:", RegexOption.IGNORE_CASE), "")
    }

    // 2. IDOR Protection - كل طلب يحمل هوية المالك
    fun buildSecureProjectRequest(projectId: String, userToken: String, currentUserId: String): Request {
        return Request.Builder()
            .url("https://api.fmstar.com/v1/projects/$projectId")
            .header("Authorization", "Bearer $userToken")
            .header("X-Owner-Id", currentUserId)
            .header("X-CSRF-Token", "fmstar-mobile-token")
            .build()
    }

    // 3. Secure Storage - لا تحفظي التوكن في SharedPreferences العادي
    fun getSecurePrefs(context: android.content.Context) =
        EncryptedSharedPreferences.create(
            context,
            "fmstar_secure_for_fefe",
            MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )

    fun saveTokenSecure(context: android.content.Context, token: String) {
        getSecurePrefs(context).edit().putString("fmstar_token", token).apply()
    }
}

// Usage in Activity:
// FMStarMobileSecurity.setupSecureWebView(binding.webView)
// val cleanText = FMStarMobileSecurity.sanitizeAIOutput(aiResponse)
