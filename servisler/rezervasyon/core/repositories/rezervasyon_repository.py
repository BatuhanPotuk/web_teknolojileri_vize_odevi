from django.db import connections, DatabaseError
from core.exceptions import IsKuraliHatasi

class RezervasyonRepository:
    @staticmethod
    def sp_rezervasyon_yap(kullanici_id: int, menu_id: int):
        with connections['default'].cursor() as cursor:
            try:
                cursor.execute("CALL sp_rezervasyon_yap(%s, %s)", [kullanici_id, menu_id])
                row = cursor.fetchone()
                return {
                    "rezervasyon_id": row[0],
                    "ucret": float(row[1]),
                    "yeni_bakiye": float(row[2])
                }
            except DatabaseError as err:
                raise IsKuraliHatasi.mysql_hatasindan(err)

    @staticmethod
    def sp_rezervasyon_iptal(kullanici_id: int, rezervasyon_id: int):
        with connections['default'].cursor() as cursor:
            try:
                cursor.execute("CALL sp_rezervasyon_iptal(%s, %s)", [kullanici_id, rezervasyon_id])
                row = cursor.fetchone()
                return {
                    "rezervasyon_id": row[0],
                    "iade": float(row[1]),
                    "yeni_bakiye": float(row[2])
                }
            except DatabaseError as err:
                raise IsKuraliHatasi.mysql_hatasindan(err)

    @staticmethod
    def sp_bakiye_yukle(kullanici_id: int, tutar: float):
        with connections['default'].cursor() as cursor:
            try:
                cursor.execute("CALL sp_bakiye_yukle(%s, %s)", [kullanici_id, tutar])
                row = cursor.fetchone()
                return {
                    "hareket_id": row[0],
                    "yeni_bakiye": float(row[1])
                }
            except DatabaseError as err:
                raise IsKuraliHatasi.mysql_hatasindan(err)

    @staticmethod
    def bakiye_getir(kullanici_id: int):
        # Kaynaktan (Primary default) anlık taze bakiye okunur
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT bakiye FROM kullanicilar WHERE id = %s", [kullanici_id])
            row = cursor.fetchone()
            return float(row[0]) if row else 0.0

    @staticmethod
    def kullanici_rezervasyonlari(kullanici_id: int):
        with connections['default'].cursor() as cursor:
            sql = """
                SELECT r.id, r.menu_id, r.durum, r.ucret, r.olusturma, r.iptal_zamani,
                       m.tarih, yh.ad AS yemekhane, o.ad AS ogun,
                       TIMESTAMP(m.tarih, o.son_saat) AS son_iptal_saati
                  FROM rezervasyonlar r
                  JOIN menuler m ON m.id = r.menu_id
                  JOIN yemekhaneler yh ON yh.id = m.yemekhane_id
                  JOIN ogunler o ON o.id = m.ogun_id
                 WHERE r.kullanici_id = %s
                 ORDER BY r.id DESC
            """
            cursor.execute(sql, [kullanici_id])
            return cursor.fetchall()

    @staticmethod
    def kullanici_bakiye_hareketleri(kullanici_id: int):
        with connections['default'].cursor() as cursor:
            sql = """
                SELECT id, tutar, tur, olusturma, rezervasyon_id, aciklama
                  FROM bakiye_hareketleri
                 WHERE kullanici_id = %s
                 ORDER BY id DESC
                 LIMIT 50
            """
            cursor.execute(sql, [kullanici_id])
            return cursor.fetchall()

    @staticmethod
    def menu_doluluk(menu_id: int):
        with connections['replica'].cursor() as cursor:
            sql = """
                SELECT yh.kapasite,
                       (SELECT COUNT(*) FROM rezervasyonlar r WHERE r.menu_id = m.id AND r.durum = 'aktif') AS aktif_rezervasyon
                  FROM menuler m
                  JOIN yemekhaneler yh ON yh.id = m.yemekhane_id
                 WHERE m.id = %s
            """
            cursor.execute(sql, [menu_id])
            row = cursor.fetchone()
            if not row:
                return None
            kapasite = row[0]
            dolu = row[1]
            return {
                "kapasite": kapasite,
                "dolu": dolu,
                "kalan": max(0, kapasite - dolu)
            }
