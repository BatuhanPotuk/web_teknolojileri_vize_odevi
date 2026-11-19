class KimlikHatasi(Exception):
    def __init__(self, mesaj="E-posta veya şifre hatalı.", kod=401):
        super().__init__(mesaj)
        self.mesaj = mesaj
        self.kod = kod
