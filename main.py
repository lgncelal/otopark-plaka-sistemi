import shutil
import os
from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from fast_alpr import ALPR

from database import engine, Base, get_db
from models import KayitliPlaka, GirisLog

# Uygulama açılırken tabloların var olduğundan emin ol
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Otopark Plaka Sistemi")

# ALPR sistemini uygulama açılırken bir kez başlat
alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="cct-xs-v1-global-model",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/giris")
async def giris(dosya: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Yüklenen fotoğrafı geçici kaydet
    gecici_yol = f"gecici_{dosya.filename}"
    with open(gecici_yol, "wb") as f:
        shutil.copyfileobj(dosya.file, f)

    # 2. Plakayı oku
    sonuclar = alpr.predict(gecici_yol)
    os.remove(gecici_yol)

    if not sonuclar:
        return {"bulundu": False, "mesaj": "Plaka okunamadı"}

    # 3. Okunan plakayı al
    sonuc = sonuclar[0]
    plaka = sonuc.ocr.text

    # 4. Bu plaka kayıtlı mı diye veritabanına bak
    kayit = db.query(KayitliPlaka).filter(KayitliPlaka.plaka == plaka).first()
    izinli = kayit is not None

    # 5. Giriş denemesini log tablosuna yaz
    log = GirisLog(plaka=plaka, izinli=izinli)
    db.add(log)
    db.commit()

    # 6. Sonucu dön
    return {
        "bulundu": True,
        "plaka": plaka,
        "izinli": izinli,
        "sahip": kayit.sahip_adi if kayit else None,
        "mesaj": "Giriş izni verildi" if izinli else "Yetkisiz araç",
    }