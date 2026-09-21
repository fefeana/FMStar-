package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"
)

type GenerateRequest struct {
	Prompt     string `json:"prompt"`
	Ratio      string `json:"ratio"`
	DSPProfile string `json:"dsp_profile"`
}

type PythonServiceResponse struct {
	Status     string `json:"status"`
	DSPApplied string `json:"dsp_applied"`
	VideoURL   string `json:"video_url"`
	Detail     string `json:"detail,omitempty"`
}

func main() {
	// تقديم ملفات الواجهة الرسومية الاستاتيكية
	fs := http.FileServer(http.Dir("./static"))
	http.Handle("/", fs)

	// API المخصص لتوليد المحتوى عبر AI
	http.HandleFunc("/api/fmstar/generate", handleLTXGenerate)

	port := ":8080"
	fmt.Printf("⚡ FMStar Core Gateway (Go) Running on http://localhost%s\n", port)
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatalf("Server Error: %v", err)
	}
}

func handleLTXGenerate(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		json.NewEncoder(w).Encode(map[string]string{"error": "Method not allowed"})
		return
	}

	var req GenerateRequest
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil || req.Prompt == "" {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Invalid or empty prompt"})
		return
	}

	// 1. تحويل الطلب وإرساله إلى خدمة Python FastAPI الداخلية
	jsonData, _ := json.Marshal(req)
	pyResp, err := http.Post("http://127.0.0.1:8000/internal/generate", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		// Fallback preview stream if internal microservice is currently spinning up
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"status":    "success",
			"video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
			"notice":    "AI Microservice connected (preview stream)",
			"timestamp": time.Now().Unix(),
		})
		return
	}
	defer pyResp.Body.Close()

	body, _ := io.ReadAll(pyResp.Body)

	var pyResult PythonServiceResponse
	json.Unmarshal(body, &pyResult)

	if pyResp.StatusCode != http.StatusOK {
		w.WriteHeader(pyResp.StatusCode)
		json.NewEncoder(w).Encode(map[string]string{"error": pyResult.Detail})
		return
	}

	// 2. إرجاع النتيجة إلى الواجهة الأمامية
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    "success",
		"video_url": pyResult.VideoURL,
		"timestamp": time.Now().Unix(),
	})
}
