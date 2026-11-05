'use client';
import { useState } from 'react';

export default function SongsPage() {
  const [style, setStyle] = useState('خليجي / طرب');
  const [lyrics, setLyrics] = useState('');
  const [loading, setLoading] = useState(false);

  const generateSong = async () => {
    setLoading(true);
    setTimeout(() => {
      setLyrics(
        `[Verse 1]\nصوت الموسيقى يعزف على الأوتار\nفي استوديو الفن ونجمة إف إم ستار\n\n[Chorus]\nيا ليل يا عين الإبداع يكمل هنا\nصنعنا ألحان تلامس روحنا`
      );
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-6 md:p-12">
      <div className="max-w-3xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-amber-400 flex items-center gap-2">
          🎙️ استوديو الأغاني والألحان
        </h1>
        <p className="text-neutral-400">
          تنسيق كلمات الأغاني والألحان الذكية للإنتاج الموسيقي.
        </p>

        <div>
          <label className="block text-sm text-neutral-400 mb-1">النمط الموسيقي:</label>
          <select
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            className="w-full p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-white focus:border-amber-500"
          >
            <option value="خليجي / طرب">طرب خليجي أصيل</option>
            <option value="عربي شرقي">شرقي / أوركسترا</option>
            <option value="Pop / Modern">باب حديث / Pop</option>
            <option value="Hip Hop / Rap">هيب هوب / راب</option>
          </select>
        </div>

        <button
          onClick={generateSong}
          disabled={loading}
          className="w-full py-3 rounded-xl bg-amber-500 text-neutral-950 font-bold hover:bg-amber-400 transition"
        >
          {loading ? 'جاري تأليف وتنسيق الأغنية...' : 'توليد كلمات الأغنية 🎵'}
        </button>

        {lyrics && (
          <div className="p-6 rounded-xl bg-neutral-900 border border-amber-500/30 whitespace-pre-line text-lg text-amber-100 font-mono">
            {lyrics}
          </div>
        )}
      </div>
    </div>
  );
}
