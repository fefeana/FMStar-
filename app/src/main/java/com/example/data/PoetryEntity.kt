package com.example.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "saved_poems")
data class SavedPoemEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val dialect: String,
    val mood: String,
    val versesRaw: String, // format: "صدر1|عجز1;;صدر2|عجز2"
    val author: String,
    val date: String,
    val isFavorite: Boolean = false,
    val isCloudSynced: Boolean = true
)

@Entity(tableName = "studio_recordings")
data class StudioRecordingEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val durationFormatted: String,
    val dialect: String,
    val dateFormatted: String,
    val cloudSynced: Boolean = true,
    val cloudUrl: String
)
