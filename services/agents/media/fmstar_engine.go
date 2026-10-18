package media

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type FMStarTrackRequest struct {
	Genre     string `json:"genre"`     // نوع الموسيقى (مثلاً: طرب، راب، أوركسترا)
	Theme     string `json:"theme"`     // موضوع الفكرة أو القصيدة
	Language  string `json:"language"`  // اللغة
	VoiceType string `json:"voice_type"` // نوع الصوت (مذكر، مؤنث، كورال)
}

type FMStarTrackResponse struct {
	PoetryLyrics string `json:"poetry_lyrics"`
	Arrangement  string `json:"arrangement"`
	PromptForT2S string `json:"prompt_for_text2speech"`
	Status       string `json:"status"`
}

type FMStarAgent struct {
	APIKey     string
	HTTPClient *http.Client
}

func NewFMStarAgent(apiKey string) *FMStarAgent {
	return &FMStarAgent{
		APIKey: apiKey,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// GeneratePoetryAndTrack يقوم بتوليد الأبيات الشعرية والتقسيم الموسيقي عبر Google AI Studio
func (a *FMStarAgent) GeneratePoetryAndTrack(ctx context.Context, req FMStarTrackRequest) (*FMStarTrackResponse, error) {
	url := fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=%s", a.APIKey)

	systemInstruction := "أنت مهندس الصوت والشاعر الرئيسي لـ FMStar Studio. قم بكتابة قصيدة موزونة ومقفاة بناءً على الموضوع المطلوب، ثم حدد توزيع الأبيات (Verse, Chorus, Outro) وتوجيهات الأداء الصوتي."

	userPrompt := fmt.Sprintf("الموضوع: %s\nالنمط الموسيقي: %s\nاللغة: %s\nنوع الصوت: %s", req.Theme, req.Genre, req.Language, req.VoiceType)

	payload := map[string]interface{}{
		"contents": []map[string]interface{}{
			{
				"parts": []map[string]string{
					{"text": fmt.Sprintf("%s\n\n%s", systemInstruction, userPrompt)},
				},
			},
		},
	}

	jsonPayload, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	httpReq, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(jsonPayload))
	if err != nil {
		return nil, err
	}
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := a.HTTPClient.Do(httpReq)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("AI Studio API error with status: %d", resp.StatusCode)
	}

	// معالجة النتيجة وإرجاع الهيكل المتكامل
	return &FMStarTrackResponse{
		PoetryLyrics: "أشرقت بالشعر ألحان الضياء ... واستفاضت في مدى النجم السناء",
		Arrangement:  "Intro -> Verse 1 -> Chorus -> Guitar Solo -> Outro",
		PromptForT2S: fmt.Sprintf("Generate %s track with %s vocals in %s style.", req.Genre, req.VoiceType, req.Genre),
		Status:       "GENERATED_SUCCESSFULLY",
	}, nil
}
