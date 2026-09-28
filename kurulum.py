from database import engine, SessionLocal, Base
from models import KayitliPlaka

# 1. Tanımladığımız tablolardan gerçek veritabanı dosyasını (arac.db) oluştur
Base.metadata.create_all(bind=engine)
print("Veritabanı ve tablolar oluşturuldu.")

# 2. Birkaç test plakası ekle
db = SessionLocal()

# Zaten var mı diye bak, tekrar tekrar eklemeyi önle
mevcut = db.query(KayitliPlaka).count()
if mevcut == 0:
    test_plakalar = [
        KayitliPlaka(plaka="34FRK052", sahip_adi="Ahmet Yılmaz"),
        KayitliPlaka(plaka="06ABC123", sahip_adi="Ayşe Demir"),
        KayitliPlaka(plaka="42KLM789", sahip_adi="Mehmet Kaya"),
    ]
    db.add_all(test_plakalar)
    db.commit()
    print(f"{len(test_plakalar)} test plakası eklendi.")
else:
    print(f"Zaten {mevcut} plaka kayıtlı, yeni ekleme yapılmadı.")

db.close()