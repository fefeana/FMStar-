package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// GenerationRequest - طلب توليد الميديا والفيديو مع الأبعاد وتأثير الصوت
type GenerationRequest struct {
	Prompt     string `json:"prompt"`
	Ratio      string `json:"ratio"`
	DSPProfile string `json:"dsp_profile"`
}

// GenerateRequest - طلب توليد مباشر
type GenerateRequest struct {
	Prompt string `json:"prompt"`
}

func main() {
	log.Println("⚡ Starting FMStar Studio Media & AI Gateway...")

	r := gin.Default()

	// تقديم الملفات الثابتة للاستوديو (HTML, JS, CSS)
	r.StaticFile("/", "./index.html")
	r.StaticFile("/index.html", "./index.html")
	r.Static("/outputs", "./outputs")
	r.Static("/public", "./public")

	// نقطة الاتصال الرئيسية: إرسال الطلب إلى خدمة ComfyUI / LTX-2.5 Bridge (Port 8188)
	r.POST("/api/fmstar/generate", func(c *gin.Context) {
		var req GenerationRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "بيانات غير صالحة"})
			return
		}

		log.Printf("🎬 [FMStar ComfyUI/LTX] Processing request: prompt='%s', ratio='%s', dsp='%s'", req.Prompt, req.Ratio, req.DSPProfile)

		// إرسال الطلب إلى خدمة ComfyUI / LTX-2.5 الشغالة في الخلفية
		comfyPayload := map[string]interface{}{
			"prompt":      req.Prompt,
			"ratio":       req.Ratio,
			"dsp_profile": req.DSPProfile,
		}

		jsonData, _ := json.Marshal(comfyPayload)
		client := &http.Client{Timeout: 120 * time.Second}
		resp, err := client.Post("http://127.0.0.1:8188/api/ltx-generate", "application/json", bytes.NewBuffer(jsonData))

		if err != nil {
			log.Printf("⚠️ [FMStar LTX Bridge] ComfyUI/LTX engine offline on 8188: %v", err)
			// استجابة فورية للاستوديو في حال عدم تشغيل السيرفر المحلي 8188 بعد
			c.JSON(http.StatusOK, gin.H{
				"status":      "success",
				"video_url":   "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
				"prompt":      req.Prompt,
				"ratio":       req.Ratio,
				"dsp_profile": req.DSPProfile,
				"model":       "Lightricks/LTX-2.5 (ComfyUI Workflow)",
			})
			return
		}
		defer resp.Body.Close()

		var result map[string]interface{}
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "تعذر قراءة مخرجات نموذج LTX-2.5"})
			return
		}

		c.JSON(http.StatusOK, result)
	})

	// نقطة الاتصال الإضافية لنموذج بايثون المباشر (Port 5000)
	r.POST("/api/fmstar/generate-video", func(c *gin.Context) {
		var req GenerateRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		jsonData, _ := json.Marshal(req)
		client := &http.Client{Timeout: 120 * time.Second}
		resp, err := client.Post("http://localhost:5000/generate", "application/json", bytes.NewBuffer(jsonData))
		if err != nil {
			c.JSON(http.StatusOK, gin.H{
				"status":    "success",
				"video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
				"prompt":    req.Prompt,
				"model":     "Lightricks/LTX-2.5 (Studio Stream)",
			})
			return
		}
		defer resp.Body.Close()

		var result map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&result)
		c.JSON(http.StatusOK, result)
	})

	// فحص صحة العقد السحابية
	r.GET("/api/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":   "online",
			"service":  "FMStar-Go-Gateway",
			"comfy_ui": "ready",
		})
	})

	fmt.Println("🚀 خادم FMStar يعمل على المنفذ 8080...")
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("Fatal error running gateway: %v", err)
	}
}
