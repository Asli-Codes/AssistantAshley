import streamlit as st
import sys
import os

# Modül yolunu ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.speech_to_text import SpeechToText
from modules.text_to_speech import TextToSpeech
from modules.intent_classifier import IntentClassifier
from modules.command_handler import CommandHandler

# Sayfa yapılandırması
st.set_page_config(
    page_title="Türkçe Sesli Asistan",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1E88E5;
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 30px;
    }

    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        animation: fadeIn 0.5s;
    }

    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }

    .assistant-message {
        background-color: #F3E5F5;
        border-left: 4px solid #9C27B0;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: black;
        font-weight: bold;
        border-radius: 10px;
        padding: 15px;
        border: none;
        transition: transform 0.2s;
    }

    .stButton > button:hover {
        transform: scale(1.05);
    }

    .info-box {
        background-color: #FFF3E0;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #FF9800;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state başlatma
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'stt' not in st.session_state:
    st.session_state.stt = None

if 'tts' not in st.session_state:
    st.session_state.tts = None

if 'classifier' not in st.session_state:
    st.session_state.classifier = None

if 'handler' not in st.session_state:
    st.session_state.handler = None

if 'initialized' not in st.session_state:
    st.session_state.initialized = False


@st.cache_resource
def load_models():
    """Modelleri yükler (cache ile)."""
    with st.spinner("🔄 Sistem başlatılıyor..."):
        # Speech-to-Text (base model - hız/doğruluk dengesi)
        stt = SpeechToText(model_size="base")

        # Text-to-Speech
        tts = TextToSpeech()

        # Intent Classifier
        classifier = IntentClassifier()

        # Model varsa yükle, yoksa eğit
        if not classifier.load_model():
            st.info("📚 Model eğitiliyor, lütfen bekleyin...")
            classifier.train()
            classifier.save_model()

        # Command Handler
        handler = CommandHandler()

    return stt, tts, classifier, handler


def process_voice_command(duration=5):
    """Sesli komutu işler."""
    try:
        # Ses kaydet ve tanı
        with st.spinner("🎤 Kayıt yapılıyor..."):
            text = st.session_state.stt.listen_and_transcribe(duration=duration)

        if not text:
            st.error("❌ Ses tanınamadı, lütfen tekrar deneyin.")
            return None, None

        # Intent tahmin et
        intent, confidence = st.session_state.classifier.predict(text)

        # Komutu işle
        response = st.session_state.handler.handle_command(intent, text, confidence)

        # Konuşmayı kaydet
        st.session_state.conversation_history.append({
            'user': text,
            'assistant': response,
            'intent': intent,
            'confidence': confidence
        })

        # Sesli yanıt ver
        st.session_state.tts.speak(response)

        return text, response

    except Exception as e:
        st.error(f"❌ Hata: {e}")
        return None, None


def main():
    """Ana uygulama."""

    # Header
    st.markdown(
        '<div class="main-header"><h1>🎤 Türkçe Sesli Akıllı Asistan</h1><p>Sesli komutlarınızla etkileşime geçin!</p></div>',
        unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Ayarlar")

        # Kayıt süresi
        duration = st.slider("🎙️ Kayıt Süresi (saniye)", 3, 10, 5)

        st.divider()

        # İstatistikler
        st.header("📊 İstatistikler")
        st.metric("Toplam Konuşma", len(st.session_state.conversation_history))

        if st.session_state.handler:
            notes_count = len(st.session_state.handler.notes)
            reminders_count = len(st.session_state.handler.reminders)

            st.metric("📝 Kaydedilen Notlar", notes_count)
            st.metric("⏰ Aktif Hatırlatıcılar", reminders_count)

        st.divider()

        # Notlar ve Hatırlatıcılar
        st.header("📋 Hızlı Erişim")

        if st.button("📝 Notlarımı Göster"):
            if st.session_state.handler:
                response = st.session_state.handler._handle_note_list("")
                st.info(response)

        if st.button("⏰ Hatırlatıcılarımı Göster"):
            if st.session_state.handler:
                response = st.session_state.handler._handle_reminder_list("")
                st.info(response)

        st.divider()

        # Temizleme
        if st.button("🗑️ Konuşma Geçmişini Temizle"):
            st.session_state.conversation_history = []
            st.success("✅ Geçmiş temizlendi!")

        st.divider()

        # Yardım
        with st.expander("❓ Nasıl Kullanılır?"):
            st.markdown("""
            **Örnek Komutlar:**
            - 🕐 "Saat kaç?"
            - 📅 "Bugün ne günü?"
            - 🧮 "5 artı 3 kaç eder?"
            - 📝 "Market listesi not al"
            - ⏰ "Yarın saat 9'da bana hatırlat"
            - 📚 "Çalışma önerisi ver"
            - 💪 "Motive et beni"

            **İpuçları:**
            - Mikrofona yakın konuşun
            - Net ve yavaş telaffuz edin
            - Sessiz bir ortamda kullanın
            """)

    # Ana içerik alanı
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("💬 Konuşma")

        # Modelleri yükle
        if not st.session_state.initialized:
            try:
                stt, tts, classifier, handler = load_models()
                st.session_state.stt = stt
                st.session_state.tts = tts
                st.session_state.classifier = classifier
                st.session_state.handler = handler
                st.session_state.initialized = True
                st.success("✅ Sistem hazır! Konuşmaya başlayabilirsiniz.")
            except Exception as e:
                st.error(f"❌ Sistem başlatma hatası: {e}")
                st.stop()

        # Ses kayıt butonu
        if st.button("🎤 Kayıt Başlat", key="record_btn"):
            user_text, assistant_response = process_voice_command(duration=duration)

        # Metin girişi (alternatif)
        st.divider()
        text_input = st.text_input("💬 Veya buraya yazın:", placeholder="Komutunuzu yazın...")

        if text_input:
            intent, confidence = st.session_state.classifier.predict(text_input)
            response = st.session_state.handler.handle_command(intent, text_input, confidence)

            st.session_state.conversation_history.append({
                'user': text_input,
                'assistant': response,
                'intent': intent,
                'confidence': confidence
            })

            # Sesli yanıt
            st.session_state.tts.speak(response)

        # Konuşma geçmişi
        st.divider()

        if st.session_state.conversation_history:
            for idx, conv in enumerate(reversed(st.session_state.conversation_history[-10:])):
                # Kullanıcı mesajı
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 Siz:</strong><br>{conv['user']}
                </div>
                """, unsafe_allow_html=True)

                # Asistan mesajı
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Asistan:</strong><br>{conv['assistant']}<br>
                    <small style="color: #666;">Intent: {conv['intent']} | Güven: {conv['confidence']:.2%}</small>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.header("📚 Komut Örnekleri")

        example_categories = {
            "⏰ Zaman": [
                "Saat kaç?",
                "Bugün ayın kaçı?",
                "Hangi gün?"
            ],
            "🧮 Hesaplama": [
                "5 artı 3",
                "10 çarpı 7",
                "100 bölü 4"
            ],
            "📝 Not Alma": [
                "Market listesi not al",
                "Notlarımı göster",
                "Notları sil"
            ],
            "⏰ Hatırlatıcı": [
                "30 dakika sonra hatırlat",
                "Yarın 9'da uyandır",
                "Hatırlatıcılar neler?"
            ],
            "📚 Öğrenci": [
                "Çalışma önerisi ver",
                "Motivasyon lazım",
                "Pomodoro başlat"
            ]
        }

        for category, examples in example_categories.items():
            with st.expander(category):
                for example in examples:
                    st.markdown(f"• {example}")

        st.divider()

        # Sistem bilgisi
        st.info("""
        **🔧 Sistem Bileşenleri:**
        - 🎤 Whisper (Ses Tanıma)
        - 🔊 pyttsx3 (Ses Sentezleme)
        - 🧠 Scikit-learn (ML)
        - 🎨 Streamlit (Arayüz)
        """)


if __name__ == "__main__":
    main()