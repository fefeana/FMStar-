'use client';
import { useState, useEffect } from 'react';

export default function RealtimeStudioNotifier() {
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    // الاتصال بمقبض الإشعارات المباشرة (WebSocket)
    const ws = new WebSocket('ws://localhost:8000/ws/notifications');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'CREATION_COMPLETE') {
        setNotification(`✨ اكتمل إنشاء مشروعك: "${data.title}" بنجاح!`);
        
        // إظهار إشعار النظام المباشر للمتصفح
        if (Notification.permission === 'granted') {
          new Notification('FMStar Studio AI', {
            body: `تم الانتهاء من توليد ${data.title}، يمكنك الاستماع الآن!`,
            icon: '/icon.png'
          });
        }
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div>
      {notification && (
        <div className="fixed bottom-5 right-5 bg-amber-500 text-neutral-950 px-6 py-4 rounded-2xl shadow-2xl font-bold flex items-center gap-3 animate-bounce z-50">
          <span>🔔</span>
          <p>{notification}</p>
          <button onClick={() => setNotification(null)} className="mr-4 text-xs underline">إغلاق</button>
        </div>
      )}
    </div>
  );
}
