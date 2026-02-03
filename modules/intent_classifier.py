import json
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import numpy as np


class IntentClassifier:
    def __init__(self, commands_file="data/commands.json"):

        self.commands_file = commands_file
        self.intents = []
        self.vectorizer = None
        self.classifier = None

        # Türkçe karakterleri küçük harfe çevirme mapping
        self.turkish_lower_map = str.maketrans(
            "İıĞğÜüŞşÖöÇç",
            "iığğüüşşööçç"
        )

        self._load_commands()

    def _load_commands(self):
        """Komut tanımlarını JSON'dan yükler."""
        try:
            with open(self.commands_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.intents = data.get('intents', [])
            print(f"✓ {len(self.intents)} intent yüklendi")
        except Exception as e:
            print(f"❌ Komut dosyası yükleme hatası: {e}")
            self.intents = []

    def preprocess_text(self, text):
        """
        Metni ön işler (Türkçe karakter desteği ile).

        Args:
            text: Ham metin

        Returns:
            str: İşlenmiş metin
        """
        # Küçük harfe çevir (Türkçe karakterlerle)
        text = text.translate(self.turkish_lower_map).lower()

        # Noktalama işaretlerini kaldır
        text = re.sub(r'[^\w\s]', ' ', text)

        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def train(self, test_size=0.2, max_features=500):
        """
        Sınıflandırma modelini eğitir.

        Args:
            test_size: Test verisi oranı
            max_features: TF-IDF maksimum özellik sayısı
        """
        print("\n=== MODEL EĞİTİMİ BAŞLIYOR ===")

        # Eğitim verisi hazırla
        texts = []
        labels = []

        for intent in self.intents:
            tag = intent['tag']
            patterns = intent['patterns']

            for pattern in patterns:
                processed = self.preprocess_text(pattern)
                texts.append(processed)
                labels.append(tag)

        print(f"✓ Toplam {len(texts)} örnek hazırlandı")
        print(f"✓ {len(set(labels))} farklı sınıf var")

        # Veri seti çok küçükse train/test split yapma
        if len(texts) < 20:
            X_train, y_train = texts, labels
            X_test, y_test = texts, labels  # Kendini test et
            print("⚠ Veri seti küçük, train/test split yapılmadı")
        else:
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=test_size, random_state=42, stratify=labels
            )

        # TF-IDF vektörleştirme
        print("\n📊 TF-IDF vektörleme yapılıyor...")
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),  # Unigram ve bigram
            lowercase=True,
            analyzer='word'
        )

        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        # Logistic Regression ile eğitim
        print("🧠 Model eğitiliyor...")
        self.classifier = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs'
        )
        self.classifier.fit(X_train_vec, y_train)

        # Model performansı
        y_pred = self.classifier.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"\n✓ Model eğitimi tamamlandı!")
        print(f"✓ Doğruluk: {accuracy:.2%}")

        # Detaylı rapor
        print("\n📈 Sınıf bazında performans:")
        print(classification_report(y_test, y_pred, zero_division=0))

        return accuracy

    def predict(self, text, threshold=0.3):
        """
        Metinden intent tahmini yapar.

        Args:
            text: Kullanıcı metni
            threshold: Minimum güven eşiği (0-1)

        Returns:
            tuple: (intent_tag, confidence)
        """
        if not self.classifier or not self.vectorizer:
            # Model eğitilmemişse kural tabanlı yöntem kullan
            return self._rule_based_prediction(text)

        # Metni ön işle
        processed = self.preprocess_text(text)

        # Vektörleştir
        vector = self.vectorizer.transform([processed])

        # Tahmin yap
        prediction = self.classifier.predict(vector)[0]
        probabilities = self.classifier.predict_proba(vector)[0]
        confidence = np.max(probabilities)

        # Güven eşiğini kontrol et
        if confidence < threshold:
            # Düşük güven, kural tabanlı yönteme dön
            return self._rule_based_prediction(text)

        return prediction, confidence

    def _rule_based_prediction(self, text):
        """
        Kural tabanlı (anahtar kelime) intent tahmini.
        Args:
            text: Kullanıcı metni
        Returns:
            tuple: (intent_tag, confidence)
        """
        processed = self.preprocess_text(text)

        best_match = None
        max_score = 0

        for intent in self.intents:
            score = 0
            for pattern in intent['patterns']:
                pattern_processed = self.preprocess_text(pattern)

                # Kelime eşleşme sayısı
                pattern_words = set(pattern_processed.split())
                text_words = set(processed.split())
                common_words = pattern_words.intersection(text_words)

                if common_words:
                    # Jaccard benzerliği
                    similarity = len(common_words) / len(pattern_words.union(text_words))
                    score = max(score, similarity)

            if score > max_score:
                max_score = score
                best_match = intent['tag']

        # Eşleşme varsa döndür
        if max_score > 0.2:  # Minimum %20 benzerlik
            return best_match, max_score

        # Hiç eşleşme yoksa
        return "unknown", 0.0

    def get_response(self, intent_tag):
        """
        Intent için rastgele bir yanıt döndür.
        Args:
            intent_tag: Intent etiketi
        Returns:
            str: Yanıt metni
        """
        for intent in self.intents:
            if intent['tag'] == intent_tag:
                responses = intent.get('responses', [])
                if responses:
                    return np.random.choice(responses)

        return "Anlayamadım, lütfen tekrar eder misiniz?"

    def save_model(self, filepath="models/intent_classifier.pkl"):
        """Eğitilmiş modeli kaydeder."""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'vectorizer': self.vectorizer,
                    'classifier': self.classifier
                }, f)
            print(f"✓ Model kaydedildi: {filepath}")
        except Exception as e:
            print(f"❌ Model kaydetme hatası: {e}")

    def load_model(self, filepath="models/intent_classifier.pkl"):
        """Kaydedilmiş modeli yükler."""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.vectorizer = data['vectorizer']
                self.classifier = data['classifier']
            print(f"✓ Model yüklendi: {filepath}")
            return True
        except Exception as e:
            print(f"⚠ Model yükleme hatası: {e}")
            return False


# Test fonksiyonu
if __name__ == "__main__":
    print("=== INTENT CLASSIFICATION TESTİ ===\n")

    # Classifier'ı başlat
    classifier = IntentClassifier()

    # Model eğit
    accuracy = classifier.train()

    # Modeli kaydet
    import os

    os.makedirs("models", exist_ok=True)
    classifier.save_model()

    print("\n" + "=" * 50)
    print("Test Tahminleri:\n")

    test_sentences = [
        "merhaba nasılsın",
        "saat kaç oldu",
        "bugün ayın kaçı",
        "5 artı 3 kaç eder",
        "bunu not al",
        "notlarımı göster",
        "yarın saat 9'da bana hatırlat",
        "çalışma önerisi ver",
        "motivasyon lazım",
        "teşekkür ederim",
        "görüşürüz"
    ]

    for sentence in test_sentences:
        intent, confidence = classifier.predict(sentence)
        response = classifier.get_response(intent)
        print(f"📝 Girdi: '{sentence}'")
        print(f"🎯 Intent: {intent} (Güven: {confidence:.2%})")
        print(f"💬 Yanıt: {response}")
        print("-" * 50)

    print("\nTest tamamlandı!")