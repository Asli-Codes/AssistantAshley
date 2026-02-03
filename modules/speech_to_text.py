import whisper
import json
import queue
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
import os
import tempfile


class SpeechToText:
    def __init__(self, model_size="base"):
        """
        Args:
            model_size: Whisper model boyutu
                - tiny: En hızlı, en düşük doğruluk (~1GB RAM)
                - base: Hızlı, orta doğruluk (~1GB RAM) - ÖNERİLEN
                - small: Orta hız, iyi doğruluk (~2GB RAM)
                - medium: Yavaş, yüksek doğruluk (~5GB RAM)
                - large: En yavaş, en yüksek doğruluk (~10GB RAM)
        """
        print(f"Whisper{model_size} modeli yükleniyor...")
        self.model = whisper.load_model(model_size)
        self.sample_rate = 16000
        print("Ses tanıma modülü hazır!")

    def record_audio(self, duration=5, sample_rate=None):
        """
        Mikrofondan ses kaydeder.

        Args:
          duration: Kayıt süresi (saniye)
          sample_rate: Örnekleme hızı (Hz)

        Returns:
          numpy array: Ses verisi
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        print(f"🎤 Kayıt başlıyor... {duration} saniye konuşun!")

        try:
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            print("✓ Kayıt tamamlandı!")

            return audio.flatten()

        except Exception as e:
            print(f"❌ Kayıt hatası: {e}")
            return None

    def transcribe_audio(self, audio_data=None, audio_file=None, language="tr"):
        """
        Ses verisini veya dosyasını metne çevirir.

        Args:
            audio_data: NumPy array ses verisi
            audio_file: Ses dosyası yolu
            language: Dil kodu ("tr" = Türkçe)

            Returns:
            str: Tanınan metin
        """

        try:
            if audio_data is not None:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_path = temp_file.name
                    sf.write(temp_path, audio_data, self.sample_rate)
                    audio_data = temp_path

            if audio_data is None:
                return ""
            print("🔍 Ses analiz ediliyor...")

            result = self.model.transcribe(
                audio_file,
                language=language,
                fp16=False
            )

            text = result["text"].strip()
            print(f"✓ Algılanan metin: '{text}'")

            if audio_data is not None and os.path.exists(temp_path):
                os.unlink(temp_path)

            return text

        except Exception as e:
            print(f"❌ Transkripsiyon hatası: {e}")
            return ""

    def listen_and_transcribe(self, duration=5):

        audio = self.record_audio(duration)
        if audio is not None:
            return self.transcribe_audio(audio_data=audio)
        return ""

    # Test fonksiyonu
if __name__ == "__main__":
    print("=== SES TANIMA TESTİ ===\n")

    # Modülü başlat (base modeli önerilir - hız/doğruluk dengesi)
    stt = SpeechToText(model_size="base")

    print("\nTest 1: Mikrofondan kayıt ve tanıma")
    print("Hazır olduğunuzda Enter'a basın...")
    input()

    text = stt.listen_and_transcribe(duration=5)
    print(f"\nSonuç: {text}")

    print("\n" + "=" * 50)
    print("Test tamamlandı!")