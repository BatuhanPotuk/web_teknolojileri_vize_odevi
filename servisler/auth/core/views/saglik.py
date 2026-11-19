from django.http import JsonResponse

def saglik_kontrolu(request):
    return JsonResponse({"durum": "ok"})
