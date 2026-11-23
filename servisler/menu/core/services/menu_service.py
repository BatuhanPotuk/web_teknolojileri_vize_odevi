from datetime import datetime, date, timedelta
from core.repositories.menu_repository import MenuRepository
from core.repositories.onbellek_repository import OnbellekRepository

class MenuService:
    @staticmethod
    def gunun_menusu_getir(yemekhane_id: int, ogun_id: int, tarih_str: str = None) -> dict:
        if not tarih_str:
            tarih_str = date.today().strftime('%Y-%m-%d')

        # 1. REDIS ÖNBELLEK KONTROLÜ (Kural: menu:{yemekhane_id}:{tarih}:{ogun_id})
        onbellek_menu = OnbellekRepository.menu_getir(yemekhane_id, tarih_str, ogun_id)
        if onbellek_menu is not None:
            print(f"[CACHE HIT] Menü Redis'ten getirildi: menu:{yemekhane_id}:{tarih_str}:{ogun_id}", flush=True)
            return onbellek_menu

        # 2. Önbellekte yoksa VERİTABANINDAN ÇEK (CACHE MISS)
        print(f"[CACHE MISS] Menü veritabanından çekiliyor: menu:{yemekhane_id}:{tarih_str}:{ogun_id}", flush=True)
        rows = MenuRepository.gunun_menusu(yemekhane_id, ogun_id, tarih_str)
        if not rows:
            return None

        ilk = rows[0]
        menu_id = ilk[0]

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

        # Toplam kaloriyi uygulama hesaplar
        toplam_kalori = sum(y['kalori'] for y in yemekler)

        menu_verisi = {
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

        # 3. REDİS'E KAYDET (O günün sonuna kadar TTL)
        OnbellekRepository.menu_kaydet(yemekhane_id, tarih_str, ogun_id, menu_verisi)
        print(f"[CACHE SAVE] Menü Redis'e kaydedildi: menu:{yemekhane_id}:{tarih_str}:{ogun_id}", flush=True)

        return menu_verisi

    @staticmethod
    def menu_guncelle(menu_id: int, ogrenci_fiyati: float = None, personel_fiyati: float = None) -> dict:
        row = MenuRepository.menu_bilgisi(menu_id)
        if not row:
            return None
        yh_id = row[1]
        tarih_str = str(row[2])
        ogun_id = row[3]

        if ogrenci_fiyati is not None or personel_fiyati is not None:
            MenuRepository.menu_fiyat_guncelle(menu_id, ogrenci_fiyati, personel_fiyati)

        # REDIS ÖNBELLEK GEÇERSİZ KILMA (EVICT / INVALIDATE)
        OnbellekRepository.menu_sil(yh_id, tarih_str, ogun_id)
        print(f"[CACHE EVICT] Menü #{menu_id} güncellendi, önbellek silindi: menu:{yh_id}:{tarih_str}:{ogun_id}", flush=True)
        return {
            "mesaj": f"Menü #{menu_id} başarıyla güncellendi ve Redis önbelleği temizlendi.",
            "anahtar": f"menu:{yh_id}:{tarih_str}:{ogun_id}"
        }

    @staticmethod
    def menu_sil(menu_id: int) -> dict:
        row = MenuRepository.menu_bilgisi(menu_id)
        if not row:
            return None
        yh_id = row[1]
        tarih_str = str(row[2])
        ogun_id = row[3]

        MenuRepository.menu_sil(menu_id)
        # REDIS ÖNBELLEK GEÇERSİZ KILMA (EVICT / INVALIDATE)
        OnbellekRepository.menu_sil(yh_id, tarih_str, ogun_id)
        print(f"[CACHE EVICT] Menü #{menu_id} silindi, önbellek temizlendi: menu:{yh_id}:{tarih_str}:{ogun_id}", flush=True)
        return {
            "mesaj": f"Menü #{menu_id} başarıyla silindi ve Redis önbelleği temizlendi.",
            "anahtar": f"menu:{yh_id}:{tarih_str}:{ogun_id}"
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

    @staticmethod
    def tum_yemekleri_getir() -> list:
        rows = MenuRepository.yemekler_tumu()
        return [{
            "id": r[0],
            "ad": r[1],
            "kategori_id": r[2],
            "kategori": r[3],
            "kategori_sira": r[4],
            "kalori": r[5],
            "vejetaryen": bool(r[6])
        } for r in rows]

    @staticmethod
    def menuleri_listele(tarih: str = None) -> list:
        rows = MenuRepository.menuler_listesi(tarih=tarih)
        return [{
            "id": r[0],
            "tarih": str(r[1]),
            "yemekhane_id": r[2],
            "yemekhane": r[3],
            "ogun_id": r[4],
            "ogun": r[5],
            "ogrenci_fiyati": float(r[6]),
            "personel_fiyati": float(r[7]),
            "yemek_sayisi": r[8],
            "aktif_rezervasyon": r[9]
        } for r in rows]

    @staticmethod
    def menu_detay(menu_id: int) -> dict:
        return MenuRepository.menu_detay_getir(menu_id)

    @staticmethod
    def yeni_menu_olustur(yemekhane_id: int, tarih: str, ogun_id: int, ogrenci_fiyati: float, personel_fiyati: float, yemek_idler: list = None) -> dict:
        menu_id = MenuRepository.menu_olustur(yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati)
        if yemek_idler:
            for y_id in yemek_idler:
                try:
                    MenuRepository.menu_yemek_ekle(menu_id, int(y_id))
                except Exception:
                    pass

        # Önbelleği temizle
        OnbellekRepository.menu_sil(yemekhane_id, tarih, ogun_id)
        print(f"[CACHE EVICT] Yeni menü #{menu_id} eklendi, önbellek temizlendi: menu:{yemekhane_id}:{tarih}:{ogun_id}", flush=True)

        return {
            "id": menu_id,
            "mesaj": f"Menü #{menu_id} başarıyla oluşturuldu.",
            "anahtar": f"menu:{yemekhane_id}:{tarih}:{ogun_id}"
        }

    @staticmethod
    def menu_yemek_ekle(menu_id: int, yemek_id: int) -> dict:
        info = MenuRepository.menu_bilgisi(menu_id)
        if not info:
            return None
        MenuRepository.menu_yemek_ekle(menu_id, yemek_id)
        yh_id = info[1]
        tarih_str = str(info[2])
        ogun_id = info[3]
        OnbellekRepository.menu_sil(yh_id, tarih_str, ogun_id)
        print(f"[CACHE EVICT] Menü #{menu_id} yemek eklendi, önbellek temizlendi: menu:{yh_id}:{tarih_str}:{ogun_id}", flush=True)
        return {"mesaj": "Yemek menüye eklendi ve önbellek güncellendi."}

    @staticmethod
    def menu_yemek_sil(menu_id: int, yemek_id: int) -> dict:
        info = MenuRepository.menu_bilgisi(menu_id)
        if not info:
            return None
        MenuRepository.menu_yemek_sil(menu_id, yemek_id)
        yh_id = info[1]
        tarih_str = str(info[2])
        ogun_id = info[3]
        OnbellekRepository.menu_sil(yh_id, tarih_str, ogun_id)
        print(f"[CACHE EVICT] Menü #{menu_id} yemek çıkarıldı, önbellek temizlendi: menu:{yh_id}:{tarih_str}:{ogun_id}", flush=True)
        return {"mesaj": "Yemek menüden çıkarıldı ve önbellek güncellendi."}



