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
    rol = request.headers.get('X-Rol', '')
    if rol != 'yonetici':
        return JsonResponse({"detail": "Bu işlem için yönetici yetkisi gereklidir."}, status=403)

    istatistik = MenuService.yonetici_istatistik_getir(rol)
    return JsonResponse(istatistik)

