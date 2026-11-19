from django.db import models

class Kullanici(models.Model):
    id = models.AutoField(primary_key=True)
    ad = models.CharField(max_length=50)
    soyad = models.CharField(max_length=50)
    eposta = models.EmailField(max_length=120, unique=True)
    sifre_hash = models.CharField(max_length=60)
    rol = models.CharField(max_length=10) # 'ogrenci', 'personel', 'yonetici'
    ogrenci_no = models.CharField(max_length=12, null=True, blank=True)
    bakiye = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    aktif = models.BooleanField(default=True)
    olusturma = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'kullanicilar'

    def __str__(self):
        return f"{self.ad} {self.soyad} ({self.eposta})"
