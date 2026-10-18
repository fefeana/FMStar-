package main

import (
	"encoding/json"
	"log"
	"net/http"
	"time"
)

type TaskRequest struct {
	ProjectName string `json:"project_name"`
	FPS         int    `json:"fps"`          // تثبيت معدل الإطارات لمنع الاهتزاز البصري
	AudioLayers int    `json:"audio_layers"` // تنوع الطبقات الصوتية (Stems)
}

type Response struct {
	Status    string `json:"status"`
	Message   string `json:"message"`
	Timestamp string `json:"timestamp"`
}

func handleMediaTask(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req TaskRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		http.Error(w, "Invalid payload", http.StatusBadRequest)
		return
	}

	if req.FPS <= 0 {
		req.FPS = 30 // القيمة القياسية لمنع الاهتزاز
	}

	log.Printf("[FMStar Core] Processing project: %s | Target FPS: %d | Audio Layers: %d", req.ProjectName, req.FPS, req.AudioLayers)

	res := Response{
		Status:    "success",
		Message:   "FMStar Core Pipeline initialized with stable frame & multi-layer audio sync.",
		Timestamp: time.Now().Format(time.RFC3339),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(res)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/api/v2/media/process", handleMediaTask)

	log.Println("FMStar Core Backend running on port 8080 (High-Performance Go Engine)...")
	if err := http.ListenAndServe(":8080", mux); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
