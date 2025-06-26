# Source Generated with Decompyle++
# File: urls.cpython-312.pyc (Python 3.12)

'''
URL маршруты для API калькулятора пробега.
'''
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_simple import DepotViewSet, TrainViewSet, TrainDailyRecordViewSet, health_check
app_name = 'mileage_calculator'
router = DefaultRouter()
router.register('depots', DepotViewSet, basename = 'depot')
router.register('trains', TrainViewSet, basename = 'train')
router.register('records', TrainDailyRecordViewSet, basename = 'record')
urlpatterns = [
    path('api/v1/health/', health_check, name = 'health-check'),
    path('api/v1/', include(router.urls))]
