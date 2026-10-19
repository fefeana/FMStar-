'use client';
import { useEffect, useState } from 'react';

export default function useStudioNotifications() {
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    // الاتصال بخدمة الـ SSE الحديثة
    const eventSource = new EventSource('/api/v2/notifications/stream?user_id=current_user');

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'CREATION_COMPLETE') {
        setNotification(data.message);
        
        // إظهار إشعار سطح المكتب للمتصفح إذا كان متاحاً
        if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
          new Notification('FMStar Studio AI', {
            body: data.message,
            icon: '/icon.png'
          });
        }
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE Connection error, retrying...', err);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return notification;
}
