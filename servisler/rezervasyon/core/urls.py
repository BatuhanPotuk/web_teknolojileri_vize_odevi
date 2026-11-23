from django.urls import path
from core.views.saglik import saglik_view
from core.views.rezervasyon_views import (
    rezervasyon_yap_view,
    rezervasyon_iptal_view,
    rezervasyonlarim_view,
    bakiye_view,
    bakiye_yukle_view,
    menu_doluluk_view,
    admin_rezervasyonlar_view,
    admin_rezervasyon_iptal_view,
)

urlpatterns = [
    path('internal/saglik', saglik_view, name='saglik'),
    path('internal/doluluk/<int:menu_id>', menu_doluluk_view, name='internal_doluluk'),
    path('api/reservations', rezervasyon_yap_view, name='rezervasyon_yap'),
    path('api/reservations/admin', admin_rezervasyonlar_view, name='admin_rezervasyonlar'),
    path('api/reservations/admin/<int:id>/cancel', admin_rezervasyon_iptal_view, name='admin_rezervasyon_iptal'),
    path('api/reservations/<int:id>', rezervasyon_iptal_view, name='rezervasyon_iptal'),
    path('api/reservations/me', rezervasyonlarim_view, name='rezervasyonlarim'),
    path('api/balance', bakiye_view, name='bakiye'),
    path('api/balance/topup', bakiye_yukle_view, name='bakiye_yukle'),
]
