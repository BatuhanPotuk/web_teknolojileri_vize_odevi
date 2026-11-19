from django.urls import path
from core.views.saglik import saglik_view
from core.views.degerlendirme_views import degerlendirme_view

urlpatterns = [
    path('internal/saglik', saglik_view, name='saglik'),
    path('api/reviews', degerlendirme_view, name='degerlendirmeler'),
]
