import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.conf import settings
from core.exceptions import IsKuraliHatasi
from core.services.rezervasyon_service import RezervasyonService

def rezervasyon_yap_view(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    kullanici_id = request.headers.get('X-Kullanici-Id')
    if not kullanici_id:
        return JsonResponse({"detail": "Oturum açılmalıdır."}, status=401)

    try:
        body = json.loads(request.body.decode('utf-8'))
        menu_id = int(body.get('menu_id'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"hata": "Geçersiz menü ID."}, status=400)

    try:
        sonuc = RezervasyonService.rezervasyon_yap(int(kullanici_id), menu_id)
        return JsonResponse(sonuc, status=201)
    except IsKuraliHatasi as err:
        return JsonResponse({"hata": err.mesaj}, status=err.durum_kodu)

def rezervasyon_iptal_view(request, id):
    if request.method != 'DELETE':
        return HttpResponseNotAllowed(['DELETE'])

    kullanici_id = request.headers.get('X-Kullanici-Id')
    if not kullanici_id:
        return JsonResponse({"detail": "Oturum açılmalıdır."}, status=401)

    try:
        sonuc = RezervasyonService.rezervasyon_iptal(int(kullanici_id), id)
        return JsonResponse(sonuc, status=200)
    except IsKuraliHatasi as err:
        return JsonResponse({"hata": err.mesaj}, status=err.durum_kodu)

def rezervasyonlarim_view(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    kullanici_id = request.headers.get('X-Kullanici-Id')
    if not kullanici_id:
        return JsonResponse({"detail": "Oturum açılmalıdır."}, status=401)

    liste = RezervasyonService.rezervasyonlarim(int(kullanici_id))
    return JsonResponse(liste, safe=False)

def bakiye_view(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    kullanici_id = request.headers.get('X-Kullanici-Id')
    if not kullanici_id:
        return JsonResponse({"detail": "Oturum açılmalıdır."}, status=401)

    bakiye = RezervasyonService.bakiye_getir(int(kullanici_id))
    hareketler = RezervasyonService.hareketler(int(kullanici_id))
    return JsonResponse({
        "bakiye": bakiye,
        "hareketler": hareketler
    })

def bakiye_yukle_view(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    kullanici_id = request.headers.get('X-Kullanici-Id')
    if not kullanici_id:
        return JsonResponse({"detail": "Oturum açılmalıdır."}, status=401)

    try:
        body = json.loads(request.body.decode('utf-8'))
        tutar = float(body.get('tutar', 0))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({"hata": "Geçersiz tutar."}, status=400)

    try:
        sonuc = RezervasyonService.bakiye_yukle(int(kullanici_id), tutar)
        return JsonResponse(sonuc, status=200)
    except IsKuraliHatasi as err:
        return JsonResponse({"hata": err.mesaj}, status=err.durum_kodu)

def menu_doluluk_view(request, menu_id):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    ic_anahtar = request.headers.get('X-Ic-Anahtar', '')
    if ic_anahtar != settings.INTERNAL_TOKEN:
        return JsonResponse({"detail": "Yetkisiz iç çağrı."}, status=403)

    doluluk = RezervasyonService.doluluk_bilgisi(menu_id)
    if not doluluk:
        return JsonResponse({"hata": "Menü bulunamadı."}, status=404)
    return JsonResponse(doluluk)
