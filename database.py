from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Veritabanı dosyasının adı ve yeri (proje klasöründe arac.db oluşacak)
VERITABANI_URL = "sqlite:///./arac.db"

# Engine: veritabanıyla kurulan asıl bağlantı
engine = create_engine(
    VERITABANI_URL,
    connect_args={"check_same_thread": False},  # SQLite + FastAPI için gerekli ayar
)

# SessionLocal: her veritabanı işlemi için açılıp kapanan "oturum" üreticisi
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: tüm tablo sınıflarımızın miras alacağı temel sınıf
Base = declarative_base()


# Her istekte kullanılacak veritabanı oturumu (aç -> kullan -> kapat)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()