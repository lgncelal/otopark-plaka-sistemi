import shutil
import os
import base64
import io
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from PIL import Image
from fast_alpr import ALPR
from datetime import date

from database import engine, Base, get_db
from models import KayitliPlaka, GirisLog

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Otopark Plaka Sistemi")

alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="cct-xs-v1-global-model",
)


@app.get("/", response_class=HTMLResponse)
def ana_sayfa():
    return FileResponse("panel.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/giris")
async def giris(dosya: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Fotoğrafı geçici kaydet
    gecici_yol = f"gecici_{dosya.filename}"
    with open(gecici_yol, "wb") as f:
        shutil.copyfileobj(dosya.file, f)

    # 2. Plakayı oku
    sonuclar = alpr.predict(gecici_yol)
    if not sonuclar:
        os.remove(gecici_yol)
        return {"bulundu": False, "mesaj": "Plaka okunamadı"}

    # 3. Plaka + konum
    sonuc = sonuclar[0]
    plaka = sonuc.ocr.text
    kutu = sonuc.detection.bounding_box

    # 4. Görselleri hazırla
    gorsel = Image.open(gecici_yol).convert("RGB")
    plaka_kirpik = gorsel.crop((kutu.x1, kutu.y1, kutu.x2, kutu.y2))

    def gorsel_to_base64(img):
        tampon = io.BytesIO()
        img.save(tampon, format="JPEG")
        return base64.b64encode(tampon.getvalue()).decode("utf-8")

    arac_foto_b64 = gorsel_to_base64(gorsel)
    plaka_foto_b64 = gorsel_to_base64(plaka_kirpik)
    os.remove(gecici_yol)

    # 5. Kayıtlı mı? -> izinli/yetkisiz
    kayit = db.query(KayitliPlaka).filter(KayitliPlaka.plaka == plaka).first()
    izinli = kayit is not None

    # 6. Logla
    log = GirisLog(plaka=plaka, izinli=izinli)
    db.add(log)
    db.commit()

    # 7. Sonucu dön
    return {
        "bulundu": True,
        "plaka": plaka,
        "izinli": izinli,
        "sahip": kayit.sahip_adi if kayit else None,
        "mesaj": "Kapı açıldı - giriş izni verildi" if izinli else "Yetkisiz araç - giriş reddedildi",
        "arac_foto": arac_foto_b64,
        "plaka_foto": plaka_foto_b64,
    }


@app.get("/kayitli-plakalar")
def kayitli_plakalar(db: Session = Depends(get_db)):
    plakalar = db.query(KayitliPlaka).all()
    return [{"id": p.id, "plaka": p.plaka, "sahip": p.sahip_adi} for p in plakalar]


@app.get("/loglar")
def loglar(db: Session = Depends(get_db)):
    kayitlar = db.query(GirisLog).order_by(GirisLog.zaman.desc()).all()
    return [
        {
            "id": k.id,
            "plaka": k.plaka,
            "zaman": k.zaman.strftime("%d.%m.%Y %H:%M:%S"),
            "izinli": k.izinli,
        }
        for k in kayitlar
    ]


@app.post("/plaka-ekle")
def plaka_ekle(plaka: str = Form(...), sahip: str = Form(...), db: Session = Depends(get_db)):
    plaka = plaka.replace(" ", "").upper()
    sahip = sahip.strip().title()

    mevcut = db.query(KayitliPlaka).filter(KayitliPlaka.plaka == plaka).first()
    if mevcut:
        raise HTTPException(status_code=400, detail="Bu plaka zaten kayıtlı")

    yeni = KayitliPlaka(plaka=plaka, sahip_adi=sahip)
    db.add(yeni)
    db.commit()
    return {"basarili": True, "plaka": plaka}


@app.delete("/plaka-sil/{plaka_id}")
def plaka_sil(plaka_id: int, db: Session = Depends(get_db)):
    kayit = db.query(KayitliPlaka).filter(KayitliPlaka.id == plaka_id).first()
    if not kayit:
        raise HTTPException(status_code=404, detail="Plaka bulunamadı")
    db.delete(kayit)
    db.commit()
    return {"basarili": True}


@app.get("/istatistik")
def istatistik(db: Session = Depends(get_db)):
    toplam_kayitli = db.query(KayitliPlaka).count()

    bugun = date.today()
    bugunku_loglar = db.query(GirisLog).filter(
        GirisLog.zaman >= datetime(bugun.year, bugun.month, bugun.day)
    ).all()

    bugun_toplam = len(bugunku_loglar)
    bugun_izinli = sum(1 for l in bugunku_loglar if l.izinli)
    bugun_yetkisiz = bugun_toplam - bugun_izinli

    return {
        "toplam_kayitli": toplam_kayitli,
        "bugun_toplam": bugun_toplam,
        "bugun_izinli": bugun_izinli,
        "bugun_yetkisiz": bugun_yetkisiz,
    }