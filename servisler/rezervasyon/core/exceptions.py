class IsKuraliHatasi(Exception):
    def __init__(self, mesaj: str, durum_kodu: int = 400):
        super().__init__(mesaj)
        self.mesaj = mesaj
        self.durum_kodu = durum_kodu

    @classmethod
    def mysql_hatasindan(cls, err: Exception):
        mesaj = str(err)
        # MySQL OperationalError (1644, 'Bakiye yetersiz.')
        if hasattr(err, 'args') and len(err.args) > 1:
            mesaj = str(err.args[1])
        elif hasattr(err, 'args') and len(err.args) == 1:
            mesaj = str(err.args[0])

        # Temizle
        mesaj = mesaj.strip()

        if "Kahvalt" in mesaj and "porsiyon" in mesaj:
            return cls(mesaj="Kahvaltı öğününde yarım porsiyon seçilemez.", durum_kodu=409)

        # Durum kodu eşleştirme
        if "Bakiye yetersiz" in mesaj:
            kod = 402
        elif any(k in mesaj for k in [
            "kapasitesi dolu",
            "rezervasyon süresi doldu",
            "zaten rezervasyonunuz var",
            "iptal süresi doldu",
            "Yalnızca aktif rezervasyonlar",
            "Kahvalt",
            "kahvalt",
            "porsiyon"
        ]):
            kod = 409
        elif any(k in mesaj for k in ["bulunamadı", "Bulunamadı"]):
            kod = 404
        elif "pasif durumda" in mesaj:
            kod = 403
        elif "Yükleme tutarı" in mesaj:
            kod = 400
        else:
            kod = 400

        return cls(mesaj=mesaj, durum_kodu=kod)
