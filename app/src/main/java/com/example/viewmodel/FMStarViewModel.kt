package com.example.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.audio.AudioPlayerManager
import com.example.data.CloudRepository
import com.example.data.FMStarDatabase
import com.example.data.PoetryGenerator
import com.example.model.BassPreset
import com.example.model.CloudProjectConfig
import com.example.model.DspSettings
import com.example.model.PoetryItem
import com.example.model.RadioStation
import com.example.model.ReverbPreset
import com.example.model.StudioRecording
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class FMStarViewModel(application: Application) : AndroidViewModel(application) {

    private val db = FMStarDatabase.getDatabase(application)
    val repository = CloudRepository(db)
    val audioManager = AudioPlayerManager()

    // Navigation Tab (0: الرئيسية, 1: لوحة التحكم, 2: الإعدادات)
    private val _selectedTab = MutableStateFlow(0)
    val selectedTab: StateFlow<Int> = _selectedTab.asStateFlow()

    // Radio & Station State
    private val _selectedStation = MutableStateFlow<RadioStation?>(null)
    val selectedStation: StateFlow<RadioStation?> = _selectedStation.asStateFlow()

    val radioStations: StateFlow<List<RadioStation>> = repository.radioStations
    val isRadioPlaying: StateFlow<Boolean> = audioManager.isPlayingRadio
    val volume: StateFlow<Float> = audioManager.volume
    val spectrumBars: StateFlow<List<Float>> = audioManager.spectrumBars

    // Poetry Studio State
    val availableDialects = PoetryGenerator.availableDialects
    val availableMoods = PoetryGenerator.availableMoods

    private val _selectedDialect = MutableStateFlow(availableDialects[0])
    val selectedDialect: StateFlow<String> = _selectedDialect.asStateFlow()

    private val _selectedMood = MutableStateFlow(availableMoods[0])
    val selectedMood: StateFlow<String> = _selectedMood.asStateFlow()

    private val _customTopic = MutableStateFlow("")
    val customTopic: StateFlow<String> = _customTopic.asStateFlow()

    private val _isGeneratingPoem = MutableStateFlow(false)
    val isGeneratingPoem: StateFlow<Boolean> = _isGeneratingPoem.asStateFlow()

    private val _currentPoem = MutableStateFlow<PoetryItem?>(null)
    val currentPoem: StateFlow<PoetryItem?> = _currentPoem.asStateFlow()

    val isRecitingPoem: StateFlow<Boolean> = audioManager.isRecitingPoem
    val activeVerseIndex: StateFlow<Int> = audioManager.activeVerseIndex

    // Saved database collections
    val savedPoems = repository.savedPoems.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        emptyList()
    )

    val studioRecordings = repository.studioRecordings.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        emptyList()
    )

    // Cloud Dashboard State
    val cloudConfig = repository.config
    val cloudServices = repository.cloudServices
    val cloudLogs = repository.cloudLogs

    // DSP & Sound Deck State
    val dspSettings = repository.dspSettings

    // Recording Studio state
    private val _isRecording = MutableStateFlow(false)
    val isRecording: StateFlow<Boolean> = _isRecording.asStateFlow()
    private val _recordingSeconds = MutableStateFlow(0)
    val recordingSeconds: StateFlow<Int> = _recordingSeconds.asStateFlow()

    // Toast / Feedback message
    private val _snackbarMessage = MutableStateFlow<String?>(null)
    val snackbarMessage: StateFlow<String?> = _snackbarMessage.asStateFlow()

    init {
        // Pre-select first station
        viewModelScope.launch {
            radioStations.collect { stations ->
                if (_selectedStation.value == null && stations.isNotEmpty()) {
                    _selectedStation.value = stations.first()
                }
            }
        }
        // Initialize with a default generated poem
        generateNewPoem()
    }

    fun selectTab(tabIndex: Int) {
        _selectedTab.value = tabIndex
    }

    fun selectStation(station: RadioStation) {
        _selectedStation.value = station
        audioManager.setRadioPlaying(true)
        repository.addLog("INFO", "RADIO", "تشغيل المحطة: ${station.name} (${station.frequency})")
    }

    fun toggleRadioPlayback() {
        audioManager.toggleRadio()
        val playing = audioManager.isPlayingRadio.value
        val name = _selectedStation.value?.name ?: "FMStar"
        repository.addLog("INFO", "RADIO", if (playing) "بدء بث: $name" else "إيقاف مؤقت للبث")
    }

    fun setVolume(vol: Float) {
        audioManager.setVolume(vol)
    }

    fun setDialect(dialect: String) {
        _selectedDialect.value = dialect
    }

    fun setMood(mood: String) {
        _selectedMood.value = mood
    }

    fun setCustomTopic(topic: String) {
        _customTopic.value = topic
    }

    fun generateNewPoem() {
        viewModelScope.launch {
            _isGeneratingPoem.value = true
            audioManager.stopRecitation()
            repository.addLog("INFO", "VERTEX_AI", "توليد قصيدة شعرية جديدة: ${_selectedDialect.value} [${_selectedMood.value}]...")
            delay(650) // Simulation of Go Backend / Vertex AI agent processing
            val generated = PoetryGenerator.generatePoem(
                dialect = _selectedDialect.value,
                mood = _selectedMood.value,
                customTopic = _customTopic.value
            )
            _currentPoem.value = generated
            _isGeneratingPoem.value = false
            repository.addLog("SUCCESS", "ROUTER", "تم توليد القصيدة بنجاح: '${generated.title}'")
        }
    }

    fun toggleRecitation() {
        val poem = _currentPoem.value ?: return
        if (isRecitingPoem.value) {
            audioManager.stopRecitation()
            showSnackbar("تم إيقاف الإلقاء الصوتي")
        } else {
            audioManager.startRecitation(poem.verses.size)
            repository.addLog("INFO", "TTS_ENGINE", "بدء الإلقاء الصوتي المتزامن لقصيدة '${poem.title}' عبر Voice Engine")
            showSnackbar("بدأ الإلقاء الصوتي عبر Voice Engine")
        }
    }

    fun saveCurrentPoemToCloud() {
        val poem = _currentPoem.value ?: return
        viewModelScope.launch {
            repository.savePoem(poem)
            showSnackbar("تم حفظ القصيدة ومزامنتها مع PostgreSQL السحابي!")
        }
    }

    fun deleteSavedPoem(id: Long) {
        viewModelScope.launch {
            repository.deletePoem(id)
            showSnackbar("تم حذف القصيدة من قاعدة البيانات")
        }
    }

    fun playDjEffect(effectId: String) {
        audioManager.playDjEffect(effectId)
        repository.addLog("INFO", "DSP_ENGINE", "تشغيل مؤثر صوتي DJ: $effectId")
    }

    fun setReverbPreset(preset: ReverbPreset) {
        val current = dspSettings.value
        repository.updateDspSettings(current.copy(reverbPreset = preset, reverbMix = preset.level))
        audioManager.playDjEffect("oud")
        showSnackbar("تم تفعيل: ${preset.displayName}")
    }

    fun setBassPreset(preset: BassPreset) {
        val current = dspSettings.value
        repository.updateDspSettings(current.copy(bassPreset = preset, bassIntensity = preset.boostDb / 12f))
        audioManager.playDjEffect("sub_drop")
        showSnackbar("تم ضبط الباس: ${preset.displayName}")
    }

    fun setReverbMix(mix: Float) {
        val current = dspSettings.value
        repository.updateDspSettings(current.copy(reverbMix = mix))
    }

    fun setBassIntensity(intensity: Float) {
        val current = dspSettings.value
        repository.updateDspSettings(current.copy(bassIntensity = intensity))
    }

    fun toggleRecording() {
        if (_isRecording.value) {
            // Stop recording & save
            _isRecording.value = false
            val secs = _recordingSeconds.value
            _recordingSeconds.value = 0
            val formattedDur = String.format(Locale.US, "%02d:%02d", secs / 60, secs % 60)
            val dateStr = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date())
            val newRecording = StudioRecording(
                title = "تسجيل استوديو (${_selectedDialect.value})",
                durationFormatted = formattedDur,
                dialect = _selectedDialect.value,
                dateFormatted = dateStr,
                cloudSynced = true
            )
            viewModelScope.launch {
                repository.saveRecording(newRecording)
                showSnackbar("تم إيقاف التسجيل ورفعه إلى السحابة $formattedDur")
            }
        } else {
            // Start recording
            _isRecording.value = true
            _recordingSeconds.value = 0
            audioManager.playDjEffect("riser")
            viewModelScope.launch {
                while (_isRecording.value) {
                    delay(1000)
                    if (_isRecording.value) {
                        _recordingSeconds.value += 1
                    }
                }
            }
            showSnackbar("جاري التسجيل الصوتي المباشر...")
        }
    }

    fun deleteRecording(id: Long) {
        viewModelScope.launch {
            repository.deleteRecording(id)
            showSnackbar("تم حذف التسجيل")
        }
    }

    fun runTerraformPlan() {
        showSnackbar("جاري فحص خطة Terraform السحابية...")
        repository.triggerTerraformPlan {
            showSnackbar("خطة Terraform جاهزة وسليمة (0 أخطاء)")
        }
    }

    fun runTerraformApply() {
        showSnackbar("جاري نشر وتطبيق البنية التحتية السحابية...")
        repository.triggerTerraformApply {
            showSnackbar("تم نشر البنية السحابية بنجاح على مشروع ${cloudConfig.value.projectId}!")
        }
    }

    fun restartGoAudioEngine() {
        showSnackbar("جاري إعادة تشغيل Go Audio Engine...")
        repository.restartAudioEngine {
            showSnackbar("يعمل محرك Go Audio الآن بكفاءة عالية على المنفذ 8080")
        }
    }

    fun updateCloudConfig(newConfig: CloudProjectConfig) {
        repository.updateConfig(newConfig)
        showSnackbar("تم حفظ الإعدادات السحابية بنجاح!")
    }

    fun showSnackbar(message: String) {
        _snackbarMessage.value = message
    }

    fun clearSnackbar() {
        _snackbarMessage.value = null
    }
}
