'use client';
import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabaseClient';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';

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
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);

  // حالة زر المزامنة السحابية الثابت في الهيدر
  const [isCloudSyncEnabled, setIsCloudSyncEnabled] = useState(true);

  useEffect(() => {
    fetchCreations();
  }, []);

  const fetchCreations = async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from('creations')
      .select('*')
      .order('created_at', { ascending: true });

    if (!error && data) {
      setCreations(data);
    }
    setLoading(false);
  };

  // تصفية البيانات
  const filteredCreations = creations.filter((item) => {
    const matchesSearch = item.title.toLowerCase().includes(search.toLowerCase()) ||
                          item.content.toLowerCase().includes(search.toLowerCase());
    const matchesType = filterType === 'all' || item.type === filterType;
    
    const itemDate = new Date(item.created_at);
    const matchesStartDate = !startDate || itemDate >= new Date(startDate);
    const matchesEndDate = !endDate || itemDate <= new Date(endDate + 'T23:59:59');

    return matchesSearch && matchesType && matchesStartDate && matchesEndDate;
  });

  // تجهيز بيانات الرسم البياني (Recharts) بناءً على التواريخ والأنواع
  const chartDataMap = filteredCreations.reduce((acc: any, curr) => {
    const dateKey = new Date(curr.created_at).toLocaleDateString('ar-SA', { month: 'short', day: 'numeric' });
    if (!acc[dateKey]) {
      acc[dateKey] = { date: dateKey, شعر: 0, أغاني: 0 };
    }
    if (curr.type === 'poetry') acc[dateKey].شعر += 1;
    if (curr.type === 'song') acc[dateKey].أغاني += 1;
    return acc;
  }, {});

  const chartData = Object.values(chartDataMap);

  // دالة تصدير CSV
  const exportToCSV = () => {
    if (filteredCreations.length === 0) return;
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
    link.setAttribute('download', `FMStar_Creations_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-6 md:p-10" dir="rtl">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* الهيدر المطور مع زر المزامنة الثابت */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-neutral-800 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold text-amber-400 flex items-center gap-2">
              🎛️ لوحة تحكم إف إم ستار الشخصية
            </h1>
            <p className="text-neutral-400 text-sm mt-1">
              إدارة وتحليل إنتاجاتك الخاصة (الشعر والأغاني) بشكل حصري وآمن
            </p>
          </div>

          <div className="flex items-center gap-4 flex-wrap">
            {/* زر المزامنة السحابية الثابت مع مؤشر حالة متحرك */}
            <div className="flex items-center gap-3 bg-neutral-900 border border-neutral-800 px-4 py-2 rounded-xl">
              <span className="relative flex h-3 w-3">
                {isCloudSyncEnabled && (
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                )}
                <span className={`relative inline-flex rounded-full h-3 w-3 ${isCloudSyncEnabled ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
              </span>
              <span className="text-xs font-medium text-neutral-300">
                المزامنة السحابية: <strong className={isCloudSyncEnabled ? 'text-emerald-400' : 'text-rose-400'}>{isCloudSyncEnabled ? 'مفعلة' : 'متوقفة'}</strong>
              </span>
              <button
                onClick={() => setIsCloudSyncEnabled(!isCloudSyncEnabled)}
                className={`text-xs px-2.5 py-1 rounded-lg font-bold transition ${
                  isCloudSyncEnabled 
                    ? 'bg-neutral-800 text-rose-400 hover:bg-neutral-700' 
                    : 'bg-emerald-600 text-white hover:bg-emerald-500'
                }`}
              >
                {isCloudSyncEnabled ? 'إيقاف' : 'تفعيل'}
              </button>
            </div>

            {/* زر التصدير */}
            <button
              onClick={exportToCSV}
              disabled={filteredCreations.length === 0}
              className="px-4 py-2 rounded-xl bg-amber-500 text-neutral-950 font-bold hover:bg-amber-400 disabled:opacity-50 transition flex items-center gap-2 text-sm shadow-lg shadow-amber-500/10"
            >
              📊 تصدير (CSV)
            </button>
          </div>
        </div>

        {/* أدوات البحث والفلترة والنطاق الزمني */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-neutral-900/60 p-4 rounded-2xl border border-neutral-800 backdrop-blur-md">
          <input
            type="text"
            placeholder="بحث بالعنوان أو النص..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-white focus:outline-none focus:border-amber-500 text-sm"
          />

          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-white focus:outline-none focus:border-amber-500 text-sm"
          >
            <option value="all">جميع الأنواع</option>
            <option value="poetry">الشعر والأدب 🖋️</option>
            <option value="song">الأغاني والموسيقى 🎙️</option>
          </select>

          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-neutral-300 focus:outline-none focus:border-amber-500 text-sm"
          />

          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="p-3 rounded-xl bg-neutral-900 border border-neutral-800 text-neutral-300 focus:outline-none focus:border-amber-500 text-sm"
          />
        </div>

        {/* قسم الرسم البياني التفاعلي (Recharts) */}
        {chartData.length > 0 && (
          <div className="bg-neutral-900/40 p-6 rounded-2xl border border-neutral-800">
            <h2 className="text-lg font-bold text-neutral-200 mb-4 flex items-center gap-2">
              📈 تحليل إحصائي للإنتاجات عبر الزمن
            </h2>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorPoetry" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorSong" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                  <XAxis dataKey="date" stroke="#737373" />
                  <YAxis stroke="#737373" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#171717', borderColor: '#262626', borderRadius: '8px', color: '#fff' }} 
                  />
                  <Area type="monotone" dataKey="شعر" stroke="#f59e0b" fillOpacity={1} fill="url(#colorPoetry)" />
                  <Area type="monotone" dataKey="أغاني" stroke="#3b82f6" fillOpacity={1} fill="url(#colorSong)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

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
