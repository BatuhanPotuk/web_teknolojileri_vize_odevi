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
    return JsonResponse({"kullanici_id": int(kullanici_id), "rol": rol}, status=200)
