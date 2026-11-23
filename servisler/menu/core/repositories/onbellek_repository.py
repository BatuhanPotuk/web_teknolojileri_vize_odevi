import json
import redis
from datetime import datetime, time
from django.conf import settings

class OnbellekRepository:
    _istemci = None

    @classmethod
    def baglanti(cls):
        if cls._istemci is None:
            try:
                cls._istemci = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
            except Exception:
                return None
        return cls._istemci

    @staticmethod
    def anahtar_olustur(yemekhane_id: int, tarih: str, ogun_id: int) -> str:
        """Kural: menu:{yemekhane_id}:{tarih}:{ogun_id}"""
        return f"menu:{yemekhane_id}:{tarih}:{ogun_id}"

    @staticmethod
    def gun_sonuna_kalan_saniye(tarih_str: str = None) -> int:
        """O günün sonuna (23:59:59) kadar kalan saniye sayısını hesaplar."""
        simdi = datetime.now()
        gece_yarisi = datetime.combine(simdi.date(), time(23, 59, 59))
        fark = int((gece_yarisi - simdi).total_seconds())
        return max(300, fark) # En az 5 dakika

    @classmethod
    def menu_getir(cls, yemekhane_id: int, tarih: str, ogun_id: int):
        """Menü verisini Redis'ten getirir."""
        try:
            r = cls.baglanti()
            if r is None:
                return None
            key = cls.anahtar_olustur(yemekhane_id, tarih, ogun_id)
            veri = r.get(key)
            return json.loads(veri) if veri else None
        except Exception:
            return None

    @classmethod
    def menu_kaydet(cls, yemekhane_id: int, tarih: str, ogun_id: int, menu_verisi: dict, ttl: int = None):
        """Menüyü o günün sonuna kadar geçerli olacak şekilde Redis'e kaydeder."""
        try:
            r = cls.baglanti()
            if r:
                key = cls.anahtar_olustur(yemekhane_id, tarih, ogun_id)
                if ttl is None:
                    ttl = cls.gun_sonuna_kalan_saniye(tarih)
                r.setex(key, ttl, json.dumps(menu_verisi))
        except Exception:
            pass

    @classmethod
    def menu_sil(cls, yemekhane_id: int, tarih: str, ogun_id: int):
        """Yönetici menüyü güncellediğinde eski önbellek kaydını siler."""
        try:
            r = cls.baglanti()
            if r:
                key = cls.anahtar_olustur(yemekhane_id, tarih, ogun_id)
                r.delete(key)
        except Exception:
            pass
