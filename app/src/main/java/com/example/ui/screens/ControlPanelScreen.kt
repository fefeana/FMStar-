package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Cloud
import androidx.compose.material.icons.filled.Code
import androidx.compose.material.icons.filled.Dns
import androidx.compose.material.icons.filled.PlayCircle
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material.icons.filled.Terminal
import androidx.compose.material.icons.filled.VpnKey
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.components.SectionTitle
import com.example.ui.components.ServiceHealthCard
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
import com.example.ui.theme.TerminalBlue
import com.example.ui.theme.TerminalDarkBg
import com.example.ui.theme.TerminalGreen
import com.example.ui.theme.TerminalYellow
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import com.example.ui.theme.TextSecondary
import com.example.viewmodel.FMStarViewModel

@Composable
fun ControlPanelScreen(
    viewModel: FMStarViewModel,
    modifier: Modifier = Modifier
) {
    val cloudConfig by viewModel.cloudConfig.collectAsState()
    val cloudServices by viewModel.cloudServices.collectAsState()
    val cloudLogs by viewModel.cloudLogs.collectAsState()

    var showTerraformCode by remember { mutableStateOf(false) }
    var selectedLogFilter by remember { mutableStateOf("ALL") }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .background(StudioDarkBg)
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Spacer(modifier = Modifier.height(8.dp))
            // Cloud Overview Hero
            CloudOverviewCard(
                projectId = cloudConfig.projectId,
                region = cloudConfig.region,
                vmIp = cloudConfig.vmIp,
                billingStatus = cloudConfig.billingStatus,
                vmMemory = cloudConfig.vmMemory,
                vmDisk = cloudConfig.vmDisk,
                backendPort = cloudConfig.backendPort,
                frontendPort = cloudConfig.frontendPort
            )
        }

        item {
            // Quick DevOps Cloud Actions
            SectionTitle(
                title = "إجراءات التحكم والتشغيل السحابي",
                subtitle = "نشر البنية وإدارة محرك الصوت Go تلقائياً",
                badgeText = "Terraform IaC"
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = { viewModel.runTerraformPlan() },
                    modifier = Modifier
                        .weight(1f)
                        .testTag("terraform_plan_button"),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = StudioCardElevated,
                        contentColor = CyanNeon
                    ),
                    border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(CyanNeon.copy(alpha = 0.5f), StudioBorder)))
                ) {
                    Icon(Icons.Default.Dns, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("فحص الخطة (Plan)", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }

                Button(
                    onClick = { viewModel.runTerraformApply() },
                    modifier = Modifier
                        .weight(1f)
                        .testTag("terraform_apply_button"),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = PurpleAccent,
                        contentColor = Color.White
                    )
                ) {
                    Icon(Icons.Default.PlayCircle, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("نشر وتطبيق (Apply)", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }

                Button(
                    onClick = { viewModel.restartGoAudioEngine() },
                    modifier = Modifier
                        .weight(1f)
                        .testTag("restart_audio_engine_button"),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = GoldAccent,
                        contentColor = Color.Black
                    )
                ) {
                    Icon(Icons.Default.Refresh, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("إعادة تشغيل Go", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                }
            }
        }

        item {
            // Cloud Services Matrix
            SectionTitle(
                title = "مصفوفة الخدمات السحابية ومراقبة الأداء",
                subtitle = "حالة خوادم GCE، قواعد بيانات SQL، ومستودعات التخزين",
                badgeText = "Google Cloud Platform"
            )

            cloudServices.forEach { service ->
                ServiceHealthCard(
                    name = service.name,
                    category = service.category,
                    resourceName = service.resourceName,
                    status = service.status,
                    metrics = service.metrics,
                    endpoint = service.endpoint
                )
            }
        }

        item {
            // Live Terminal Console
            SectionTitle(
                title = "وحدة التحكم وسجلات المحرك السحابي (Live Terminal)",
                subtitle = "متابعة طلبات gRPC / REST API ومحرك الصوت Go مباشرة",
                badgeText = "Port :8080 Active"
            )

            // Filter Chips
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf("ALL", "TERRAFORM", "GO_ENGINE", "POSTGRES", "ROUTER").forEach { filter ->
                    val isSelected = selectedLogFilter == filter
                    FilterChip(
                        selected = isSelected,
                        onClick = { selectedLogFilter = filter },
                        label = { Text(filter, fontSize = 10.sp) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = PurpleAccent,
                            selectedLabelColor = Color.White,
                            containerColor = StudioCardElevated,
                            labelColor = TextSecondary
                        )
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Terminal Box
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(230.dp),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = TerminalDarkBg),
                border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(StudioBorder, CyanNeon.copy(alpha = 0.3f))))
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(modifier = Modifier.size(8.dp).clip(CircleShape).background(Color(0xFFFF5F56)))
                            Spacer(modifier = Modifier.width(6.dp))
                            Box(modifier = Modifier.size(8.dp).clip(CircleShape).background(Color(0xFFFFBD2E)))
                            Spacer(modifier = Modifier.width(6.dp))
                            Box(modifier = Modifier.size(8.dp).clip(CircleShape).background(Color(0xFF27C93F)))
                            Spacer(modifier = Modifier.width(10.dp))
                            Text(
                                text = "cloud-shell@${cloudConfig.projectId}:~/jimi-mira-studio",
                                style = MaterialTheme.typography.bodySmall,
                                color = TextMuted,
                                fontSize = 10.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    val filteredLogs = if (selectedLogFilter == "ALL") {
                        cloudLogs
                    } else {
                        cloudLogs.filter { it.service.equals(selectedLogFilter, ignoreCase = true) }
                    }

                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        items(filteredLogs) { log ->
                            val color = when (log.level) {
                                "SUCCESS" -> TerminalGreen
                                "WARN" -> TerminalYellow
                                "API" -> TerminalBlue
                                else -> TextSecondary
                            }
                            Row(modifier = Modifier.fillMaxWidth()) {
                                Text(
                                    text = "[${log.timestamp}]",
                                    color = TextMuted,
                                    fontSize = 11.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = "<${log.service}>",
                                    color = CyanNeon,
                                    fontSize = 11.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = log.message,
                                    color = color,
                                    fontSize = 11.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                            }
                        }
                    }
                }
            }
        }

        item {
            // Terraform main.tf Code Inspector
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { showTerraformCode = !showTerraformCode },
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = StudioCardElevated),
                border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(PurpleDark, StudioBorder)))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Code, contentDescription = null, tint = GoldAccent)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "معاينة كود البناء السحابي (main.tf)",
                                fontWeight = FontWeight.Bold,
                                color = TextPrimary
                            )
                        }
                        Text(
                            text = if (showTerraformCode) "إخفاء ▲" else "عرض ▼",
                            color = GoldAccent,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    AnimatedVisibility(visible = showTerraformCode) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 10.dp)
                                .clip(RoundedCornerShape(8.dp))
                                .background(TerminalDarkBg)
                                .padding(12.dp)
                        ) {
                            Text(
                                text = """
provider "google" {
  project = "${cloudConfig.projectId}"
  region  = "${cloudConfig.region}"
}

# 1. المساحة التخزينية لملفات الاستوديو الصوتية
resource "google_storage_bucket" "audio_bucket" {
  name          = "${cloudConfig.bucketName}"
  location      = "${cloudConfig.region}"
  force_destroy = true
}

# 2. الخزنة الرقمية لإدارة المفاتيح وتشفير البيانات
resource "google_secret_manager_secret" "studio_secrets" {
  secret_id = "${cloudConfig.secretId}"
  replication { auto {} }
}

# 3. قاعدة البيانات السحابية العملاقة PostgreSQL
resource "google_sql_database_instance" "postgres_db" {
  name             = "${cloudConfig.dbInstance}"
  database_version = "POSTGRES_15"
  region           = "${cloudConfig.region}"
}
                                """.trimIndent(),
                                color = TerminalGreen,
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace
                            )
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
fun CloudOverviewCard(
    projectId: String,
    region: String,
    vmIp: String,
    billingStatus: String,
    vmMemory: String,
    vmDisk: String,
    backendPort: Int,
    frontendPort: Int,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = StudioCardBg),
        border = CardDefaults.outlinedCardBorder().copy(brush = Brush.linearGradient(listOf(CyanNeon.copy(alpha = 0.6f), PurpleAccent.copy(alpha = 0.6f))))
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "مشروع Google Cloud",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextSecondary
                    )
                    Text(
                        text = projectId,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = GoldGlow
                    )
                }

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(EmeraldLive.copy(alpha = 0.15f))
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Icon(
                        Icons.Default.CheckCircle,
                        contentDescription = null,
                        tint = EmeraldLive,
                        modifier = Modifier.size(14.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = billingStatus,
                        color = EmeraldLive,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Compute Engine VM Specs Grid
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                CloudMetricItem(
                    label = "الجهاز الافتراضي",
                    value = "GCE VM (web-app-tpl)",
                    subValue = region,
                    modifier = Modifier.weight(1f)
                )
                CloudMetricItem(
                    label = "عنوان الـ IP الثابت",
                    value = vmIp,
                    subValue = "Port :$backendPort & :$frontendPort",
                    modifier = Modifier.weight(1f)
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                CloudMetricItem(
                    label = "الذاكرة العشوائية",
                    value = vmMemory,
                    subValue = "High Throughput Audio",
                    modifier = Modifier.weight(1f)
                )
                CloudMetricItem(
                    label = "القرص الصلب السحابي",
                    value = vmDisk,
                    subValue = "Fast I/O SSD",
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
fun CloudMetricItem(
    label: String,
    value: String,
    subValue: String,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(12.dp))
            .background(StudioCardElevated)
            .border(1.dp, StudioBorder, RoundedCornerShape(12.dp))
            .padding(10.dp)
    ) {
        Column {
            Text(text = label, style = MaterialTheme.typography.bodySmall, color = TextMuted, fontSize = 10.sp)
            Text(text = value, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = TextPrimary, maxLines = 1)
            Text(text = subValue, style = MaterialTheme.typography.bodySmall, color = CyanNeon, fontSize = 10.sp, maxLines = 1)
        }
    }
}
