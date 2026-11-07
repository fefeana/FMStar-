import React, { useState } from 'react';
import { Home, Compass, FolderHeart, Users, Library, Settings, Video, Music, BookOpen, Mic, Sparkles, ChevronDown, Play } from 'lucide-react';

export default function StarFMStudio() {
  const [selectedTool, setSelectedTool] = useState('توليد الأغنية');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [videoResult, setVideoResult] = useState<string | null>(null);
  const [selectedStyles, setSelectedStyles] = useState<string[]>(['سينمائي', 'حزين']); // الستايلات المختارة

  const tools = [
    { name: 'توليد الأغنية', icon: Music },
    { name: 'توليد الفيديو', icon: Video },
    { name: 'توليد الشعر', icon: BookOpen },
    { name: 'توليد الألحان', icon: Music },
    { name: 'توليد الصوت', icon: Mic },
  ];

  const styles = ['سينمائي', 'حزين', 'رومانسي', 'ليلي', 'هادئ', 'حماسي'];

  const toggleStyle = (style: string) => {
    if (selectedStyles.includes(style)) {
      setSelectedStyles(selectedStyles.filter(s => s !== style));
    } else {
      setSelectedStyles([...selectedStyles, style]);
    }
  };

  // دالة الاتصال بالباك إند (FastAPI)
  const handleGenerate = async () => {
    if (!prompt.trim()) return alert("اكتب فكرتك هنا أولاً...");
    
    setIsLoading(true);
    setVideoResult(null);

    try {
      // الاتصال بالسيرفر المحلي بتاعك (تأكدي إنه شغال)
      const response = await fetch('http://127.0.0.1:8000/internal/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-FMStar-Key': 'samurai_secret_2026' // المفتاح بتاعك
        },
        body: JSON.stringify({
          prompt: prompt,
          ratio: "16:9",
          dsp_profile: selectedStyles.join(', ') // بنبعت الستايلات المختارة
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setVideoResult(data.direct_stream_url); // عرض الفيديو الناتج
      } else {
        alert("حدث خطأ: " + data.detail);
      }
    } catch (error) {
      console.error(error);
      alert("فشل الاتصال بالسيرفر. تأكدي من تشغيل FastAPI (uvicorn).");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0a0514] text-white font-sans overflow-hidden relative" dir="rtl">
      
      {/* إضاءة الخلفية البنفسجية */}
      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-purple-900/20 via-[#0a0514] to-[#0a0514] pointer-events-none"></div>

      {/* 1. القائمة الجانبية */}
      <aside className="w-64 h-full bg-black/40 backdrop-blur-2xl border-l border-white/10 flex flex-col py-6 px-4 z-10">
        <div className="flex items-center gap-2 mb-10 px-2">
          <Sparkles className="text-purple-400" size={28} />
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">Star FM</h1>
        </div>
        
        <nav className="space-y-2 flex-1">
          {[{icon: Home, name: 'الرئيسية'}, {icon: Compass, name: 'استوديو AI', active: true}, {icon: FolderHeart, name: 'إبداعاتي'}, {icon: Users, name: 'المجتمع'}, {icon: Library, name: 'المكتبة'}].map((item, i) => (
            <button key={i} className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all ${item.active ? 'bg-purple-600/20 text-purple-300 border border-purple-500/30' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}>
              <item.icon size={20} /> <span className="font-medium">{item.name}</span>
            </button>
          ))}
        </nav>
        
        <button className="w-full flex items-center gap-4 px-4 py-3 text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all mt-auto">
          <Settings size={20} /> <span>الإعدادات</span>
        </button>
      </aside>

      {/* 2. المنطقة الرئيسية */}
      <main className="flex-1 relative flex flex-col items-center justify-center z-10 p-8 overflow-y-auto">
        
        {/* الشعار العلوي */}
        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-5xl font-bold tracking-wider mb-2 text-white">Star FM <span className="text-purple-400">AI STUDIO</span></h2>
          <p className="text-purple-300 text-sm tracking-widest font-semibold mt-2">حيث يلتقي الإبداع بذكاء أعلى</p>
        </div>

        {/* مشغل الفيديو (لو النتيجة ظهرت) */}
        <div className="w-full max-w-2xl bg-[#1a1025]/80 backdrop-blur-xl border border-purple-500/30 rounded-3xl p-4 mb-6 relative overflow-hidden shadow-[0_0_40px_rgba(168,85,247,0.15)]">
           <div className="absolute top-4 left-4 text-xs text-gray-400">1 / 3</div>
           <div className="w-full h-64 md:h-80 bg-gray-900 rounded-2xl overflow-hidden relative mb-4">
              {videoResult ? (
                <video controls src={videoResult} className="w-full h-full object-cover"></video>
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-[url('https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center">
                   <div className="absolute inset-0 bg-black/50"></div>
                   <div className="relative w-16 h-16 bg-pink-500 rounded-full flex items-center justify-center cursor-pointer shadow-[0_0_20px_rgba(236,72,153,0.6)]">
                      <Play size={28} className="text-white ml-1" />
                   </div>
                </div>
              )}
           </div>
           <h3 className="text-center text-2xl font-bold text-white mb-2">بيئة من صنعك</h3>
           <p className="text-center text-sm text-purple-300">الآن بث مباشر عبر الأثير</p>
        </div>

        {/* صندوق الإدخال */}
        <div className="w-full max-w-2xl bg-[#1a1025]/80 backdrop-blur-xl border border-purple-500/30 rounded-3xl p-6 shadow-2xl relative">
          
          <div className="flex justify-between items-center mb-4">
            <div className="relative w-full md:w-1/2 ml-2">
              <button 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="w-full flex items-center justify-between bg-purple-900/30 border border-purple-500/30 p-3 rounded-xl hover:bg-purple-900/50 transition-all text-sm"
              >
                <div className="flex items-center gap-3">
                  <Music size={18} className="text-purple-400" />
                  <span>{selectedTool}</span>
                </div>
                <ChevronDown size={18} />
              </button>

              {isDropdownOpen && (
                <div className="absolute top-full right-0 mt-2 w-full bg-[#1a1025] border border-purple-500/30 rounded-xl shadow-2xl overflow-hidden z-50">
                  {tools.map((tool, idx) => (
                    <button 
                      key={idx}
                      onClick={() => { setSelectedTool(tool.name); setIsDropdownOpen(false); }}
                      className="w-full flex items-center gap-3 p-3 hover:bg-purple-600/20 text-right transition-colors border-b border-purple-500/10 last:border-0 text-sm"
                    >
                      <tool.icon size={18} className="text-gray-400" />
                      <span>{tool.name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <span className="text-xs text-purple-300">0 / 280</span>
          </div>

          <textarea 
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full h-32 bg-transparent border-none outline-none resize-none placeholder-gray-500 text-lg text-white"
            placeholder="اكتب فكرتك هنا... أغنية، قصيدة، أو فيديو"
          ></textarea>

          {/* اختيار التأثيرات (الستايلات) */}
          <div className="mt-4 border-t border-purple-500/20 pt-4">
            <div className="flex items-center gap-2 mb-3">
               <span className="text-sm font-medium">التأثيرات</span>
               <span className="text-xs bg-purple-600/30 text-purple-300 px-2 py-0.5 rounded-full">{selectedStyles.length} مختار</span>
            </div>
            <div className="flex flex-wrap gap-2">
               {styles.map((style) => (
                 <button
                   key={style}
                   onClick={() => toggleStyle(style)}
                   className={`px-4 py-2 rounded-xl text-sm border transition-all ${selectedStyles.includes(style) ? 'bg-purple-600/40 border-purple-400 text-white shadow-[0_0_10px_rgba(168,85,247,0.3)]' : 'bg-transparent border-gray-600 text-gray-400 hover:border-purple-500'}`}
                 >
                   {style}
                 </button>
               ))}
            </div>
          </div>

          <button 
            onClick={handleGenerate}
            disabled={isLoading}
            className="mt-6 w-full bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-500 hover:to-pink-400 text-white font-bold py-4 rounded-xl shadow-[0_0_20px_rgba(168,85,247,0.4)] transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Sparkles size={20} />
            {isLoading ? "جاري التوليد..." : "✨ توليد بالذكاء الاصطناعي"}
          </button>

        </div>
      </main>
    </div>
  );
                                        }
