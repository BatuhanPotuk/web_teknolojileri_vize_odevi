import json
import redis
from django.conf import settings

class OturumRepository:
    _istemci = None

    @classmethod
    def baglanti(cls):
        if cls._istemci is None:
            cls._istemci = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
        return cls._istemci

    @classmethod
    def oturum_olustur(cls, token: str, veri: dict, ttl: int = 86400):
        r = cls.baglanti()
        r.setex(f"oturum:{token}", ttl, json.dumps(veri))

    @classmethod
    def oturum_getir(cls, token: str) -> dict:
        r = cls.baglanti()
        veri = r.get(f"oturum:{token}")
        return json.loads(veri) if veri else None

    @classmethod
    def oturum_sil(cls, token: str):
        r = cls.baglanti()
        r.delete(f"oturum:{token}")
