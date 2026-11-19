import bcrypt
import secrets
from core.exceptions import KimlikHatasi
from core.repositories.kullanici_repository import KullaniciRepository
from core.repositories.oturum_repository import OturumRepository

class AuthService:
    @staticmethod
    def giris_yap(eposta: str, sifre: str) -> dict:
        kullanici = KullaniciRepository.eposta_ile_getir(eposta)
        if not kullanici:
            raise KimlikHatasi("E-posta veya şifre hatalı.")

        # bcrypt doğrulaması
        sifre_bytes = sifre.encode('utf-8')
        hash_bytes = kullanici.sifre_hash.encode('utf-8')

        try:
            eslesme = bcrypt.checkpw(sifre_bytes, hash_bytes)
        except Exception:
            raise KimlikHatasi("E-posta veya şifre hatalı.")

        if not eslesme:
            raise KimlikHatasi("E-posta veya şifre hatalı.")

        # secrets.token_urlsafe ile güvenli jeton (token) üretimi (JWT kullanılmaz kuralı)
        token = secrets.token_urlsafe(32)

        oturum_verisi = {
            "id": kullanici.id,
            "rol": kullanici.rol,
            "ad": kullanici.ad,
            "soyad": kullanici.soyad,
            "eposta": kullanici.eposta,
            "ogrenci_no": kullanici.ogrenci_no,
            "bakiye": float(kullanici.bakiye)
        }

        # Redis'te sakla (24 saat TTL)
        OturumRepository.oturum_olustur(token, oturum_verisi, ttl=86400)

        return {
            "token": token,
            "kullanici": oturum_verisi
        }

    @staticmethod
    def cikis_yap(token: str):
        if token:
            OturumRepository.oturum_sil(token)

    @staticmethod
    def dogrula(token: str) -> dict:
        if not token:
            return None
        return OturumRepository.oturum_getir(token)
