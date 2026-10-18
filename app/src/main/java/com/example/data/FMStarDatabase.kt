package com.example.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [SavedPoemEntity::class, StudioRecordingEntity::class],
    version = 1,
    exportSchema = false
)
abstract class FMStarDatabase : RoomDatabase() {
    abstract fun poetryDao(): PoetryDao

    companion object {
        @Volatile
        private var INSTANCE: FMStarDatabase? = null

        fun getDatabase(context: Context): FMStarDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    FMStarDatabase::class.java,
                    "fmstar_cloud_studio.db"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
