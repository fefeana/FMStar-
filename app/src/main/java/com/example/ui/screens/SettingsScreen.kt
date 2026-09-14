package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.CloudQueue
import androidx.compose.material.icons.filled.CreditCard
import androidx.compose.material.icons.filled.GraphicEq
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Save
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.components.SectionTitle
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

@Composable
fun SettingsScreen(
    viewModel: FMStarViewModel,
    modifier: Modifier = Modifier
) {
    val cloudConfig by viewModel.cloudConfig.collectAsState()

    var projectId by remember(cloudConfig) { mutableStateOf(cloudConfig.projectId) }
    var region by remember(cloudConfig) { mutableStateOf(cloudConfig.region) }
    var vmIp by remember(cloudConfig) { mutableStateOf(cloudConfig.vmIp) }
    var bucketName by remember(cloudConfig) { mutableStateOf(cloudConfig.bucketName) }
    var dbInstance by remember(cloudConfig) { mutableStateOf(cloudConfig.dbInstance) }

    var autoSyncEnabled by remember { mutableStateOf(true) }
    var studioMasterQuality by remember { mutableStateOf(true) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(StudioDarkBg)
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Spacer(modifier = Modifier.height(8.dp))
            SectionTitle(
                title = "إعدادات الربط السحابي (Google Cloud Platform)",
                subtitle = "تخصيص المشروع والمستودعات السحابية لتطبيق FMStar",
                badgeText = "GCP Config"
            )

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = StudioCardBg),
                border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(StudioBorder, CyanNeon.copy(alpha = 0.3f))))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    OutlinedTextField(
                        value = projectId,
                        onValueChange = { projectId = it },
                        label = { Text("معرف المشروع (Google Cloud Project ID)") },
                        modifier = Modifier
                            .fillMaxWidth()
                            .testTag("settings_project_id_input"),
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyanNeon,
                            unfocusedBorderColor = StudioBorder,
                            focusedTextColor = TextPrimary,
                            unfocusedTextColor = TextPrimary,
                            focusedLabelColor = CyanNeon,
                            unfocusedLabelColor = TextSecondary
                        )
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        OutlinedTextField(
                            value = region,
                            onValueChange = { region = it },
                            label = { Text("المنطقة السحابية (Region)") },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(12.dp),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = CyanNeon,
                                unfocusedBorderColor = StudioBorder,
                                focusedTextColor = TextPrimary,
                                unfocusedTextColor = TextPrimary
                            )
                        )

                        OutlinedTextField(
                            value = vmIp,
                            onValueChange = { vmIp = it },
                            label = { Text("IP خادم Go Backend") },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(12.dp),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = CyanNeon,
                                unfocusedBorderColor = StudioBorder,
                                focusedTextColor = TextPrimary,
                                unfocusedTextColor = TextPrimary
                            )
                        )
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    OutlinedTextField(
                        value = bucketName,
                        onValueChange = { bucketName = it },
                        label = { Text("مستودع التخزين الصوتي (GCS Bucket)") },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyanNeon,
                            unfocusedBorderColor = StudioBorder,
                            focusedTextColor = TextPrimary,
                            unfocusedTextColor = TextPrimary
                        )
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    OutlinedTextField(
                        value = dbInstance,
                        onValueChange = { dbInstance = it },
                        label = { Text("قاعدة بيانات PostgreSQL (Cloud SQL)") },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = CyanNeon,
                            unfocusedBorderColor = StudioBorder,
                            focusedTextColor = TextPrimary,
                            unfocusedTextColor = TextPrimary
                        )
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    Button(
                        onClick = {
                            viewModel.updateCloudConfig(
                                cloudConfig.copy(
                                    projectId = projectId,
                                    region = region,
                                    vmIp = vmIp,
                                    bucketName = bucketName,
                                    dbInstance = dbInstance
                                )
                            )
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(46.dp)
                            .testTag("save_cloud_settings_button"),
                        shape = RoundedCornerShape(12.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = CyanNeon,
                            contentColor = Color.Black
                        )
                    ) {
                        Icon(Icons.Default.Save, contentDescription = null, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("حفظ وتحديث الإعدادات السحابية", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        item {
            // Billing & Service Status
            SectionTitle(
                title = "حالة الحساب المالي (Billing Account)",
                subtitle = "التحقق من تفعيل الفواتير لتجنب إيقاف خوادم البناء السحابية",
                badgeText = "Verified"
            )

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = StudioCardElevated),
                border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(StudioBorder, EmeraldLive.copy(alpha = 0.3f))))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(38.dp)
                                    .clip(CircleShape)
                                    .background(EmeraldLive.copy(alpha = 0.15f)),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.Default.CreditCard, contentDescription = null, tint = EmeraldLive)
                            }
                            Spacer(modifier = Modifier.width(10.dp))
                            Column {
                                Text(
                                    text = "حساب الدفع السحابي (Billing)",
                                    fontWeight = FontWeight.Bold,
                                    color = TextPrimary
                                )
                                Text(
                                    text = "مربوط ببطاقة دفع نشطة (Active)",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = TextSecondary,
                                    fontSize = 11.sp
                                )
                            }
                        }

                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .background(EmeraldLive.copy(alpha = 0.15f))
                                .padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Icon(Icons.Default.CheckCircle, contentDescription = null, tint = EmeraldLive, modifier = Modifier.size(14.dp))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("نشط وموثق", color = EmeraldLive, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        text = "• النسخ الاحتياطي: Point-in-time recovery مفعل لمدة 7 أيام.\n• حماية الموارد: Deletion Protection مفعلة لقواعد البيانات.",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextMuted,
                        fontSize = 11.sp
                    )
                }
            }
        }

        item {
            // Audio Engineering & DSP Settings
            SectionTitle(
                title = "إعدادات هندسة الصوت ومعالجة الإشارة",
                subtitle = "جودة البث، التزامن، والمزامنة التلقائية",
                badgeText = "DSP v1.2"
            )

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = StudioCardBg),
                border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(StudioBorder, PurpleAccent.copy(alpha = 0.3f))))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    // Studio Master switch
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "جودة الماستر (Studio Master 320 kbps)",
                                fontWeight = FontWeight.Bold,
                                color = TextPrimary
                            )
                            Text(
                                text = "معدل عينات 48 kHz مع خوارزمية Daimyo Reverb",
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary,
                                fontSize = 11.sp
                            )
                        }
                        Switch(
                            checked = studioMasterQuality,
                            onCheckedChange = { studioMasterQuality = it },
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = GoldAccent,
                                checkedTrackColor = PurpleDark
                            )
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Auto-sync switch
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "المزامنة التلقائية مع السحابة (Cloud Auto-Sync)",
                                fontWeight = FontWeight.Bold,
                                color = TextPrimary
                            )
                            Text(
                                text = "رفع التسجيلات والقصائد فوراً إلى مستودع GCS",
                                style = MaterialTheme.typography.bodySmall,
                                color = TextSecondary,
                                fontSize = 11.sp
                            )
                        }
                        Switch(
                            checked = autoSyncEnabled,
                            onCheckedChange = { autoSyncEnabled = it },
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = CyanNeon,
                                checkedTrackColor = StudioCardElevated
                            )
                        )
                    }
                }
            }
        }

        item {
            // App About & Architecture
            SectionTitle(
                title = "حول تطبيق FMStar ✨",
                subtitle = "استوديو الصوت والذكاء الاصطناعي Jimi & Mira Studio",
                badgeText = "v1.0.0"
            )

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = StudioCardElevated),
                border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(PurpleDark, StudioBorder)))
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "FMStar AI Audio Studio",
                        fontWeight = FontWeight.Bold,
                        style = MaterialTheme.typography.titleMedium,
                        color = GoldGlow
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "تطبيق متكامل يجمع بين البث الإذاعي السحابي، تأليف الشعر المتعدد اللهجات بالذكاء الاصطناعي (يمني، خليجي، فصيح)، هندسة الصوت الرقمي (DSP Engine)، ولوحة تحكم سحابية مستقلة متصلة بخوادم Google Cloud و Terraform.",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary,
                        fontSize = 12.sp,
                        lineHeight = 18.sp
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        text = "المحرك: Go Audio Engine • السحابة: GCP Compute VM • قاعدة البيانات: PostgreSQL 15",
                        style = MaterialTheme.typography.bodySmall,
                        color = CyanNeon,
                        fontSize = 11.sp
                    )
                }
            }
        }

        item {
            Spacer(modifier = Modifier.height(48.dp))
        }
    }
}
