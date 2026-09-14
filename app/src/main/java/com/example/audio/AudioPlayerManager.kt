package com.example.audio

import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlin.math.sin
import kotlin.random.Random

class AudioPlayerManager {
    private val scope = CoroutineScope(Dispatchers.Default)
    private var visualizerJob: Job? = null

    // Amplitudes for the dynamic visualizer (16 frequency bars)
    private val _spectrumBars = MutableStateFlow(List(16) { 0.15f })
    val spectrumBars: StateFlow<List<Float>> = _spectrumBars.asStateFlow()

    // Radio playback state
    private val _isPlayingRadio = MutableStateFlow(false)
    val isPlayingRadio: StateFlow<Boolean> = _isPlayingRadio.asStateFlow()

    // Current Station Volume
    private val _volume = MutableStateFlow(0.85f)
    val volume: StateFlow<Float> = _volume.asStateFlow()

    // Poetry recitation state
    private val _isRecitingPoem = MutableStateFlow(false)
    val isRecitingPoem: StateFlow<Boolean> = _isRecitingPoem.asStateFlow()

    private val _activeVerseIndex = MutableStateFlow(-1)
    val activeVerseIndex: StateFlow<Int> = _activeVerseIndex.asStateFlow()

    init {
        startVisualizerLoop()
    }

    private fun startVisualizerLoop() {
        visualizerJob?.cancel()
        visualizerJob = scope.launch {
            while (isActive) {
                if (_isPlayingRadio.value || _isRecitingPoem.value) {
                    val baseEnergy = if (_isRecitingPoem.value) 0.6f else 0.85f
                    val newBars = List(16) { index ->
                        val curve = sin(index.toDouble() / 15.0 * Math.PI).toFloat()
                        val randomVariance = Random.nextFloat() * 0.45f
                        ((curve * 0.55f + randomVariance) * baseEnergy * _volume.value).coerceIn(0.08f, 1.0f)
                    }
                    _spectrumBars.value = newBars
                } else {
                    // Ambient idling noise
                    _spectrumBars.value = List(16) { (0.05f + Random.nextFloat() * 0.08f) }
                }
                delay(65)
            }
        }
    }

    fun toggleRadio() {
        val newState = !_isPlayingRadio.value
        _isPlayingRadio.value = newState
        if (newState) {
            playSynthTone(frequency = 520, durationMs = 120, sampleRate = 44100)
        }
    }

    fun setRadioPlaying(playing: Boolean) {
        _isPlayingRadio.value = playing
    }

    fun setVolume(newVolume: Float) {
        _volume.value = newVolume.coerceIn(0f, 1f)
    }

    fun startRecitation(verseCount: Int, onVerseChanged: (Int) -> Unit = {}) {
        scope.launch {
            _isRecitingPoem.value = true
            playSynthTone(frequency = 440, durationMs = 250, sampleRate = 44100)
            for (i in 0 until verseCount) {
                if (!_isRecitingPoem.value) break
                _activeVerseIndex.value = i
                onVerseChanged(i)
                // Audible chime tone transition between verses
                playSynthTone(frequency = 330 + (i * 40), durationMs = 180, sampleRate = 44100)
                delay(3200)
            }
            _isRecitingPoem.value = false
            _activeVerseIndex.value = -1
        }
    }

    fun stopRecitation() {
        _isRecitingPoem.value = false
        _activeVerseIndex.value = -1
    }

    /**
     * Synthesizes audio waveforms directly via AudioTrack for authentic DJ Sound FX.
     */
    fun playDjEffect(effectId: String) {
        scope.launch {
            when (effectId) {
                "airhorn" -> {
                    // DJ Airhorn sequence
                    playSynthTone(587, 100)
                    delay(30)
                    playSynthTone(587, 100)
                    delay(30)
                    playSynthTone(587, 280)
                }
                "scratch" -> {
                    // Vinyl scratch sweep
                    playFrequencySweep(fromFreq = 800, toFreq = 200, durationMs = 180)
                }
                "riser" -> {
                    // Filter Riser sweep
                    playFrequencySweep(fromFreq = 180, toFreq = 950, durationMs = 350)
                }
                "sub_drop" -> {
                    // Shogun Bass Sub Drop
                    playFrequencySweep(fromFreq = 160, toFreq = 45, durationMs = 400)
                }
                "oud" -> {
                    // Traditional Oud chord plucks
                    playSynthTone(220, 150)
                    delay(40)
                    playSynthTone(277, 150)
                    delay(40)
                    playSynthTone(330, 220)
                }
                "applause" -> {
                    // Noise burst simulation
                    playWhiteNoise(durationMs = 300)
                }
                else -> {
                    playSynthTone(440, 150)
                }
            }
        }
    }

    private fun playSynthTone(frequency: Int, durationMs: Int, sampleRate: Int = 44100) {
        try {
            val numSamples = (sampleRate * (durationMs / 1000.0)).toInt().coerceAtLeast(100)
            val generatedSnd = ShortArray(numSamples)
            val angularFreq = 2.0 * Math.PI * frequency / sampleRate

            for (i in 0 until numSamples) {
                // Apply subtle attack & decay envelope to avoid speaker clicks
                val envelope = when {
                    i < 200 -> i / 200.0
                    i > numSamples - 300 -> (numSamples - i) / 300.0
                    else -> 1.0
                }
                val sample = sin(angularFreq * i) * envelope * 0.7
                generatedSnd[i] = (sample * Short.MAX_VALUE).toInt().toShort()
            }

            val audioTrack = AudioTrack.Builder()
                .setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                        .build()
                )
                .setAudioFormat(
                    AudioFormat.Builder()
                        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                        .setSampleRate(sampleRate)
                        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                        .build()
                )
                .setBufferSizeInBytes(numSamples * 2)
                .setTransferMode(AudioTrack.MODE_STATIC)
                .build()

            audioTrack.write(generatedSnd, 0, numSamples)
            audioTrack.play()
            // Release after playing
            scope.launch {
                delay(durationMs.toLong() + 100)
                audioTrack.stop()
                audioTrack.release()
            }
        } catch (_: Exception) {
            // Graceful fallback
        }
    }

    private fun playFrequencySweep(fromFreq: Int, toFreq: Int, durationMs: Int, sampleRate: Int = 44100) {
        try {
            val numSamples = (sampleRate * (durationMs / 1000.0)).toInt().coerceAtLeast(100)
            val generatedSnd = ShortArray(numSamples)

            for (i in 0 until numSamples) {
                val progress = i.toDouble() / numSamples
                val currentFreq = fromFreq + (toFreq - fromFreq) * progress
                val angularFreq = 2.0 * Math.PI * currentFreq / sampleRate
                val envelope = (1.0 - progress * 0.3)
                val sample = sin(angularFreq * i) * envelope * 0.65
                generatedSnd[i] = (sample * Short.MAX_VALUE).toInt().toShort()
            }

            val audioTrack = AudioTrack.Builder()
                .setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                        .build()
                )
                .setAudioFormat(
                    AudioFormat.Builder()
                        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                        .setSampleRate(sampleRate)
                        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                        .build()
                )
                .setBufferSizeInBytes(numSamples * 2)
                .setTransferMode(AudioTrack.MODE_STATIC)
                .build()

            audioTrack.write(generatedSnd, 0, numSamples)
            audioTrack.play()
            scope.launch {
                delay(durationMs.toLong() + 100)
                audioTrack.stop()
                audioTrack.release()
            }
        } catch (_: Exception) {}
    }

    private fun playWhiteNoise(durationMs: Int, sampleRate: Int = 44100) {
        try {
            val numSamples = (sampleRate * (durationMs / 1000.0)).toInt().coerceAtLeast(100)
            val generatedSnd = ShortArray(numSamples)
            val random = Random.Default

            for (i in 0 until numSamples) {
                val decay = (1.0 - i.toDouble() / numSamples)
                val sample = (random.nextDouble() * 2.0 - 1.0) * decay * 0.4
                generatedSnd[i] = (sample * Short.MAX_VALUE).toInt().toShort()
            }

            val audioTrack = AudioTrack.Builder()
                .setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_MEDIA)
                        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                        .build()
                )
                .setAudioFormat(
                    AudioFormat.Builder()
                        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                        .setSampleRate(sampleRate)
                        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                        .build()
                )
                .setBufferSizeInBytes(numSamples * 2)
                .setTransferMode(AudioTrack.MODE_STATIC)
                .build()

            audioTrack.write(generatedSnd, 0, numSamples)
            audioTrack.play()
            scope.launch {
                delay(durationMs.toLong() + 100)
                audioTrack.stop()
                audioTrack.release()
            }
        } catch (_: Exception) {}
    }
}
