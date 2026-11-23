import json
from django.http import JsonResponse, HttpResponseNotAllowed
from core.services.degerlendirme_service import DegerlendirmeService

def degerlendirme_view(request):
    if request.method == 'GET':
        menu_id = request.GET.get('menu_id')
        admin_istek = (request.GET.get('admin') == '1') or (not menu_id) or (menu_id == '0')
        
        if admin_istek:
            sonuc = DegerlendirmeService.admin_degerlendirmeler_getir()
            return JsonResponse(sonuc)

        try:
            m_id = int(menu_id)
        except (ValueError, TypeError):
            return JsonResponse({"hata": "Geçersiz menu_id parametresi."}, status=400)

        sonuc = DegerlendirmeService.degerlendirmeler_getir(m_id)
        return JsonResponse(sonuc)


    elif request.method == 'POST':
        kullanici_id = request.headers.get('X-Kullanici-Id')
        if not kullanici_id:
            return JsonResponse({"detail": "Oturum açılmalıdır."}, status=401)

        try:
            body = json.loads(request.body.decode('utf-8'))
            menu_id = int(body.get('menu_id'))
            puan = int(body.get('puan'))
            yorum = body.get('yorum', '').strip() or None
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({"hata": "Geçersiz veri formatı."}, status=400)

        try:
            sonuc = DegerlendirmeService.degerlendir(int(kullanici_id), menu_id, puan, yorum)
            return JsonResponse(sonuc, status=201)
        except ValueError as err:
            return JsonResponse({"hata": str(err)}, status=400)

    return HttpResponseNotAllowed(['GET', 'POST'])
