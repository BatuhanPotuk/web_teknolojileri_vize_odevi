import json
from django.http import JsonResponse
from core.services.menu_service import MenuService

def gunun_menusu_view(request):
    try:
        yemekhane_id = int(request.GET.get('yemekhane_id', 1))
        ogun_id = int(request.GET.get('ogun_id', 2))
    except (ValueError, TypeError):
        return JsonResponse({"hata": "Geçersiz parametre formatı."}, status=400)

    tarih_str = request.GET.get('tarih') # Opsiyonel: YYYY-MM-DD
    menu = MenuService.gunun_menusu_getir(yemekhane_id, ogun_id, tarih_str)
    if not menu:
        return JsonResponse({"hata": "Belirtilen kriterlerde menü bulunamadı."}, status=404)

    return JsonResponse(menu)

def haftalik_menu_view(request):
    try:
        yemekhane_id = int(request.GET.get('yemekhane_id', 1))
    except (ValueError, TypeError):
        return JsonResponse({"hata": "Geçersiz yemekhane_id parametresi."}, status=400)

    rol = request.headers.get('X-Rol', 'ogrenci')
    baslangic_str = request.GET.get('baslangic') # Opsiyonel

    menuler = MenuService.haftalik_menuleri_getir(yemekhane_id, rol=rol, baslangic_str=baslangic_str)
    return JsonResponse(menuler, safe=False)

def yemekhaneler_view(request):
    yemekhaneler = MenuService.yemekhaneler_getir()
    return JsonResponse(yemekhaneler, safe=False)

def ogunler_view(request):
    ogunler = MenuService.ogunler_getir()
    return JsonResponse(ogunler, safe=False)

def yonetici_istatistik_view(request):
    istatistik = MenuService.yonetici_istatistik_getir('yonetici')
    return JsonResponse(istatistik)

def menu_guncelle_view(request, id):
    if request.method == 'GET':
        detay = MenuService.menu_detay(id)
        if not detay:
            return JsonResponse({"hata": "Menü bulunamadı."}, status=404)
        return JsonResponse(detay)

    rol = request.headers.get('X-Rol', '')
    if rol != 'yonetici':
        return JsonResponse({"detail": "Bu işlem için yönetici yetkisi gereklidir."}, status=403)

    if request.method == 'DELETE':
        sonuc = MenuService.menu_sil(id)
        if not sonuc:
            return JsonResponse({"hata": "Menü bulunamadı."}, status=404)
        return JsonResponse(sonuc)

    if request.method not in ['POST', 'PUT']:
        return JsonResponse({"hata": "Yalnızca GET, POST, PUT veya DELETE kabul edilir."}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
        ogrenci_fiyati = float(body.get('ogrenci_fiyati')) if 'ogrenci_fiyati' in body else None
        personel_fiyati = float(body.get('personel_fiyati')) if 'personel_fiyati' in body else None
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"hata": "Geçersiz veri formatı."}, status=400)

    sonuc = MenuService.menu_guncelle(id, ogrenci_fiyati, personel_fiyati)
    if not sonuc:
        return JsonResponse({"hata": "Menü bulunamadı."}, status=404)
    return JsonResponse(sonuc)

def admin_menus_view(request):
    if request.method == 'GET':
        tarih = request.GET.get('tarih')
        menuler = MenuService.menuleri_listele(tarih=tarih)
        return JsonResponse(menuler, safe=False)

    elif request.method == 'POST':
        rol = request.headers.get('X-Rol', '')
        if rol != 'yonetici':
            return JsonResponse({"detail": "Bu işlem için yönetici yetkisi gereklidir."}, status=403)

        try:
            body = json.loads(request.body.decode('utf-8'))
            yemekhane_id = int(body.get('yemekhane_id'))
            tarih = str(body.get('tarih')).strip()
            ogun_id = int(body.get('ogun_id'))
            ogrenci_fiyati = float(body.get('ogrenci_fiyati'))
            personel_fiyati = float(body.get('personel_fiyati'))
            yemek_idler = body.get('yemekler', [])
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({"hata": "Eksik veya geçersiz parametreler."}, status=400)

        try:
            sonuc = MenuService.yeni_menu_olustur(yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati, yemek_idler)
            return JsonResponse(sonuc, status=201)
        except Exception as err:
            return JsonResponse({"hata": f"Menü oluşturulamadı: {str(err)}"}, status=400)

    return JsonResponse({"hata": "Yalnızca GET veya POST kabul edilir."}, status=405)

def admin_menu_items_view(request, id):
    rol = request.headers.get('X-Rol', '')
    if rol != 'yonetici':
        return JsonResponse({"detail": "Bu işlem için yönetici yetkisi gereklidir."}, status=403)

    if request.method != 'POST':
        return JsonResponse({"hata": "Yalnızca POST kabul edilir."}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
        yemek_id = int(body.get('yemek_id'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"hata": "Geçersiz yemek_id."}, status=400)

    sonuc = MenuService.menu_yemek_ekle(id, yemek_id)
    if not sonuc:
        return JsonResponse({"hata": "Menü bulunamadı."}, status=404)
    return JsonResponse(sonuc)

def admin_menu_item_delete_view(request, id, yemek_id):
    rol = request.headers.get('X-Rol', '')
    if rol != 'yonetici':
        return JsonResponse({"detail": "Bu işlem için yönetici yetkisi gereklidir."}, status=403)

    if request.method != 'DELETE':
        return JsonResponse({"hata": "Yalnızca DELETE kabul edilir."}, status=405)

    sonuc = MenuService.menu_yemek_sil(id, yemek_id)
    if not sonuc:
        return JsonResponse({"hata": "Menü bulunamadı."}, status=404)
    return JsonResponse(sonuc)

def admin_foods_view(request):
    yemekler = MenuService.tum_yemekleri_getir()
    return JsonResponse(yemekler, safe=False)

def admin_cache_flush_view(request):
    silinen = MenuService.tum_onbellegi_temizle()
    return JsonResponse({
        "mesaj": f"Tüm menü önbelleği temizlendi ({silinen} kayıt silindi).",
        "silinen": silinen
    })




