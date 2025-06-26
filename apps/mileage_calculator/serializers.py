# Source Generated with Decompyle++
# File: serializers.cpython-312.pyc (Python 3.12)

'''
Сериализаторы для API калькулятора пробега.
'''
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
from .models import Depot, Train, TrainDailyRecord
from .services.calculation_service import MileageCalculationService
from .services.analytics_service import AnalyticsService

class DepotSerializer(serializers.ModelSerializer):
    '''Сериализатор депо.'''
    trains_count = serializers.SerializerMethodField()
    active_trains_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Depot
        fields = [
            'id',
            'name',
            'trains_count',
            'active_trains_count']

    
    def validate_name(self, value):
        '''Валидация названия депо.'''
        if not value or not value.strip():
            raise serializers.ValidationError('Название депо не может быть пустым')
        if len(value) > 255:
            raise serializers.ValidationError('Название депо не может быть длиннее 255 символов')
        return value.strip()

    
    def get_trains_count(self, obj):
        '''Общее количество поездов.'''
        return obj.trains.count()

    
    def get_active_trains_count(self, obj):
        '''Количество активных поездов.'''
        return obj.trains.filter(is_active=True).count()



class TrainSerializer(serializers.ModelSerializer):
    '''Сериализатор поезда.'''
    depot_name = serializers.CharField(source='depot.name', read_only=True)
    records_count = serializers.SerializerMethodField()
    latest_record_date = serializers.SerializerMethodField()
    latest_total_mileage = serializers.SerializerMethodField()
    
    class Meta:
        model = Train
        fields = [
            'id', 'name', 'type', 'is_manual_mileage', 'depot', 'depot_name',
            'is_active', 'created_at', 'updated_at', 'records_count',
            'latest_record_date', 'latest_total_mileage'
        ]
        read_only_fields = ['created_at', 'updated_at']

    
    def validate_name(self, value):
        '''Валидация названия поезда.'''
        if not value or not value.strip():
            raise serializers.ValidationError('Название поезда не может быть пустым')
        if len(value) > 255:
            raise serializers.ValidationError('Название поезда не может быть длиннее 255 символов')
        return value.strip()

    
    def get_records_count(self, obj):
        '''Количество записей.'''
        return obj.daily_records.count()

    
    def get_latest_record_date(self, obj):
        '''Дата последней записи.'''
        latest = obj.daily_records.order_by('-record_date').first()
        if latest:
            return latest.record_date.isoformat()
        return None

    
    def get_latest_total_mileage(self, obj):
        '''Последний общий пробег.'''
        latest = obj.daily_records.order_by('-record_date').first()
        if latest:
            return latest.total_mileage
        return None



class TrainDailyRecordSerializer(serializers.ModelSerializer):
    '''Базовый сериализатор ежедневных записей.'''
    train_name = serializers.CharField(source='train.name', read_only=True)
    train_type = serializers.CharField(source='train.type', read_only=True)
    depot_name = serializers.CharField(source='train.depot.name', read_only=True)
    next_block_date = serializers.DateField(read_only=True)
    next_kp_date = serializers.DateField(read_only=True)
    indicator_color = serializers.CharField(read_only=True)
    mileage_indicator_color = serializers.CharField(read_only=True)
    
    class Meta:
        model = TrainDailyRecord
        fields = [
            'id',
            'train',
            'train_name',
            'train_type',
            'depot_name',
            'record_date',
            'total_mileage',
            'daily_mileage',
            'last_to_mileage',
            'last_to_date',
            'last_to_type',
            'next_to_type',
            'planned_to_date',
            'last_block_date',
            'last_kp_measure_date',
            'inspection_counter',
            'to_l_mileage',
            'to_n_mileage',
            'is510_mileage',
            'is520_mileage',
            'is530_mileage',
            'mileage_since_to',
            'mileage_to_to',
            'days_since_to',
            'avg_mileage',
            'manual_indicator_train',
            'manual_indicator_next_to',
            'next_block_date',
            'next_kp_date',
            'indicator_color',
            'mileage_indicator_color',
            'created_at',
            'updated_at']
        read_only_fields = [
            'mileage_since_to',
            'mileage_to_to',
            'days_since_to',
            'avg_mileage',
            'next_block_date',
            'next_kp_date',
            'indicator_color',
            'mileage_indicator_color',
            'created_at',
            'updated_at']

    
    def validate(self, data):
        """Валидация данных."""
        record_date = data.get('record_date')
        if record_date and record_date > date.today():
            raise serializers.ValidationError({
                'record_date': 'Дата записи не может быть в будущем'
            })
        
        train = data.get('train')
        if train and record_date:
            existing = TrainDailyRecord.objects.filter(train=train, record_date=record_date)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            if existing.exists():
                raise serializers.ValidationError({
                    'record_date': f'Запись для поезда {train.name} на {record_date} уже существует'
                })
        
        total_mileage = data.get('total_mileage')
        daily_mileage = data.get('daily_mileage')
        if total_mileage is not None and total_mileage < 0:
            raise serializers.ValidationError({
                'total_mileage': 'Общий пробег не может быть отрицательным'
            })
        if daily_mileage is not None and daily_mileage < 0:
            raise serializers.ValidationError({
                'daily_mileage': 'Суточный пробег не может быть отрицательным'
            })
        
        return data



class TrainDailyRecordDetailSerializer(TrainDailyRecordSerializer):
    '''Детальный сериализатор с дополнительными вычислениями.'''
    metrics = serializers.SerializerMethodField()
    analytics = serializers.SerializerMethodField()
    
    class Meta(TrainDailyRecordSerializer.Meta):
        fields = TrainDailyRecordSerializer.Meta.fields + [
            'metrics',
            'analytics']

    
    def get_metrics(self, obj):
        '''Все расчетные метрики.'''
        return MileageCalculationService.calculate_all_metrics(obj)

    
    def get_analytics(self, obj):
        '''Аналитические данные.'''
        if obj.train:
            return {
                'maintenance_prediction': AnalyticsService.predict_maintenance_date(obj.train),
                'mileage_patterns': AnalyticsService.analyze_mileage_patterns(obj.train, days = 30) }



class TrainDailyRecordCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор для создания записей с автоматическими расчетами.'''
    
    class Meta:
        model = TrainDailyRecord
        fields = [
            'train',
            'record_date',
            'total_mileage',
            'daily_mileage',
            'last_to_mileage',
            'last_to_date',
            'last_to_type',
            'next_to_type',
            'last_block_date',
            'last_kp_measure_date',
            'inspection_counter',
            'to_l_mileage',
            'to_n_mileage',
            'is510_mileage',
            'is520_mileage',
            'is530_mileage',
            'manual_indicator_train',
            'manual_indicator_next_to']

    
    def create(self, validated_data):
        """Создание записи с автоматическими расчетами."""
        with transaction.atomic():
            record = TrainDailyRecord.objects.create(**validated_data)
            MileageCalculationService.calculate_all_metrics(record, force_recalculate=True)
            record.refresh_from_db()
            return record



class BulkRecalculateSerializer(serializers.Serializer):
    '''Сериализатор для массового пересчета.'''
    train_ids = serializers.ListField(child = serializers.IntegerField(), required = False, help_text = 'Список ID поездов для пересчета (если не указан - все поезда)')
    start_date = serializers.DateField(required = False, help_text = 'Начальная дата для пересчета (по умолчанию - 30 дней назад)')
    end_date = serializers.DateField(required = False, help_text = 'Конечная дата для пересчета (по умолчанию - сегодня)')
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError('Начальная дата не может быть больше конечной')
        return data



class DepotStatisticsSerializer(serializers.Serializer):
    '''Сериализатор статистики депо.'''
    depot_id = serializers.IntegerField()
    period_days = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_trains = serializers.IntegerField()
    active_trains = serializers.IntegerField()
    aggregated_stats = serializers.DictField()
    train_type_stats = serializers.DictField()
    maintenance_analysis = serializers.DictField()
    trends = serializers.DictField()
    efficiency_metrics = serializers.DictField()


class MaintenancePredictionSerializer(serializers.Serializer):
    '''Сериализатор прогноза ТО.'''
    train_id = serializers.IntegerField()
    train_name = serializers.CharField()
    current_mileage_since_to = serializers.IntegerField(allow_null = True)
    target_mileage = serializers.IntegerField()
    remaining_mileage = serializers.IntegerField()
    predicted_date = serializers.DateField()
    confidence_interval = serializers.DictField()
    statistics = serializers.DictField()
    risk_assessment = serializers.DictField()


class ExcelImportSerializer(serializers.Serializer):
    '''Сериализатор для импорта Excel файлов.'''
    file = serializers.FileField(help_text = 'Excel файл (.xlsx или .xls) с данными')
    sheet_name = serializers.CharField(required = False, default = 'Sheet1', help_text = 'Название листа (по умолчанию Sheet1)')
    skip_rows = serializers.IntegerField(required = False, default = 0, min_value = 0, help_text = 'Количество строк для пропуска сверху')
    update_existing = serializers.BooleanField(required = False, default = False, help_text = 'Обновлять существующие записи')
    
    def validate_file(self, value):
        """Валидация файла."""
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError('Файл должен быть в формате Excel (.xlsx или .xls)')
        if value.size > 10485760:  # 10 MB
            raise serializers.ValidationError('Размер файла не должен превышать 10 МБ')
        return value



class ExcelExportSerializer(serializers.Serializer):
    '''Сериализатор для экспорта в Excel.'''
    train_ids = serializers.ListField(child = serializers.IntegerField(), required = False, help_text = 'Список ID поездов для экспорта (если не указан - все поезда)')
    depot_ids = serializers.ListField(child = serializers.IntegerField(), required = False, help_text = 'Список ID депо для экспорта')
    start_date = serializers.DateField(required = False, help_text = 'Начальная дата для экспорта')
    end_date = serializers.DateField(required = False, help_text = 'Конечная дата для экспорта')
    include_calculations = serializers.BooleanField(required = False, default = True, help_text = 'Включать расчетные поля')
    format = serializers.ChoiceField(choices = [
        ('xlsx', 'Excel 2007+'),
        ('xls', 'Excel 97-2003')], default = 'xlsx', help_text = 'Формат файла')


class TrainAnalyticsSerializer(serializers.Serializer):
    '''Сериализатор аналитики поезда.'''
    train_id = serializers.IntegerField()
    train_name = serializers.CharField()
    analysis_period = serializers.DictField()
    basic_statistics = serializers.DictField()
    trend_analysis = serializers.DictField()
    weekday_patterns = serializers.DictField()
    outliers = serializers.ListField()
    performance_indicators = serializers.DictField()

