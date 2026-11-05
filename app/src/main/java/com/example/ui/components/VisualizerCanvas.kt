package com.example.ui.components

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.ui.theme.CyanNeon
import com.example.ui.theme.GoldAccent
import com.example.ui.theme.PurpleAccent

@Composable
fun AudioVisualizerCanvas(
    spectrumBars: List<Float>,
    isPlaying: Boolean,
    modifier: Modifier = Modifier
) {
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val glowPhase by infiniteTransition.animateFloat(
        initialValue = 0.8f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow"
    )

    Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(56.dp)
    ) {
        val count = spectrumBars.size
        if (count == 0) return@Canvas

        val totalWidth = size.width
        val canvasHeight = size.height
        val barSpacing = 4.dp.toPx()
        val totalSpacing = barSpacing * (count - 1)
        val barWidth = ((totalWidth - totalSpacing) / count).coerceAtLeast(4f)

        val gradient = Brush.verticalGradient(
            colors = listOf(
                GoldAccent,
                PurpleAccent,
                CyanNeon
            ),
            startY = 0f,
            endY = canvasHeight
        )

        val inactiveColor = Color(0x338B5CF6)

        for (i in 0 until count) {
            val rawAmp = spectrumBars[i]
            val amp = if (isPlaying) (rawAmp * glowPhase).coerceIn(0.12f, 1.0f) else 0.08f
            val barHeight = (amp * canvasHeight).coerceAtLeast(4.dp.toPx())
            val x = i * (barWidth + barSpacing)
            val y = canvasHeight - barHeight

            drawRoundRect(
                brush = if (isPlaying) gradient else Brush.linearGradient(listOf(inactiveColor, inactiveColor)),
                topLeft = Offset(x, y),
                size = Size(barWidth, barHeight),
                cornerRadius = CornerRadius(4.dp.toPx(), 4.dp.toPx())
            )
        }
    }
}
