package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

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
		BridgeURL:   getEnvOrDefault("LTX_BRIDGE_URL", "http://localhost:8000"),
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
	http.HandleFunc("/api/v1/config/status", app.handleConfigStatus)
	http.HandleFunc("/api/v1/tracks", app.handleSaveTrack)
	http.HandleFunc("/api/v1/tracks/recent", app.handleGetRecentTracks)
	http.HandleFunc("/health", app.handleHealth)

	port := getEnvOrDefault("PORT", "8080")
	log.Printf("⚡ FMStar Studio Go Core running on port %s...", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
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
