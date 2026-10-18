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
  
  // 1️⃣ حالة أدوات الفلترة حسب التاريخ
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);

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

  // 2️⃣ تصفية البيانات المتقدمة (البحث + النوع + النطاق الزمني)
  const filteredCreations = creations.filter((item) => {
    const matchesSearch = item.title.toLowerCase().includes(search.toLowerCase()) ||
                          item.content.toLowerCase().includes(search.toLowerCase());
    const matchesType = filterType === 'all' || item.type === filterType;
    
    // فلترة التواريخ
    const itemDate = new Date(item.created_at);
    const matchesStartDate = !startDate || itemDate >= new Date(startDate);
    const matchesEndDate = !endDate || itemDate <= new Date(endDate + 'T23:59:59');

    return matchesSearch && matchesType && matchesStartDate && matchesEndDate;
  });

  // 3️⃣ دالة تصدير البيانات القائمة المفلترة إلى ملف CSV
  const exportToCSV = () => {
    if (filteredCreations.length === 0) return;

    // تجهيز رأس ورسائل ملف CSV
    const headers = ['العنوان (Title)', 'النوع (Type)', 'تاريخ الإنشاء (Timestamp)'];
    const rows = filteredCreations.map(item => [
      `"${item.title.replace(/"/g, '""')}"`,
      item.type === 'poetry' ? 'شعر' : 'أغنية',
      `"${new Date(item.created_at).toLocaleString('ar-SA')}"`
    ]);

    const csvContent = '\uFEFF' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `FMStar_Creations_Export_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-6 md:p-12" dir="rtl">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* الهيدر مع زر تصدير CSV */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-neutral-800 pb-6">
          <div>
            <h1 className="text-3xl font-bold text-amber-400 flex items-center gap-2">
              🎛️ لوحة تحكم إف إم ستار
            </h1>
            <p className="text-neutral-400 mt-1">
              إدارة واستعراض كافة إبداعاتك الشعريّة والموسيقيّة
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={exportToCSV}
              disabled={filteredCreations.length === 0}
              className="px-4 py-2 rounded-xl bg-amber-500 text-neutral-950 font-bold hover:bg-amber-400 disabled:opacity-50 transition flex items-center gap-2 text-sm"
            >
              📊 تصدير القائمة (CSV)
            </button>
          </div>
        </div>

        {/* أدوات البحث، الفلترة، واختيار النطاق الزمني (Date Range Picker) */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-neutral-900/60 p-4 rounded-2xl border border-neutral-800">
          {/* حقل البحث */}
          <input
            type="text"
            placeholder="بحث بالعنوان أو النص..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-white focus:outline-none focus:border-amber-500 text-sm"
          />

          {/* نوع الإنتاج */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-white focus:outline-none focus:border-amber-500 text-sm"
          >
            <option value="all">جميع الأنواع</option>
            <option value="poetry">الشعر والأدب 🖋️</option>
            <option value="song">الأغاني والموسيقى 🎙️</option>
          </select>

          {/* تاريخ البداية */}
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-neutral-300 focus:outline-none focus:border-amber-500 text-sm"
            title="تاريخ البداية"
          />

          {/* تاريخ النهاية */}
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-neutral-300 focus:outline-none focus:border-amber-500 text-sm"
            title="تاريخ النهاية"
          />
        </div>

        {/* عرض قائمة الإنتاجات */}
        {loading ? (
          <p className="text-center text-neutral-500 py-12">جاري تحميل البيانات...</p>
        ) : filteredCreations.length === 0 ? (
          <div className="text-center py-16 bg-neutral-900/50 rounded-2xl border border-dashed border-neutral-800">
            <p className="text-neutral-400 text-lg">لا توجد نتائج مطابقة للفلاتر المحددة</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredCreations.map((item) => (
              <div
                key={item.id}
                className="p-6 rounded-2xl bg-neutral-900 border border-neutral-800 hover:border-amber-500/50 transition flex flex-col justify-between space-y-4"
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
                  <p className="text-neutral-400 text-sm whitespace-pre-line line-clamp-3 font-serif">
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
