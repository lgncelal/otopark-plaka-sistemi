# 🅿️ Otopark Plaka Tanıma Sistemi

Araç fotoğrafından plakayı otomatik okuyup, aracın kayıtlı olup olmadığını kontrol eden ve giriş iznini yöneten web tabanlı bir otopark sistemi. Kapalı/özel otoparklar (site, kurum, tesis) için tasarlanmıştır.

## 🎯 Ne Yapar?

- Yüklenen araç fotoğrafından plakayı otomatik tespit edip okur
- Plakanın kayıtlı (izinli) araçlar listesinde olup olmadığını kontrol eder
- Kayıtlıysa giriş izni verir, değilse reddeder
- Her giriş denemesini zaman damgasıyla kaydeder (log)
- Kayıtlı araçları panelden ekleyip silmeyi sağlar
- Günlük istatistikleri (toplam giriş, izinli/yetkisiz sayısı) gösterir

## 🛠️ Kullanılan Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Plaka Tanıma | fast-alpr (YOLOv9 plaka tespiti + CCT tabanlı OCR) |
| Backend | Python, FastAPI |
| Veritabanı | SQLite + SQLAlchemy (ORM) |
| Görüntü İşleme | Pillow |
| Arayüz | HTML, CSS, JavaScript |
| Model Çalıştırma | ONNX Runtime |

## 🏗️ Mimari
┌─────────────┐ HTTP ┌──────────────┐
│ Panel │ ──────────────► │ FastAPI │
│ (HTML/JS) │ ◄────────────── │ (Backend) │
└─────────────┘ JSON cevap └──────┬───────┘
│
┌──────────────┼──────────────┐
▼ ▼
┌─────────────┐ ┌─────────────┐
│ fast-alpr │ │ SQLite │
│ (Plaka AI) │ │ (Veritabanı)│
└─────────────┘ └─────────────┘


Kullanıcı panelden araç fotoğrafı yükler → FastAPI fotoğrafı alır → fast-alpr plakayı okur → SQLite'ta kayıtlı mı diye kontrol edilir → sonuç ve giriş kaydı panele döner.

## 🚀 Kurulum ve Çalıştırma

```bash
# Depoyu klonlayın
git clone https://github.com/lgncelal/otopark-plaka-sistemi.git
cd otopark-plaka-sistemi

# Sanal ortam oluşturun ve aktive edin
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Veritabanını oluşturun ve test verisini ekleyin
python kurulum.py

# Servisi başlatın
uvicorn main:app --reload
```

Tarayıcıda `http://127.0.0.1:8000/` adresini açın.

## 📁 Proje Yapısı

| Dosya | Açıklama |
|-------|----------|
| `main.py` | FastAPI uygulaması, API endpoint'leri ve iş mantığı |
| `database.py` | Veritabanı bağlantısı ve oturum yönetimi |
| `models.py` | Veritabanı tabloları (kayıtlı plakalar, giriş logları) |
| `kurulum.py` | Veritabanını oluşturan ve test verisi ekleyen betik |
| `panel.html` | Web arayüzü (frontend) |
| `requirements.txt` | Python bağımlılıkları |

## 🔌 API Endpoint'leri

| Metod | Yol | Açıklama |
|-------|-----|----------|
| GET | `/` | Web panelini açar |
| POST | `/giris` | Fotoğraf alır, plakayı okur, giriş kontrolü yapar |
| GET | `/kayitli-plakalar` | Kayıtlı araçları listeler |
| GET | `/loglar` | Giriş kayıtlarını listeler |
| GET | `/istatistik` | Günlük özet istatistikleri döner |
| POST | `/plaka-ekle` | Yeni kayıtlı plaka ekler |
| DELETE | `/plaka-sil/{id}` | Kayıtlı plaka siler |

## 📝 Notlar

- Plaka tanıma için hazır eğitilmiş fast-alpr modelleri kullanılmıştır; sıfırdan model eğitimi yapılmamıştır.
- SQLite, kurulum gerektirmeyen yapısı sayesinde seçilmiştir; daha büyük ölçek için PostgreSQL'e geçiş ORM sayesinde kolaydır.