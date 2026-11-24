#!/usr/bin/env python3
"""
Yemekhane Otomasyonu · Aşama 4
Redis Eski Menü Önbelleği Temizleme Betiği
Kullanım:
    python scripts/redis_menu_temizle.py
    veya docker üzerinden:
    docker compose exec menu-servisi python /app/core/repositories/onbellek_repository.py --flush
    veya doğrudan redis-cli ile:
    docker compose exec redis redis-cli EVAL "local k=redis.call('keys','menu:*'); if #k>0 then return redis.call('del',unpack(k)) else return 0 end" 0
"""
import os
import sys

try:
    import redis
except ImportError:
    print("Hata: 'redis' modülü yüklü değil. 'pip install redis' çalıştırın.")
    sys.exit(1)

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

def menu_onbellegini_temizle():
    print(f"[*] Redis sunucusuna bağlanılıyor: {REDIS_HOST}:{REDIS_PORT}...")
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=3)
        r.ping()
    except Exception as e:
        print(f"[!] Redis bağlantı hatası: {e}")
        # Eğer localhost ile bağlanılamadıysa ve Docker ortamındaysak 'redis' host'unu dene
        if REDIS_HOST == "localhost":
            try:
                print("[*] 'redis' hostu üzerinden yeniden deneniyor...")
                r = redis.Redis(host="redis", port=REDIS_PORT, decode_responses=True, socket_connect_timeout=3)
                r.ping()
            except Exception as e2:
                print(f"[!] 'redis' hostu ile de bağlanılamadı: {e2}")
                return
        else:
            return

    # menu:* şablonundaki tüm anahtarları tara
    anahtarlar = r.keys("menu:*")
    if not anahtarlar:
        print("[+] Redis'te silinecek 'menu:*' anahtarı bulunamadı (Önbellek zaten temiz).")
        return

    print(f"[*] Bulunan menü anahtarı sayısı: {len(anahtarlar)}")
    for k in anahtarlar:
        print(f"    - Siliniyor: {k}")

    silinen = r.delete(*anahtarlar)
    print(f"[✓] Başarılı: Toplam {silinen} adet menü önbellek anahtarı temizlendi.")

if __name__ == "__main__":
    menu_onbellegini_temizle()
