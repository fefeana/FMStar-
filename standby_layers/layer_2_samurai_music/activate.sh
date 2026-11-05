#!/bin/bash
# تفعيل الطبقة 2 (Samurai Music & Canvas Mixer)
cp "$(dirname "$0")/index.html" index.html
cp "$(dirname "$0")/index.html" public/index.html 2>/dev/null || true
echo "✅ تم تفعيل الطبقة الاحتياطية 2 (ساموراي ميوزيك وميكسر الكانفاس) بنجاح."
