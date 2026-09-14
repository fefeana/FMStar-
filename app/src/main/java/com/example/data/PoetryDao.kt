package com.example.data

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

@Dao
interface PoetryDao {
    @Query("SELECT * FROM saved_poems ORDER BY id DESC")
    fun getAllPoems(): Flow<List<SavedPoemEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPoem(poem: SavedPoemEntity): Long

    @Update
    suspend fun updatePoem(poem: SavedPoemEntity)

    @Delete
    suspend fun deletePoem(poem: SavedPoemEntity)

    @Query("SELECT * FROM studio_recordings ORDER BY id DESC")
    fun getAllRecordings(): Flow<List<StudioRecordingEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertRecording(recording: StudioRecordingEntity): Long

    @Delete
    suspend fun deleteRecording(recording: StudioRecordingEntity)
}
