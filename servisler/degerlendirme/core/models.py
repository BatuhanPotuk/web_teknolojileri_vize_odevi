from django.db import models

class Degerlendirme(models.Model):
    id = models.AutoField(primary_key=True)
    kullanici_id = models.PositiveIntegerField()
    menu_id = models.PositiveIntegerField()
    puan = models.PositiveSmallIntegerField()
    yorum = models.CharField(max_length=500, null=True, blank=True)
    olusturma = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'degerlendirmeler'
        unique_together = (('kullanici_id', 'menu_id'),)
