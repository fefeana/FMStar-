package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"fmstar/agents" // استدعاء مجلد الوكلاء اللي عملناه
	"github.com/jackc/pgx/v5/pgxpool"
)

// (احتفظ بباقي الـ Structs الخاصة بك: TrackMedia, Config, Application... كما هي)
type Config struct {
	SupabaseURL string
	BridgeURL   string
}
type Application struct {
	DBPool *pgxpool.Pool
	Config Config
}
type AIRequest struct {
	Prompt string `json:"prompt"`
	Type   string `json:"type"` // "song", "poetry", "long_story", "code"
}
type AIResponse struct {
	Result    string `json:"result"`
	ModelUsed string `json:"model_used"`
}

func getEnvOrDefault(key, fallback string) string {
	if val := os.Getenv(key); val != "" { return val }
	return fallback
}

func main() {
	// إعدادات قاعدة البيانات
	cfg := Config{
		SupabaseURL: os.Getenv("SUPABASE_DB_URL"),
		BridgeURL:   getEnvOrDefault("LTX_BRIDGE_URL", "http://localhost:8000"),
	}
	
	var dbPool *pgxpool.Pool
	if cfg.SupabaseURL != "" {
		pool, err := pgxpool.New(context.Background(), cfg.SupabaseURL)
		if err == nil { dbPool = pool; defer dbPool.Close() }
	}
	
	app := &Application{DBPool: dbPool, Config: cfg}

	// المسارات
	http.HandleFunc("/api/v1/generate", app.handleGenerateAI)
	http.HandleFunc("/health", app.handleHealth)

	port := getEnvOrDefault("PORT", "8080")
	log.Printf("⚡ FMStar running on port %s...\n", port)
	http.ListenAndServe(":"+port, nil)
}

// 🎻 قائد الأوركسترا (التوجيه الذكي)
func (app *Application) handleGenerateAI(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	
	if r.Method != http.MethodPost { http.Error(w, "Method not allowed", 405); return }

	var req AIRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil { http.Error(w, "Invalid request", 400); return }

	log.Printf("📥 طلب جديد: %s (النوع: %s)\n", req.Prompt, req.Type)

	var result string
	var err error
	modelUsed := ""

	// هنا بيتم توزيع المهام (Tasks) على الوكلاء
	switch req.Type {
	case "long_story", "album":
		log.Println("⏳ التوجيه إلى Kimi...")
		result, err = agents.AskKimi(req.Prompt)
		modelUsed = "Kimi"
	case "poetry", "song":
		log.Println("⏳ التوجيه إلى DeepSeek...")
		result, err = agents.AskDeepSeek(req.Prompt)
		modelUsed = "DeepSeek"
	case "code", "review":
		log.Println("⏳ التوجيه إلى Copilot...")
		result, err = agents.AskCopilot(req.Prompt)
		modelUsed = "Copilot"
	default:
		log.Println("⏳ التوجيه إلى Gemini...")
		result, err = agents.AskGemini(req.Prompt)
		modelUsed = "Gemini"
	}

	// لو حصل خطأ (أو مفتاح مش موجود)، بنحول لـ Gemini كخطة إنقاذ
	if err != nil {
		log.Printf("⚠️ %s فشل، جاري التحويل إلى Gemini...\n", modelUsed)
		result, err = agents.AskGemini(req.Prompt)
		modelUsed = "Gemini (Fallback)"
	}

	if err != nil {
		http.Error(w, "All models failed", 500)
		return
	}

	json.NewEncoder(w).Encode(AIResponse{Result: result, ModelUsed: modelUsed})
}

func (app *Application) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte(`{"status":"healthy"}`))
}
