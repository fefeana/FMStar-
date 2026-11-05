#!/bin/bash
# push_to_github.sh - أداة الرفع الآمن باستخدام المفاتيح المؤقتة (GitHub Temporary Tokens)
set -e

REPO="$1"
TOKEN="$2"
COMMIT_MSG="${3:-Update FMStar AI Studio & Standby Layers}"

if [ -z "$REPO" ] || [ -z "$TOKEN" ]; then
    echo "=========================================================="
    echo "🔐 نظام الرفع الآمن بالمفاتيح المؤقتة (GitHub Temporary PAT)"
    echo "=========================================================="
    echo "الاستخدام:"
    echo "  ./push_to_github.sh <username/repo> <temporary_token> [commit_message]"
    echo ""
    echo "مثال:"
    echo "  ./push_to_github.sh 'username/fmstar-ai' 'github_pat_xxxx' 'تحديث جديد'"
    echo "=========================================================="
    exit 1
fi

# تنظيف اسم المستودع في حال تم إدخال رابط كامل
CLEAN_REPO=$(echo "$REPO" | sed -E "s/https:\/\/.*@//; s/https:\/\///; s/git@github.com://; s/\.git$//; s/github\.com\///")

echo "📦 تجهيز الـ Commit والملفات..."
git config --global --add safe.directory /app/applet 2>/dev/null || true
git add .
git commit -m "$COMMIT_MSG" 2>/dev/null || true

echo "🚀 جاري الرفع إلى GitHub (${CLEAN_REPO}) عبر المفتاح المؤقت..."
git push "https://x-access-token:${TOKEN}@github.com/${CLEAN_REPO}.git" main:main

echo "🔒 تنظيف ومسح المفتاح المؤقت من تكوين Git..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${CLEAN_REPO}.git"

unset TOKEN
echo "✅ تم الرفع بنجاح! وتم مسح المفتاح المؤقت فوراً دون حفظه في أي مكان."
