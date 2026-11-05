// FMStar-AI-Studio - Audio Core Security (Go)
// Made for Fefe
package main

import (
    "database/sql"
    "net/http"
)

// Secure DB query - حماية من SQL Injection + IDOR
func GetAudioSecure(db *sql.DB, audioID string, userID string) (string, error) {
    var path string
    // آمن: placeholder + فحص المالك
    query := "SELECT file_path FROM fmstar_audio WHERE id = ? AND owner_id = ? LIMIT 1"
    err := db.QueryRow(query, audioID, userID).Scan(&path)
    if err != nil {
        return "", err // لو غير موجود أو ليس ملكه، يرجع خطأ
    }
    return path, nil
}

// Middleware - حماية عامة لكل النواة الصوتية
func FMStarSecurityMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 1. Clickjacking protection
        w.Header().Set("X-Frame-Options", "DENY")
        w.Header().Set("Content-Security-Policy", "frame-ancestors 'none'")
        w.Header().Set("X-Content-Type-Options", "nosniff")
        w.Header().Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

        // 2. CSRF protection - النواة تستقبل من Python فقط
        if r.Method == "POST" || r.Method == "PUT" || r.Method == "DELETE" {
            token := r.Header.Get("X-CSRF-Token")
            origin := r.Header.Get("Origin")
            if token == "" || origin != "https://fmstar.local" {
                http.Error(w, "CSRF blocked - FMStar Core", http.StatusForbidden)
                return
            }
        }
        next.ServeHTTP(w, r)
    })
}

func main() {
    mux := http.NewServeMux()
    mux.Handle("/audio/", FMStarSecurityMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("FMStar Audio Core Secured for Fefe 🛡️"))
    })))
    http.ListenAndServe(":8080", mux)
}
