from django.http import JsonResponse, HttpResponse
from django.conf import settings
from core.services.auth_service import AuthService

def dogrula_view(request):
    # 1. Dahili token kontrolü (X-Ic-Anahtar)
    ic_anahtar = request.headers.get('X-Ic-Anahtar', '')
    if ic_anahtar != settings.INTERNAL_TOKEN:
        return JsonResponse({"detail": "Yetkisiz iç çağrı."}, status=403)

    # 2. Authorization Bearer token kontrolü
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return JsonResponse({"detail": "Jeton eksik."}, status=401)

    token = auth_header.replace('Bearer ', '').strip()
    oturum = AuthService.dogrula(token)
    if not oturum:
        return JsonResponse({"detail": "Oturum geçersiz veya süresi dolmuş."}, status=401)

    # Gateway'in okuyacağı başlıkları yanıta ekle (auth_request_set)
    response = HttpResponse(status=200)
    response['X-Kullanici-Id'] = str(oturum['id'])
    response['X-Rol'] = str(oturum['rol'])
    return response

def istege_bagli_dogrula_view(request):
    ic_anahtar = request.headers.get('X-Ic-Anahtar', '')
    if ic_anahtar != settings.INTERNAL_TOKEN:
        return JsonResponse({"detail": "Yetkisiz iç çağrı."}, status=403)

    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.replace('Bearer ', '').strip()
        oturum = AuthService.dogrula(token)
        if oturum:
            response = HttpResponse(status=200)
            response['X-Kullanici-Id'] = str(oturum['id'])
            response['X-Rol'] = str(oturum['rol'])
            return response

    response = HttpResponse(status=200)
    response['X-Kullanici-Id'] = ""
    response['X-Rol'] = "ogrenci"
    return response

