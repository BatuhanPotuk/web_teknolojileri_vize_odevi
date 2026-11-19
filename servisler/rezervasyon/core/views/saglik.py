from django.http import JsonResponse

def saglik_view(request):
    return JsonResponse({"durum": "ok", "servis": "rezervasyon"})
