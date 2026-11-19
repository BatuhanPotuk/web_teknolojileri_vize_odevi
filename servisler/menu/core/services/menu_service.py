from datetime import datetime, date, timedelta
from core.repositories.menu_repository import MenuRepository
from core.repositories.onbellek_repository import OnbellekRepository

class MenuService:
    @staticmethod
    def gunun_menusu_getir(yemekhane_id: int, ogun_id: int, tarih_str: str = None) -> dict:
        if not tarih_str:
            tarih_str = date.today().strftime('%Y-%m-%d')

        rows = MenuRepository.gunun_menusu(yemekhane_id, ogun_id, tarih_str)
        if not rows:
            return None

        ilk = rows[0]
        menu_id = ilk[0]

        # 1. Redis önbellek kontrolü (yalnızca yemek içerikleri önbelleklenir)
        onbellek_yemekler = OnbellekRepository.menu_icerik_getir(menu_id)
        if onbellek_yemekler is not None:
            yemekler = onbellek_yemekler
        else:
            yemekler = []
            for r in rows:
                yemekler.append({
                    "id": r[9],
                    "ad": r[10],
                    "kategori": r[12],
                    "kategori_sira": r[13],
                    "kalori": r[14],
                    "vejetaryen": bool(r[15]),
                    "alerjenler": r[16] if r[16] else ""
                })
            # Redis'e kaydet (1 saat TTL)
            OnbellekRepository.menu_icerik_kaydet(menu_id, yemekler, ttl=3600)

        # Toplam kaloriyi uygulama toplar
        toplam_kalori = sum(y['kalori'] for y in yemekler)

        return {
            "menu_id": menu_id,
            "tarih": str(ilk[1]),
            "yemekhane_id": ilk[2],
            "yemekhane": ilk[3],
            "ogun_id": ilk[4],
            "ogun": ilk[5],
            "rezervasyon_son": str(ilk[6]),
            "ogrenci_fiyati": float(ilk[7]),
            "personel_fiyati": float(ilk[8]),
            "toplam_kalori": toplam_kalori,
            "yemekler": yemekler
        }

    @staticmethod
    def haftalik_menuleri_getir(yemekhane_id: int, rol: str = 'ogrenci', baslangic_str: str = None) -> list:
        simdi = datetime.now()
        if not baslangic_str:
            baslangic = date.today()
        else:
            baslangic = datetime.strptime(baslangic_str, '%Y-%m-%d').date()

        bitis = baslangic + timedelta(days=6)

        rows = MenuRepository.haftalik_menuler(yemekhane_id, baslangic.strftime('%Y-%m-%d'), bitis.strftime('%Y-%m-%d'))
        
        sonuclar = []
        for r in rows:
            menu_id = r[0]
            m_tarih = r[1]
            kapasite = r[4]
            rezervasyon_son = r[8] # datetime

            # Son saat kontrolü: datetime.now() >= rezervasyon_son ise canReserve = False
            can_reserve = simdi < rezervasyon_son if isinstance(rezervasyon_son, datetime) else True
            
            # Role göre fiyatlandırma (yönetici personel fiyatı öder)
            fiyat = float(r[9]) if rol == 'ogrenci' else float(r[10])

            sonuclar.append({
                "menu_id": menu_id,
                "tarih": str(m_tarih),
                "gun_adi": m_tarih.strftime('%A'),
                "yemekhane_id": r[2],
                "yemekhane": r[3],
                "kapasite": kapasite,
                "ogun_id": r[5],
                "ogun": r[6],
                "rezervasyon_son": str(rezervasyon_son),
                "fiyat": fiyat,
                "ogrenci_fiyati": float(r[9]),
                "personel_fiyati": float(r[10]),
                "can_reserve": can_reserve,
                "kalan_yer": kapasite # Rezervasyon servisi doluluk iç çağrısı ile güncellenir
            })

        return sonuclar

    @staticmethod
    def yemekhaneler_getir() -> list:
        rows = MenuRepository.yemekhaneler_getir()
        return [{"id": r[0], "ad": r[1], "kapasite": r[2]} for r in rows]

    @staticmethod
    def ogunler_getir() -> list:
        rows = MenuRepository.ogunler_getir()
        return [{"id": r[0], "ad": r[1], "sira": r[2], "son_saat": str(r[3])} for r in rows]

    @staticmethod
    def yonetici_istatistik_getir(rol: str) -> dict:
        if rol != 'yonetici':
            return None
        return MenuRepository.yonetici_istatistik()


