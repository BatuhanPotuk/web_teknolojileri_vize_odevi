import json
import redis
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

    @classmethod
    def menu_icerik_getir(cls, menu_id: int):
        try:
            r = cls.baglanti()
            if r is None:
                return None
            veri = r.get(f"menu:icerik:{menu_id}")
            return json.loads(veri) if veri else None
        except Exception:
            return None

    @classmethod
    def menu_icerik_kaydet(cls, menu_id: int, yemekler: list, ttl: int = 3600):
        try:
            r = cls.baglanti()
            if r:
                r.setex(f"menu:icerik:{menu_id}", ttl, json.dumps(yemekler))
        except Exception:
            pass

    @classmethod
    def menu_onbellek_temizle(cls, menu_id: int):
        try:
            r = cls.baglanti()
            if r:
                r.delete(f"menu:icerik:{menu_id}")
        except Exception:
            pass
