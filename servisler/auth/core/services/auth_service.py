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

        alerjenler = KullaniciRepository.kullanici_alerjen_idleri(kullanici.id)

        oturum_verisi = {
            "id": kullanici.id,
            "rol": kullanici.rol,
            "ad": kullanici.ad,
            "soyad": kullanici.soyad,
            "eposta": kullanici.eposta,
            "ogrenci_no": kullanici.ogrenci_no,
            "bakiye": float(kullanici.bakiye),
            "alerjenler": alerjenler
        }

        # Redis'te sakla (30 dakika = 1800 sn TTL)
        OturumRepository.oturum_olustur(token, oturum_verisi, ttl=1800)
        print(f"[AUTH REDIS] Yeni oturum oluşturuldu (TTL: 1800s): oturum:{token}", flush=True)

        return {
            "token": token,
            "kullanici": oturum_verisi
        }

    @staticmethod
    def cikis_yap(token: str):
        if token:
            OturumRepository.oturum_sil(token)
            print(f"[AUTH REDIS] Çıkış yapıldı, oturum silindi: oturum:{token}", flush=True)

    @staticmethod
    def dogrula(token: str) -> dict:
        if not token:
            return None
        oturum = OturumRepository.oturum_getir(token)
        if oturum:
            # Her istekte süreyi 30 dakika yenile (sliding expiration)
            OturumRepository.oturum_sure_uzat(token, ttl=1800)
            print(f"[AUTH REDIS] Oturum doğrulandı ve 1800s yenilendi: oturum:{token[:10]}...", flush=True)
        return oturum

    @staticmethod
    def alerjenleri_getir(kullanici_id: int) -> dict:
        tum = KullaniciRepository.tum_alerjenler()
        secili = KullaniciRepository.kullanici_alerjen_idleri(kullanici_id)
        return {
            "tum_alerjenler": tum,
            "kullanici_alerjenleri": secili
        }

    @staticmethod
    def alerjenleri_kaydet(kullanici_id: int, alerjen_idler: list, token: str = None) -> list:
        KullaniciRepository.kullanici_alerjenleri_kaydet(kullanici_id, alerjen_idler)
        # Eğer aktif oturum token'ı varsa Redis önbelleğindeki oturumu da güncelle
        if token:
            oturum = OturumRepository.oturum_getir(token)
            if oturum:
                oturum["alerjenler"] = alerjen_idler
                OturumRepository.oturum_olustur(token, oturum, ttl=1800)
        return alerjen_idler


