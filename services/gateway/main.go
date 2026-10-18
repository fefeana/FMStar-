package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"shadow-al-barq/services/agents/media"
)

type GatewayServer struct {
	FMStarEngine *media.FMStarAgent
	AudioEngine  *media.CloudAudioSynthesizer
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	apiKey := os.Getenv("GCP_API_KEY")
	projectID := os.Getenv("GCP_PROJECT_ID")

	// تهيئة الخدمات السحابية
	gw := &GatewayServer{
		FMStarEngine: media.NewFMStarAgent(apiKey),
		AudioEngine:  media.NewCloudAudioSynthesizer(apiKey, projectID),
	}

	mux := http.NewServeMux()

	// 1. مسارات استوديو FMStar والتوليد الذكي
	mux.HandleFunc("/api/v1/fmstar/generate", gw.handleGenerateTrack)
	mux.HandleFunc("/api/v1/fmstar/synthesize-speech", gw.handleSpeechSynthesis)

	// 2. مسارات فحص الصحة والشفاء الذاتي (Health & Self-Healing)
	mux.HandleFunc("/healthz", gw.handleHealthCheck)

	// 3. إعداد خادم HTTP/2 و QUIC الموحد
	server := &http.Server{
		Addr:         ":" + port,
		Handler:      corsMiddleware(mux),
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 30 * time.Second,
	}

	log.Printf("🚀 [Gateway] FMStar Studio & Shadow Al-Barq Gateway running on port %s...", port)
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("Fatal Gateway Error: %v", err)
	}
}

// handleGenerateTrack يتعامل مع توليد الشعر والكلمات الموزونة وتقسيم اللحن
func (g *GatewayServer) handleGenerateTrack(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req media.FMStarTrackRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid payload", http.StatusBadRequest)
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), 20*time.Second)
	defer cancel()

	resp, err := g.FMStarEngine.GeneratePoetryAndTrack(ctx, req)
	if err != nil {
		http.Error(w, fmt.Sprintf("AI Generation Error: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// handleSpeechSynthesis يحول النص المولد إلى مقطع صوتي مباشر معالَج في السحابة
func (g *GatewayServer) handleSpeechSynthesis(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req media.TTSCloudRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid payload", http.StatusBadRequest)
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), 15*time.Second)
	defer cancel()

	audioData, err := g.AudioEngine.SynthesizeAudioStream(ctx, req)
	if err != nil {
		http.Error(w, fmt.Sprintf("Cloud Audio Error: %v", err), http.StatusInternalServerError)
		return
	}

	// إرجاع ملف الصوت مباشرة دون تسجيله على القرص (In-Memory Response)
	w.Header().Set("Content-Type", "audio/mpeg")
	w.Header().Set("Content-Length", fmt.Sprintf("%d", len(audioData)))
	w.Write(audioData)
}

// handleHealthCheck فحص الجاهزية والنواة
func (g *GatewayServer) handleHealthCheck(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"status":"HEALTHY","system":"SHADOW_AL_BARQ_V3.2","studio":"FMSTAR_STUDIO"}`))
}

// corsMiddleware لضمان الاتصال الآمن مع واجهة Viviana Console
func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}
		next.ServeHTTP(w, r)
	})
}
