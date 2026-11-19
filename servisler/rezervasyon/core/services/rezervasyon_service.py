from datetime import datetime
from core.repositories.rezervasyon_repository import RezervasyonRepository

class RezervasyonService:
    @staticmethod
    def rezervasyon_yap(kullanici_id: int, menu_id: int) -> dict:
        return RezervasyonRepository.sp_rezervasyon_yap(kullanici_id, menu_id)

    @staticmethod
    def rezervasyon_iptal(kullanici_id: int, rezervasyon_id: int) -> dict:
        return RezervasyonRepository.sp_rezervasyon_iptal(kullanici_id, rezervasyon_id)

    @staticmethod
    def bakiye_yukle(kullanici_id: int, tutar: float) -> dict:
        return RezervasyonRepository.sp_bakiye_yukle(kullanici_id, tutar)

    @staticmethod
    def bakiye_getir(kullanici_id: int) -> float:
        return RezervasyonRepository.bakiye_getir(kullanici_id)

    @staticmethod
    def rezervasyonlarim(kullanici_id: int) -> list:
        rows = RezervasyonRepository.kullanici_rezervasyonlari(kullanici_id)
        simdi = datetime.now()
        liste = []
        for r in rows:
            durum = r[2]
            son_iptal = r[9] # datetime
            can_cancel = (durum == 'aktif') and (simdi < son_iptal if isinstance(son_iptal, datetime) else True)

            liste.append({
                "id": r[0],
                "menu_id": r[1],
                "durum": durum,
                "ucret": float(r[3]),
                "olusturma": str(r[4]),
                "iptal_zamani": str(r[5]) if r[5] else None,
                "tarih": str(r[6]),
                "yemekhane": r[7],
                "ogun": r[8],
                "son_iptal_saati": str(son_iptal),
                "can_cancel": can_cancel
            })
        return liste

    @staticmethod
    def hareketler(kullanici_id: int) -> list:
        rows = RezervasyonRepository.kullanici_bakiye_hareketleri(kullanici_id)
        return [{
            "id": r[0],
            "tutar": float(r[1]),
            "tur": r[2],
            "zaman": str(r[3]),
            "rezervasyon_id": r[4],
            "aciklama": r[5]
        } for r in rows]

    @staticmethod
    def doluluk_bilgisi(menu_id: int) -> dict:
        return RezervasyonRepository.menu_doluluk(menu_id)
