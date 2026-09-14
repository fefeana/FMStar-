package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.CloudDone
import androidx.compose.material.icons.filled.GraphicEq
import androidx.compose.material.icons.filled.Headphones
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.MusicNote
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Radio
import androidx.compose.material.icons.filled.RecordVoiceOver
import androidx.compose.material.icons.filled.SpatialAudioOff
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.BassPreset
import com.example.model.RadioStation
import com.example.model.ReverbPreset
import com.example.ui.components.AudioVisualizerCanvas
import com.example.ui.components.DjPadButton
import com.example.ui.components.SectionTitle
import com.example.ui.theme.CoralWarning
import com.example.ui.theme.CyanNeon
import com.example.ui.theme.EmeraldLive
import com.example.ui.theme.GoldAccent
import com.example.ui.theme.GoldGlow
import com.example.ui.theme.PurpleAccent
import com.example.ui.theme.PurpleDark
import com.example.ui.theme.StudioBorder
import com.example.ui.theme.StudioCardBg
import com.example.ui.theme.StudioCardElevated
import com.example.ui.theme.StudioDarkBg
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import com.example.ui.theme.TextSecondary
import com.example.viewmodel.FMStarViewModel

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun MainStudioScreen(
    viewModel: FMStarViewModel,
    modifier: Modifier = Modifier
) {
    val selectedStation by viewModel.selectedStation.collectAsState()
    val stations by viewModel.radioStations.collectAsState()
    val isPlaying by viewModel.isRadioPlaying.collectAsState()
    val volume by viewModel.volume.collectAsState()
    val spectrumBars by viewModel.spectrumBars.collectAsState()

    val currentPoem by viewModel.currentPoem.collectAsState()
    val isGeneratingPoem by viewModel.isGeneratingPoem.collectAsState()
    val isRecitingPoem by viewModel.isRecitingPoem.collectAsState()
    val activeVerseIndex by viewModel.activeVerseIndex.collectAsState()
    val selectedDialect by viewModel.selectedDialect.collectAsState()
    val selectedMood by viewModel.selectedMood.collectAsState()

    val dspSettings by viewModel.dspSettings.collectAsState()
    val isRecording by viewModel.isRecording.collectAsState()
    val recordingSeconds by viewModel.recordingSeconds.collectAsState()
    val savedPoems by viewModel.savedPoems.collectAsState()
    val studioRecordings by viewModel.studioRecordings.collectAsState()

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(StudioDarkBg)
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Spacer(modifier = Modifier.height(8.dp))
            // Live Radio Player Card
            RadioPlayerCard(
                station = selectedStation,
                isPlaying = isPlaying,
                volume = volume,
                spectrumBars = spectrumBars,
                onTogglePlay = { viewModel.toggleRadioPlayback() },
                onVolumeChange = { viewModel.setVolume(it) }
            )
        }

        item {
            // Stations List
            SectionTitle(
                title = "محطات أثير FMStar السحابية",
                subtitle = "بث فائق الجودة من سيرفر Go Audio Engine",
                badgeText = "Go Engine :8080"
            )
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.padding(top = 4.dp)
            ) {
                items(stations) { station ->
                    val isCurrent = station.id == selectedStation?.id
                    StationMiniCard(
                        station = station,
                        isSelected = isCurrent,
                        onClick = { viewModel.selectStation(station) }
                    )
                }
            }
        }

        item {
            // AI Poetry Studio Section
            SectionTitle(
                title = "استوديو التأليف والشعر بالذكاء الاصطناعي",
                subtitle = "توليد فوري للشعر بمختلف اللهجات (يمني، خليجي، فصيح)",
                badgeText = "Vertex AI Studio"
            )

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = StudioCardBg),
                border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(StudioBorder, PurpleAccent.copy(alpha = 0.4f))))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    // Dialect Selector
                    Text(
                        text = "اختر اللهجة / النمط الشعري:",
                        style = MaterialTheme.typography.labelMedium,
                        color = TextSecondary
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        viewModel.availableDialects.forEach { dialect ->
                            val selected = dialect == selectedDialect
                            FilterChip(
                                selected = selected,
                                onClick = { viewModel.setDialect(dialect) },
                                label = { Text(dialect) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = PurpleAccent,
                                    selectedLabelColor = Color.White,
                                    containerColor = StudioCardElevated,
                                    labelColor = TextSecondary
                                )
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))
                    // Mood Selector
                    Text(
                        text = "طابع القصيدة (الغرض):",
                        style = MaterialTheme.typography.labelMedium,
                        color = TextSecondary
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        viewModel.availableMoods.forEach { mood ->
                            val selected = mood == selectedMood
                            FilterChip(
                                selected = selected,
                                onClick = { viewModel.setMood(mood) },
                                label = { Text(mood) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = GoldAccent,
                                    selectedLabelColor = Color.Black,
                                    containerColor = StudioCardElevated,
                                    labelColor = TextSecondary
                                )
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))
                    // Generate Button
                    Button(
                        onClick = { viewModel.generateNewPoem() },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(48.dp)
                            .testTag("generate_poem_button"),
                        shape = RoundedCornerShape(14.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = PurpleAccent,
                            contentColor = Color.White
                        ),
                        enabled = !isGeneratingPoem
                    ) {
                        if (isGeneratingPoem) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                color = Color.White,
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("جاري التأليف والتناغم الشعري...")
                        } else {
                            Icon(Icons.Default.AutoAwesome, contentDescription = null, tint = GoldAccent)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("توليد قصيدة جديدة بالذكاء الاصطناعي", fontWeight = FontWeight.Bold)
                        }
                    }

                    // Display Current Generated Poem
                    currentPoem?.let { poem ->
                        Spacer(modifier = Modifier.height(16.dp))
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(16.dp))
                                .background(StudioCardElevated)
                                .border(1.dp, StudioBorder, RoundedCornerShape(16.dp))
                                .padding(16.dp)
                        ) {
                            Column {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Column {
                                        Text(
                                            text = poem.title,
                                            style = MaterialTheme.typography.titleMedium,
                                            fontWeight = FontWeight.Bold,
                                            color = GoldGlow
                                        )
                                        Text(
                                            text = "${poem.dialect} • ${poem.mood}",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = TextSecondary,
                                            fontSize = 11.sp
                                        )
                                    }

                                    // Cloud Badge
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(EmeraldLive.copy(alpha = 0.15f))
                                            .padding(horizontal = 8.dp, vertical = 4.dp)
                                    ) {
                                        Icon(
                                            Icons.Default.CloudDone,
                                            contentDescription = null,
                                            tint = EmeraldLive,
                                            modifier = Modifier.size(14.dp)
                                        )
                                        Spacer(modifier = Modifier.width(4.dp))
                                        Text(
                                            "Cloud SQL",
                                            color = EmeraldLive,
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.Bold
                                        )
                                    }
                                }

                                Spacer(modifier = Modifier.height(12.dp))

                                // Verses
                                poem.verses.forEachIndexed { index, verse ->
                                    val isRecitingThis = isRecitingPoem && activeVerseIndex == index
                                    val rowBg = if (isRecitingThis) PurpleDark.copy(alpha = 0.4f) else Color.Transparent
                                    val textColor = if (isRecitingThis) GoldAccent else TextPrimary

                                    Column(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(rowBg)
                                            .padding(vertical = 6.dp, horizontal = 8.dp)
                                    ) {
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween
                                        ) {
                                            Text(
                                                text = verse.firstHemistich,
                                                style = MaterialTheme.typography.bodyMedium,
                                                fontWeight = if (isRecitingThis) FontWeight.Bold else FontWeight.Medium,
                                                color = textColor,
                                                modifier = Modifier.weight(1f),
                                                textAlign = TextAlign.Start
                                            )
                                            Text(
                                                text = "...",
                                                color = TextMuted,
                                                modifier = Modifier.padding(horizontal = 4.dp)
                                            )
                                            Text(
                                                text = verse.secondHemistich,
                                                style = MaterialTheme.typography.bodyMedium,
                                                fontWeight = if (isRecitingThis) FontWeight.Bold else FontWeight.Medium,
                                                color = textColor,
                                                modifier = Modifier.weight(1f),
                                                textAlign = TextAlign.End
                                            )
                                        }
                                    }
                                }

                                Spacer(modifier = Modifier.height(14.dp))
                                // Poem Action Buttons
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    Button(
                                        onClick = { viewModel.toggleRecitation() },
                                        modifier = Modifier
                                            .weight(1f)
                                            .testTag("recite_poem_button"),
                                        shape = RoundedCornerShape(12.dp),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (isRecitingPoem) CoralWarning else CyanNeon,
                                            contentColor = Color.Black
                                        )
                                    ) {
                                        Icon(
                                            if (isRecitingPoem) Icons.Default.Stop else Icons.Default.RecordVoiceOver,
                                            contentDescription = null,
                                            modifier = Modifier.size(18.dp)
                                        )
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Text(
                                            if (isRecitingPoem) "إيقاف الإلقاء" else "إلقاء صوتي",
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 12.sp
                                        )
                                    }

                                    OutlinedButton(
                                        onClick = { viewModel.saveCurrentPoemToCloud() },
                                        modifier = Modifier
                                            .weight(1f)
                                            .testTag("save_poem_button"),
                                        shape = RoundedCornerShape(12.dp)
                                    ) {
                                        Icon(
                                            Icons.Default.Bookmark,
                                            contentDescription = null,
                                            tint = GoldAccent,
                                            modifier = Modifier.size(18.dp)
                                        )
                                        Spacer(modifier = Modifier.width(6.dp))
                                        Text("حفظ بالسحابة", color = GoldAccent, fontSize = 12.sp)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        item {
            // DSP & DJ Sound Deck Section
            SectionTitle(
                title = "هندسة الصوت ومؤثرات الـ DJ",
                subtitle = "محرك Daimyo Reverb ومضخم Shogun Bass",
                badgeText = "DSP Engine"
            )

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = StudioCardBg),
                border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(StudioBorder, CyanNeon.copy(alpha = 0.3f))))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    // Reverb Presets
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "مؤثر الصدى (Daimyo Reverb):",
                            style = MaterialTheme.typography.labelLarge,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary
                        )
                        Text(
                            text = dspSettings.reverbPreset.displayName,
                            color = CyanNeon,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                    Spacer(modifier = Modifier.height(6.dp))
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        ReverbPreset.values().forEach { preset ->
                            val selected = preset == dspSettings.reverbPreset
                            FilterChip(
                                selected = selected,
                                onClick = { viewModel.setReverbPreset(preset) },
                                label = { Text(preset.displayName, fontSize = 11.sp) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = CyanNeon,
                                    selectedLabelColor = Color.Black,
                                    containerColor = StudioCardElevated,
                                    labelColor = TextSecondary
                                )
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))
                    // Bass Presets
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "مضخم البيز (Shogun Bass Booster):",
                            style = MaterialTheme.typography.labelLarge,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary
                        )
                        Text(
                            text = dspSettings.bassPreset.displayName,
                            color = GoldAccent,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                    Spacer(modifier = Modifier.height(6.dp))
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        BassPreset.values().forEach { preset ->
                            val selected = preset == dspSettings.bassPreset
                            FilterChip(
                                selected = selected,
                                onClick = { viewModel.setBassPreset(preset) },
                                label = { Text(preset.displayName, fontSize = 11.sp) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = GoldAccent,
                                    selectedLabelColor = Color.Black,
                                    containerColor = StudioCardElevated,
                                    labelColor = TextSecondary
                                )
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "لوحة المؤثرات التفاعلية (DJ Sound FX Pad):",
                        style = MaterialTheme.typography.labelMedium,
                        color = TextSecondary
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    // DJ FX Buttons Grid
                    FlowRow(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                        maxItemsInEachRow = 3
                    ) {
                        DjPadButton(
                            title = "DJ Airhorn",
                            subtitle = "بوق دي جي",
                            icon = Icons.Default.GraphicEq,
                            accentColor = CoralWarning,
                            onClick = { viewModel.playDjEffect("airhorn") },
                            modifier = Modifier.weight(1f)
                        )
                        DjPadButton(
                            title = "Scratch",
                            subtitle = "سحب فاينل",
                            icon = Icons.Default.Tune,
                            accentColor = CyanNeon,
                            onClick = { viewModel.playDjEffect("scratch") },
                            modifier = Modifier.weight(1f)
                        )
                        DjPadButton(
                            title = "Sub Drop",
                            subtitle = "ضربة بيز قوية",
                            icon = Icons.Default.MusicNote,
                            accentColor = PurpleAccent,
                            onClick = { viewModel.playDjEffect("sub_drop") },
                            modifier = Modifier.weight(1f)
                        )
                        DjPadButton(
                            title = "Oud Touch",
                            subtitle = "نغمة عود يماني",
                            icon = Icons.Default.Headphones,
                            accentColor = GoldAccent,
                            onClick = { viewModel.playDjEffect("oud") },
                            modifier = Modifier.weight(1f)
                        )
                        DjPadButton(
                            title = "DJ Riser",
                            subtitle = "تصعيد إيقاعي",
                            icon = Icons.Default.AutoAwesome,
                            accentColor = EmeraldLive,
                            onClick = { viewModel.playDjEffect("riser") },
                            modifier = Modifier.weight(1f)
                        )
                        DjPadButton(
                            title = "Crowd",
                            subtitle = "تصفيق جمهور",
                            icon = Icons.Default.Radio,
                            accentColor = GoldGlow,
                            onClick = { viewModel.playDjEffect("applause") },
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
        }

        item {
            // Vocal Recording Studio Section
            SectionTitle(
                title = "مسجل الصوت والاستوديو الحي",
                subtitle = "تسجيل فوري ورفع إلى GCS Bucket السحابي",
                badgeText = "GCS Cloud Sync"
            )

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = StudioCardBg),
                border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(StudioBorder, CoralWarning.copy(alpha = 0.3f))))
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Box(
                        modifier = Modifier
                            .size(72.dp)
                            .clip(CircleShape)
                            .background(if (isRecording) CoralWarning.copy(alpha = 0.2f) else StudioCardElevated)
                            .border(
                                2.dp,
                                if (isRecording) CoralWarning else PurpleAccent,
                                CircleShape
                            )
                            .clickable { viewModel.toggleRecording() },
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            if (isRecording) Icons.Default.Stop else Icons.Default.Mic,
                            contentDescription = if (isRecording) "إيقاف التسجيل" else "بدء التسجيل",
                            tint = if (isRecording) CoralWarning else GoldAccent,
                            modifier = Modifier.size(36.dp)
                        )
                    }

                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        text = if (isRecording) "جاري التسجيل الصوتي المباشر..." else "انقر لبدء التسجيل الصوتي",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Bold,
                        color = if (isRecording) CoralWarning else TextPrimary
                    )

                    if (isRecording) {
                        Text(
                            text = String.format("%02d:%02d", recordingSeconds / 60, recordingSeconds % 60),
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold,
                            color = CoralWarning
                        )
                    }

                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "المستودع السحابي: gs://jimi-mira-audio-studio-bucket-087817",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextMuted,
                        fontSize = 11.sp
                    )
                }
            }
        }

        item {
            // Cloud Saved Vault (Poems & Recordings)
            if (savedPoems.isNotEmpty() || studioRecordings.isNotEmpty()) {
                SectionTitle(
                    title = "خزينة استوديو FMStar المحفوظة",
                    subtitle = "قصائد وتسجيلات متزامنة في قاعدة البيانات",
                    badgeText = "${savedPoems.size + studioRecordings.size} سجل"
                )

                savedPoems.forEach { savedPoem ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = StudioCardElevated)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = savedPoem.title,
                                    fontWeight = FontWeight.Bold,
                                    color = TextPrimary
                                )
                                Text(
                                    text = "${savedPoem.dialect} • ${savedPoem.date}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = TextSecondary,
                                    fontSize = 11.sp
                                )
                            }
                            IconButton(onClick = { viewModel.deleteSavedPoem(savedPoem.id) }) {
                                Icon(
                                    Icons.Default.Stop,
                                    contentDescription = "حذف",
                                    tint = CoralWarning.copy(alpha = 0.8f)
                                )
                            }
                        }
                    }
                }

                studioRecordings.forEach { recording ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = StudioCardElevated)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = recording.title,
                                    fontWeight = FontWeight.Bold,
                                    color = CyanNeon
                                )
                                Text(
                                    text = "المدة: ${recording.durationFormatted} • ${recording.dateFormatted}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = TextSecondary,
                                    fontSize = 11.sp
                                )
                            }
                            IconButton(onClick = { viewModel.deleteRecording(recording.id) }) {
                                Icon(
                                    Icons.Default.Stop,
                                    contentDescription = "حذف",
                                    tint = CoralWarning.copy(alpha = 0.8f)
                                )
                            }
                        }
                    }
                }
            }
        }

        item {
            Spacer(modifier = Modifier.height(48.dp))
        }
    }
}

@Composable
fun RadioPlayerCard(
    station: RadioStation?,
    isPlaying: Boolean,
    volume: Float,
    spectrumBars: List<Float>,
    onTogglePlay: () -> Unit,
    onVolumeChange: (Float) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = StudioCardBg),
        border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(GoldAccent.copy(alpha = 0.6f), PurpleAccent.copy(alpha = 0.6f))))
    ) {
        Column(
            modifier = Modifier.padding(18.dp)
        ) {
            // Live Status Row
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .clip(CircleShape)
                            .background(if (isPlaying) EmeraldLive else CoralWarning)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = if (isPlaying) "بث أثيري مباشر (Live FM)" else "جاهز للبث",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (isPlaying) EmeraldLive else TextSecondary
                    )
                }

                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(StudioCardElevated)
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = station?.frequency ?: "104.2 FM",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = GoldAccent
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))
            // Station Details
            Text(
                text = station?.name ?: "FMStar Live Cloud Studio",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
            Text(
                text = station?.currentTrack ?: "جيمي وميرا: تناغم الأصوات والصدى السحابي",
                style = MaterialTheme.typography.bodyMedium,
                color = CyanNeon
            )
            Text(
                text = "جودة الصوت: ${station?.bitRate ?: "320 kbps Studio Master"}",
                style = MaterialTheme.typography.bodySmall,
                color = TextMuted,
                fontSize = 11.sp
            )

            Spacer(modifier = Modifier.height(16.dp))
            // Dynamic Audio Visualizer
            AudioVisualizerCanvas(
                spectrumBars = spectrumBars,
                isPlaying = isPlaying,
                modifier = Modifier.padding(vertical = 4.dp)
            )

            Spacer(modifier = Modifier.height(14.dp))
            // Controls & Volume Slider
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                // Play / Pause Button
                Box(
                    modifier = Modifier
                        .size(54.dp)
                        .clip(CircleShape)
                        .background(GoldAccent)
                        .clickable { onTogglePlay() }
                        .testTag("radio_play_toggle_button"),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = if (isPlaying) Icons.Default.Pause else Icons.Default.PlayArrow,
                        contentDescription = if (isPlaying) "إيقاف مؤقت" else "تشغيل",
                        tint = Color.Black,
                        modifier = Modifier.size(32.dp)
                    )
                }

                Spacer(modifier = Modifier.width(16.dp))

                // Volume slider
                Row(
                    modifier = Modifier.weight(1f),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.VolumeUp,
                        contentDescription = null,
                        tint = TextSecondary,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Slider(
                        value = volume,
                        onValueChange = onVolumeChange,
                        modifier = Modifier.weight(1f),
                        colors = SliderDefaults.colors(
                            thumbColor = GoldAccent,
                            activeTrackColor = GoldAccent,
                            inactiveTrackColor = StudioCardElevated
                        )
                    )
                }
            }
        }
    }
}

@Composable
fun StationMiniCard(
    station: RadioStation,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val borderColor by animateColorAsState(
        targetValue = if (isSelected) GoldAccent else StudioBorder,
        label = "stationBorder"
    )

    Card(
        modifier = modifier
            .width(170.dp)
            .clickable { onClick() }
            .testTag("station_card_${station.id}"),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = if (isSelected) StudioCardElevated else StudioCardBg),
        border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(borderColor, StudioBorder)))
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = station.frequency,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = if (isSelected) GoldAccent else CyanNeon
                )
                Box(
                    modifier = Modifier
                        .size(6.dp)
                        .clip(CircleShape)
                        .background(if (isSelected) EmeraldLive else TextMuted)
                )
            }
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = station.name,
                fontWeight = FontWeight.Bold,
                style = MaterialTheme.typography.bodyMedium,
                color = TextPrimary,
                maxLines = 1
            )
            Text(
                text = station.genre,
                style = MaterialTheme.typography.bodySmall,
                color = TextSecondary,
                fontSize = 10.sp,
                maxLines = 1
            )
        }
    }
}
