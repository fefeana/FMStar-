package main

import (
	"archive/zip"
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"html"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

type GenerationRequest struct {
	Tool    string `json:"tool"`
	Dialect string `json:"dialect"`
	Prompt  string `json:"prompt"`
}

type rateLimitEntry struct {
	Count       int
	WindowStart time.Time
}

// هيكل لتخزين بيانات Rate Limiting بناءً على الـ IP
var (
	requestCounts = make(map[string]*rateLimitEntry)
	mu            sync.Mutex
	scriptTagRe   = regexp.MustCompile(`(?is)<\s*script[^>]*>.*?<\s*/\s*script\s*>|javascript:|on\w+\s*=`)
)

type DownloadRequest struct {
	FilePaths []string `json:"file_paths"`
}

type Creation struct {
	ID       string `json:"id"`
	Title    string `json:"title"`
	Type     string `json:"type"` // "poetry" or "song"
	FilePath string `json:"file_path"`
}

var sampleCreations = []Creation{
	{ID: "1", Title: "قصيدة النجم", Type: "poetry", FilePath: "uploads/poetry1.txt"},
	{ID: "2", Title: "أغنية الأمل", Type: "song", FilePath: "uploads/song1.mp3"},
}

// Config - إعدادات بيئة تشغيل السيرفر والمفاتيح
type Config struct {
	SupabaseURL string `json:"supabase_url,omitempty"`
	KimiAPIKey  string `json:"-"`
	BridgeURL   string `json:"bridge_url"`
}

// Application - حاوية الاتصالات والإعدادات
type Application struct {
	DBPool *pgxpool.Pool
	Config Config
}

// TrackMedia - إدارة تسجيل الوسائط والموسيقى المطبوعة
type TrackMedia struct {
	ID        string    `json:"id,omitempty"`
	Title     string    `json:"title"`
	Prompt    string    `json:"prompt"`
	StreamURL string    `json:"stream_url"`
	Status    string    `json:"status"`
	CreatedAt time.Time `json:"created_at"`
}

func getEnvOrDefault(key, fallback string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return fallback
}

func main() {
	cfg := Config{
		SupabaseURL: os.Getenv("SUPABASE_DB_URL"),
		KimiAPIKey:  os.Getenv("KIMI_API_KEY"),
		BridgeURL:   getEnvOrDefault("LTX_BRIDGE_URL", "http://localhost:8001"),
	}

	if cfg.KimiAPIKey == "" {
		log.Println("⚠️ تنبيه: KIMI_API_KEY غير محدد، سيعمل الاستوديو في الوضع الافتراضي (Fallback Mode).")
	} else {
		log.Println("🔑 تم تحميل KIMI_API_KEY بنجاح من متغيرات البيئة السحابية.")
	}

	ctx := context.Background()
	var dbPool *pgxpool.Pool

	if cfg.SupabaseURL != "" {
		config, err := pgxpool.ParseConfig(cfg.SupabaseURL)
		if err != nil {
			log.Printf("⚠️ Unable to parse Supabase URL: %v\n", err)
		} else {
			config.MaxConns = 15
			config.MinConns = 2
			config.MaxConnLifetime = 30 * time.Minute

			pool, err := pgxpool.NewWithConfig(ctx, config)
			if err != nil {
				log.Printf("⚠️ Unable to connect to Supabase: %v\n", err)
			} else {
				dbPool = pool
				defer dbPool.Close()
				if err := dbPool.Ping(ctx); err != nil {
					log.Printf("⚠️ Supabase Ping failed: %v\n", err)
				} else {
					log.Println("🚀 Successfully connected to Supabase Database!")
				}
			}
		}
	} else {
		log.Println("⚠️ SUPABASE_DB_URL not set. Running in local fallback mode.")
	}

	app := &Application{
		DBPool: dbPool,
		Config: cfg,
	}

	// Routes
	http.HandleFunc("/api/generate", HandleGenerate)
	http.HandleFunc("/api/auth/session", HandleSessionInit)
	http.HandleFunc("/api/v1/config/status", app.handleConfigStatus)
	http.HandleFunc("/api/v1/tracks", app.handleSaveTrack)
	http.HandleFunc("/api/v1/tracks/recent", app.handleGetRecentTracks)
	http.HandleFunc("/api/creations/download-zip", DownloadBatchZipHandler)
	http.HandleFunc("/api/creations/batch-download", DownloadBatchZipHandler)
	http.HandleFunc("/api/creations/search", SearchHandler)
	http.HandleFunc("/health", app.handleHealth)

	port := getEnvOrDefault("PORT", "8080")
	log.Printf("⚡ FMStar Studio Go Core running on port %s...", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

func generateSecureToken() string {
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil {
		return fmt.Sprintf("%d", time.Now().UnixNano())
	}
	return hex.EncodeToString(b)
}

func setStrictSessionCookie(w http.ResponseWriter, token string) {
	cookie := http.Cookie{
		Name:     "session_token",
		Value:    token,
		Path:     "/",
		HttpOnly: true,
		Secure:   true, // حصرياً عبر HTTPS
		SameSite: http.SameSiteStrictMode,
		MaxAge:   3600,
	}
	http.SetCookie(w, &cookie)
}

func sanitizeInput(input string) string {
	cleaned := scriptTagRe.ReplaceAllString(input, "")
	cleaned = html.EscapeString(strings.TrimSpace(cleaned))
	return cleaned
}

func extractClientIP(r *http.Request) string {
	if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
		parts := strings.Split(xff, ",")
		return strings.TrimSpace(parts[0])
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return host
}

func applyStrictCORS(w http.ResponseWriter, r *http.Request) {
	allowedOrigin := getEnvOrDefault("ALLOWED_ORIGIN", "https://mustafabushra.com")
	origin := r.Header.Get("Origin")
	if origin != "" && (origin == allowedOrigin || strings.HasSuffix(origin, ".run.app") || strings.HasSuffix(origin, ".trycloudflare.com")) {
		w.Header().Set("Access-Control-Allow-Origin", origin)
	} else {
		w.Header().Set("Access-Control-Allow-Origin", allowedOrigin)
	}
	w.Header().Set("Vary", "Origin")
	w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
	w.Header().Set("Access-Control-Allow-Credentials", "true")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.Header().Set("X-Frame-Options", "DENY")
}

// HandleSessionInit - إصدار كوكي الجلسة بمعايير صارمة
func HandleSessionInit(w http.ResponseWriter, r *http.Request) {
	applyStrictCORS(w, r)
	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusOK)
		return
	}
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	token := generateSecureToken()
	setStrictSessionCookie(w, token)

	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{
		"status": "authenticated",
	})
}

// HandleGenerate - حماية مسار توليد المحتوى (CORS + Rate Limiting + XSS Sanitization + Strict Cookie)
func HandleGenerate(w http.ResponseWriter, r *http.Request) {
	// 1. تقييد CORS ورؤوس الأمان
	applyStrictCORS(w, r)

	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusOK)
		return
	}

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 2. حماية Rate Limiting (10 طلبات في الدقيقة لكل مستخدم)
	ip := extractClientIP(r)
	now := time.Now()
	mu.Lock()
	entry, exists := requestCounts[ip]
	if !exists || now.Sub(entry.WindowStart) >= time.Minute {
		entry = &rateLimitEntry{Count: 1, WindowStart: now}
		requestCounts[ip] = entry
	} else {
		entry.Count++
	}
	count := entry.Count
	mu.Unlock()

	if count > 10 {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.WriteHeader(http.StatusTooManyRequests)
		json.NewEncoder(w).Encode(map[string]string{
			"error": "Too Many Requests, please slow down.",
		})
		return
	}

	// 3. قراءة البيانات والتحقق من صحتها مع تحديد الحد الأقصى للحجم
	r.Body = http.MaxBytesReader(w, r.Body, 64*1024)
	var req GenerationRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil || strings.TrimSpace(req.Prompt) == "" {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{
			"error": "Invalid input data",
		})
		return
	}

	// 4. تنظيف المدخلات لمنع حقن السكريبتات (XSS Prevention)
	safeTool := sanitizeInput(req.Tool)
	if safeTool == "" {
		safeTool = "أغنية / قصيدة"
	}
	safeDialect := sanitizeInput(req.Dialect)
	if safeDialect == "" {
		safeDialect = "سينمائي، ليلي"
	}
	safePrompt := sanitizeInput(req.Prompt)

	// 5. إصدار كوكي جلسة محمي إذا لم يكن موجوداً
	if _, cookieErr := r.Cookie("session_token"); cookieErr != nil {
		setStrictSessionCookie(w, generateSecureToken())
	}

	// 6. استجابة محرك Omni-Root Engine الآمن
	resultText := fmt.Sprintf(
		"✨ [تم التوليد بنجاح عبر استوديو FMStar | %s]:\n"+
			"━━━━━━━━━━━━━━━━━━━━━━\n"+
			"🎙️ الفكرة: %s\n\n"+
			"يا هاجس الشعر هات القاف من بدري\n"+
			"واسجِ المعاني على أوتار ألحاني\n"+
			"في ليلةٍ يزهر الإحساس في صدري\n"+
			"ويغرد الصوت في أثيرٍ وأوزانِ\n"+
			"━━━━━━━━━━━━━━━━━━━━━━\n"+
			"🎛️ التأثيرات والنمط: %s\n"+
			"🛡️ محمي عبر Omni-Root v4.2",
		safeTool, safePrompt, safeDialect,
	)

	response := map[string]interface{}{
		"status":  "success",
		"engine":  "Omni-Root v4.2",
		"tool":    safeTool,
		"dialect": safeDialect,
		"result":  resultText,
	}

	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(response)
}

// Endpoint لفحص حالة تكوين KIMI ومحرك البث
func (app *Application) handleConfigStatus(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	json.NewEncoder(w).Encode(map[string]interface{}{
		"kimi_configured": app.Config.KimiAPIKey != "",
		"bridge_url":      app.Config.BridgeURL,
		"status":          "online",
		"database":        app.DBPool != nil,
	})
}

// Endpoint لحفظ التراك في قاعدة بيانات Supabase
func (app *Application) handleSaveTrack(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusOK)
		return
	}

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var track TrackMedia
	if err := json.NewDecoder(r.Body).Decode(&track); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if app.DBPool == nil {
		track.ID = time.Now().Format("20060102150405")
		track.CreatedAt = time.Now()
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status":  "mock_saved",
			"message": "Database not connected, running in memory-only mode.",
			"data":    track,
		})
		return
	}

	query := `
		INSERT INTO studio_tracks (title, prompt, stream_url, status, created_at)
		VALUES ($1, $2, $3, $4, NOW())
		RETURNING id, created_at;
	`

	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()

	err := app.DBPool.QueryRow(ctx, query, track.Title, track.Prompt, track.StreamURL, track.Status).Scan(&track.ID, &track.CreatedAt)
	if err != nil {
		log.Printf("Supabase insert error: %v", err)
		http.Error(w, "Failed to save track to Supabase", http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "success",
		"track":  track,
	})
}

// Endpoint لاسترجاع أحدث التراكات
func (app *Application) handleGetRecentTracks(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if app.DBPool == nil {
		json.NewEncoder(w).Encode([]TrackMedia{})
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()

	rows, err := app.DBPool.Query(ctx, "SELECT id, title, prompt, stream_url, status, created_at FROM studio_tracks ORDER BY created_at DESC LIMIT 20")
	if err != nil {
		log.Printf("Query error: %v", err)
		http.Error(w, "Database query error", http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var tracks []TrackMedia
	for rows.Next() {
		var t TrackMedia
		if err := rows.Scan(&t.ID, &t.Title, &t.Prompt, &t.StreamURL, &t.Status, &t.CreatedAt); err != nil {
			continue
		}
		tracks = append(tracks, t)
	}

	json.NewEncoder(w).Encode(tracks)
}

// Health Check
func (app *Application) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	status := "healthy"
	dbStatus := "connected"

	if app.DBPool == nil || app.DBPool.Ping(r.Context()) != nil {
		dbStatus = "disconnected"
	}

	json.NewEncoder(w).Encode(map[string]string{
		"status":    status,
		"database":  dbStatus,
		"framework": "Go bare-metal",
	})
}

// 1. Endpoint: Zipping Multiple Creation Files
func DownloadBatchZipHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusOK)
		return
	}

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req DownloadRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || len(req.FilePaths) == 0 {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/zip")
	w.Header().Set("Content-Disposition", "attachment; filename=\"fmstar_creations.zip\"")

	zipWriter := zip.NewWriter(w)
	defer zipWriter.Close()

	for _, path := range req.FilePaths {
		cleanPath := filepath.Clean(path)
		fileToZip, err := os.Open(cleanPath)
		if err != nil {
			continue
		}

		writer, err := zipWriter.Create(filepath.Base(cleanPath))
		if err != nil {
			fileToZip.Close()
			continue
		}

		_, err = io.Copy(writer, fileToZip)
		fileToZip.Close()
	}
}

// 2. Function: Search & Filter Creations
func SearchAndFilterCreations(query string, creationType string) []Creation {
	var filtered []Creation
	query = strings.ToLower(strings.TrimSpace(query))
	creationType = strings.ToLower(strings.TrimSpace(creationType))

	for _, item := range sampleCreations {
		matchesQuery := query == "" || strings.Contains(strings.ToLower(item.Title), query)
		matchesType := creationType == "" || creationType == "all" || strings.ToLower(item.Type) == creationType

		if matchesQuery && matchesType {
			filtered = append(filtered, item)
		}
	}
	return filtered
}

func SearchHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	query := r.URL.Query().Get("q")
	cType := r.URL.Query().Get("type")

	results := SearchAndFilterCreations(query, cType)
	json.NewEncoder(w).Encode(results)
}
