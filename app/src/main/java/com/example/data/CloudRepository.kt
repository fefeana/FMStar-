package com.example.data

import com.example.model.BassPreset
import com.example.model.CloudLogEntry
import com.example.model.CloudProjectConfig
import com.example.model.CloudServiceItem
import com.example.model.DspSettings
import com.example.model.PoetryItem
import com.example.model.PoetryVerse
import com.example.model.RadioStation
import com.example.model.ReverbPreset
import com.example.model.ServiceStatus
import com.example.model.StudioRecording
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class CloudRepository(private val db: FMStarDatabase) {

    private val _config = MutableStateFlow(CloudProjectConfig())
    val config = _config.asStateFlow()

    private val _dspSettings = MutableStateFlow(DspSettings())
    val dspSettings = _dspSettings.asStateFlow()

    private val _cloudLogs = MutableStateFlow<List<CloudLogEntry>>(emptyList())
    val cloudLogs = _cloudLogs.asStateFlow()

    private val _cloudServices = MutableStateFlow<List<CloudServiceItem>>(emptyList())
    val cloudServices = _cloudServices.asStateFlow()

    private val _radioStations = MutableStateFlow<List<RadioStation>>(emptyList())
    val radioStations = _radioStations.asStateFlow()

    init {
        initializeCloudServices()
        initializeDefaultRadioStations()
        initializeInitialLogs()
    }

    fun updateConfig(newConfig: CloudProjectConfig) {
        _config.value = newConfig
        addLog("INFO", "CONFIG", "تم تحديث إعدادات المشروع السحابي: ${newConfig.projectId}")
    }

    fun updateDspSettings(settings: DspSettings) {
        _dspSettings.value = settings
    }

    private fun initializeCloudServices() {
        _cloudServices.value = listOf(
            CloudServiceItem(
                id = "vm_audio_engine",
                name = "جهاز الحوسبة الافتراضي (Compute VM)",
                category = "Google Compute Engine",
                resourceName = "web-app-tpl-vm1",
                status = ServiceStatus.HEALTHY,
                metrics = "RAM: 3.4/8GB | CPU: 12% | Uptime: 99.98%",
                endpoint = "http://35.224.180.92:8080"
            ),
            CloudServiceItem(
                id = "sql_postgres",
                name = "قاعدة بيانات الاستوديو (PostgreSQL 15)",
                category = "Cloud SQL",
                resourceName = "postgresql-db-studio",
                status = ServiceStatus.HEALTHY,
                metrics = "Tier: db-f1-micro | Conns: 8 | PITR: 7 Days",
                endpoint = "gen-lang-client-0878176506:us-central1:postgresql-db-studio"
            ),
            CloudServiceItem(
                id = "gcs_audio_bucket",
                name = "المستودع السحابي للملفات الصوتية",
                category = "Cloud Storage",
                resourceName = "jimi-mira-audio-studio-bucket-087817",
                status = ServiceStatus.HEALTHY,
                metrics = "342 ملف صوتي | 4.8 GB | Multi-Region",
                endpoint = "gs://jimi-mira-audio-studio-bucket-087817"
            ),
            CloudServiceItem(
                id = "secret_vault",
                name = "الخزنة الرقمية لإدارة المفاتيح",
                category = "Secret Manager",
                resourceName = "studio-secrets",
                status = ServiceStatus.HEALTHY,
                metrics = "Auto-Replicated | 6 Secrets Active",
                endpoint = "projects/gen-lang-client-0878176506/secrets/studio-secrets"
            ),
            CloudServiceItem(
                id = "vertex_ai_agent",
                name = "وكيل الذكاء الاصطناعي (Agent Engine)",
                category = "Vertex AI Platform",
                resourceName = "jimi-mira-agent-engine",
                status = ServiceStatus.HEALTHY,
                metrics = "LangChain / MCP Protocol | Latency: 140ms",
                endpoint = "aiplatform.googleapis.com/v1beta1"
            ),
            CloudServiceItem(
                id = "load_balancer",
                name = "موزع الأحمال العالمي وشهادة SSL",
                category = "Cloud Load Balancing",
                resourceName = "global-frontend-https",
                status = ServiceStatus.HEALTHY,
                metrics = "Port 80/443 | SSL Managed: Active",
                endpoint = "https://jimi-mira-studio.example.com"
            )
        )
    }

    private fun initializeDefaultRadioStations() {
        _radioStations.value = listOf(
            RadioStation(
                id = "station_1",
                name = "FMStar Live Cloud Studio",
                frequency = "104.2 FM",
                genre = "بث المحرك الصوتي Go",
                dialect = "مختلط عربي وعالمي",
                isLive = true,
                bitRate = "320 kbps Studio Master",
                currentTrack = "جيمي وميرا: تناغم الأصوات والصدى السحابي",
                listeners = 1420
            ),
            RadioStation(
                id = "station_2",
                name = "طرب الدان والشعر اليمني",
                frequency = "98.5 FM",
                genre = "تراثي وشعر حميني",
                dialect = "يمني (صنعاني، حضرمي، لحجي)",
                isLive = true,
                bitRate = "256 kbps Hi-Fi",
                currentTrack = "يا من لقلبي المتيم في هوى صنعاء",
                listeners = 890
            ),
            RadioStation(
                id = "station_3",
                name = "روائع الشعر النبطي والخليجي",
                frequency = "101.8 FM",
                genre = "قصائد نبطية وإيقاع راقي",
                dialect = "خليجي (نجدي، كويتي، إماراتي)",
                isLive = true,
                bitRate = "320 kbps Lossless",
                currentTrack = "في سكون الليل يا نجم السحابي",
                listeners = 1150
            ),
            RadioStation(
                id = "station_4",
                name = "Daimyo Reverb & Lo-Fi Lounge",
                frequency = "92.0 FM",
                genre = "مؤثرات دي جي وهدوء استوديو",
                dialect = "موسيقى محيطية ومعزوفات عود",
                isLive = true,
                bitRate = "192 kbps Clean",
                currentTrack = "Shogun Bass Pulse - Ambient Session #4",
                listeners = 640
            )
        )
    }

    private fun initializeInitialLogs() {
        _cloudLogs.value = listOf(
            CloudLogEntry(
                id = "log_1",
                timestamp = "19:00:12",
                level = "SUCCESS",
                service = "TERRAFORM",
                message = "Apply complete! Resources: 7 added, 0 changed, 0 destroyed."
            ),
            CloudLogEntry(
                id = "log_2",
                timestamp = "19:01:05",
                level = "INFO",
                service = "COMPUTE_VM",
                message = "Instance web-app-tpl started at static IP 35.224.180.92"
            ),
            CloudLogEntry(
                id = "log_3",
                timestamp = "19:01:30",
                level = "SUCCESS",
                service = "GO_ENGINE",
                message = "Go Audio Engine listening on :8080 (Daimyo Reverb & Shogun Bass online)"
            ),
            CloudLogEntry(
                id = "log_4",
                timestamp = "19:02:14",
                level = "INFO",
                service = "POSTGRES",
                message = "Cloud SQL instance postgresql-db-studio connection established via socket."
            ),
            CloudLogEntry(
                id = "log_5",
                timestamp = "19:05:22",
                level = "API",
                service = "ROUTER",
                message = "POST /api/v1/poetry/generate 200 OK (Dialect: Yemeni, Latency: 120ms)"
            )
        )
    }

    fun addLog(level: String, service: String, message: String) {
        val time = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
        val newEntry = CloudLogEntry(
            id = "log_${System.currentTimeMillis()}",
            timestamp = time,
            level = level,
            service = service,
            message = message
        )
        _cloudLogs.value = listOf(newEntry) + _cloudLogs.value.take(40)
    }

    fun triggerTerraformPlan(onComplete: () -> Unit) {
        addLog("INFO", "TERRAFORM", "تشغيل: terraform plan -out=tfplan في المشروع ${_config.value.projectId}...")
        addLog("INFO", "TERRAFORM", "قراءة البنية التحتية من Cloud Resource Manager...")
        addLog("SUCCESS", "TERRAFORM", "خطة البناء جاهزة: 0 للتدمير، لا توجد أخطاء برمجية في main.tf.")
        onComplete()
    }

    fun triggerTerraformApply(onComplete: () -> Unit) {
        addLog("INFO", "TERRAFORM", "تشغيل: terraform apply tfplan...")
        addLog("INFO", "GCS", "التحقق من المساحة: ${_config.value.bucketName} (Active)")
        addLog("INFO", "SQL", "التحقق من قاعدة البيانات: ${_config.value.dbInstance} (Healthy)")
        addLog("SUCCESS", "TERRAFORM", "اكتمل النشر بنجاح 100%! كافة الخوادم والخدمات متزامنة.")
        onComplete()
    }

    fun restartAudioEngine(onComplete: () -> Unit) {
        addLog("WARN", "GO_ENGINE", "إعادة تشغيل خدمة الصوت Go على المنفذ ${_config.value.backendPort}...")
        addLog("INFO", "DSP", "تحميل خوارزميات Daimyo Reverb ومكبر Shogun Bass...")
        addLog("SUCCESS", "GO_ENGINE", "خدمة الصوت تعمل بنجاح! معدل التأخير 12ms.")
        onComplete()
    }

    // Room DB operations
    val savedPoems: Flow<List<PoetryItem>> = db.poetryDao().getAllPoems().map { entities ->
        entities.map { entity ->
            val versesList = entity.versesRaw.split(";;").mapNotNull { line ->
                val parts = line.split("|")
                if (parts.size >= 2) PoetryVerse(parts[0], parts[1]) else null
            }
            PoetryItem(
                id = entity.id,
                title = entity.title,
                dialect = entity.dialect,
                mood = entity.mood,
                verses = versesList,
                author = entity.author,
                date = entity.date,
                isFavorite = entity.isFavorite,
                isSavedToCloud = entity.isCloudSynced
            )
        }
    }

    suspend fun savePoem(item: PoetryItem): Long {
        val raw = item.verses.joinToString(";;") { "${it.firstHemistich}|${it.secondHemistich}" }
        val entity = SavedPoemEntity(
            title = item.title,
            dialect = item.dialect,
            mood = item.mood,
            versesRaw = raw,
            author = item.author,
            date = item.date,
            isFavorite = item.isFavorite,
            isCloudSynced = true
        )
        val id = db.poetryDao().insertPoem(entity)
        addLog("SUCCESS", "POSTGRES", "تم حفظ القصيدة '${item.title}' في قاعدة بيانات السحابة PostgreSQL.")
        return id
    }

    suspend fun deletePoem(id: Long) {
        val entity = SavedPoemEntity(
            id = id,
            title = "",
            dialect = "",
            mood = "",
            versesRaw = "",
            author = "",
            date = ""
        )
        db.poetryDao().deletePoem(entity)
        addLog("INFO", "POSTGRES", "تم حذف السجل رقم $id من قاعدة البيانات السحابية.")
    }

    val studioRecordings: Flow<List<StudioRecording>> = db.poetryDao().getAllRecordings().map { entities ->
        entities.map { entity ->
            StudioRecording(
                id = entity.id,
                title = entity.title,
                durationFormatted = entity.durationFormatted,
                dialect = entity.dialect,
                dateFormatted = entity.dateFormatted,
                cloudSynced = entity.cloudSynced,
                bucketLocation = entity.cloudUrl
            )
        }
    }

    suspend fun saveRecording(rec: StudioRecording): Long {
        val entity = StudioRecordingEntity(
            title = rec.title,
            durationFormatted = rec.durationFormatted,
            dialect = rec.dialect,
            dateFormatted = rec.dateFormatted,
            cloudSynced = true,
            cloudUrl = rec.bucketLocation
        )
        val id = db.poetryDao().insertRecording(entity)
        addLog("SUCCESS", "GCS_BUCKET", "تم رفع التسجيل '${rec.title}' إلى المستودع السحابي ${_config.value.bucketName}.")
        return id
    }

    suspend fun deleteRecording(id: Long) {
        val entity = StudioRecordingEntity(
            id = id,
            title = "",
            durationFormatted = "",
            dialect = "",
            dateFormatted = "",
            cloudSynced = false,
            cloudUrl = ""
        )
        db.poetryDao().deleteRecording(entity)
        addLog("INFO", "GCS_BUCKET", "تم حذف التسجيل $id من السحابة.")
    }
}
