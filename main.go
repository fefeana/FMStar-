package main

import (
	"archive/zip"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

type DownloadRequest struct {
	FilePaths []string `json:"file_paths"`
}

type Creation struct {
	ID       string `json:"id"`
	Title    string `json:"title"`
	Type     string `json:"type"`
	FilePath string `json:"file_path"`
}

var sampleCreations = []Creation{
	{ID: "1", Title: "قصيدة النجم", Type: "poetry", FilePath: "uploads/poetry1.txt"},
	{ID: "2", Title: "أغنية الأمل", Type: "song", FilePath: "uploads/song1.mp3"},
}

// Config - إعدادات بيئة تشغيل السيرفر والمفاتيح
type Config struct {
	SupabaseURL    string `json:"supabase_url,omitempty"`
	KimiAPIKey     string `json:"-"`
	GeminiAPIKey   string `json:"-"`
	DeepSeekAPIKey string `json:"-"`
	BridgeURL      string `json:"bridge_url"`
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

// AIRequest - هيكل الطلب القادم من الواجهة
type AIRequest struct {
	Prompt string `json:"prompt"`
}

// AIResponse - هيكل الرد
type AIResponse struct {
	Result    string `json:"result"`
	ModelUsed string `json:"model_used"`
}

func getEnvOrDefault(key, fallback string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return fallback
}

func main() {
	cfg := Config{
		SupabaseURL:    os.Getenv("SUPABASE_DB_URL"),
		KimiAPIKey:     os.Getenv("KIMI_API_KEY"),
		GeminiAPIKey:   os.Getenv("GEMINI_API_KEY"),
		DeepSeekAPIKey: os.Getenv("DEEPSEEK_API_KEY"),
		BridgeURL:      getEnvOrDefault("LTX_BRIDGE_URL", "http://localhost:8000"),
	}

	if cfg.GeminiAPIKey == "" {
		log.Println("⚠️ تنبيه: GEMINI_API_KEY غير محدد.")
	}
	if cfg.DeepSeekAPIKey == "" {
		log.Println("⚠️ تنبيه: DEEPSEEK_API_KEY غير محدد.")
	}

	ctx := context.Background()
	var dbPool *pgxpool.Pool

	if cfg.SupabaseURL != "" {
		config, err := pgxpool.ParseConfig(cfg.SupabaseURL)
		if err == nil {
			config.MaxConns = 15
			config.MinConns = 2
			config.MaxConnLifetime = 30 * time.Minute
			pool, err := pgxpool.NewWithConfig(ctx, config)
			if err == nil {
				dbPool = pool
				defer dbPool.Close()
				if err := dbPool.Ping(ctx); err != nil {
					log.Printf("⚠️ Supabase Ping failed: %v\n", err)
				} else {
					log.Println("🚀 Successfully connected to Supabase Database!")
				}
			}
		}
	}

	app := &Application{
		DBPool: dbPool,
		Config: cfg,
	}

	// Routes
	http.HandleFunc("/api/v1/generate", app.handleGenerateAI) // <--- المسار الجديد للـ AI
	http.HandleFunc("/api/v1/config/status", app.handleConfigStatus)
	http.HandleFunc("/api/v1/tracks", app.handleSaveTrack)
	http.HandleFunc("/api/v1/tracks/recent", app.handleGetRecentTracks)
	http.HandleFunc("/api/creations/download-zip", DownloadBatchZipHandler)
	http.HandleFunc("/api/creations/batch-download", DownloadBatchZipHandler)
	http.HandleFunc("/api/creations/search", SearchHandler)
	http.HandleFunc("/health", app.handleHealth)

	port := getEnvOrDefault("PORT", "8080")
	log.Printf("⚡ FMStar Studio Go Core running on port %s...\n", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

// =====================================================================
// 🧠 محركات الذكاء الاصطناعي (AI Agents)
// =====================================================================

// 1. Gemini Agent
func (app *Application) askGemini(prompt string) (string, error) {
	if app.Config.GeminiAPIKey == "" {
		return "", fmt.Errorf("Gemini API key missing")
	}
	url := "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + app.Config.GeminiAPIKey
	requestBody, _ := json.Marshal(map[string]interface{}{
		"contents": []map[string]interface{}{
			{"parts": []map[string]string{{"text": prompt}}},
		},
	})
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
	req.Header.Set("Content-Type", "application/json")
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil || resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("Gemini failed")
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)
	
	// Safely extract text
	candidates, ok := result["candidates"].([]interface{})
	if !ok || len(candidates) == 0 { return "", fmt.Errorf("invalid gemini response") }
	content := candidates[0].(map[string]interface{})["content"].(map[string]interface{})
	parts := content["parts"].([]interface{})
	return parts[0].(map[string]interface{})["text"].(string), nil
}

// 2. DeepSeek Agent
func (app *Application) askDeepSeek(prompt string) (string, error) {
	if app.Config.DeepSeekAPIKey == "" {
		return "", fmt.Errorf("DeepSeek API key missing")
	}
	url := "https://api.deepseek.com/chat/completions"
	requestBody, _ := json.Marshal(map[string]interface{}{
		"model": "deepseek-chat",
		"messages": []map[string]string{
			{"role": "system", "content": "أنت جيمي، مساعد ذكي في تطبيق FMStar."},
			{"role": "user", "content": prompt},
		},
	})
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+app.Config.DeepSeekAPIKey)
	client := &http.Client{Timeout: 15 * time.Second}
	resp, err := client.Do(req)
	if err != nil || resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("DeepSeek failed")
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)
	choices := result["choices"].([]interface{})
	message := choices[0].(map[string]interface{})["message"].(map[string]interface{})
	return message["content"].(string), nil
}

// 3. AI Orchestrator Handler (قائد الأوركسترا)
func (app *Application) handleGenerateAI(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req AIRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	log.Printf("📥 طلب جديد: %s\n", req.Prompt)

	// 1. تجربة Gemini
	result, err := app.askGemini(req.Prompt)
	modelUsed := "Gemini"

	// 2. في حالة فشل Gemini، التحول إلى DeepSeek
	if err != nil {
		log.Println("⚠️ Gemini فشل، جاري التحويل إلى DeepSeek...")
		result, err = app.askDeepSeek(req.Prompt)
		modelUsed = "DeepSeek"
	}

	if err != nil {
		http.Error(w, "All AI models failed", http.StatusInternalServerError)
		return
	}

	log.Printf("✅ تم الرد بواسطة: %s\n", modelUsed)
	json.NewEncoder(w).Encode(AIResponse{Result: result, ModelUsed: modelUsed})
}

// =====================================================================
// دوال الإدارة والتخزين (الأصلية الخاصة بك)
// =====================================================================

func (app *Application) handleConfigStatus(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"kimi_configured": app.Config.KimiAPIKey != "",
		"gemini_configured": app.Config.GeminiAPIKey != "",
		"deepseek_configured": app.Config.DeepSeekAPIKey != "",
		"bridge_url":      app.Config.BridgeURL,
		"status":          "online",
		"database":        app.DBPool != nil,
	})
}

func (app *Application) handleSaveTrack(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	if r.Method == http.MethodOptions { w.WriteHeader(http.StatusOK); return }
	if r.Method != http.MethodPost { http.Error(w, "Method not allowed", http.StatusMethodNotAllowed); return }

	var track TrackMedia
	if err := json.NewDecoder(r.Body).Decode(&track); err != nil { http.Error(w, err.Error(), http.StatusBadRequest); return }

	if app.DBPool == nil {
		track.ID = time.Now().Format("20060102150405")
		track.CreatedAt = time.Now()
		json.NewEncoder(w).Encode(map[string]interface{}{"status": "mock_saved", "message": "Database not connected", "data": track})
		return
	}

	query := `INSERT INTO studio_tracks (title, prompt, stream_url, status, created_at) VALUES ($1, $2, $3, $4, NOW()) RETURNING id, created_at;`
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()

	err := app.DBPool.QueryRow(ctx, query, track.Title, track.Prompt, track.StreamURL, track.Status).Scan(&track.ID, &track.CreatedAt)
	if err != nil { http.Error(w, "Failed to save track to Supabase", http.StatusInternalServerError); return }
	json.NewEncoder(w).Encode(map[string]interface{}{"status": "success", "track":  track})
}

func (app *Application) handleGetRecentTracks(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	if app.DBPool == nil { json.NewEncoder(w).Encode([]TrackMedia{}); return }

	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()
	rows, err := app.DBPool.Query(ctx, "SELECT id, title, prompt, stream_url, status, created_at FROM studio_tracks ORDER BY created_at DESC LIMIT 20")
	if err != nil { http.Error(w, "Database query error", http.StatusInternalServerError); return }
	defer rows.Close()

	var tracks []TrackMedia
	for rows.Next() {
		var t TrackMedia
		if err := rows.Scan(&t.ID, &t.Title, &t.Prompt, &t.StreamURL, &t.Status, &t.CreatedAt); err != nil { continue }
		tracks = append(tracks, t)
	}
	json.NewEncoder(w).Encode(tracks)
}

func (app *Application) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	dbStatus := "connected"
	if app.DBPool == nil || app.DBPool.Ping(r.Context()) != nil { dbStatus = "disconnected" }
	json.NewEncoder(w).Encode(map[string]string{"status": "healthy", "database": dbStatus, "framework": "Go bare-metal"})
}

func DownloadBatchZipHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
	if r.Method == http.MethodOptions { w.WriteHeader(http.StatusOK); return }
	if r.Method != http.MethodPost { http.Error(w, "Method not allowed", http.StatusMethodNotAllowed); return }

	var req DownloadRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || len(req.FilePaths) == 0 { http.Error(w, "Invalid request body", http.StatusBadRequest); return }

	w.Header().Set("Content-Type", "application/zip")
	w.Header().Set("Content-Disposition", "attachment; filename=\"fmstar_creations.zip\"")
	zipWriter := zip.NewWriter(w)
	defer zipWriter.Close()

	for _, path := range req.FilePaths {
		cleanPath := filepath.Clean(path)
		fileToZip, err := os.Open(cleanPath)
		if err != nil { continue }
		writer, err := zipWriter.Create(filepath.Base(cleanPath))
		if err != nil { fileToZip.Close(); continue }
		io.Copy(writer, fileToZip)
		fileToZip.Close()
	}
}

func SearchAndFilterCreations(query string, creationType string) []Creation {
	var filtered []Creation
	query = strings.ToLower(strings.TrimSpace(query))
	creationType = strings.ToLower(strings.TrimSpace(creationType))
	for _, item := range sampleCreations {
		matchesQuery := query == "" || strings.Contains(strings.ToLower(item.Title), query)
		matchesType := creationType == "" || creationType == "all" || strings.ToLower(item.Type) == creationType
		if matchesQuery && matchesType { filtered = append(filtered, item) }
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
