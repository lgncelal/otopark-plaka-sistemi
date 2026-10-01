from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base


class KayitliPlaka(Base):
    __tablename__ = "kayitli_plakalar"

    id = Column(Integer, primary_key=True, index=True)
    plaka = Column(String, unique=True, index=True, nullable=False)
    sahip_adi = Column(String, nullable=True)


class GirisLog(Base):
    __tablename__ = "giris_loglari"

    id = Column(Integer, primary_key=True, index=True)
    plaka = Column(String, index=True, nullable=False)
    zaman = Column(DateTime, default=datetime.now)
    izinli = Column(Boolean, default=False)