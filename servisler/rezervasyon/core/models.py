from django.db import models

class Rezervasyon(models.Model):
    id = models.AutoField(primary_key=True)
    kullanici_id = models.PositiveIntegerField()
    menu_id = models.PositiveIntegerField()
    olusturma = models.DateTimeField(auto_now_add=True)
    durum = models.CharField(max_length=20, default='aktif')
    iptal_zamani = models.DateTimeField(null=True, blank=True)
    ucret = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'rezervasyonlar'

class BakiyeHareketi(models.Model):
    id = models.AutoField(primary_key=True)
    kullanici_id = models.PositiveIntegerField()
    tutar = models.DecimalField(max_digits=8, decimal_places=2)
    tur = models.CharField(max_length=20)
    olusturma = models.DateTimeField(auto_now_add=True)
    rezervasyon_id = models.PositiveIntegerField(null=True, blank=True)
    aciklama = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'bakiye_hareketleri'
