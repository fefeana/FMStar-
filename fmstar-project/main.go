package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"
)

func handleGenerateStreamFast(w http.ResponseWriter, r *http.Request) {
	// ضبط رؤوس Stream العالمية لتجاوز أي Proxy Buffer
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache, no-store, must-revalidate")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("X-Accel-Buffering", "no")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming unsupported", http.StatusInternalServerError)
		return
	}

	prompt := r.URL.Query().Get("prompt")
	if prompt == "" {
		prompt = "JM Studio Video"
	}

	// إعداد طلب HTTP سريع للجسر مع timeout مرن
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Minute)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "GET", fmt.Sprintf("http://127.0.0.1:5000/generate-stream?prompt=%s", prompt), nil)
	if err != nil {
		fmt.Fprintf(w, "data: {\"status\": \"error\", \"message\": \"%v\"}\n\n", err)
		flusher.Flush()
		return
	}

	// استخدام HTTP Client افتراضي مهيأ للـ Keep-Alive
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		fmt.Fprintf(w, "data: {\"status\": \"error\", \"message\": \"LTX Bridge Offline\"}\n\n", err)
		flusher.Flush()
		return
	}
	defer resp.Body.Close()

	// تمرير مجرى البيانات فوراً بتكتيك Zero-Copy Buffer
	buf := make([]byte, 1024)
	for {
		n, err := resp.Body.Read(buf)
		if n > 0 {
			w.Write(buf[:n])
			flusher.Flush() // تمرير البيانات فوراً إلى المتصفح بدون انتظار
		}
		if err != nil {
			if err == io.EOF {
				break
			}
			break
		}
	}
}

func main() {
	http.HandleFunc("/api/v1/generate-stream", handleGenerateStreamFast)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("⚡ High-Speed Engine Active on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
