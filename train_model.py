import sys
import os
from modules.intent_classifier import IntentClassifier


def main():
    print("=" * 60)
    print("TÜRKÇE SESLİ ASİSTAN - MODEL EĞİTİMİ")
    print("=" * 60)

    # Classifier başlat
    print("\n📂 Komutlar yükleniyor...")
    classifier = IntentClassifier(commands_file="data/commands.json")

    if not classifier.intents:
        print("❌ HATA: Komut dosyası bulunamadı veya boş!")
        print("data/commands.json dosyasını kontrol edin.")
        return

    print(f"✓ {len(classifier.intents)} intent yüklendi")

    # Intent'leri göster
    print("\n📋 Eğitilecek Intent'ler:")
    for idx, intent in enumerate(classifier.intents, 1):
        print(f"  {idx}. {intent['tag']} - {len(intent['patterns'])} örnek")

    # Eğitime başla
    print("\n" + "=" * 60)
    input("Eğitime başlamak için Enter'a basın...")
    print()

    # Model eğit
    accuracy = classifier.train(test_size=0.2, max_features=500)

    # Modeli kaydet
    print("\n💾 Model kaydediliyor...")
    os.makedirs("models", exist_ok=True)
    classifier.save_model("models/intent_classifier.pkl")

    print("\n" + "=" * 60)
    print(f"✅ EĞİTİM TAMAMLANDI!")
    print(f"📊 Model Doğruluğu: {accuracy:.2%}")
    print(f"💾 Model Konumu: models/intent_classifier.pkl")
    print("=" * 60)

    # Test tahminleri
    print("\n🧪 Test Tahminleri:")
    print("-" * 60)

    test_sentences = [
        "merhaba nasılsın",
        "saat kaç şimdi",
        "bugün ne günü",
        "5 artı 3 kaç eder",
        "bunu not al lütfen",
        "notlarımı göster",
        "yarın sabah 8'de hatırlat",
        "çalışma planı yap",
        "motivasyon lazım bana",
        "teşekkürler çok sağol"
    ]

    for sentence in test_sentences:
        intent, confidence = classifier.predict(sentence)
        response = classifier.get_response(intent)

        print(f"\n📝 Girdi: '{sentence}'")
        print(f"🎯 Intent: {intent}")
        print(f"📊 Güven: {confidence:.2%}")
        print(f"💬 Yanıt: {response}")
        print("-" * 60)

    print("\n✅ Test tamamlandı!")
    print("\n💡 Şimdi uygulamayı çalıştırabilirsiniz:")
    print("   streamlit run app.py")


if __name__ == "__main__":
    main()
