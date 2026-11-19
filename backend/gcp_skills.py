import os
from google.cloud import storage, texttospeech

class GoogleCloudSkills:
    def __init__(self):
        # تهيئة عملاء Google Cloud باستخدام المفتاح السحابي المعتمد
        self.storage_client = storage.Client()
        self.tts_client = texttospeech.TextToSpeechClient()

    def upload_media_to_gcp(self, bucket_name: str, source_file_path: str, destination_blob_name: str):
        """رفع الإنتاجات الصوتية والشعرية إلى Google Cloud Storage"""
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)
        return blob.public_url

    def generate_high_quality_voice(self, text: str, voice_name: str = "ar-XA-Wavenet-B"):
        """توليد تعليق صوتي احترافي بالنطق العربي الفصيح عبر Google TTS"""
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ar-XA", name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        return response.audio_content
