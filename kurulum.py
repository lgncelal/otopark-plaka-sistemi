from database import engine, SessionLocal, Base
from models import KayitliPlaka, Kullanici
import bcrypt

def sifre_hashle(sifre: str) -> str:
    return bcrypt.hashpw(sifre.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# 1. Tabloları oluştur
Base.metadata.create_all(bind=engine)
print("Veritabanı ve tablolar oluşturuldu.")

db = SessionLocal()

# 2. Test plakaları
if db.query(KayitliPlaka).count() == 0:
    test_plakalar = [
        KayitliPlaka(plaka="34FRK052", sahip_adi="Ahmet Yılmaz"),
        KayitliPlaka(plaka="06ABC123", sahip_adi="Ayşe Demir"),
        KayitliPlaka(plaka="42KLM789", sahip_adi="Mehmet Kaya"),
    ]
    db.add_all(test_plakalar)
    db.commit()
    print(f"{len(test_plakalar)} test plakası eklendi.")
else:
    print("Plakalar zaten kayıtlı, yeni ekleme yapılmadı.")

# 3. Test kullanıcıları
if db.query(Kullanici).count() == 0:
    kullanicilar = [
        Kullanici(kullanici_adi="admin", sifre_hash=sifre_hashle("admin123"), rol="admin"),
        Kullanici(kullanici_adi="gorevli", sifre_hash=sifre_hashle("gorevli123"), rol="gorevli"),
    ]
    db.add_all(kullanicilar)
    db.commit()
    print("2 test kullanıcısı eklendi (admin / admin123, gorevli / gorevli123)")
else:
    print("Kullanıcılar zaten kayıtlı, yeni ekleme yapılmadı.")

db.close()