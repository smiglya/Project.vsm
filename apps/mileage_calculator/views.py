# Source Generated with Decompyle++
# File: views.cpython-312.pyc (Python 3.12)

'''
API Views для калькулятора пробега.
'''
from datetime import date, timedelta
from django.db.models import Q, Prefetch
from django.http import HttpResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Depot, Train, TrainDailyRecord
from .serializers import DepotSerializer, TrainSerializer, TrainDailyRecordSerializer, TrainDailyRecordDetailSerializer, TrainDailyRecordCreateSerializer, BulkRecalculateSerializer, DepotStatisticsSerializer, MaintenancePredictionSerializer, ExcelImportSerializer, ExcelExportSerializer, TrainAnalyticsSerializer
from .services.calculation_service import MileageCalculationService
from .services.analytics_service import AnalyticsService
from .services.excel_service import ExcelService

class DepotViewSet(viewsets.ModelViewSet):
    '''ViewSet для управления депо.'''
    queryset = Depot.objects.all()
    serializer_class = DepotSerializer
    permission_classes = [
        IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter]
    search_fields = [
        'name']
    ordering_fields = [
        'name',
        'created_at']
    ordering = [
        'name']

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        '''Получение статистики депо.'''
        depot = self.get_object()
        days = int(request.query_params.get('days', 30))
        stats = AnalyticsService.get_depot_statistics(depot.id, days)
        serializer = DepotStatisticsSerializer(stats)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        '''Запуск пересчета для всех поездов депо.'''
        depot = self.get_object()
        serializer = BulkRecalculateSerializer(data=request.data)
        if serializer.is_valid():
            # Здесь можно запустить Celery задачу для пересчета
            return Response({
                'message': f'Пересчет запущен для депо {depot.name}',
                'depot_id': depot.id
            }, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainViewSet(viewsets.ModelViewSet):
    '''ViewSet для управления поездами.'''
    queryset = Train.objects.select_related('depot').all()
    serializer_class = TrainSerializer
    permission_classes = [
        IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter]
    filterset_fields = [
        'type',
        'depot',
        'is_active',
        'is_manual_mileage']
    search_fields = [
        'name',
        'depot__name']
    ordering_fields = [
        'name',
        'type',
        'created_at']
    ordering = [
        'name']

    @action(detail=True, methods=['get'])
    def maintenance_prediction(self, request, pk=None):
        '''Прогнозирование технического обслуживания.'''
        train = self.get_object()
        confidence = float(request.query_params.get('confidence', 0.95))
        
        if not (0.9 <= confidence <= 0.99):
            return Response({
                'error': 'Уровень доверия должен быть от 0.9 до 0.99'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            prediction = AnalyticsService.predict_maintenance_date(train, confidence)
            if 'error' in prediction:
                return Response(prediction, status=status.HTTP_404_NOT_FOUND)
            
            serializer = MaintenancePredictionSerializer(prediction)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': f'Ошибка при расчете прогноза: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        '''Аналитика по поезду.'''
        train = self.get_object()
        days = int(request.query_params.get('days', 90))
        
        try:
            analytics = AnalyticsService.analyze_mileage_patterns(train, days)
            if 'error' in analytics:
                return Response(analytics, status=status.HTTP_404_NOT_FOUND)
            
            serializer = TrainAnalyticsSerializer(analytics)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': f'Ошибка при анализе: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        '''Пересчет данных поезда.'''
        train = self.get_object()
        serializer = BulkRecalculateSerializer(data=request.data)
        
        if serializer.is_valid():
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')
            
            if not start_date:
                start_date = date.today() - timedelta(days=30)
            if not end_date:
                end_date = date.today()
            
            # Здесь можно запустить Celery задачу для пересчета
            return Response({
                'message': f'Пересчет запущен для поезда {train.name}',
                'train_id': train.id,
                'period': f'{start_date} - {end_date}'
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainDailyRecordViewSet(viewsets.ModelViewSet):
    '''ViewSet для управления ежедневными записями.'''
    permission_classes = [
        IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter]
    filterset_fields = [
        'train',
        'train__type',
        'train__depot',
        'record_date',
        'last_to_type',
        'next_to_type',
        'manual_indicator_train']
    search_fields = [
        'train__name',
        'train__depot__name']
    ordering_fields = [
        'record_date',
        'total_mileage',
        'daily_mileage',
        'days_since_to']
    ordering = [
        '-record_date',
        'train__name']
    
    def get_queryset(self):
        '''Оптимизированный queryset с выборкой связанных объектов.'''
        return TrainDailyRecord.objects.select_related('train__depot').prefetch_related(Prefetch('train', queryset = Train.objects.select_related('depot')))

    
    def get_serializer_class(self):
        '''Выбор сериализатора в зависимости от действия.'''
        if self.action == 'create':
            return TrainDailyRecordCreateSerializer
        if self.action == 'retrieve':
            return TrainDailyRecordDetailSerializer
        return TrainDailyRecordSerializer

    @action(detail=False, methods=['post'])
    def export_excel(self, request):
        '''Экспорт данных в Excel.'''
        serializer = ExcelExportSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            queryset = self.filter_queryset(self.get_queryset())
            
            # Применение фильтров
            if data.get('train_ids'):
                queryset = queryset.filter(train_id__in=data['train_ids'])
            if data.get('depot_ids'):
                queryset = queryset.filter(train__depot_id__in=data['depot_ids'])
            if data.get('start_date'):
                queryset = queryset.filter(record_date__gte=data['start_date'])
            if data.get('end_date'):
                queryset = queryset.filter(record_date__lte=data['end_date'])
            
            filename = f'vsm_data_{date.today().isoformat()}.{data["format"]}'
            
            try:
                response = ExcelService.export_to_excel(
                    queryset,
                    filename=filename,
                    include_calculations=data['include_calculations'],
                    format=data['format']
                )
                return response
            except Exception as e:
                return Response({
                    'error': f'Ошибка экспорта: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def import_excel(self, request):
        '''Импорт данных из Excel.'''
        serializer = ExcelImportSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            try:
                result = ExcelService.import_from_excel(
                    data['file'],
                    sheet_name=data['sheet_name'],
                    skip_rows=data['skip_rows'],
                    update_existing=data['update_existing']
                )
                
                return Response({
                    'success': True,
                    'message': 'Импорт завершен успешно',
                    'results': result
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Ошибка импорта: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def download_template(self, request):
        '''Скачивание шаблона Excel.'''
        try:
            return ExcelService.export_template()
        except Exception as e:
            return Response({
                'error': f'Ошибка создания шаблона: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def bulk_recalculate(self, request):
        '''Массовый пересчет записей.'''
        serializer = BulkRecalculateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            train_ids = data.get('train_ids', [])
            
            if not train_ids:
                train_ids = list(Train.objects.filter(is_active=True).values_list('id', flat=True))
            
            start_date = data.get('start_date') or date.today() - timedelta(days=30)
            end_date = data.get('end_date') or date.today()
            
            # Здесь можно запустить Celery задачу для пересчета
            return Response({
                'message': f'Запущен пересчет для {len(train_ids)} поездов',
                'period': f'{start_date} - {end_date}',
                'trains_count': len(train_ids)
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_indicator(self, request):
        '''Фильтрация по цветовому индикатору.'''
        indicator_color = request.query_params.get('indicator') or request.query_params.get('indicator_color')
        filter_date = request.query_params.get('date', date.today())
        
        if isinstance(filter_date, str):
            try:
                filter_date = date.fromisoformat(filter_date)
            except ValueError:
                return Response({
                    'error': 'Неверный формат даты. Используйте YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(record_date=filter_date)
        
        if indicator_color == 'yellow':
            queryset = queryset.filter(days_since_to__gte=45, days_since_to__lte=55)
        elif indicator_color == 'red':
            queryset = queryset.filter(
                Q(days_since_to__gt=55) | Q(mileage_since_to__gt=23000)
            )
        elif indicator_color == 'green':
            queryset = queryset.filter(
                Q(indicator_color='green') | Q(days_since_to__lt=45)
            )
        else:
            return Response({
                'error': 'Неверный цвет индикации. Доступны: yellow, red, green'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def maintenance_summary(self, request):
        '''Сводка по техническому обслуживанию.'''
        filter_date = request.query_params.get('date', date.today())
        
        if isinstance(filter_date, str):
            try:
                filter_date = date.fromisoformat(filter_date)
            except ValueError:
                filter_date = date.today()
        
        queryset = self.get_queryset().filter(record_date=filter_date)
        
        # Статистика по дням с ТО
        days_stats = {
            'critical': queryset.filter(days_since_to__gte=56).count(),
            'warning': queryset.filter(days_since_to__gt=45, days_since_to__lt=55).count(),
            'normal': queryset.filter(days_since_to__lte=45).count(),
            'no_data': queryset.filter(days_since_to__isnull=True).count()
        }
        
        # Статистика по пробегу
        mileage_stats = {
            'critical': queryset.filter(mileage_since_to__gt=23000).count(),
            'warning': queryset.filter(mileage_since_to__gt=20000, mileage_since_to__lte=23000).count(),
            'normal': queryset.filter(mileage_since_to__lte=20000).count(),
            'no_data': queryset.filter(mileage_since_to__isnull=True).count()
        }
        
        # Предстоящие ТО
        upcoming_to = queryset.filter(
            planned_to_date__gte=filter_date,
            planned_to_date__lte=filter_date + timedelta(days=7)
        ).order_by('planned_to_date')
        
        upcoming_serializer = self.get_serializer(upcoming_to, many=True)
        
        return Response({
            'date': filter_date,
            'total_records': queryset.count(),
            'days_since_to_stats': days_stats,
            'mileage_stats': mileage_stats,
            'upcoming_maintenance': upcoming_serializer.data
        })

