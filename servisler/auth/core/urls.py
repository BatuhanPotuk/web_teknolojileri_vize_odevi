from django.urls import path
from .views.saglik import saglik_kontrolu
from .views.auth_views import login_view, logout_view, profil_view, allergens_view
from .views.dogrula_view import dogrula_view, istege_bagli_dogrula_view

urlpatterns = [
    path('internal/saglik', saglik_kontrolu, name='saglik_kontrolu'),
    path('internal/dogrula', dogrula_view, name='dogrula'),
    path('internal/dogrula-istege-bagli', istege_bagli_dogrula_view, name='dogrula_istege_bagli'),
    path('api/auth/login', login_view, name='login'),
    path('api/auth/logout', logout_view, name='logout'),
    path('api/auth/me', profil_view, name='profil'),
    path('api/auth/allergens', allergens_view, name='auth_allergens'),
    path('api/allergens', allergens_view, name='allergens'),
]
