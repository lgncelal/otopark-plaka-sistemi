from fast_alpr import ALPR

# ALPR sistemini başlat (plaka bulan + okuyan hazır modeller)
alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="cct-xs-v1-global-model",
)

# Test fotoğrafını oku
sonuclar = alpr.predict("test.jpeg")

# Bulunan her plakayı ekrana yaz
if sonuclar:
    for sonuc in sonuclar:
        plaka = sonuc.ocr.text
        guven = sonuc.ocr.confidence
        # guven bir liste olabilir (karakter başına skor) -> ortalamasını al
        if isinstance(guven, (list, tuple)):
            guven = sum(guven) / len(guven)
        print(f"Okunan plaka: {plaka}  (güven: {guven:.2f})")
else:
    print("Plaka bulunamadı.")