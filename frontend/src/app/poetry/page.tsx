'use client';
import { useState } from 'react';

export default function PoetryPage() {
  const [topic, setTopic] = useState('');
  const [meter, setMeter] = useState('الطويل');
  const [rhyme, setRhyme] = useState('مرفوعة (الراء)');
  const [poem, setPoem] = useState('');
  const [loading, setLoading] = useState(false);

  const generatePoem = async () => {
    setLoading(true);
    setTimeout(() => {
      setPoem(
        `يا فخر إف إم ستار والابداعُ ... في واحة الشعر للأبيات إبداعُ\nنظمتُ قافيةً تزهو برونقها ... كأنها النجم في العلياءِ تلماعُ`
      );
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-6 md:p-12">
      <div className="max-w-3xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-amber-400 flex items-center gap-2">
          🖋️ قسم الشعر والأدب الموزون
        </h1>
        <p className="text-neutral-400">
          توليد قصائد موزونة بالذكاء الاصطناعي مع تحديد البحور والقوافي.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-neutral-400 mb-1">اختر البحر الشعري:</label>
            <select
              value={meter}
              onChange={(e) => setMeter(e.target.value)}
              className="w-full p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-white focus:border-amber-500"
            >
              <option value="الطويل">بحر الطويل</option>
              <option value="الكامل">بحر الكامل</option>
              <option value="البسيط">بحر البسيط</option>
              <option value="الخفيف">بحر الخفيف</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-neutral-400 mb-1">نوع القافية:</label>
            <input
              type="text"
              value={rhyme}
              onChange={(e) => setRhyme(e.target.value)}
              className="w-full p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-white focus:border-amber-500"
            />
          </div>
        </div>

        <textarea
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="اكتب فكرة القصيدة هنا..."
          className="w-full h-32 p-4 rounded-xl bg-neutral-900 border border-neutral-800 text-white focus:border-amber-500"
        />

        <button
          onClick={generatePoem}
          disabled={loading}
          className="w-full py-3 rounded-xl bg-amber-500 text-neutral-950 font-bold hover:bg-amber-400 transition"
        >
          {loading ? 'جاري نظم القصيدة...' : 'توليد القصيدة ✨'}
        </button>

        {poem && (
          <div className="p-6 rounded-xl bg-neutral-900 border border-amber-500/30 whitespace-pre-line text-lg text-amber-100 font-serif">
            {poem}
          </div>
        )}
      </div>
    </div>
  );
}
