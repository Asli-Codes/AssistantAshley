import pyttsx3
import platform


class TextToSpeech:
    def __init__(self):
        """TTS motorunu başlatır ve Türkçe için optimize eder."""
        print("TTS motoru başlatılıyor...")

        try:
            self.engine = pyttsx3.init()

            # Ses ayarlarını yapılandır
            self._configure_voice()

            print("✓ TTS motoru hazır!")

        except Exception as e:
            print(f"❌ TTS başlatma hatası: {e}")
            self.engine = None

    def _configure_voice(self):
        """Ses parametrelerini ayarlar."""
        if self.engine is None:
            return

        # Mevcut sesleri listele
        voices = self.engine.getProperty('voices')

        # Türkçe ses ara (varsa)
        turkish_voice = None
        for voice in voices:
            # Türkçe dil kodu: tr, tr-TR
            if 'tr' in voice.languages or 'turkish' in voice.name.lower():
                turkish_voice = voice.id
                print(f"✓ Türkçe ses bulundu: {voice.name}")
                break

        # Türkçe ses varsa ayarla
        if turkish_voice:
            self.engine.setProperty('voice', turkish_voice)
        else:
            print("⚠ Türkçe ses bulunamadı, varsayılan ses kullanılacak")
            # İlk kadın sesi varsa onu kullan (genelde daha iyi)
            for voice in voices:
                if 'female' in voice.name.lower() or 'kadın' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break

        # Hız ayarı (150-200 arası optimal)
        self.engine.setProperty('rate', 175)

        # Ses seviyesi (0.0 - 1.0)
        self.engine.setProperty('volume', 0.9)

    def speak(self, text, wait=True):
        """
        Metni sesli olarak okur.
        """
        if self.engine is None or not text:
            return

        try:
            print(f"🔊 Konuşuluyor: '{text}'")

            # Metni seslendir
            self.engine.say(text)

            if wait:
                self.engine.runAndWait()
            else:
                # Asenkron çalış (arka planda)
                self.engine.startLoop(False)
                self.engine.iterate()
                self.engine.endLoop()

        except Exception as e:
            print(f"❌ TTS hatası: {e}")

    def set_rate(self, rate):
        """
        Konuşma hızını ayarlar.

        Args:
            rate: Hız değeri (50-300 arası, varsayılan 175)
        """
        if self.engine:
            rate = max(50, min(300, rate))  # 50-300 arasında sınırla
            self.engine.setProperty('rate', rate)
            print(f"Konuşma hızı: {rate}")

    def set_volume(self, volume):
        """
        Ses seviyesini ayarlar.

        Args:
            volume: Ses seviyesi (0.0 - 1.0)
        """
        if self.engine:
            volume = max(0.0, min(1.0, volume))  # 0-1 arasında sınırla
            self.engine.setProperty('volume', volume)
            print(f"Ses seviyesi: {volume}")

    def list_voices(self):
        """Sistemdeki mevcut sesleri listeler."""
        if self.engine is None:
            return []

        voices = self.engine.getProperty('voices')
        voice_list = []

        print("\n=== Mevcut Sesler ===")
        for idx, voice in enumerate(voices):
            info = {
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages
            }
            voice_list.append(info)
            print(f"{idx}. {voice.name} - Diller: {voice.languages}")

        return voice_list

    def save_to_file(self, text, filename="output.mp3"):
        """
        Metni ses dosyası olarak kaydeder.
        """
        if self.engine is None:
            return

        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            print(f"✓ Ses dosyası kaydedildi: {filename}")
        except Exception as e:
            print(f"❌ Dosya kaydetme hatası: {e}")


# Test fonksiyonu
if __name__ == "__main__":
    print("=== METIN-SES DÖNÜŞTÜRME TESTİ ===\n")

    # TTS başlat
    tts = TextToSpeech()

    # Mevcut sesleri listele
    print("\nSistem sesleri:")
    tts.list_voices()

    print("\n" + "=" * 50)
    print("Test 1: Basit Türkçe cümle")
    tts.speak("Merhaba! Ben Türkçe sesli asistanınızım. Size nasıl yardımcı olabilirim?")

    print("\n" + "=" * 50)
    print("Test 2: Farklı hız ayarları")

    tts.set_rate(150)
    tts.speak("Bu yavaş hızda konuşma.")

    tts.set_rate(200)
    tts.speak("Bu ise hızlı konuşma.")

    tts.set_rate(175)  # Normal hıza dön

    print("\n" + "=" * 50)
    print("Test 3: Uzun metin")
    long_text = """
    Pomodoro tekniğini deneyebilirsiniz: 
    Yirmi beş dakika çalışın, beş dakika mola verin. 
    Dört tur sonra on beş ile otuz dakika uzun mola yapın.
    """
    tts.speak(long_text)

    print("\nTest tamamlandı!")