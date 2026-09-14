package com.example.model

data class CloudProjectConfig(
    val projectId: String = "gen-lang-client-0878176506",
    val region: String = "us-central1",
    val vmInstanceName: String = "web-app-tpl-vm1",
    val vmIp: String = "35.224.180.92",
    val backendPort: Int = 8080,
    val frontendPort: Int = 3001,
    val bucketName: String = "jimi-mira-audio-studio-bucket-087817",
    val dbInstance: String = "postgresql-db-studio",
    val secretId: String = "studio-secrets",
    val billingStatus: String = "نشط (Active)",
    val isConnected: Boolean = true,
    val vmMemory: String = "8 GB RAM",
    val vmDisk: String = "1000 GB SSD (pd-ssd)",
    val audioEngine: String = "Go High-Concurrency Audio DSP v1.21.5"
)

enum class ServiceStatus {
    HEALTHY, WARNING, STOPPED, DEPLOYING
}

data class CloudServiceItem(
    val id: String,
    val name: String,
    val category: String,
    val resourceName: String,
    val status: ServiceStatus,
    val metrics: String,
    val endpoint: String
)

data class CloudLogEntry(
    val id: String,
    val timestamp: String,
    val level: String, // "INFO", "SUCCESS", "WARN", "API"
    val service: String,
    val message: String
)

data class RadioStation(
    val id: String,
    val name: String,
    val frequency: String,
    val genre: String,
    val dialect: String,
    val isLive: Boolean,
    val bitRate: String,
    val currentTrack: String,
    val listeners: Int
)

data class PoetryVerse(
    val firstHemistich: String, // الصدر
    val secondHemistich: String  // العجز
)

data class PoetryItem(
    val id: Long = 0,
    val title: String,
    val dialect: String,
    val mood: String,
    val verses: List<PoetryVerse>,
    val author: String = "جيمي & ميرا الذكي",
    val date: String,
    val isSavedToCloud: Boolean = true,
    val isFavorite: Boolean = false,
    val hasRecitation: Boolean = true
)

enum class ReverbPreset(val displayName: String, val level: Float) {
    OFF("مُغلق", 0.0f),
    STUDIO_ROOM("غرفة الاستوديو", 0.25f),
    DAIMYO_REVERB("دايميو ريفيرب (Daimyo)", 0.65f),
    GRAND_HALL("قاعة كبرى (Concert)", 0.85f),
    SPACE_ECHO("صدى الفضاء (Cosmic)", 0.95f)
}

enum class BassPreset(val displayName: String, val boostDb: Float) {
    NATURAL("طبيعي", 0f),
    SHOGUN_BASS("شوجن باس (Shogun)", 6f),
    DEEP_SUB("صب-باس عميق", 9f),
    CLUB_BOOST("كلوب دي جي (Club)", 12f)
}

data class DspSettings(
    val reverbPreset: ReverbPreset = ReverbPreset.DAIMYO_REVERB,
    val reverbMix: Float = 0.55f,
    val bassPreset: BassPreset = BassPreset.SHOGUN_BASS,
    val bassIntensity: Float = 0.70f,
    val pitchShift: Float = 0f,
    val tempo: Float = 1.0f,
    val djFilterCutoff: Float = 0.5f
)

data class DjSoundEffect(
    val id: String,
    val name: String,
    val subtitle: String,
    val toneFrequency: Int,
    val durationMs: Int
)

data class StudioRecording(
    val id: Long = 0,
    val title: String,
    val durationFormatted: String,
    val dialect: String,
    val dateFormatted: String,
    val cloudSynced: Boolean = true,
    val bucketLocation: String = "gs://jimi-mira-audio-studio-bucket-087817/recordings/"
)
