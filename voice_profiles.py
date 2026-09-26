# voice_profiles.py - تحديث وتصنيف قائمة اللهجات والنبرات الصوتية

DIALECT_CONFIGS = {
    # --- اليمن والجزيرة العربية ---
    "yemeni_zamel": {"voice_id": "YEM_ZAMEL_ID", "stability": 0.30, "style": 0.85, "title": "اليمن - زوامل وإلقاء حماسي", "tempo": 128},
    "yemeni_humayni": {"voice_id": "YEM_HUMAYNI_ID", "stability": 0.45, "style": 0.60, "title": "اليمن - شعر حميني وتراثي", "tempo": 105},
    "khaleeji_nabati": {"voice_id": "KHAL_NABATI_ID", "stability": 0.35, "style": 0.75, "title": "الخليج - شعر نبطي وشيلات", "tempo": 120},
    "khaleeji_classic": {"voice_id": "KHAL_CLASSIC_ID", "stability": 0.50, "style": 0.50, "title": "الخليج - إلقاء دافئ وهادئ", "tempo": 90},

    # --- الشام والعراق ---
    "iraqi_darami": {"voice_id": "IRQ_DARAMI_ID", "stability": 0.25, "style": 0.90, "title": "العراق - دارمي وأبوذية (حزين/وجداني)", "tempo": 80}, # إحساس عالي
    "syrian_zajal": {"voice_id": "SYR_ZAJAL_ID", "stability": 0.40, "style": 0.70, "title": "سوريا - زجل وشعر شامي", "tempo": 115},
    "lebanese_romantic": {"voice_id": "LEB_ROMANTIC_ID", "stability": 0.55, "style": 0.45, "title": "لبنان - خواطر وإلقاء رومانسي", "tempo": 85},

    # --- مصر والمغرب ---
    "egyptian_ammiya": {"voice_id": "EGY_AMMIYA_ID", "stability": 0.50, "style": 0.65, "title": "مصر - شعر عامي ومسرحي", "tempo": 110},
    "maghrebi_malhoun": {"voice_id": "MAG_MALHOUN_ID", "stability": 0.35, "style": 0.75, "title": "المغرب الكبير - شعر ملحون وموال", "tempo": 95},

    # --- الفصيح ---
    "fus_ha_jahili": {"voice_id": "FUS_JAHILI_ID", "stability": 0.20, "style": 0.80, "title": "فصيح - إلقاء جاهلي ورصين (قوي)", "tempo": 100},
    "fus_ha_modern": {"voice_id": "FUS_MODERN_ID", "stability": 0.45, "style": 0.55, "title": "فصيح - شعر حديث وخواطر", "tempo": 90},

    # --- الأنماط العالمية ---
    "turkish_dramatic": {"voice_id": "TUR_DRAMA_ID", "stability": 0.30, "style": 0.80, "title": "التركية - إلقاء درامي ورومانسي", "tempo": 88},
    "kurdish_folklore": {"voice_id": "KUR_FOLK_ID", "stability": 0.35, "style": 0.75, "title": "الكردية - إلقاء جبالي وفلكلوري", "tempo": 118},
    "hindi_urdu_ghazal": {"voice_id": "HIN_URDU_ID", "stability": 0.40, "style": 0.60, "title": "الهندية / الأردو - غزل وخواطر", "tempo": 82},
    "russian_classic": {"voice_id": "RUS_CLASSIC_ID", "stability": 0.25, "style": 0.85, "title": "الروسية - إلقاء كلاسيكي عميق", "tempo": 75},
    "asian_zen": {"voice_id": "ASI_ZEN_ID", "stability": 0.60, "style": 0.40, "title": "الآسيوية (كوري/صيني) - شعر موزون وهادئ", "tempo": 70},
    "western_spoken_word": {"voice_id": "ENG_SPOKEN_ID", "stability": 0.35, "style": 0.70, "title": "الغربية (إنجليزي) - Spoken Word إيقاعي", "tempo": 105},
}
