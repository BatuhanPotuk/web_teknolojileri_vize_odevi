from django.db import connections
from core.models import Kullanici

class KullaniciRepository:
    @staticmethod
    def eposta_ile_getir(eposta: str):
        # Okuma işlemleri kural gereği salt-okunur Replica üzerinden yapılır
        return Kullanici.objects.using('replica').filter(eposta=eposta, aktif=True).first()

    @staticmethod
    def id_ile_getir(kullanici_id: int):
        return Kullanici.objects.using('replica').filter(id=kullanici_id, aktif=True).first()

    @staticmethod
    def tum_alerjenler():
        with connections['replica'].cursor() as cursor:
            cursor.execute("SELECT id, ad FROM alerjenler ORDER BY id")
            rows = cursor.fetchall()
            return [{"id": r[0], "ad": r[1]} for r in rows]

    @staticmethod
    def kullanici_alerjen_idleri(kullanici_id: int):
        with connections['default'].cursor() as cursor:
            cursor.execute(
                "SELECT alerjen_id FROM kullanici_alerjenleri WHERE kullanici_id = %s ORDER BY alerjen_id",
                [kullanici_id]
            )
            return [r[0] for r in cursor.fetchall()]

    @staticmethod
    def kullanici_alerjenleri_kaydet(kullanici_id: int, alerjen_idler: list):
        with connections['default'].cursor() as cursor:
            cursor.execute("DELETE FROM kullanici_alerjenleri WHERE kullanici_id = %s", [kullanici_id])
            for aid in alerjen_idler:
                cursor.execute(
                    "INSERT INTO kullanici_alerjenleri (kullanici_id, alerjen_id) VALUES (%s, %s)",
                    [kullanici_id, int(aid)]
                )

