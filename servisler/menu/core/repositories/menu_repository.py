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
    def yonetici_istatistik():
        with connections['replica'].cursor() as cursor:
            # Bugünün rezervasyon sayısı ve geliri
            sql_genel = """
                SELECT COUNT(r.id) AS toplam_rezervasyon,
                       COALESCE(SUM(r.ucret), 0) AS toplam_gelir
                  FROM rezervasyonlar r
                  JOIN menuler m ON m.id = r.menu_id
                 WHERE m.tarih = CURDATE() AND r.durum = 'aktif'
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

            return {
                "toplam_rezervasyon": genel[0] if genel else 0,
                "toplam_gelir": float(genel[1]) if genel else 0.0,
                "yemekhaneler": [{
                    "id": y[0],
                    "ad": y[1],
                    "kapasite": y[2],
                    "dolu": y[3],
                    "doluluk_orani": f"%{round((y[3] / y[2] * 100), 1)}" if y[2] > 0 else "%0"
                } for y in yemekhaneler]
            }

