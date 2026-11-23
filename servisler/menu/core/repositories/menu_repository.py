from django.db import connections

class MenuRepository:
    @staticmethod
    def gunun_menusu(yemekhane_id: int, ogun_id: int, tarih: str):
        with connections['replica'].cursor() as cursor:
            sql = """
                SELECT menu_id, tarih, yemekhane_id, yemekhane, ogun_id, ogun,
                       rezervasyon_son, ogrenci_fiyati, personel_fiyati,
                       yemek_id, yemek, kategori_id, kategori, kategori_sira,
                       kalori, vejetaryen, alerjenler
                  FROM v_menu_detay
                 WHERE yemekhane_id = %s AND ogun_id = %s AND tarih = %s
                 ORDER BY kategori_sira, yemek
            """
            cursor.execute(sql, [yemekhane_id, ogun_id, tarih])
            rows = cursor.fetchall()
            return rows

    @staticmethod
    def haftalik_menuler(yemekhane_id: int, baslangic_tarih: str, bitis_tarih: str):
        with connections['replica'].cursor() as cursor:
            sql = """
                SELECT m.id AS menu_id, m.tarih, m.yemekhane_id, yh.ad AS yemekhane, yh.kapasite,
                       m.ogun_id, o.ad AS ogun, o.sira AS ogun_sira,
                       TIMESTAMP(m.tarih, o.son_saat) AS rezervasyon_son,
                       m.ogrenci_fiyati, m.personel_fiyati
                  FROM menuler m
                  JOIN yemekhaneler yh ON yh.id = m.yemekhane_id
                  JOIN ogunler o ON o.id = m.ogun_id
                 WHERE m.yemekhane_id = %s AND m.tarih BETWEEN %s AND %s
                 ORDER BY m.tarih, o.sira
            """
            cursor.execute(sql, [yemekhane_id, baslangic_tarih, bitis_tarih])
            rows = cursor.fetchall()
            return rows

    @staticmethod
    def yemekhaneler_getir():
        with connections['replica'].cursor() as cursor:
            cursor.execute("SELECT id, ad, kapasite FROM yemekhaneler ORDER BY id")
            return cursor.fetchall()

    @staticmethod
    def ogunler_getir():
        with connections['replica'].cursor() as cursor:
            cursor.execute("SELECT id, ad, sira, son_saat FROM ogunler ORDER BY sira")
            return cursor.fetchall()

    @staticmethod
    def menu_bilgisi(menu_id: int):
        with connections['replica'].cursor() as cursor:
            cursor.execute("SELECT id, yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati FROM menuler WHERE id = %s", [menu_id])
            return cursor.fetchone()

    @staticmethod
    def menu_fiyat_guncelle(menu_id: int, ogrenci_fiyati: float, personel_fiyati: float):
        with connections['default'].cursor() as cursor:
            cursor.execute(
                "UPDATE menuler SET ogrenci_fiyati = %s, personel_fiyati = %s WHERE id = %s",
                [ogrenci_fiyati, personel_fiyati, menu_id]
            )

    @staticmethod
    def yemekler_tumu():
        with connections['replica'].cursor() as cursor:
            sql = """
                SELECT y.id, y.ad, y.kategori_id, k.ad AS kategori, k.sira AS kategori_sira,
                       y.kalori, y.vejetaryen
                  FROM yemekler y
                  JOIN yemek_kategorileri k ON k.id = y.kategori_id
                 ORDER BY k.sira, y.ad
            """
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def menuler_listesi(tarih: str = None, limit: int = 50):
        with connections['replica'].cursor() as cursor:
            params = []
            where_sql = ""
            if tarih:
                where_sql = "WHERE m.tarih = %s"
                params.append(tarih)
            sql = f"""
                SELECT m.id, m.tarih, m.yemekhane_id, yh.ad AS yemekhane,
                       m.ogun_id, o.ad AS ogun, m.ogrenci_fiyati, m.personel_fiyati,
                       (SELECT COUNT(*) FROM menu_yemekleri my WHERE my.menu_id = m.id) AS yemek_sayisi,
                       (SELECT COUNT(*) FROM rezervasyonlar r WHERE r.menu_id = m.id AND r.durum = 'aktif') AS aktif_rezervasyon
                  FROM menuler m
                  JOIN yemekhaneler yh ON yh.id = m.yemekhane_id
                  JOIN ogunler o ON o.id = m.ogun_id
                 {where_sql}
                 ORDER BY m.tarih DESC, o.sira ASC
                 LIMIT {limit}
            """
            cursor.execute(sql, params)
            return cursor.fetchall()

    @staticmethod
    def menu_detay_getir(menu_id: int):
        with connections['replica'].cursor() as cursor:
            sql_m = """
                SELECT m.id, m.tarih, m.yemekhane_id, yh.ad AS yemekhane,
                       m.ogun_id, o.ad AS ogun, m.ogrenci_fiyati, m.personel_fiyati
                  FROM menuler m
                  JOIN yemekhaneler yh ON yh.id = m.yemekhane_id
                  JOIN ogunler o ON o.id = m.ogun_id
                 WHERE m.id = %s
            """
            cursor.execute(sql_m, [menu_id])
            menu_row = cursor.fetchone()
            if not menu_row:
                return None

            sql_y = """
                SELECT y.id, y.ad, k.ad AS kategori, y.kalori, y.vejetaryen
                  FROM menu_yemekleri my
                  JOIN yemekler y ON y.id = my.yemek_id
                  JOIN yemek_kategorileri k ON k.id = y.kategori_id
                 WHERE my.menu_id = %s
                 ORDER BY k.sira, y.ad
            """
            cursor.execute(sql_y, [menu_id])
            yemek_rows = cursor.fetchall()

            return {
                "id": menu_row[0],
                "tarih": str(menu_row[1]),
                "yemekhane_id": menu_row[2],
                "yemekhane": menu_row[3],
                "ogun_id": menu_row[4],
                "ogun": menu_row[5],
                "ogrenci_fiyati": float(menu_row[6]),
                "personel_fiyati": float(menu_row[7]),
                "yemekler": [{
                    "id": yr[0],
                    "ad": yr[1],
                    "kategori": yr[2],
                    "kalori": yr[3],
                    "vejetaryen": bool(yr[4])
                } for yr in yemek_rows]
            }

    @staticmethod
    def menu_olustur(yemekhane_id: int, tarih: str, ogun_id: int, ogrenci_fiyati: float, personel_fiyati: float):
        with connections['default'].cursor() as cursor:
            sql = """
                INSERT INTO menuler (yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, [yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati])
            return cursor.lastrowid

    @staticmethod
    def menu_yemek_ekle(menu_id: int, yemek_id: int):
        with connections['default'].cursor() as cursor:
            sql = "INSERT IGNORE INTO menu_yemekleri (menu_id, yemek_id) VALUES (%s, %s)"
            cursor.execute(sql, [menu_id, yemek_id])
            return True

    @staticmethod
    def menu_yemek_sil(menu_id: int, yemek_id: int):
        with connections['default'].cursor() as cursor:
            sql = "DELETE FROM menu_yemekleri WHERE menu_id = %s AND yemek_id = %s"
            cursor.execute(sql, [menu_id, yemek_id])
            return True

    @staticmethod
    def menu_sil(menu_id: int):
        with connections['default'].cursor() as cursor:
            cursor.execute("DELETE FROM menuler WHERE id = %s", [menu_id])
            return True

    @staticmethod
    def yonetici_istatistik():
        with connections['replica'].cursor() as cursor:
            # Bugünün rezervasyon sayıları ve gelir kırılımları
            sql_genel = """
                SELECT 
                    SUM(CASE WHEN r.durum = 'aktif' THEN 1 ELSE 0 END) AS aktif_rezervasyon,
                    SUM(CASE WHEN r.durum = 'iptal' THEN 1 ELSE 0 END) AS iptal_rezervasyon,
                    COUNT(r.id) AS toplam_rezervasyon,
                    COALESCE(SUM(CASE WHEN r.durum = 'aktif' THEN r.ucret ELSE 0 END), 0) AS toplam_gelir,
                    COALESCE(SUM(CASE WHEN r.durum = 'aktif' AND k.rol = 'ogrenci' THEN r.ucret ELSE 0 END), 0) AS ogrenci_gelir,
                    COALESCE(SUM(CASE WHEN r.durum = 'aktif' AND k.rol = 'personel' THEN r.ucret ELSE 0 END), 0) AS personel_gelir
                FROM rezervasyonlar r
                JOIN kullanicilar k ON k.id = r.kullanici_id
                JOIN menuler m ON m.id = r.menu_id
                WHERE m.tarih = CURDATE()
            """
            cursor.execute(sql_genel)
            genel = cursor.fetchone()

            # Yemekhane bazlı doluluk
            sql_yh = """
                SELECT yh.id, yh.ad, yh.kapasite,
                       COUNT(r.id) AS aktif_rezervasyon
                  FROM yemekhaneler yh
                  LEFT JOIN menuler m ON m.yemekhane_id = yh.id AND m.tarih = CURDATE()
                  LEFT JOIN rezervasyonlar r ON r.menu_id = m.id AND r.durum = 'aktif'
                 GROUP BY yh.id, yh.ad, yh.kapasite
                 ORDER BY yh.id
            """
            cursor.execute(sql_yh)
            yemekhaneler = cursor.fetchall()

            # Genel değerlendirme ortalaması
            sql_puan = "SELECT ROUND(AVG(puan), 1), COUNT(*) FROM degerlendirmeler"
            cursor.execute(sql_puan)
            puan_row = cursor.fetchone()
            ortalama_puan = float(puan_row[0]) if (puan_row and puan_row[0] is not None) else 0.0
            toplam_yorum = puan_row[1] if puan_row else 0

            # En çok tercih edilen 5 yemek
            sql_populer = """
                SELECT y.ad, k.ad AS kategori, COUNT(r.id) AS tercih_sayisi
                  FROM rezervasyonlar r
                  JOIN menuler m ON m.id = r.menu_id
                  JOIN menu_yemekleri my ON my.menu_id = m.id
                  JOIN yemekler y ON y.id = my.yemek_id
                  JOIN yemek_kategorileri k ON k.id = y.kategori_id
                 WHERE r.durum IN ('aktif', 'kullanildi')
                 GROUP BY y.id, y.ad, k.ad
                 ORDER BY tercih_sayisi DESC
                 LIMIT 5
            """
            cursor.execute(sql_populer)
            populer_rows = cursor.fetchall()

            aktif_sayi = int(genel[0] or 0) if genel else 0
            iptal_sayi = int(genel[1] or 0) if genel else 0
            toplam_sayi = int(genel[2] or 0) if genel else 0

            return {
                "toplam_rezervasyon": aktif_sayi,
                "aktif_rezervasyon": aktif_sayi,
                "iptal_rezervasyon": iptal_sayi,
                "tum_rezervasyon": toplam_sayi,
                "toplam_gelir": float(genel[3] or 0.0) if genel else 0.0,
                "ogrenci_gelir": float(genel[4] or 0.0) if genel else 0.0,
                "personel_gelir": float(genel[5] or 0.0) if genel else 0.0,
                "ortalama_puan": ortalama_puan,
                "toplam_yorum": toplam_yorum,
                "en_populer_yemekler": [{
                    "yemek": pr[0],
                    "kategori": pr[1],
                    "tercih": pr[2]
                } for pr in populer_rows],
                "yemekhaneler": [{
                    "id": y[0],
                    "ad": y[1],
                    "kapasite": y[2],
                    "dolu": y[3],
                    "kalan": max(0, y[2] - y[3]),
                    "doluluk_orani": f"%{round((y[3] / y[2] * 100), 1)}" if y[2] > 0 else "%0"
                } for y in yemekhaneler]
            }

