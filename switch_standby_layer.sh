#!/bin/bash
# switch_standby_layer.sh
# أداة التبديل والتبديل السريع بين طبقات المشروع الاحتياطية قيد الاستعداد
# Standby Layer Failover & Activation Tool

set -e

LAYER="$1"

if [ -z "$LAYER" ]; then
    echo "=========================================================="
    echo "🛡️ نظام إدارة طبقات المشروع الاحتياطية (Standby Layers)"
    echo "=========================================================="
    echo "الاستخدام: ./switch_standby_layer.sh [1 | 2 | 3]"
    echo ""
    echo "  1: تفعيل [الطبقة 1: استوديو الإهداءات الشامل - Omni Gifts]"
    echo "  2: تفعيل [الطبقة 2: استوديو الساموراي والميكسر - Samurai Music & Canvas]"
    echo "  3: تفعيل [الطبقة 3: استوديو FMStar واللهجات الشعرية - FMStar Audio Platform]"
    echo "=========================================================="
    exit 1
fi

case "$LAYER" in
    1)
        echo "⚡ جارٍ تفعيل [الطبقة الاحتياطية 1: استوديو الإهداءات] كطبقة إنتاج أساسية..."
        cp standby_layers/layer_1_omni_gifts/index.html index.html
        cp standby_layers/layer_1_omni_gifts/index.html public/index.html 2>/dev/null || true
        echo "✅ تم تفعيل الطبقة 1 بنجاح! التطبيق يعمل الآن في وضع: استوديو الإهداءات."
        ;;
    2)
        echo "⚡ جارٍ تفعيل [الطبقة الاحتياطية 2: ساموراي ميوزيك وميكسر الكانفاس] كطبقة إنتاج أساسية..."
        cp standby_layers/layer_2_samurai_music/index.html index.html
        cp standby_layers/layer_2_samurai_music/index.html public/index.html 2>/dev/null || true
        echo "✅ تم تفعيل الطبقة 2 بنجاح! التطبيق يعمل الآن في وضع: استوديو الساموراي والموجات الصوتية."
        ;;
    3)
        echo "⚡ جارٍ تفعيل [الطبقة الاحتياطية 3: استوديو FMStar الشامل] كطبقة إنتاج أساسية..."
        cp standby_layers/layer_3_fmstar_audio/index.html index.html
        cp standby_layers/layer_3_fmstar_audio/index.html public/index.html 2>/dev/null || true
        echo "✅ تم تفعيل الطبقة 3 بنجاح! التطبيق يعمل الآن في وضع: استوديو FMStar واللهجات التراثية."
        ;;
    *)
        echo "❌ خيار غير صالح. اختر 1 أو 2 أو 3."
        exit 1
        ;;
esac
