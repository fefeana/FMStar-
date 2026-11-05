#!/bin/bash
# تفعيل الطبقة 3 (FMStar Audio Platform)
cp "$(dirname "$0")/index.html" index.html
cp "$(dirname "$0")/index.html" public/index.html 2>/dev/null || true
echo "✅ تم تفعيل الطبقة الاحتياطية 3 (منصة FMStar الشاملة) بنجاح."
