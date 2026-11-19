from core.models import Kullanici

class KullaniciRepository:
    @staticmethod
    def eposta_ile_getir(eposta: str):
        # Okuma işlemleri kural gereği salt-okunur Replica üzerinden yapılır
        return Kullanici.objects.using('replica').filter(eposta=eposta, aktif=True).first()

    @staticmethod
    def id_ile_getir(kullanici_id: int):
        return Kullanici.objects.using('replica').filter(id=kullanici_id, aktif=True).first()
