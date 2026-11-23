from django.db import connections, IntegrityError

class DegerlendirmeRepository:
    @staticmethod
    def kullanici_rezervasyonu_var_mi(kullanici_id: int, menu_id: int) -> bool:
        with connections['replica'].cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM rezervasyonlar WHERE kullanici_id = %s AND menu_id = %s LIMIT 1",
                [kullanici_id, menu_id]
            )
            return cursor.fetchone() is not None

    @staticmethod
    def degerlendirme_ekle(kullanici_id: int, menu_id: int, puan: int, yorum: str = None):
        with connections['default'].cursor() as cursor:
            sql = """
                INSERT INTO degerlendirmeler (kullanici_id, menu_id, puan, yorum, olusturma)
                VALUES (%s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE puan = VALUES(puan), yorum = VALUES(yorum), olusturma = NOW()
            """
            cursor.execute(sql, [kullanici_id, menu_id, puan, yorum])
            return True

    @staticmethod
    def menu_degerlendirmeleri(menu_id: int):
        with connections['replica'].cursor() as cursor:
            sql = """
                SELECT d.id, d.kullanici_id, CONCAT(k.ad, ' ', LEFT(k.soyad, 1), '.') AS kullanici,
                       d.puan, d.yorum, d.olusturma
                  FROM degerlendirmeler d
                  JOIN kullanicilar k ON k.id = d.kullanici_id
                 WHERE d.menu_id = %s
                 ORDER BY d.id DESC
            """
            cursor.execute(sql, [menu_id])
            return cursor.fetchall()

    @staticmethod
    def menu_ortalama(menu_id: int):
        with connections['replica'].cursor() as cursor:
            sql = """
                SELECT ROUND(AVG(puan), 1) AS ortalama, COUNT(*) AS sayi
                  FROM degerlendirmeler
                 WHERE menu_id = %s
            """
            cursor.execute(sql, [menu_id])
            row = cursor.fetchone()
            if not row or row[0] is None:
                return {"ortalama": 0.0, "sayi": 0}
            return {"ortalama": float(row[0]), "sayi": int(row[1])}

    @staticmethod
    def tum_degerlendirmeler(limit: int = 50):
        with connections['replica'].cursor() as cursor:
            sql = f"""
                SELECT d.id, d.kullanici_id, CONCAT(k.ad, ' ', k.soyad) AS kullanici,
                       k.rol, d.menu_id, m.tarih, yh.ad AS yemekhane, o.ad AS ogun,
                       d.puan, d.yorum, d.olusturma
                  FROM degerlendirmeler d
                  JOIN kullanicilar k ON k.id = d.kullanici_id
                  JOIN menuler m ON m.id = d.menu_id
                  JOIN yemekhaneler yh ON yh.id = m.yemekhane_id
                  JOIN ogunler o ON o.id = m.ogun_id
                 ORDER BY d.id DESC
                 LIMIT {limit}
            """
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def genel_ozet():
        with connections['replica'].cursor() as cursor:
            sql = """
                SELECT ROUND(AVG(puan), 1) AS ortalama,
                       COUNT(*) AS toplam,
                       SUM(CASE WHEN puan = 5 THEN 1 ELSE 0 END) AS bes_yildiz,
                       SUM(CASE WHEN puan = 4 THEN 1 ELSE 0 END) AS dort_yildiz,
                       SUM(CASE WHEN puan = 3 THEN 1 ELSE 0 END) AS uc_yildiz,
                       SUM(CASE WHEN puan = 2 THEN 1 ELSE 0 END) AS iki_yildiz,
                       SUM(CASE WHEN puan = 1 THEN 1 ELSE 0 END) AS bir_yildiz
                  FROM degerlendirmeler
            """
            cursor.execute(sql)
            row = cursor.fetchone()
            if not row or row[0] is None:
                return {"ortalama": 0.0, "toplam": 0, "dagilim": {}}
            return {
                "ortalama": float(row[0]),
                "toplam": int(row[1]),
                "dagilim": {
                    "5": int(row[2] or 0),
                    "4": int(row[3] or 0),
                    "3": int(row[4] or 0),
                    "2": int(row[5] or 0),
                    "1": int(row[6] or 0),
                }
            }
