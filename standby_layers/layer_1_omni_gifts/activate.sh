#!/bin/bash
# تفعيل الطبقة 1 (Omni Gifts)
cp "$(dirname "$0")/index.html" index.html
cp "$(dirname "$0")/index.html" public/index.html 2>/dev/null || true
echo "✅ تم تفعيل الطبقة الاحتياطية 1 (استوديو الإهداءات) بنجاح."
