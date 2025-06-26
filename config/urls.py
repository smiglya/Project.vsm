# Source Generated with Decompyle++
# File: urls.cpython-312.pyc (Python 3.12)

'''
URL configuration для VSM проекта.
Калькулятор пробега и планирования ТО электропоездов.
'''
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.mileage_calculator.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name = 'schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name = 'schema'), name = 'swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name = 'schema'), name = 'redoc'),
    path('api-auth/', include('rest_framework.urls'))]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
