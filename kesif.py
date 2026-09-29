from fast_alpr import ALPR

alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="cct-xs-v1-global-model",
)

sonuclar = alpr.predict("test.jpeg")

# İlk sonucun tüm yapısını görelim
sonuc = sonuclar[0]
print("=== SONUÇ YAPISI ===")
print(sonuc)
print()
print("=== detection (tespit) ===")
print(sonuc.detection)
print()
print("=== bounding box ===")
print(sonuc.detection.bounding_box)