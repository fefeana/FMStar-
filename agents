package agents

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

// =====================================================================
// 1. Gemini (سريع - للمهام العامة والتوجيه)
// =====================================================================
func AskGemini(prompt string) (string, error) {
	apiKey := os.Getenv("GEMINI_API_KEY")
	if apiKey == "" { return "", fmt.Errorf("Gemini API key missing") }
	
	url := "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + apiKey
	body, _ := json.Marshal(map[string]interface{}{"contents": []map[string]interface{}{{"parts": []map[string]string{{"text": prompt}}}}})
	
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	
	resp, err := (&http.Client{Timeout: 15 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 { return "", fmt.Errorf("gemini failed") }
	defer resp.Body.Close()
	
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	candidates, ok := result["candidates"].([]interface{})
	if !ok || len(candidates) == 0 { return "", fmt.Errorf("invalid gemini response") }
	content := candidates[0].(map[string]interface{})["content"].(map[string]interface{})
	return content["parts"].([]interface{})[0].(map[string]interface{})["text"].(string), nil
}

// =====================================================================
// 2. DeepSeek (دقيق - للأغاني، الشعر، والبرمجة)
// =====================================================================
func AskDeepSeek(prompt string) (string, error) {
	apiKey := os.Getenv("DEEPSEEK_API_KEY")
	if apiKey == "" { return "", fmt.Errorf("DeepSeek API key missing") }
	
	url := "https://api.deepseek.com/chat/completions"
	body, _ := json.Marshal(map[string]interface{}{
		"model": "deepseek-chat",
		"messages": []map[string]string{
			{"role": "system", "content": "أنت جيمي، مساعد ذكي في تطبيق FMStar. متخصص في الأغاني والشعر بدقة عالية."},
			{"role": "user", "content": prompt},
		},
	})
	
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)
	
	resp, err := (&http.Client{Timeout: 20 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 { return "", fmt.Errorf("deepseek failed") }
	defer resp.Body.Close()
	
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	choices := result["choices"].([]interface{})
	return choices[0].(map[string]interface{})["message"].(map[string]interface{})["content"].(string), nil
}

// =====================================================================
// 3. Kimi (سياق طويل - للألبومات والقصص)
// =====================================================================
func AskKimi(prompt string) (string, error) {
	apiKey := os.Getenv("KIMI_API_KEY")
	if apiKey == "" { return "", fmt.Errorf("Kimi API key missing") }
	
	url := "https://api.moonshot.cn/v1/chat/completions"
	body, _ := json.Marshal(map[string]interface{}{
		"model": "moonshot-v1-8k",
		"messages": []map[string]string{{"role": "user", "content": prompt}},
	})
	
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)
	
	resp, err := (&http.Client{Timeout: 30 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 { return "", fmt.Errorf("kimi failed") }
	defer resp.Body.Close()
	
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	choices := result["choices"].([]interface{})
	return choices[0].(map[string]interface{})["message"].(map[string]interface{})["content"].(string), nil
}

// =====================================================================
// 4. GitHub Copilot (عبر GitHub Models - للبرمجة والمراجعة)
// =====================================================================
func AskCopilot(prompt string) (string, error) {
	apiKey := os.Getenv("GITHUB_TOKEN") // توكن GitHub الخاص بك
	if apiKey == "" { return "", fmt.Errorf("GitHub Token missing") }
	
	url := "https://models.inference.ai.azure.com/chat/completions"
	body, _ := json.Marshal(map[string]interface{}{
		"model": "gpt-4o", // أو deepseek-r1
		"messages": []map[string]string{{"role": "user", "content": prompt}},
	})
	
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)
	
	resp, err := (&http.Client{Timeout: 20 * time.Second}).Do(req)
	if err != nil || resp.StatusCode != 200 { return "", fmt.Errorf("copilot failed") }
	defer resp.Body.Close()
	
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)
	choices := result["choices"].([]interface{})
	return choices[0].(map[string]interface{})["message"].(map[string]interface{})["content"].(string), nil
}
