from django.urls import path
from core.views.saglik import saglik_view
from core.views.menu_views import (
    gunun_menusu_view,
    haftalik_menu_view,
    yemekhaneler_view,
    ogunler_view,
    yonetici_istatistik_view,
)

urlpatterns = [
    path('internal/saglik', saglik_view, name='saglik'),
    path('api/menus/today', gunun_menusu_view, name='gunun_menusu'),
    path('api/menus/week', haftalik_menu_view, name='haftalik_menu'),
    path('api/menus/cafeterias', yemekhaneler_view, name='yemekhaneler_menu'),
    path('api/menus/meals', ogunler_view, name='ogunler_menu'),
    path('api/cafeterias', yemekhaneler_view, name='yemekhaneler'),
    path('api/meals', ogunler_view, name='ogunler'),
    path('api/admin/stats', yonetici_istatistik_view, name='admin_stats'),
]

