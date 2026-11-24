import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from core.services.auth_service import AuthService
from core.exceptions import KimlikHatasi

@require_POST
def login_view(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        eposta = data.get('eposta', '').strip()
        sifre = data.get('sifre', '')
    except Exception:
        return JsonResponse({"detail": "Geçersiz istek gövdesi."}, status=400)

    if not eposta or not sifre:
        return JsonResponse({"detail": "E-posta ve şifre zorunludur."}, status=400)

    try:
        sonuc = AuthService.giris_yap(eposta, sifre)
        return JsonResponse(sonuc, status=200)
    except KimlikHatasi as e:
        return JsonResponse({"detail": e.mesaj}, status=e.kod)

@require_POST
def logout_view(request):
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '').strip() if 'Bearer ' in auth_header else ''
    AuthService.cikis_yap(token)
    return JsonResponse({"mesaj": "Başarıyla çıkış yapıldı."}, status=200)

@require_GET
def profil_view(request):
    # Gateway auth_request doğrulamasından sonra gelen X-Kullanici-Id ve X-Rol başlıklarını okur
    kullanici_id = request.headers.get('X-Kullanici-Id')
    rol = request.headers.get('X-Rol')
    if not kullanici_id:
        return JsonResponse({"detail": "Oturum geçersiz."}, status=401)
    
    alerjenler = AuthService.alerjenleri_getir(int(kullanici_id))["kullanici_alerjenleri"]
    return JsonResponse({
        "kullanici_id": int(kullanici_id),
        "rol": rol,
        "alerjenler": alerjenler
    }, status=200)

def allergens_view(request):
    kullanici_id = request.headers.get('X-Kullanici-Id') or request.META.get('HTTP_X_KULLANICI_ID')
    token = None
    auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.replace('Bearer ', '').strip()

    if (not kullanici_id or kullanici_id == "") and token:
        oturum = AuthService.dogrula(token)
        if oturum:
            kullanici_id = oturum.get('id')

    # Query param token fallback
    if (not kullanici_id or kullanici_id == ""):
        q_token = request.GET.get('token')
        if q_token:
            oturum = AuthService.dogrula(q_token)
            if oturum:
                kullanici_id = oturum.get('id')
                token = q_token

    if request.method == 'GET':
        if not kullanici_id:
            tum = AuthService.alerjenleri_getir(0)
            return JsonResponse({"tum_alerjenler": tum["tum_alerjenler"], "kullanici_alerjenleri": []}, status=200)
        veri = AuthService.alerjenleri_getir(int(kullanici_id))
        return JsonResponse(veri, status=200)

    elif request.method in ('POST', 'PUT'):
        if not kullanici_id:
            return JsonResponse({"detail": "Oturum açılmalıdır."}, status=401)
        try:
            body = json.loads(request.body.decode('utf-8'))
            alerjen_idler = body.get('alerjen_idler', [])
            if not isinstance(alerjen_idler, list):
                return JsonResponse({"detail": "Alerjen listesi geçersiz."}, status=400)
        except Exception:
            return JsonResponse({"detail": "Geçersiz istek gövdesi."}, status=400)

        kaydedilenler = AuthService.alerjenleri_kaydet(int(kullanici_id), alerjen_idler, token=token)
        return JsonResponse({
            "mesaj": "Alerjen tercihleriniz başarıyla kaydedildi.",
            "kullanici_alerjenleri": kaydedilenler
        }, status=200)

    return JsonResponse({"detail": "İzin verilmeyen yöntem."}, status=405)

