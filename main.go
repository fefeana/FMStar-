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

type Config struct {
	SupabaseURL    string
	KimiAPIKey     string
	GeminiAPIKey   string
	DeepSeekAPIKey string
	BridgeURL      string
}

type Application struct {
	DBPool *pgxpool.Pool
	Config Config
}

type TrackMedia struct {
	ID        string    `json:"id,omitempty"`
	Title     string    `json:"title"`
	Prompt    string    `json:"prompt"`
	StreamURL string    `json:"stream_url"`
	Status    string    `json:"status"`
	CreatedAt time.Time `json:"created_at"`
}

type AIRequest struct {
	Prompt string `json:"prompt"`
	Type   string `json:"type"` // "song", "poetry", "long_story"
}

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

	ctx := context.Background()
	var dbPool *pgxpool.Pool

	if cfg.SupabaseURL != "" {
		config, err := pgxpool.ParseConfig(cfg.SupabaseURL)
		if err == nil {
			pool, err := pgxpool.NewWithConfig(ctx, config)
			if err == nil {
				dbPool = pool
				defer dbPool.Close()
				dbPool.Ping(ctx) // فحص الاتصال
			}
		}
	}

	app := &Application{DBPool: dbPool, Config: cfg}

	// Routes
	http.HandleFunc("/api/v1/generate", app.handleGenerateAI)
	http.HandleFunc("/api/v1/config/status", app.handleConfigStatus)
	http.HandleFunc("/api/v1/tracks", app.handleSaveTrack)
	http.HandleFunc("/api/v1/tracks/recent", app.handleGetRecentTracks)
	http.HandleFunc("/api/creations/download-zip", DownloadBatchZipHandler)
	http.HandleFunc("/health", app.handleHealth)

	port := getEnvOrDefault("PORT", "8080")
	log.Printf("⚡ FMStar Orchestrator running on port %s...\n", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

// =====================================================================
// 🧠 محركات الذكاء الاصطناعي (The Orchestra)
// =====================================================================

// 1. Gemini
func (app *Application) askGemini(prompt string) (string, error) {
	if app.Config.GeminiAPIKey == "" { return "", fmt.Errorf("no gemini key") }
	url := "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + app.Config.GeminiAPIKey
	body, _ := json.Marshal(map[string]interface{}{"contents": []map[string]interface{}{{"parts": []map[string]string{{"text": prompt}}}}})
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	resp, err := (&http.Client{Timeout: 10 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 { return "", fmt.Errorf("gemini failed") }
	defer resp.Body.Close()
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result["candidates"].([]interface{})[0].(map[string]interface{})["content"].(map[string]interface{})["parts"].([]interface{})[0].(map[string]interface{})["text"].(string), nil
}

// 2. DeepSeek
func (app *Application) askDeepSeek(prompt string) (string, error) {
	if app.Config.DeepSeekAPIKey == "" { return "", fmt.Errorf("no deepseek key") }
	url := "https://api.deepseek.com/chat/completions"
	body, _ := json.Marshal(map[string]interface{}{
		"model": "deepseek-chat",
		"messages": []map[string]string{{"role": "user", "content": prompt}},
	})
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+app.Config.DeepSeekAPIKey)
	resp, err := (&http.Client{Timeout: 15 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 { return "", fmt.Errorf("deepseek failed") }
	defer resp.Body.Close()
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result["choices"].([]interface{})[0].(map[string]interface{})["message"].(map[string]interface{})["content"].(string), nil
}

// 3. Kimi
func (app *Application) askKimi(prompt string) (string, error) {
	if app.Config.KimiAPIKey == "" { return "", fmt.Errorf("no kimi key") }
	url := "https://api.moonshot.cn/v1/chat/completions"
	body, _ := json.Marshal(map[string]interface{}{
		"model": "moonshot-v1-8k",
		"messages": []map[string]string{{"role": "user", "content": prompt}},
	})
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+app.Config.KimiAPIKey)
	resp, err := (&http.Client{Timeout: 20 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 { return "", fmt.Errorf("kimi failed") }
	defer resp.Body.Close()
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	return result["choices"].([]interface{})[0].(map[string]interface{})["message"].(map[string]interface{})["content"].(string), nil
}

// 🎻 قائد الأوركسترا (Orchestrator)
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

	var result string
	var err error
	modelUsed := ""

	// التوجيه الذكي (بيشتغل حتى لو المفاتيح ناقصة)
	if req.Type == "long_story" || req.Type == "album" {
		result, err = app.askKimi(req.Prompt)
		modelUsed = "Kimi"
		if err != nil { 
			result, err = app.askDeepSeek(req.Prompt) 
			modelUsed = "DeepSeek"
			if err != nil {
				result, err = app.askGemini(req.Prompt) 
				modelUsed = "Gemini"
			}
		}
	} else if req.Type == "poetry" || req.Type == "song" {
		result, err = app.askDeepSeek(req.Prompt)
		modelUsed = "DeepSeek"
		if err != nil { 
			result, err = app.askGemini(req.Prompt) 
			modelUsed = "Gemini"
		}
	} else {
		result, err = app.askGemini(req.Prompt)
		modelUsed = "Gemini"
		if err != nil { 
			result, err = app.askDeepSeek(req.Prompt) 
			modelUsed = "DeepSeek"
		}
	}

	if err != nil {
		log.Println("❌ جميع المحركات فشلت أو المفاتيح غير متوفرة.")
		http.Error(w, "All AI models failed or missing keys", http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(AIResponse{Result: result, ModelUsed: modelUsed})
}

// =====================================================================
// دوال الإدارة (بقية الكود الخاص بك)
// =====================================================================
func (app *Application) handleConfigStatus(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"kimi_configured": app.Config.KimiAPIKey != "",
		"gemini_configured": app.Config.GeminiAPIKey != "",
		"deepseek_configured": app.Config.DeepSeekAPIKey != "",
		"database": app.DBPool != nil,
	})
}

func (app *Application) handleSaveTrack(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	if r.Method != http.MethodPost { http.Error(w, "Method not allowed", http.StatusMethodNotAllowed); return }
	var track TrackMedia
	json.NewDecoder(r.Body).Decode(&track)
	if app.DBPool == nil { http.Error(w, "No DB", http.StatusInternalServerError); return }
	
	query := `INSERT INTO studio_tracks (title, prompt, stream_url, status, created_at) VALUES ($1, $2, $3, $4, NOW()) RETURNING id, created_at;`
	err := app.DBPool.QueryRow(r.Context(), query, track.Title, track.Prompt, track.StreamURL, track.Status).Scan(&track.ID, &track.CreatedAt)
	if err != nil { http.Error(w, "Failed", http.StatusInternalServerError); return }
	json.NewEncoder(w).Encode(map[string]interface{}{"status": "success", "track": track})
}

func (app *Application) handleGetRecentTracks(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	if app.DBPool == nil { json.NewEncoder(w).Encode([]TrackMedia{}); return }
	rows, _ := app.DBPool.Query(r.Context(), "SELECT id, title, prompt, stream_url, status, created_at FROM studio_tracks ORDER BY created_at DESC LIMIT 20")
	defer rows.Close()
	var tracks []TrackMedia
	for rows.Next() { var t TrackMedia; rows.Scan(&t.ID, &t.Title, &t.Prompt, &t.StreamURL, &t.Status, &t.CreatedAt); tracks = append(tracks, t) }
	json.NewEncoder(w).Encode(tracks)
}

func (app *Application) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	dbStatus := "connected"
	if app.DBPool == nil || app.DBPool.Ping(r.Context()) != nil { dbStatus = "disconnected" }
	json.NewEncoder(w).Encode(map[string]string{"status": "healthy", "database": dbStatus})
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
