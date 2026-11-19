from django.db import models

class Yemekhane(models.Model):
    id = models.SmallAutoField(primary_key=True)
    ad = models.CharField(max_length=60)
    konum = models.CharField(max_length=120, null=True, blank=True)
    kapasite = models.PositiveSmallIntegerField()
    class Meta:
        managed = False
        db_table = 'yemekhaneler'

class Ogun(models.Model):
    id = models.SmallAutoField(primary_key=True)
    ad = models.CharField(max_length=20)
    sira = models.PositiveSmallIntegerField()
    son_saat = models.TimeField()
    servis_baslangic = models.TimeField()
    servis_bitis = models.TimeField()
    class Meta:
        managed = False
        db_table = 'ogunler'

class YemekKategori(models.Model):
    id = models.SmallAutoField(primary_key=True)
    ad = models.CharField(max_length=40)
    sira = models.PositiveSmallIntegerField()
    class Meta:
        managed = False
        db_table = 'yemek_kategorileri'

class Yemek(models.Model):
    id = models.SmallAutoField(primary_key=True)
    kategori = models.ForeignKey(YemekKategori, on_delete=models.DO_NOTHING, db_column='kategori_id')
    ad = models.CharField(max_length=80)
    kalori = models.PositiveSmallIntegerField()
    vejetaryen = models.BooleanField(default=False)
    class Meta:
        managed = False
        db_table = 'yemekler'

class Alerjen(models.Model):
    id = models.SmallAutoField(primary_key=True)
    ad = models.CharField(max_length=40)
    class Meta:
        managed = False
        db_table = 'alerjenler'

class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    yemekhane = models.ForeignKey(Yemekhane, on_delete=models.DO_NOTHING, db_column='yemekhane_id')
    tarih = models.DateField()
    ogun = models.ForeignKey(Ogun, on_delete=models.DO_NOTHING, db_column='ogun_id')
    ogrenci_fiyati = models.DecimalField(max_digits=8, decimal_places=2)
    personel_fiyati = models.DecimalField(max_digits=8, decimal_places=2)
    class Meta:
        managed = False
        db_table = 'menuler'
