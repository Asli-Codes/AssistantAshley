import json
import re
from datetime import datetime, timedelta
import os


class CommandHandler:
    def __init__(self, notes_file="data/notes.json", reminders_file="data/reminders.json"):
        """
        Args:
            notes_file: Notların saklandığı dosya
            reminders_file: Hatırlatıcıların saklandığı dosya
        """
        self.notes_file = notes_file
        self.reminders_file = reminders_file

        # Veri yapılarını başlat
        self.notes = self._load_json(notes_file, default=[])
        self.reminders = self._load_json(reminders_file, default=[])

        print("✓ Komut işleyici hazır!")

    def _load_json(self, filepath, default=None):
        """JSON dosyasını yüklüyor."""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠ {filepath} yüklenemedi: {e}")
        return default if default is not None else {}

    def _save_json(self, data, filepath):
        """JSON dosyasına kaydeder."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ {filepath} kaydedilemedi: {e}")
            return False

    def handle_command(self, intent, original_text, confidence):
        """
        Intent'e göre komutu işler ve yanıt üretir.

        Args:
            intent: Tespit edilen intent
            original_text: Orijinal kullanıcı metni
            confidence: Tahmin güveni

        Returns:
            str: İşlenmiş yanıt
        """
        handlers = {
            'time': self._handle_time,
            'date': self._handle_date,
            'calculator': self._handle_calculator,
            'note_add': self._handle_note_add,
            'note_list': self._handle_note_list,
            'note_delete': self._handle_note_delete,
            'reminder_add': self._handle_reminder_add,
            'reminder_list': self._handle_reminder_list,
            'study_advice': self._handle_study_advice,
            'study_timer': self._handle_study_timer,
            'motivate': self._handle_motivate,
        }

        # Özel handler varsa çağır
        if intent in handlers:
            return handlers[intent](original_text)

        # Yoksa basit yanıt döndür
        return self._get_default_response(intent)

    def _get_default_response(self, intent):
        """Basit yanıt şablonları."""
        responses = {
            'greeting': "Merhaba! Size nasıl yardımcı olabilirim?",
            'goodbye': "Görüşürüz! İyi günler dilerim.",
            'thanks': "Rica ederim! Her zaman yardımcı olmaktan mutluluk duyarım.",
            'help': "Yapabileceklerim: Saat/tarih bilgisi, hesaplama, not alma, hatırlatıcı, çalışma önerileri ve daha fazlası!",
            'name': "Ben Türkçe sesli asistanınızım. Bana istediğiniz ismi verebilirsiniz!",
            'unknown': "Anlayamadım, lütfen başka şekilde ifade eder misiniz?"
        }
        return responses.get(intent, "İlginç bir soru, ama şu an cevaplayamıyorum.")

    # ============= ZAMAN İŞLEMLERİ =============

    def _handle_time(self, text):
        """Şu anki saati söyler."""
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        return f"Şu an saat {time_str}"

    def _handle_date(self, text):
        """Bugünün tarihini söyler."""
        now = datetime.now()

        # Türkçe gün isimleri
        days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        day_name = days[now.weekday()]

        # Türkçe ay isimleri
        months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                  'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
        month_name = months[now.month - 1]

        date_str = f"{day_name}, {now.day} {month_name} {now.year}"
        return f"Bugün {date_str}"

    # ============= HESAP MAKİNESİ =============

    def _handle_calculator(self, text):
        """Matematiksel hesaplama yapar."""
        # Sayıları ve operatörleri bul
        # Türkçe sayı kelimeleri
        numbers_tr = {
            'bir': 1, 'iki': 2, 'üç': 3, 'dört': 4, 'beş': 5,
            'altı': 6, 'yedi': 7, 'sekiz': 8, 'dokuz': 9, 'on': 10,
            'sıfır': 0, 'yüz': 100, 'bin': 1000
        }

        # Operatör kelimeleri
        ops = {
            'artı': '+', 'ekle': '+', 'topla': '+',
            'eksi': '-', 'çıkar': '-', 'çıkart': '-',
            'çarpı': '*', 'çarp': '*', 'kere': '*',
            'bölü': '/', 'böl': '/'
        }

        # Sayıları ve operatörleri çıkar
        expression = text.lower()

        # Kelimeleri rakama çevir
        for word, num in numbers_tr.items():
            expression = expression.replace(word, str(num))

        # Operatörleri çevir
        for word, op in ops.items():
            expression = expression.replace(word, op)

        # Sadece sayı ve operatörleri tut
        expression = re.sub(r'[^0-9+\-*/\.]', '', expression)

        # Hesapla
        try:
            result = eval(expression)  # Güvenlik: Sadece basit ifadelerde kullan
            return f"Sonuç: {result}"
        except:
            # İfade çıkarılamadıysa, rakamları topla
            numbers = re.findall(r'\d+\.?\d*', text)
            if len(numbers) >= 2:
                nums = [float(n) for n in numbers]

                # Operatör tahmin et
                if 'artı' in text or 'topla' in text:
                    result = sum(nums)
                    return f"Sonuç: {result}"
                elif 'çarp' in text:
                    result = nums[0]
                    for n in nums[1:]:
                        result *= n
                    return f"Sonuç: {result}"

            return "Hesaplama yapamadım. Örnek: '5 artı 3' veya '10 çarpı 2'"

    # ============= NOT SİSTEMİ =============

    def _handle_note_add(self, text):
        """Not ekler."""
        # "not al" gibi komut kelimelerini çıkar
        note_text = re.sub(r'(not\s+al|not\s+tut|kaydet|yaz|hatırla)', '', text, flags=re.IGNORECASE).strip()

        if not note_text or len(note_text) < 3:
            return "Ne not almamı istiyorsunuz?"

        # Not ekle
        note = {
            'id': len(self.notes) + 1,
            'text': note_text,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.notes.append(note)
        self._save_json(self.notes, self.notes_file)

        return f"Not alındı: '{note_text}'"

    def _handle_note_list(self, text):
        """Notları listeler."""
        if not self.notes:
            return "Henüz kaydedilmiş notunuz yok."

        response = f"Toplam {len(self.notes)} notunuz var:\n\n"

        for note in self.notes[-5:]:  # Son 5 notu göster
            response += f"• {note['text']}\n"

        if len(self.notes) > 5:
            response += f"\n(Ve {len(self.notes) - 5} not daha...)"

        return response

    def _handle_note_delete(self, text):
        """Notları siler."""
        if not self.notes:
            return "Silinecek not bulunamadı."

        self.notes.clear()
        self._save_json(self.notes, self.notes_file)

        return "Tüm notlar silindi."

    # ============= HATIRLATICI SİSTEMİ =============

    def _handle_reminder_add(self, text):
        """Hatırlatıcı ekler."""
        # Zaman ifadelerini ara
        time_patterns = {
            r'(\d+)\s*(dakika|dk)': 'minutes',
            r'(\d+)\s*(saat|sa)': 'hours',
            r'yarın': 'tomorrow',
            r'(\d+)\.(\d+)': 'time'  # 14.30 gibi
        }

        reminder_time = None
        time_str = ""

        for pattern, time_type in time_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if time_type == 'minutes':
                    minutes = int(match.group(1))
                    reminder_time = datetime.now() + timedelta(minutes=minutes)
                    time_str = f"{minutes} dakika sonra"
                elif time_type == 'hours':
                    hours = int(match.group(1))
                    reminder_time = datetime.now() + timedelta(hours=hours)
                    time_str = f"{hours} saat sonra"
                elif time_type == 'tomorrow':
                    reminder_time = datetime.now() + timedelta(days=1)
                    reminder_time = reminder_time.replace(hour=9, minute=0)
                    time_str = "yarın saat 09:00'da"
                elif time_type == 'time':
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    reminder_time = datetime.now().replace(hour=hour, minute=minute)
                    if reminder_time < datetime.now():
                        reminder_time += timedelta(days=1)
                    time_str = f"saat {hour:02d}:{minute:02d}'te"
                break

        if not reminder_time:
            return "Zaman belirtmediniz. Örnek: '30 dakika sonra hatırlat' veya 'yarın 14.30'da hatırlat'"

        # Hatırlatıcı metni çıkar
        reminder_text = re.sub(r'(hatırlat|hatırlatıcı|alarm|uyar)', '', text, flags=re.IGNORECASE)
        reminder_text = re.sub(r'\d+\s*(dakika|saat|dk|sa)', '', reminder_text)
        reminder_text = re.sub(r'\d+\.\d+', '', reminder_text).strip()

        if not reminder_text:
            reminder_text = "Hatırlatıcı"

        # Hatırlatıcı ekle
        reminder = {
            'id': len(self.reminders) + 1,
            'text': reminder_text,
            'time': reminder_time.strftime("%Y-%m-%d %H:%M:%S"),
            'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.reminders.append(reminder)
        self._save_json(self.reminders, self.reminders_file)

        return f"Hatırlatıcı eklendi: '{reminder_text}' - {time_str}"

    def _handle_reminder_list(self, text):
        """Hatırlatıcıları listeler."""
        if not self.reminders:
            return "Aktif hatırlatıcınız bulunmuyor."

        response = f"Toplam {len(self.reminders)} hatırlatıcınız var:\n\n"

        for reminder in self.reminders:
            time_obj = datetime.strptime(reminder['time'], "%Y-%m-%d %H:%M:%S")
            time_str = time_obj.strftime("%d.%m.%Y %H:%M")
            response += f"• {reminder['text']} - {time_str}\n"

        return response

    # ============= ÖĞRENCİ ÖZELLİKLERİ =============

    def _handle_study_advice(self, text):
        """Çalışma önerisi verir."""
        tips = [
            "🎯 Pomodoro tekniği: 25 dakika çalış, 5 dakika mola. Odaklanmanızı artırır!",
            "📚 Aktif öğrenme: Okuduklarınızı kendi cümlelerinizle not alın. Pasif okumadan çok daha etkili!",
            "🧠 Hafızayı güçlendirme: Öğrendiklerinizi başkasına anlatmaya çalışın. Anlatamazsan anlamamışsın demektir.",
            "⏰ Düzenli çalışma: Her gün aynı saatte kısa süreli çalışmak, yoğun tek seanstan daha verimlidir.",
            "💡 Çalışma ortamı: Sessiz, aydınlık ve düzenli bir ortam konsantrasyonu artırır.",
            "🎧 Müzik seçimi: Enstrümantal müzik ya da doğa sesleri odaklanmayı kolaylaştırabilir.",
            "📝 Özet çıkarma: Her konuyu bitirdiğinizde kısa bir özet yapın. Tekrar için altın değerinde!",
            "🔄 Tekrar sistemi: 1 gün, 3 gün, 1 hafta, 1 ay sonra tekrar edin. Kalıcı öğrenme böyle olur!"
        ]

        import random
        return random.choice(tips)

    def _handle_study_timer(self, text):
        """Çalışma zamanlayıcısı başlatır."""
        # Süre çıkar
        duration = 25  # Varsayılan Pomodoro

        match = re.search(r'(\d+)\s*(dakika|dk)', text, re.IGNORECASE)
        if match:
            duration = int(match.group(1))

        return f"⏱️ {duration} dakikalık çalışma süreniz başladı! Konsantre olun, başarılar! 🚀"

    def _handle_motivate(self, text):
        """Motivasyon mesajı verir."""
        quotes = [
            "💪 'Başarısızlık sadece tekrar denemek için bir fırsattır.' - Henry Ford",
            "🌟 Her büyük başarı küçük adımlarla başlar. Siz de bugün bir adım atın!",
            "🎯 'Yapabileceğine inandığında, yarı yoldasın demektir.' - Theodore Roosevelt",
            "🚀 Zorluklar sizi durdurmasın, her zorluk bir öğrenme fırsatıdır!",
            "✨ Başarı sabır ister. Devam edin, çünkü siz bunu hak ediyorsunuz!",
            "🔥 'Bir gün veya birinci gün. Sen karar ver.' - Anonim",
            "🌈 Hedefinize giden yolda her gün biraz daha ilerleyin. Küçük adımlar büyük farklar yaratır!",
            "💎 Bugün kendiniz için yaptığınız çalışma, yarının başarısıdır!"
        ]

        import random
        return random.choice(quotes)


# Test fonksiyonu
if __name__ == "__main__":
    print("=== KOMUT İŞLEYİCİ TESTİ ===\n")

    handler = CommandHandler()

    test_commands = [
        ('time', 'saat kaç'),
        ('date', 'bugün ne günü'),
        ('calculator', '5 artı 3 kaç eder'),
        ('note_add', 'bunu not al: yarın market'),
        ('note_list', 'notlarım neler'),
        ('reminder_add', '30 dakika sonra çay içmeyi hatırlat'),
        ('reminder_list', 'hatırlatıcılar neler'),
        ('study_advice', 'çalışma önerisi ver'),
        ('motivate', 'motive et beni'),
    ]

    for intent, text in test_commands:
        print(f"📝 Intent: {intent}")
        print(f"💬 Komut: '{text}'")
        response = handler.handle_command(intent, text, 0.9)
        print(f"✅ Yanıt: {response}")
        print("-" * 60)

    print("\nTest tamamlandı!")