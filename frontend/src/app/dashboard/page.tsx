'use client';
import { useState, useEffect, useMemo } from 'react';
import { supabase } from '@/lib/supabaseClient';
import { db } from '@/lib/firebase';
import { doc, setDoc } from 'firebase/firestore';
import { jsPDF } from 'jspdf';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
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
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  // ميزات التحديد المتعدد
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [bulkDeleting, setBulkDeleting] = useState(false);

  // ميزة المزامنة السحابية مع Firestore
  const [cloudSyncEnabled, setCloudSyncEnabled] = useState(false);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'synced' | 'error'>('idle');

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

  // المزامنة التلقائية مع Firestore في الخلفية
  useEffect(() => {
    if (!cloudSyncEnabled || creations.length === 0) return;

    let isMounted = true;
    const syncToFirestore = async () => {
      try {
        setSyncStatus('syncing');
        for (const item of creations) {
          if (!isMounted) break;
          const ref = doc(db, 'creations_backup', item.id);
          await setDoc(ref, {
            ...item,
            synced_at: new Date().toISOString(),
          }, { merge: true });
        }
        if (isMounted) setSyncStatus('synced');
      } catch (err) {
        console.error('Firestore sync error:', err);
        if (isMounted) setSyncStatus('error');
      }
    };

    syncToFirestore();
    return () => {
      isMounted = false;
    };
  }, [cloudSyncEnabled, creations]);

  // حذف عنصر فردي من Supabase
  const handleDelete = async (id: string) => {
    const confirmed = window.confirm('هل أنت متأكد من حذف هذا العمل الإبداعي؟');
    if (!confirmed) return;

    setActionLoadingId(id);
    const { error } = await supabase
      .from('creations')
      .delete()
      .eq('id', id);

    if (!error) {
      setCreations((prev) => prev.filter((item) => item.id !== id));
      setSelectedIds((prev) => prev.filter((selectedId) => selectedId !== id));
    } else {
      alert(`حدث خطأ أثناء الحذف: ${error.message}`);
    }
    setActionLoadingId(null);
  };

  // حذف متعدد دفعة واحدة عبر طلب فوري واحد في Supabase
  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;

    const confirmed = window.confirm(`هل أنت متأكد من حذف ${selectedIds.length} من الأعمال المحددة دفعة واحدة؟`);
    if (!confirmed) return;

    setBulkDeleting(true);
    const { error } = await supabase
      .from('creations')
      .delete()
      .in('id', selectedIds);

    if (!error) {
      setCreations((prev) => prev.filter((item) => !selectedIds.includes(item.id)));
      setSelectedIds([]);
    } else {
      alert(`حدث خطأ أثناء الحذف الجماعي: ${error.message}`);
    }
    setBulkDeleting(false);
  };

  // إدارة التحديد
  const toggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === filteredCreations.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredCreations.map((item) => item.id));
    }
  };

  // تصدير العمل الفردي إلى ملف PDF باستخدام jsPDF
  const exportToPDF = (item: Creation) => {
    const docPdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    const isPoetry = item.type === 'poetry';
    const typeLabel = isPoetry ? 'FMStar Poetry Studio' : 'FMStar Songs & Lyrics';
    const dateFormatted = new Date(item.created_at).toLocaleDateString('en-US');

    docPdf.setFillColor(20, 20, 24);
    docPdf.rect(0, 0, 210, 297, 'F');

    docPdf.setFont('helvetica', 'bold');
    docPdf.setFontSize(22);
    docPdf.setTextColor(245, 158, 11);
    docPdf.text('FMSTAR STUDIO AI', 105, 30, { align: 'center' });

    docPdf.setFontSize(12);
    docPdf.setTextColor(163, 163, 163);
    docPdf.text(`${typeLabel} | Date: ${dateFormatted}`, 105, 40, { align: 'center' });

    docPdf.setDrawColor(245, 158, 11);
    docPdf.setLineWidth(0.6);
    docPdf.line(30, 48, 180, 48);

    docPdf.setFontSize(16);
    docPdf.setTextColor(255, 255, 255);
    docPdf.text(`Title: ${item.title || 'Untitled Creation'}`, 105, 60, { align: 'center' });

    docPdf.setFont('helvetica', 'normal');
    docPdf.setFontSize(12);
    docPdf.setTextColor(229, 231, 235);

    const splitContent = docPdf.splitTextToSize(item.content, 150);
    docPdf.text(splitContent, 105, 75, { align: 'center' });

    docPdf.setFontSize(10);
    docPdf.setTextColor(115, 115, 115);
    docPdf.text('Generated by FMStar AI Platform - Official Export', 105, 280, { align: 'center' });

    const safeTitle = (item.title || 'creation').replace(/[^a-zA-Z0-9_\u0600-\u06FF]/g, '_');
    docPdf.save(`${safeTitle}_${item.type}.pdf`);
  };

  // تصدير قائمة الأعمال المفلترة الحالية إلى ملف CSV
  const exportToCSV = () => {
    if (filteredCreations.length === 0) {
      alert('لا توجد عناصر لتصديرها');
      return;
    }

    const headers = ['ID', 'Title', 'Type', 'CreatedAt', 'Content'];
    const rows = filteredCreations.map((item) => {
      const cleanContent = `"${(item.content || '').replace(/"/g, '""').replace(/\n/g, ' ')}"`;
      const cleanTitle = `"${(item.title || '').replace(/"/g, '""')}"`;
      return [item.id, cleanTitle, item.type, item.created_at, cleanContent].join(',');
    });

    const csvContent = '\uFEFF' + [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `fmstar_creations_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // التصفية بحسب البحث والنوع والنطاق الزمني
  const filteredCreations = useMemo(() => {
    return creations.filter((item) => {
      const matchesSearch =
        item.title.toLowerCase().includes(search.toLowerCase()) ||
        item.content.toLowerCase().includes(search.toLowerCase());
      const matchesType = filterType === 'all' || item.type === filterType;

      const itemDate = new Date(item.created_at);
      const matchesStart = !startDate || itemDate >= new Date(startDate);
      const matchesEnd = !endDate || itemDate <= new Date(`${endDate}T23:59:59`);

      return matchesSearch && matchesType && matchesStart && matchesEnd;
    });
  }, [creations, search, filterType, startDate, endDate]);

  // إعداد بيانات الرسم البياني حسب التواريخ
  const chartData = useMemo(() => {
    const map = new Map<string, { date: string; poetry: number; song: number; total: number }>();

    const sorted = [...filteredCreations].sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );

    sorted.forEach((item) => {
      const dateKey = new Date(item.created_at).toLocaleDateString('ar-SA', {
        month: 'short',
        day: 'numeric',
      });

      if (!map.has(dateKey)) {
        map.set(dateKey, { date: dateKey, poetry: 0, song: 0, total: 0 });
      }
      const entry = map.get(dateKey)!;
      if (item.type === 'poetry') {
        entry.poetry += 1;
      } else {
        entry.song += 1;
      }
      entry.total += 1;
    });

    return Array.from(map.values());
  }, [filteredCreations]);

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-6 md:p-12">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* الهيدر والإحصائيات وزر المزامنة وحذف المحدد وتصدير CSV */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-neutral-800 pb-6">
          <div>
            <h1 className="text-3xl font-bold text-amber-400 flex items-center gap-2">
              🎛️ لوحة تحكم إف إم ستار
            </h1>
            <p className="text-neutral-400 mt-1">
              إدارة واستعراض وحفظ وتحليل كافة إبداعاتك الشعريّة والموسيقيّة
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* زر المزامنة السحابية مع مؤشر متحرك */}
            <button
              onClick={() => setCloudSyncEnabled(!cloudSyncEnabled)}
              className={`px-3 py-2 rounded-xl text-xs font-bold border transition flex items-center gap-2 ${
                cloudSyncEnabled
                  ? 'bg-amber-500/10 border-amber-500/50 text-amber-300'
                  : 'bg-neutral-900 border-neutral-800 text-neutral-400 hover:border-neutral-700'
              }`}
              title="مزامنة خلفية تلقائية مع Firestore"
            >
              <span className="relative flex h-2.5 w-2.5">
                {cloudSyncEnabled && (
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                )}
                <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                  cloudSyncEnabled
                    ? syncStatus === 'syncing' ? 'bg-amber-400' : 'bg-emerald-500'
                    : 'bg-neutral-600'
                }`}></span>
              </span>
              <span>{cloudSyncEnabled ? (syncStatus === 'syncing' ? 'جاري المزامنة...' : 'المزامنة السحابية مفعلة') : 'مزامنة سحابية'}</span>
            </button>

            {/* زر الحذف الجماعي للعناصر المحددة */}
            {selectedIds.length > 0 && (
              <button
                onClick={handleBulkDelete}
                disabled={bulkDeleting}
                className="bg-red-600 hover:bg-red-500 text-white px-3 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition shadow-lg shadow-red-600/20 disabled:opacity-50"
              >
                <span>🗑️ حذف المحدد ({selectedIds.length})</span>
              </button>
            )}

            <button
              onClick={exportToCSV}
              className="bg-amber-500 hover:bg-amber-400 text-neutral-950 px-3 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition shadow-lg shadow-amber-500/10"
              title="تصدير القائمة المعروضة إلى CSV"
            >
              📊 تصدير CSV
            </button>

            <div className="bg-neutral-900 border border-neutral-800 px-3 py-1.5 rounded-xl text-center">
              <span className="block text-[10px] text-neutral-500">الأغاني</span>
              <span className="text-sm font-bold text-amber-400">
                {creations.filter((c) => c.type === 'song').length}
              </span>
            </div>
            <div className="bg-neutral-900 border border-neutral-800 px-3 py-1.5 rounded-xl text-center">
              <span className="block text-[10px] text-neutral-500">القصائد</span>
              <span className="text-sm font-bold text-amber-400">
                {creations.filter((c) => c.type === 'poetry').length}
              </span>
            </div>
          </div>
        </div>

        {/* رسم بياني تحليلي باستخدام Recharts */}
        {chartData.length > 0 && (
          <div className="bg-neutral-900/80 border border-neutral-800 p-6 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-neutral-200 flex items-center gap-2">
                📈 تحليل معدل الإنتاج الزمني (Recharts Analytics)
              </h2>
              <span className="text-xs text-neutral-400">توزيع القصائد والأغاني حسب التاريخ</span>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="amberGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                  <XAxis dataKey="date" stroke="#737373" fontSize={12} />
                  <YAxis stroke="#737373" fontSize={12} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#171717',
                      borderColor: '#404040',
                      borderRadius: '0.75rem',
                      color: '#ffffff',
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="poetry"
                    name="الشعر والأدب 🖋️"
                    stroke="#f59e0b"
                    fillOpacity={1}
                    fill="url(#amberGradient)"
                  />
                  <Area
                    type="monotone"
                    dataKey="song"
                    name="الأغاني والموسيقى 🎙️"
                    stroke="#3b82f6"
                    fillOpacity={1}
                    fill="url(#blueGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* أدوات البحث والفلترة والنطاق الزمني والتحديد الشامل */}
        <div className="space-y-4">
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

          {/* منتقي النطاق الزمني والتحديد الشامل */}
          <div className="flex flex-wrap items-center justify-between gap-4 bg-neutral-900/60 p-4 rounded-xl border border-neutral-800/80">
            <div className="flex flex-wrap items-center gap-4">
              <span className="text-sm font-medium text-amber-400 flex items-center gap-1.5">
                📅 النطاق الزمني:
              </span>
              <div className="flex items-center gap-2">
                <label className="text-xs text-neutral-400">من:</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="p-2 rounded-lg bg-neutral-900 border border-neutral-700 text-sm text-neutral-200 focus:border-amber-500 focus:outline-none"
                />
              </div>
              <div className="flex items-center gap-2">
                <label className="text-xs text-neutral-400">إلى:</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="p-2 rounded-lg bg-neutral-900 border border-neutral-700 text-sm text-neutral-200 focus:border-amber-500 focus:outline-none"
                />
              </div>
              {(startDate || endDate) && (
                <button
                  onClick={() => {
                    setStartDate('');
                    setEndDate('');
                  }}
                  className="text-xs text-neutral-400 hover:text-amber-400 underline transition"
                >
                  إعادة ضبط
                </button>
              )}
            </div>

            {filteredCreations.length > 0 && (
              <button
                onClick={toggleSelectAll}
                className="text-xs text-amber-400 hover:text-amber-300 transition font-medium border border-amber-500/30 px-3 py-1.5 rounded-lg"
              >
                {selectedIds.length === filteredCreations.length ? 'إلغاء تحديد الكل' : 'تحديد كل المعروض'}
              </button>
            )}
          </div>
        </div>

        {/* قائمة الإنتاجات */}
        {loading ? (
          <p className="text-center text-neutral-500 py-12">جاري تحميل الإبداعات...</p>
        ) : filteredCreations.length === 0 ? (
          <div className="text-center py-16 bg-neutral-900/50 rounded-2xl border border-dashed border-neutral-800">
            <p className="text-neutral-400 text-lg">لا توجد إنتاجات مطابقة لمعايير البحث والفلترة</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredCreations.map((item) => (
              <div
                key={item.id}
                className={`p-6 rounded-2xl bg-neutral-900 border transition flex flex-col justify-between ${
                  selectedIds.includes(item.id)
                    ? 'border-amber-500 ring-1 ring-amber-500/50 bg-neutral-900/90'
                    : 'border-neutral-800 hover:border-amber-500/50'
                }`}
              >
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(item.id)}
                        onChange={() => toggleSelect(item.id)}
                        className="w-4 h-4 rounded border-neutral-700 text-amber-500 focus:ring-amber-500 bg-neutral-800 cursor-pointer"
                      />
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-bold ${
                          item.type === 'poetry'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                        }`}
                      >
                        {item.type === 'poetry' ? '🖋️ شعر' : '🎙️ أغنية'}
                      </span>
                    </div>
                    <span className="text-xs text-neutral-500">
                      {new Date(item.created_at).toLocaleDateString('ar-SA')}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-neutral-100 mb-2">{item.title}</h3>
                  <p className="text-neutral-400 text-sm whitespace-pre-line line-clamp-4 font-serif">
                    {item.content}
                  </p>
                </div>

                {/* أزرار الإجراءات: تصدير PDF وحذف فردي */}
                <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-neutral-800/80">
                  <button
                    onClick={() => exportToPDF(item)}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-neutral-800 hover:bg-neutral-700 text-neutral-200 border border-neutral-700 transition flex items-center gap-1.5"
                    title="تصدير إلى PDF"
                  >
                    📄 تصدير PDF
                  </button>

                  <button
                    onClick={() => handleDelete(item.id)}
                    disabled={actionLoadingId === item.id}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-950/40 hover:bg-red-900/60 text-red-400 border border-red-800/50 transition flex items-center gap-1.5 disabled:opacity-50"
                    title="حذف من Supabase"
                  >
                    {actionLoadingId === item.id ? 'جاري الحذف...' : '🗑️ حذف'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
