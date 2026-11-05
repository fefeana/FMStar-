import React, { useState, useRef } from 'react';

interface StudioState {
  theme: string;
  genre: string;
  voiceName: string;
  isGenerating: boolean;
  lyrics: string;
  audioUrl: string | null;
  statusMessage: string;
}

export const FMStarStudio: React.FC = () => {
  const [state, setState] = useState<StudioState>({
    theme: '',
    genre: 'أوركسترا',
    voiceName: 'ar-XA-Wavenet-B',
    isGenerating: false,
    lyrics: '',
    audioUrl: null,
    statusMessage: 'الاستوديو جاهز لبدء العمل...'
  });

  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handleGenerateAndSynthesize = async () => {
    if (!state.theme) return;

    setState((prev) => ({
      ...prev,
      isGenerating: true,
      audioUrl: null,
      statusMessage: '1/2: جاري توليد الشعر وتقسيم اللحن عبر Gemini Engine...'
    }));

    try {
      // 1. توليد القصيدة والتراك
      const genResponse = await fetch('/api/v1/fmstar/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          theme: state.theme,
          genre: state.genre,
          language: 'ar',
          voice_type: 'مذكر'
        })
      });

      if (!genResponse.ok) throw new Error('فشل توليد النص الشعري');
      const genData = await genResponse.json();

      setState((prev) => ({
        ...prev,
        lyrics: genData.poetry_lyrics,
        statusMessage: '2/2: تحويل النص الشعري إلى صوت سحابي وتجهيز البث المباشر...'
      }));

      // 2. تحويل النص إلى صوت واستيعابه كتدفق (Blob URL)
      const speechResponse = await fetch('/api/v1/fmstar/synthesize-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: genData.poetry_lyrics,
          voice_name: state.voiceName,
          speaking_rate: 1.0
        })
      });

      if (!speechResponse.ok) throw new Error('فشل توليد الصوت السحابي');

      const audioBlob = await speechResponse.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      setState((prev) => ({
        ...prev,
        isGenerating: false,
        audioUrl: audioUrl,
        statusMessage: 'تم تجهيز الأغنية والصوت بنجاح! جاهز للإطلاق.'
      }));

      // تشغيل الصوت تلقائياً
      if (audioRef.current) {
        audioRef.current.load();
        audioRef.current.play();
      }

    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        isGenerating: false,
        statusMessage: `خطأ أثناء المعالجة: ${err.message}`
      }));
    }
  };

  return (
    <div style={{ padding: '24px', background: '#0a0a12', color: '#00ffcc', borderRadius: '16px', fontFamily: 'sans-serif', border: '1px solid #00ffcc33' }}>
      <h2>🎙️ FMStar Studio — Viviana Live Audio Console</h2>
      <p style={{ color: '#aaa', fontSize: '14px' }}>توليد الشعر، التوزيع الموسيقي، والبث الصوتي السحابي المباشر بدون مكتبات محليّة.</p>
      
      <hr style={{ borderColor: '#00ffcc33', margin: '16px 0' }} />

      <div style={{ display: 'grid', gap: '12px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '6px' }}>فكرة أو موضوع القصيدة:</label>
          <input
            type="text"
            value={state.theme}
            onChange={(e) => setState({ ...state, theme: e.target.value })}
            placeholder="مثال: الشبح الطائر فوق الأفق، سرعة البرق..."
            style={{ width: '100%', padding: '12px', background: '#121220', color: '#fff', border: '1px solid #00ffcc', borderRadius: '8px' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '6px' }}>النمط الموسيقي:</label>
            <select
              value={state.genre}
              onChange={(e) => setState({ ...state, genre: e.target.value })}
              style={{ width: '100%', padding: '12px', background: '#121220', color: '#fff', border: '1px solid #00ffcc', borderRadius: '8px' }}
            >
              <option value="أوركسترا">أوركسترا / ملحمي</option>
              <option value="طرب">طرب أصيل</option>
              <option value="راب">راب / هيپ هوپ</option>
              <option value="إلكترونيك">إلكترونيك / Ambient</option>
            </select>
          </div>

          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '6px' }}>الصوت السحابي (Cloud Voice):</label>
            <select
              value={state.voiceName}
              onChange={(e) => setState({ ...state, voiceName: e.target.value })}
              style={{ width: '100%', padding: '12px', background: '#121220', color: '#fff', border: '1px solid #00ffcc', borderRadius: '8px' }}
            >
              <option value="ar-XA-Wavenet-B">صوت رجالي (Wavenet HQ)</option>
              <option value="ar-XA-Wavenet-A">صوت نسائي (Wavenet HQ)</option>
              <option value="ar-XA-Standard-A">صوت قياسي (Standard)</option>
            </select>
          </div>
        </div>
      </div>

      <button
        onClick={handleGenerateAndSynthesize}
        disabled={state.isGenerating}
        style={{
          width: '100%',
          padding: '14px',
          marginTop: '20px',
          background: state.isGenerating ? '#444' : '#00ffcc',
          color: '#000',
          fontSize: '16px',
          fontWeight: 'bold',
          border: 'none',
          borderRadius: '8px',
          cursor: state.isGenerating ? 'not-allowed' : 'pointer'
        }}
      >
        {state.isGenerating ? '⌛ جاري التوليد والمعالجة السحابية...' : '🎼 توليد الأغنية وعرض المشغل الصوتي'}
      </button>

      {/* لوحة العرض والمشغل الصوتي المباشر */}
      <div style={{ marginTop: '24px', background: '#050508', padding: '16px', borderRadius: '12px', border: '1px solid #222' }}>
        <h4 style={{ margin: '0 0 10px 0', color: '#888' }}>الحالة: <span style={{ color: '#00ffcc' }}>{state.statusMessage}</span></h4>

        {state.lyrics && (
          <div style={{ margin: '16px 0', padding: '12px', background: '#0d0d18', borderRadius: '8px', borderLeft: '4px solid #00ffcc' }}>
            <h5 style={{ margin: '0 0 8px 0', color: '#00ffcc' }}>الأبيات الشعرية المباشرة:</h5>
            <pre style={{ whiteSpace: 'pre-wrap', color: '#fff', margin: 0, fontFamily: 'inherit' }}>{state.lyrics}</pre>
          </div>
        )}

        {state.audioUrl && (
          <div style={{ marginTop: '16px', textAlign: 'center' }}>
            <h5 style={{ color: '#00ffcc', marginBottom: '8px' }}>🎧 البث الصوتي السحابي الفوري:</h5>
            <audio ref={audioRef} controls src={state.audioUrl} style={{ width: '100%', outline: 'none' }}>
              متصفحك لا يدعم مشغل الصوت.
            </audio>
          </div>
        )}
      </div>
    </div>
  );
};
