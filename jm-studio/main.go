package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	_ "github.com/lib/pq"
)

func initSupabaseDB() (*sql.DB, error) {
	dbURL := os.Getenv("SUPABASE_DB_URL")
	if dbURL == "" {
		return nil, fmt.Errorf("SUPABASE_DB_URL غير محدد")
	}

	db, err := sql.Open("postgres", dbURL)
	if err != nil {
		return nil, err
	}

	return db, db.Ping()
}

func sseStreamHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming unsupported", http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "data: %s\n\n", `{"status": "Jimi & Mira Studio Engine Active", "backend": "Go + Supabase"}`)
	flusher.Flush()
}

func main() {
	db, err := initSupabaseDB()
	if err != nil {
		log.Printf("⚠️ تنبيه الاتصال بـ Supabase: %v", err)
	} else {
		defer db.Close()
		log.Println("✅ تم الاتصال بقاعدة بيانات Supabase بنجاح!")
	}

	http.HandleFunc("/api/v1/stream", sseStreamHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("🚀 جيمي وميرا استوديو يعمل الآن على المنفذ %s", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("خطأ السيرفر: %v", err)
	}
}
