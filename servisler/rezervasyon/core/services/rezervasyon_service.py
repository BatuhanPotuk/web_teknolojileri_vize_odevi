from datetime import datetime
from core.repositories.rezervasyon_repository import RezervasyonRepository

class RezervasyonService:
    @staticmethod
    def rezervasyon_yap(kullanici_id: int, menu_id: int, porsiyon: str = 'tam') -> dict:
        if porsiyon not in ('tam', 'yarim'):
            porsiyon = 'tam'
        return RezervasyonRepository.sp_rezervasyon_yap(kullanici_id, menu_id, porsiyon)

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
            son_iptal = r[10] # datetime
            can_cancel = (durum == 'aktif') and (simdi < son_iptal if isinstance(son_iptal, datetime) else True)

            liste.append({
                "id": r[0],
                "menu_id": r[1],
                "durum": durum,
                "ucret": float(r[3]),
                "porsiyon": r[4] if len(r) > 4 else "tam",
                "olusturma": str(r[5]),
                "iptal_zamani": str(r[6]) if r[6] else None,
                "tarih": str(r[7]),
                "yemekhane": r[8],
                "ogun": r[9],
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

    @staticmethod
    def admin_rezervasyonlari(tarih: str = None, durum: str = None, rol: str = None) -> list:
        rows = RezervasyonRepository.admin_rezervasyonlar(tarih=tarih, durum=durum, rol=rol)
        return [{
            "id": r[0],
            "kullanici_id": r[1],
            "ad_soyad": r[2],
            "eposta": r[3],
            "ogrenci_no": r[4],
            "rol": r[5],
            "menu_id": r[6],
            "durum": r[7],
            "ucret": float(r[8]),
            "porsiyon": r[9] if len(r) > 9 else "tam",
            "olusturma": str(r[10]),
            "iptal_zamani": str(r[11]) if r[11] else None,
            "tarih": str(r[12]),
            "yemekhane": r[13],
            "ogun": r[14]
        } for r in rows]

    @staticmethod
    def admin_iptal_et(rezervasyon_id: int) -> dict:
        kullanici_id = RezervasyonRepository.rezervasyon_kullanici_id(rezervasyon_id)
        if not kullanici_id:
            raise ValueError("Rezervasyon bulunamadı.")
        return RezervasyonRepository.sp_rezervasyon_iptal(kullanici_id, rezervasyon_id)

