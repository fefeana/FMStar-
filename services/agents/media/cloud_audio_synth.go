package media

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"bytes"
	"encoding/json"
)

// CloudAudioSynthesizer يتصل مباشرة بخدمات Google Cloud Audio Engine
type CloudAudioSynthesizer struct {
	GCPProjectID string
	APIKey       string
	HTTPClient   *http.Client
}

type TTSCloudRequest struct {
	Text         string `json:"text"`
	VoiceName    string `json:"voice_name"`    // مثل: ar-XA-Wavenet-B
	SpeakingRate float64 `json:"speaking_rate"` // سرعة الإلقاء
}

func NewCloudAudioSynthesizer(apiKey string, projectID string) *CloudAudioSynthesizer {
	return &CloudAudioSynthesizer{
		APIKey:       apiKey,
		GCPProjectID: projectID,
		HTTPClient:   &http.Client{},
	}
}

// SynthesizeAudioStream يحول النص المولد من القصيدة/الأغنية إلى تدفق صوتي سحابي فوري
func (s *CloudAudioSynthesizer) SynthesizeAudioStream(ctx context.Context, req TTSCloudRequest) ([]byte, error) {
	// الاستدعاء المباشر لـ Google Cloud Text-to-Speech API المدارة سحابياً
	endpoint := fmt.Sprintf("https://texttospeech.googleapis.com/v1/text:synthesize?key=%s", s.APIKey)

	payload := map[string]interface{}{
		"input": map[string]string{
			"text": req.Text,
		},
		"voice": map[string]string{
			"languageCode": "ar-XA",
			"name":         req.VoiceName,
		},
		"audioConfig": map[string]interface{}{
			"audioEncoding": "MP3",
			"speakingRate":  req.SpeakingRate,
		},
	}

	bodyBytes, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	httpReq, err := http.NewRequestWithContext(ctx, "POST", endpoint, bytes.NewBuffer(bodyBytes))
	if err != nil {
		return nil, err
	}
	httpReq.Header.Set("Content-Type", "application/json")

	resp, err := s.HTTPClient.Do(httpReq)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("GCP Cloud TTS Error (Status %d): %s", resp.StatusCode, string(respBody))
	}

	var gcpResp struct {
		AudioContent []byte `json:"audioContent"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&gcpResp); err != nil {
		return nil, err
	}

	return gcpResp.AudioContent, nil
}
