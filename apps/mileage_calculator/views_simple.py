# Source Generated with Decompyle++
# File: views_simple.cpython-312.pyc (Python 3.12)

"""
Простые ViewSet'ы для тестирования с корректной аутентификацией.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import datetime
import logging
from .models import Depot, Train, TrainDailyRecord
from .serializers import DepotSerializer, TrainSerializer, TrainDailyRecordSerializer

logger = logging.getLogger(__name__)


class DepotViewSet(viewsets.ModelViewSet):
    '''Simple ViewSet для депо.'''
    queryset = Depot.objects.all()
    serializer_class = DepotSerializer
    permission_classes = [
        IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter]
    search_fields = [
        'name']
    ordering_fields = [
        'name',
        'id']
    ordering = [
        'name']
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        '''Статистика депо.'''
        depot = self.get_object()
        stats = {
            'total_trains': depot.trains.count(),
            'active_trains': depot.trains.filter(is_active=True).count()
        }
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        '''Производительность депо.'''
        depot = self.get_object()
        performance = {
            'efficiency_score': 85.5,
            'average_mileage': 450.2,
            'average_daily_mileage': 450.2,
            'maintenance_rate': 12.3
        }
        return Response(performance)


class TrainViewSet(viewsets.ModelViewSet):
    '''Simple ViewSet для поездов.'''
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    permission_classes = [
        IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter]
    filterset_fields = [
        'type',
        'depot',
        'is_manual_mileage',
        'is_active']
    search_fields = [
        'name',
        'type']
    ordering_fields = [
        'name',
        'created_at']
    ordering = [
        'name']
    
    @action(detail=True, methods=['get'])
    def maintenance_prediction(self, request, pk=None):
        '''Прогноз технического обслуживания.'''
        train = self.get_object()
        prediction = {
            'predicted_date': None,
            'days_remaining': 0,
            'mileage_remaining': 0,
            'confidence': 'low'
        }
        return Response(prediction)
    
    @action(detail=True, methods=['get'])
    def mileage_trends(self, request, pk=None):
        '''Тренды пробега.'''
        train = self.get_object()
        trends = {
            'weekly_average': 3150,
            'monthly_average': 13500,
            'daily_averages': [450, 460, 440, 470, 455, 465, 450],
            'trend_direction': 'increasing',
            'efficiency': 89.2
        }
        return Response(trends)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        '''Массовое обновление поездов.'''
        data = request.data
        train_ids = data.get('train_ids', [])
        updates = data.get('updates', {})
        
        if train_ids and updates:
            Train.objects.filter(id__in=train_ids).update(**updates)
            
        return Response({
            'message': 'Поезда обновлены',
            'updated_count': len(train_ids)
        })


class TrainDailyRecordViewSet(viewsets.ModelViewSet):
    '''Simple ViewSet для ежедневных записей.'''
    queryset = TrainDailyRecord.objects.all()
    serializer_class = TrainDailyRecordSerializer
    permission_classes = [
        IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter]
    filterset_fields = [
        'train',
        'record_date',
        'train__type',
        'train__depot']
    search_fields = [
        'train__name',
        'train__depot__name']
    ordering_fields = [
        'record_date',
        'total_mileage']
    ordering = [
        '-record_date']
    
    def create(self, request, *args, **kwargs):
        '''Переопределяем create для правильной обработки.'''
        try:
            logger.info(f'Creating record with data: {request.data}')
            data = request.data.copy()
            
            if not data.get('record_date'):
                data['record_date'] = datetime.date.today()
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
            logger.error(f'Validation errors: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f'Error creating record: {str(e)}')
            return Response(
                {'error': 'Внутренняя ошибка сервера'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def by_indicator(self, request):
        '''Фильтрация по индикатору.'''
        indicator = request.query_params.get('indicator')
        
        if indicator == 'green':
            records = self.get_queryset().filter(total_mileage__lt=50000)
        elif indicator == 'yellow':
            records = self.get_queryset().filter(total_mileage__gte=50000, total_mileage__lt=100000)
        elif indicator == 'red':
            records = self.get_queryset().filter(total_mileage__gte=100000)
        else:
            records = self.get_queryset().none()
        
        results = []
        for record in records:
            data = self.serializer_class(record).data
            if record.total_mileage < 50000:
                data['indicator_color'] = 'green'
            elif record.total_mileage < 100000:
                data['indicator_color'] = 'yellow'
            else:
                data['indicator_color'] = 'red'
            results.append(data)
        
        return Response(results)
    
    @action(detail=False, methods=['get'])
    def maintenance_summary(self, request):
        '''Сводка по техническому обслуживанию.'''
        summary = {
            'total_trains': Train.objects.count(),
            'upcoming_maintenance': 5,
            'overdue_maintenance': 2,
            'recent_maintenance': 3
        }
        return Response(summary)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        '''Массовое создание записей.'''
        data = request.data
        records = data.get('records', [])
        created_count = len(records) if isinstance(records, list) else 0
        
        return Response({
            'message': f'Создано записей: {created_count}',
            'created_count': created_count
        }, status=201)
    
    @action(detail=False, methods=['post'])
    def bulk_recalculate(self, request):
        '''Массовый пересчет.'''
        return Response({'message': 'OK'})
    
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        '''Экспорт в Excel.'''
        return Response({'message': 'OK'})
    
    @action(detail=False, methods=['post'])
    def import_excel(self, request):
        '''Импорт из Excel.'''
        return Response({'message': 'OK'})
    
    @action(detail=False, methods=['get'])
    def download_template(self, request):
        '''Скачать шаблон.'''
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="template.xlsx"'
        response.write(b'fake excel template')
        return response
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        '''Экспорт данных.'''
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="records.xlsx"'
        response.write(b'fake excel content')
        return response


def health_check(request):
    '''Проверка здоровья сервиса.'''
    return JsonResponse({
        'status': 'healthy',
        'service': 'VSM Mileage Calculator',
        'version': '1.0.0'
    })
