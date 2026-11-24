from django.urls import path
from core.views.saglik import saglik_view
from core.views.menu_views import (
    gunun_menusu_view,
    haftalik_menu_view,
    yemekhaneler_view,
    ogunler_view,
    yonetici_istatistik_view,
    menu_guncelle_view,
    admin_menus_view,
    admin_menu_items_view,
    admin_menu_item_delete_view,
    admin_foods_view,
    admin_cache_flush_view,
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
    path('api/admin/menus', admin_menus_view, name='admin_menus'),
    path('api/admin/menus/<int:id>', menu_guncelle_view, name='admin_menu_guncelle'),
    path('api/admin/menus/<int:id>/items', admin_menu_items_view, name='admin_menu_items'),
    path('api/admin/menus/<int:id>/items/<int:yemek_id>', admin_menu_item_delete_view, name='admin_menu_item_delete'),
    path('api/admin/foods', admin_foods_view, name='admin_foods'),
    path('api/admin/cache/flush', admin_cache_flush_view, name='admin_cache_flush'),
]


