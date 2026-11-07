import React, { useState } from 'react';
import { Home, Compass, FolderHeart, Users, Library, Settings, Video, Music, BookOpen, Mic, Image as ImageIcon, Sparkles, Paperclip, ChevronDown } from 'lucide-react';

export default function FMStarStudio() {
  const [selectedTool, setSelectedTool] = useState('Video Generation');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [videoResult, setVideoResult] = useState<string | null>(null);

  const tools = [
    { name: 'Video Generation', icon: Video },
    { name: 'Music Generation', icon: Music },
    { name: 'Song Creation', icon: Music },
    { name: 'Poetry Creation', icon: BookOpen },
    { name: 'Melody Composer', icon: Music },
    { name: 'Voice Creator', icon: Mic },
    { name: 'Image Generator', icon: ImageIcon },
  ];

  // الدالة اللي بتربط الواجهة بالباك إند بتاعك
  const handleGenerate = async () => {
    if (!prompt.trim()) return alert("Please describe your imagination first!");
    
    setIsLoading(true);
    setVideoResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/internal/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-FMStar-Key': 'samurai_secret_2026' // المفتاح اللي في الباك إند
        },
        body: JSON.stringify({
          prompt: prompt,
          ratio: "16:9",
          dsp_profile: "hybrid"
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setVideoResult(data.direct_stream_url);
      } else {
        alert("Error: " + data.detail);
      }
    } catch (error) {
      console.error(error);
      alert("Failed to connect to the server. Make sure FastAPI is running.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#050505] text-white font-sans overflow-hidden relative">
      
      {/* خلفية دبي (يمكنك تغيير الرابط لصورة برج خليفة) */}
      <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1512453979798-5ea266f8880c?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center opacity-20"></div>
      <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-[#050505]"></div>

      {/* 1. القائمة الجانبية (Sidebar) */}
      <aside className="w-64 h-full bg-black/40 backdrop-blur-2xl border-r border-white/10 flex flex-col py-6 px-4 z-10">
        <div className="flex items-center gap-2 mb-10 px-2">
          <Sparkles className="text-yellow-400" size={28} />
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-yellow-500">FMStar</h1>
        </div>
        
        <nav className="space-y-2 flex-1">
          {[{icon: Home, name: 'Home'}, {icon: Compass, name: 'AI Studio', active: true}, {icon: FolderHeart, name: 'My Creations'}, {icon: Users, name: 'Community'}, {icon: Library, name: 'Library'}].map((item, i) => (
            <button key={i} className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all ${item.active ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}>
              <item.icon size={20} /> <span className="font-medium">{item.name}</span>
            </button>
          ))}
        </nav>
        
        <button className="w-full flex items-center gap-4 px-4 py-3 text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all mt-auto">
          <Settings size={20} /> <span>Settings</span>
        </button>
      </aside>

      {/* 2. المنطقة الرئيسية (Main Content) */}
      <main className="flex-1 relative flex flex-col items-center justify-center z-10 p-8">
        
        {/* الشعار الرئيسي */}
        <div className="text-center mb-8">
          <h2 className="text-4xl md:text-5xl font-bold tracking-wider mb-2">IF YOU CAN IMAGINE IT</h2>
          <h2 className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-yellow-400 mb-2">AI CAN CREATE IT</h2>
          <p className="text-yellow-500 text-sm tracking-widest font-semibold">ONLY PASSION</p>
        </div>

        {/* الصندوق الزجاجي المركزي */}
        <div className="w-full max-w-3xl bg-black/40 backdrop-blur-xl border border-white/20 rounded-3xl p-6 shadow-[0_0_50px_rgba(0,100,255,0.1)] relative">
          
          <div className="flex flex-col md:flex-row gap-6">
            
            {/* القائمة المنسدلة للأدوات */}
            <div className="w-full md:w-1/2 relative">
              <label className="text-sm text-gray-400 mb-2 block">Select AI Creation Tool</label>
              <button 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="w-full flex items-center justify-between bg-white/5 border border-white/10 p-3 rounded-xl hover:bg-white/10 transition-all"
              >
                <div className="flex items-center gap-3">
                  <Video size={18} className="text-blue-400" />
                  <span>{selectedTool}</span>
                </div>
                <ChevronDown size={18} />
              </button>

              {/* القائمة المنسدلة */}
              {isDropdownOpen && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-[#1a1a1a] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50">
                  {tools.map((tool, idx) => (
                    <button 
                      key={idx}
                      onClick={() => { setSelectedTool(tool.name); setIsDropdownOpen(false); }}
                      className="w-full flex items-center gap-3 p-3 hover:bg-blue-600/20 text-left transition-colors border-b border-white/5 last:border-0"
                    >
                      <tool.icon size={18} className="text-gray-400" />
                      <span>{tool.name}</span>
                    </button>
                  ))}
                </div>
              )}
              
              {/* صورة توضيحية صغيرة (زي اللي في التصميم) */}
              <div className="mt-4 rounded-xl overflow-hidden border border-white/10 relative h-32">
                <img src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop" alt="preview" className="w-full h-full object-cover" />
                <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                  <div className="w-10 h-10 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center cursor-pointer">
                    <span className="text-white text-xl ml-1">▶</span>
                  </div>
                </div>
              </div>
            </div>

            {/* مربع الوصف وزر التوليد */}
            <div className="w-full md:w-1/2 flex flex-col">
              <label className="text-sm text-gray-400 mb-2 block">Describe your imagination...</label>
              <textarea 
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full flex-1 bg-white/5 border border-white/10 rounded-xl p-4 outline-none resize-none placeholder-gray-500 focus:border-blue-500 transition-colors"
                placeholder="Examples: A cinematic video of a girl in a futuristic city..."
              ></textarea>
              
              <div className="flex justify-between items-center mt-3">
                <button className="text-gray-400 hover:text-white flex items-center gap-2 text-sm bg-white/5 px-3 py-1.5 rounded-lg">
                  <Paperclip size={14} /> Attach
                </button>
                <span className="text-xs text-gray-500">{prompt.length} / 4000</span>
              </div>

              <button 
                onClick={handleGenerate}
                disabled={isLoading}
                className="mt-4 w-full bg-gradient-to-r from-blue-600 to-blue-400 hover:from-blue-500 hover:to-blue-300 text-white font-bold py-4 rounded-xl shadow-[0_0_20px_rgba(37,99,235,0.4)] transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Sparkles size={18} />
                {isLoading ? "Generating Magic..." : "Generate Now"}
              </button>
            </div>
          </div>
          
          <div className="text-center mt-6 text-xs text-gray-500 tracking-widest">
            FAST • POWERFUL • LIMITLESS
          </div>
        </div>

        {/* عرض الفيديو الناتج */}
        {videoResult && (
          <div className="mt-8 w-full max-w-3xl bg-black/60 backdrop-blur-xl border border-white/20 p-4 rounded-2xl">
            <h3 className="text-center text-green-400 mb-4 font-bold">🎉 Your Creation is Ready!</h3>
            <video controls src={videoResult} className="w-full rounded-xl border border-white/10"></video>
          </div>
        )}

        {/* الأيقونات الجانبية (Instant Results, etc.) */}
        <div className="absolute right-8 top-1/2 -translate-y-1/2 hidden lg:flex flex-col gap-4">
           {['Instant Results', 'Premium Quality', 'AI Powered', 'Secure & Private'].map((feature, i) => (
             <div key={i} className="flex items-center gap-3 bg-white/5 backdrop-blur-md border border-white/10 px-4 py-3 rounded-xl">
               <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400">
                 {i === 0 ? <Sparkles size={16}/> : i === 1 ? <Video size={16}/> : i === 2 ? <Settings size={16}/> : <Home size={16}/>}
               </div>
               <span className="text-sm font-medium">{feature}</span>
             </div>
           ))}
        </div>

      </main>
    </div>
  );
        }
