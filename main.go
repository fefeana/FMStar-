package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

// =====================================================================
// الهياكل الأساسية
// =====================================================================
type AIRequest struct {
	Prompt string `json:"prompt"`
	Type   string `json:"type"` // "song", "poetry", "album", "code", "general"
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

// =====================================================================
// التشغيل الرئيسي
// =====================================================================
func main() {
	http.HandleFunc("/api/v1/generate", handleGenerateAI)
	http.HandleFunc("/health", handleHealth)

	port := getEnvOrDefault("PORT", "8080")
	fmt.Printf("⚡ FMStar Orchestrator running on port %s...\n", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatal(err)
	}
}

// =====================================================================
// 🎻 قائد الأوركسترا (التوجيه الذكي)
// =====================================================================
func handleGenerateAI(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusOK)
		return
	}
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req AIRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	log.Printf("📥 طلب جديد: %s (النوع: %s)\n", req.Prompt, req.Type)

	var result string
	var err error
	modelUsed := ""

	// التوجيه (Routing) - هنا بنوزع الشغل على الفريق
	switch req.Type {
	case "long_story", "album":
		log.Println("⏳ التوجيه إلى Kimi (للسياق الطويل)...")
		result, err = AskKimi(req.Prompt)
		modelUsed = "Kimi"

	case "code", "logic":
		log.Println("⏳ التوجيه إلى Copilot...")
		result, err = AskCopilot(req.Prompt)
		modelUsed = "Copilot"

	case "song", "poetry":
		log.Println("⏳ التوجيه إلى DeepSeek...")
		result, err = AskDeepSeek(req.Prompt)
		modelUsed = "DeepSeek"

	default:
		log.Println("⏳ التوجيه إلى Gemini...")
		result, err = AskGemini(req.Prompt)
		modelUsed = "Gemini"
	}

	// لو أي محرك فشل، بنروح لـ Gemini كخطة إنقاذ
	if err != nil {
		log.Printf("⚠️ %s فشل، جاري التحويل إلى Gemini...\n", modelUsed)
		result, err = AskGemini(req.Prompt)
		modelUsed = "Gemini (Fallback)"
	}

	if err != nil {
		log.Println("❌ جميع المحركات فشلت.")
		http.Error(w, `{"error": "All AI models failed"}`, http.StatusInternalServerError)
		return
	}

	log.Printf("✅ تم الرد بنجاح بواسطة: %s\n", modelUsed)
	json.NewEncoder(w).Encode(AIResponse{Result: result, ModelUsed: modelUsed})
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(`{"status": "healthy"}`))
}

// =====================================================================
// 🧠 محركات الذكاء الاصطناعي (AI Engines)
// =====================================================================

// 1. Kimi (عبر OpenRouter - للقصص والألبومات)
func AskKimi(prompt string) (string, error) {
	apiKey := os.Getenv("OPENROUTER_API_KEY")
	if apiKey == "" {
		return "", fmt.Errorf("OpenRouter API key missing")
	}

	url := "https://openrouter.ai/api/v1/chat/completions"
	body, _ := json.Marshal(map[string]interface{}{
		// موديل Kimi عبر OpenRouter (يدعم السياقات الطويلة)
		"model": "moonshotai/moonshot-v1-8k", 
		"messages": []map[string]string{
			{"role": "system", "content": "أنت ميرا، مساعدة ذكية في تطبيق FMStar. متخصصة في القصص الطويلة والألبومات المتكاملة."},
			{"role": "user", "content": prompt},
		},
	})

	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("HTTP-Referer", "https://fmstar.ai")
	req.Header.Set("X-Title", "FMStar Studio")

	resp, err := (&http.Client{Timeout: 30 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 {
		return "", fmt.Errorf("kimi/openrouter failed")
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	choices, ok := result["choices"].([]interface{})
	if !ok || len(choices) == 0 {
		return "", fmt.Errorf("invalid openrouter response")
	}
	return choices[0].(map[string]interface{})["message"].(map[string]interface{})["content"].(string), nil
}

// 2. DeepSeek (عبر OpenRouter - للأغاني والشعر)
func AskDeepSeek(prompt string) (string, error) {
	apiKey := os.Getenv("OPENROUTER_API_KEY")
	if apiKey == "" {
		return "", fmt.Errorf("OpenRouter API key missing")
	}

	url := "https://openrouter.ai/api/v1/chat/completions"
	body, _ := json.Marshal(map[string]interface{}{
		"model": "deepseek/deepseek-chat",
		"messages": []map[string]string{
			{"role": "system", "content": "أنت جيمي، مساعد ذكي في تطبيق FMStar. متخصص في الأغاني والشعر بدقة عالية."},
			{"role": "user", "content": prompt},
		},
	})

	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("HTTP-Referer", "https://fmstar.ai")
	req.Header.Set("X-Title", "FMStar Studio")

	resp, err := (&http.Client{Timeout: 20 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 {
		return "", fmt.Errorf("deepseek/openrouter failed")
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	choices, ok := result["choices"].([]interface{})
	if !ok || len(choices) == 0 {
		return "", fmt.Errorf("invalid openrouter response")
	}
	return choices[0].(map[string]interface{})["message"].(map[string]interface{})["content"].(string), nil
}

// 3. Copilot (عبر GitHub Models - للبرمجة والمنطق)
func AskCopilot(prompt string) (string, error) {
	apiKey := os.Getenv("GITHUB_TOKEN")
	if apiKey == "" {
		return "", fmt.Errorf("GitHub Token missing")
	}

	url := "https://models.inference.ai.azure.com/chat/completions"
	body, _ := json.Marshal(map[string]interface{}{
		"model": "gpt-4o",
		"messages": []map[string]string{
			{"role": "system", "content": "أنت مساعد برمجي ذكي في تطبيق FMStar."},
			{"role": "user", "content": prompt},
		},
	})

	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	resp, err := (&http.Client{Timeout: 20 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 {
		return "", fmt.Errorf("copilot failed")
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	choices, ok := result["choices"].([]interface{})
	if !ok || len(choices) == 0 {
		return "", fmt.Errorf("invalid copilot response")
	}
	return choices[0].(map[string]interface{})["message"].(map[string]interface{})["content"].(string), nil
}

// 4. Gemini (الخيار الأساسي السريع)
func AskGemini(prompt string) (string, error) {
	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" {
		return "", fmt.Errorf("Gemini API key missing")
	}

	url := "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + apiKey
	body, _ := json.Marshal(map[string]interface{}{
		"contents": []map[string]interface{}{
			{"parts": []map[string]string{{"text": prompt}}},
		},
	})

	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")

	resp, err := (&http.Client{Timeout: 15 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 {
		return "", fmt.Errorf("gemini failed")
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)

	candidates, ok := result["candidates"].([]interface{})
	if !ok || len(candidates) == 0 {
		return "", fmt.Errorf("invalid gemini response")
	}
	content := candidates[0].(map[string]interface{})["content"].(map[string]interface{})
	return content["parts"].([]interface{})[0].(map[string]interface{})["text"].(string), nil
}
