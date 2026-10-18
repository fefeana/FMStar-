'use client';
import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabaseClient';

interface Creation {
  id: string;
  title: string;
  content: string;
  type: 'poetry' | 'song';
  created_at: string;
}

export default function DashboardPage() {
  const [creations, setCreations] = useState<Creation[]>([]);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [loading, setLoading] = useState(false);

  // جلب البيانات من Supabase
  useEffect(() => {
    fetchCreations();
  }, []);

  const fetchCreations = async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from('creations')
      .select('*')
      .order('created_at', { ascending: false });

    if (!error && data) {
      setCreations(data);
    }
    setLoading(false);
  };

  const filteredCreations = creations.filter((item) => {
    const matchesSearch = item.title.toLowerCase().includes(search.toLowerCase()) ||
                          item.content.toLowerCase().includes(search.toLowerCase());
    const matchesType = filterType === 'all' || item.type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-6 md:p-12">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* الهيدر والإحصائيات */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-neutral-800 pb-6">
          <div>
            <h1 className="text-3xl font-bold text-amber-400 flex items-center gap-2">
              🎛️ لوحة تحكم إف إم ستار
            </h1>
            <p className="text-neutral-400 mt-1">
              إدارة واستعراض كافة إبداعاتك الشعريّة والموسيقيّة
            </p>
          </div>
          <div className="flex gap-4">
            <div className="bg-neutral-900 border border-neutral-800 px-4 py-2 rounded-xl text-center">
              <span className="block text-xs text-neutral-500">إجمالي الأغاني</span>
              <span className="text-xl font-bold text-amber-400">
                {creations.filter(c => c.type === 'song').length}
              </span>
            </div>
            <div className="bg-neutral-900 border border-neutral-800 px-4 py-2 rounded-xl text-center">
              <span className="block text-xs text-neutral-500">إجمالي القصائد</span>
              <span className="text-xl font-bold text-amber-400">
                {creations.filter(c => c.type === 'poetry').length}
              </span>
            </div>
          </div>
        </div>

        {/* أدوات البحث والفلترة */}
        <div className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            placeholder="بحث في العناوين أو النصوص..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-white focus:outline-none focus:border-amber-500"
          />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-white focus:outline-none focus:border-amber-500"
          >
            <option value="all">جميع الإنتاجات</option>
            <option value="poetry">الشعر والأدب 🖋️</option>
            <option value="song">الأغاني والموسيقى 🎙️</option>
          </select>
        </div>

        {/* قائمة الإنتاجات */}
        {loading ? (
          <p className="text-center text-neutral-500 py-12">جاري تحميل الإبداعات...</p>
        ) : filteredCreations.length === 0 ? (
          <div className="text-center py-16 bg-neutral-900/50 rounded-2xl border border-dashed border-neutral-800">
            <p className="text-neutral-400 text-lg">لا توجد إنتاجات مطابقة حتى الآن</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredCreations.map((item) => (
              <div
                key={item.id}
                className="p-6 rounded-2xl bg-neutral-900 border border-neutral-800 hover:border-amber-500/50 transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      item.type === 'poetry' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                    }`}>
                      {item.type === 'poetry' ? '🖋️ شعر' : '🎙️ أغنية'}
                    </span>
                    <span className="text-xs text-neutral-500">
                      {new Date(item.created_at).toLocaleDateString('ar-SA')}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-neutral-100 mb-2">{item.title}</h3>
                  <p className="text-neutral-400 text-sm whitespace-pre-line line-clamp-4 font-serif">
                    {item.content}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
