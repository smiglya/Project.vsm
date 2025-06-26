'''
Сервис для расчета пробега и планирования ТО поездов.
Реализует 12 формул автоматического расчета согласно ТЗ.
'''
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
from django.core.cache import cache
from django.db.models import Avg, Sum, Max, Min
import logging

logger = logging.getLogger(__name__)


class MileageCalculationService:
    '''Сервис расчета пробега и планирования ТО.'''

    @staticmethod
    def calculate_total_mileage(record=None, previous_total=None, daily_mileage=None):
        '''Формула 1: Общий пробег = Предыдущий общий пробег + Суточный пробег'''
        if previous_total is not None and daily_mileage is not None:
            return previous_total + daily_mileage
            
        # Для обратной совместимости - старый способ
        if record:
            if record.total_mileage:
                return record.total_mileage
            
            # Ищем предыдущую запись 
            from ..models import TrainDailyRecord
            previous_record = TrainDailyRecord.objects.filter(
                train=record.train,
                record_date__lt=record.record_date
            ).order_by('-record_date').first()
            
            previous_total = previous_record.total_mileage if previous_record else 0
            return previous_total + (record.daily_mileage or 0)
        
        return 0

    @staticmethod
    def calculate_daily_mileage(record=None, today_total=None, yesterday_total=None):
        '''Формула 2: Суточный пробег = Общий пробег сегодня - Общий пробег вчера'''
        if today_total is not None and yesterday_total is not None:
            return max(0, today_total - yesterday_total)
            
        # Для обратной совместимости
        if record:
            if record.daily_mileage:
                return record.daily_mileage
                
            from ..models import TrainDailyRecord
            previous_record = TrainDailyRecord.objects.filter(
                train=record.train,
                record_date__lt=record.record_date
            ).order_by('-record_date').first()
            
            if previous_record and record.total_mileage:
                return max(0, record.total_mileage - previous_record.total_mileage)
        
        return 0

    @staticmethod
    def calculate_mileage_since_to(record=None, total_mileage=None, last_to_mileage=None):
        '''Формула 3: Пробег от ТО = Общий пробег - Километраж с последнего ТО'''
        if total_mileage is not None and last_to_mileage is not None:
            return max(0, total_mileage - last_to_mileage)
            
        # Для обратной совместимости
        if record and record.total_mileage and record.last_to_mileage:
            return max(0, record.total_mileage - record.last_to_mileage)
        return 0

    @staticmethod
    def calculate_mileage_to_to(record=None, train_type='Ласточка', limit=None, mileage_since_to=None):
        '''Формула 4: Остаток до ТО = Лимит километража - Пробег от ТО'''
        # Если переданы конкретные параметры
        if limit is not None and mileage_since_to is not None:
            return max(0, limit - mileage_since_to)
            
        # Для обратной совместимости
        if record:
            if record.train:
                train_type = record.train.type
            
            # Определяем лимит по типу поезда
            limits = {
                'Ласточка': 15000,
                'Финист': 20000,
                'Сапсан': 25000
            }
            
            limit = limits.get(train_type, 15000)
            mileage_since_to = record.mileage_since_to or 0
            
            return max(0, limit - mileage_since_to)
        
        return 0

    @staticmethod
    def calculate_days_since_to(record=None, current_date=None, last_to_date=None):
        '''Формула 5: Дней с последнего ТО'''
        if current_date is not None and last_to_date is not None:
            return (current_date - last_to_date).days
            
        # Для обратной совместимости
        if record and record.last_to_date:
            current_date = record.record_date or date.today()
            return (current_date - record.last_to_date).days
        return 0

    @staticmethod
    def calculate_average_mileage(train, current_date=None, days=90):
        '''Формула 6: Средний пробег за заданное количество дней'''
        from ..models import TrainDailyRecord
        
        cache_key = f'avg_mileage_{train.id}_{days}'
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
            
        if not current_date:
            current_date = date.today()
            
        start_date = current_date - timedelta(days=days)
        
        records = TrainDailyRecord.objects.filter(
            train=train,
            record_date__gte=start_date,
            record_date__lte=current_date
        ).values_list('daily_mileage', flat=True)
        
        if not records:
            return 0.0
            
        # Исключаем записи с нулевым пробегом (простои)
        working_records = [r for r in records if r and r > 0]
        
        if not working_records:
            return 0.0
            
        avg = sum(working_records) / len(working_records)
        cache.set(cache_key, avg, 3600)  # Кеш на час
        
        return round(avg, 2)

    @staticmethod
    def calculate_planned_to_date(record=None, avg_mileage=None, train_type=None, current_date=None, avg_daily_mileage=None, remaining_mileage=None):
        '''Формула 7: Планируемая дата ТО'''
        # Если переданы конкретные параметры
        if current_date is not None and avg_daily_mileage is not None and remaining_mileage is not None:
            if avg_daily_mileage <= 0 or remaining_mileage <= 0:
                return current_date
            days_to_add = int(remaining_mileage / avg_daily_mileage)
            return current_date + timedelta(days=days_to_add)
            
        # Для обратной совместимости
        if not record:
            return None
            
        if not avg_mileage:
            avg_mileage = MileageCalculationService.calculate_average_mileage(record.train)
            
        if not train_type:
            train_type = record.train.type
            
        if not avg_mileage or avg_mileage <= 0:
            return None
            
        mileage_since_to = record.mileage_since_to or 0
        
        # Лимит до ТО
        if train_type == 'Сапсан':
            limit = 25000
        else:
            limit = 25000
            
        remaining_mileage = limit - mileage_since_to
        
        if remaining_mileage <= 0:
            return record.record_date
            
        days_to_to = remaining_mileage / avg_mileage
        return record.record_date + timedelta(days=int(days_to_to))

    @staticmethod
    def calculate_next_block_date(record=None, last_block_date=None):
        '''Формула 8: Дата следующего БЛОК = Дата последнего БЛОК + 45 дней'''
        if last_block_date is not None:
            return last_block_date + timedelta(days=45)
            
        # Для обратной совместимости
        if record and record.last_block_date:
            return record.last_block_date + timedelta(days=45)
        return None

    @staticmethod
    def calculate_next_kp_date(record=None, last_kp_date=None):
        '''Формула 9: Дата следующего БЗКП = Дата последнего БЗКП + 30 дней'''
        if last_kp_date is not None:
            return last_kp_date + timedelta(days=30)
            
        # Для обратной совместимости
        if record and record.last_kp_measure_date:
            return record.last_kp_measure_date + timedelta(days=30)
        return None

    @staticmethod
    def calculate_sapsan_mileage_from_to_l(record=None, total_mileage=None, to_l_mileage=None):
        '''Формула 10: Пробег от ТО-L = Общий пробег - Километраж ТО-L (Сапсан)'''
        if total_mileage is not None and to_l_mileage is not None:
            return max(0, total_mileage - to_l_mileage)
            
        # Для обратной совместимости
        if record:
            if record.train.type != 'Сапсан':
                return None
                
            if record.to_l_mileage and record.total_mileage:
                return record.total_mileage - record.to_l_mileage
        return 0

    @staticmethod
    def calculate_sapsan_mileage_to_to_l(record=None, limit=None, mileage_from_to_l=None):
        '''Формула 11: Остаток до ТО-L = Лимит - пробег от ТО-L (Сапсан)'''
        if limit is not None and mileage_from_to_l is not None:
            return max(0, limit - mileage_from_to_l)
            
        # Для обратной совместимости
        if record:
            if record.train.type != 'Сапсан':
                return None
                
            mileage_from_to_l = MileageCalculationService.calculate_sapsan_mileage_from_to_l(record)
            if mileage_from_to_l is not None:
                return max(0, 25000 - mileage_from_to_l)
        return None

    @staticmethod
    def calculate_sapsan_mileage_to_to_n(record=None, limit=None, mileage_from_to_n=None):
        '''Формула 12: Остаток до ТО-N = Лимит - пробег от ТО-N (Сапсан)'''
        if limit is not None and mileage_from_to_n is not None:
            return max(0, limit - mileage_from_to_n)
            
        # Для обратной совместимости
        if record:
            if record.train.type != 'Сапсан':
                return None
                
            if record.to_n_mileage and record.total_mileage:
                return max(0, 150000 + record.to_n_mileage - record.total_mileage)
        return None

    @staticmethod
    def calculate_indicator_color(record):
        '''Расчет цветового индикатора по времени'''
        days_since_to = record.days_since_to
        
        if days_since_to is None:
            return 'gray'
            
        if days_since_to < 45:
            return 'green'
        elif 45 <= days_since_to <= 55:
            return 'yellow'
        else:
            return 'red'

    @staticmethod
    def calculate_mileage_indicator_color(record):
        '''Расчет цветового индикатора по пробегу'''
        mileage_since_to = record.mileage_since_to
        
        if mileage_since_to is None:
            return 'gray'
            
        if mileage_since_to < 23000:
            return 'green'
        elif 23000 <= mileage_since_to < 25000:
            return 'yellow'
        else:
            return 'red'

    @staticmethod
    def calculate_maintenance_forecast(train):
        '''Прогноз технического обслуживания'''
        from ..models import TrainDailyRecord
        
        latest_record = TrainDailyRecord.objects.filter(
            train=train
        ).order_by('-record_date').first()
        
        if not latest_record:
            return {'error': 'Нет записей для прогноза'}
            
        avg_daily = MileageCalculationService.calculate_average_mileage(train)
        
        if avg_daily == 0:
            return {'error': 'Недостаточно данных для прогноза'}
            
        remaining_mileage = 25000 - (latest_record.mileage_since_to or 0)
        
        if remaining_mileage <= 0:
            return {
                'status': 'overdue',
                'message': 'ТО требуется немедленно'
            }
            
        days_to_to = int(remaining_mileage / avg_daily)
        forecast_date = date.today() + timedelta(days=days_to_to)
        
        return {
            'status': 'forecast',
            'days_to_to': days_to_to,
            'forecast_date': forecast_date,
            'avg_daily_mileage': float(avg_daily),
            'remaining_mileage': remaining_mileage
        }

    @staticmethod
    def calculate_performance_metrics(train):
        '''Расчет метрик производительности поезда'''
        from ..models import TrainDailyRecord
        
        records = TrainDailyRecord.objects.filter(train=train)
        
        if not records.exists():
            return {'error': 'Нет данных для расчета метрик'}
            
        total_mileage = sum(r.daily_mileage for r in records if r.daily_mileage)
        avg_daily = total_mileage / records.count()
        max_daily = max(r.daily_mileage for r in records if r.daily_mileage)
        min_daily = min(r.daily_mileage for r in records if r.daily_mileage)
        
        # Подсчет рабочих дней
        working_days = records.filter(daily_mileage__gt=0).count()
        total_days = records.count()
        efficiency_ratio = round(working_days / total_days, 3) if total_days > 0 else 0
        
        return {
            'total_records': records.count(),
            'total_mileage': int(total_mileage),
            'avg_daily_mileage': round(avg_daily, 2),
            'max_daily_mileage': max_daily,
            'min_daily_mileage': min_daily,
            'efficiency_ratio': efficiency_ratio
        }

    @staticmethod
    def clear_calculation_cache(train_id=None):
        '''Очистка кеша расчетов'''
        if train_id:
            cache_keys = [
                f'train_calculations_{train_id}',
                f'avg_mileage_{train_id}',
                f'to_forecast_{train_id}'
            ]
            cache.delete_many(cache_keys)
        else:
            cache.clear()

    @staticmethod
    def recalculate_all_fields(record):
        '''Пересчет всех полей записи'''
        train_type = record.train.type
        
        # Основные расчеты
        record.mileage_since_to = MileageCalculationService.calculate_mileage_since_to(record)
        record.mileage_to_to = MileageCalculationService.calculate_mileage_to_to(record, train_type)
        record.days_since_to = MileageCalculationService.calculate_days_since_to(record)
        
        # Средний пробег
        record.avg_mileage = MileageCalculationService.calculate_average_mileage(
            record.train, record.record_date
        )
        
        # Плановая дата ТО
        if record.avg_mileage and record.mileage_since_to is not None:
            record.planned_to_date = MileageCalculationService.calculate_planned_to_date(
                record, record.avg_mileage, train_type
            )
        
        # Цветовые индикаторы
        record.indicator_color = MileageCalculationService.calculate_indicator_color(record)
        record.mileage_indicator_color = MileageCalculationService.calculate_mileage_indicator_color(record)
        
        return record 

    @staticmethod
    def calculate_all_metrics(record, force_recalculate=False):
        '''Расчет всех метрик для записи'''
        if not record:
            return {}
            
        try:
            train_type = record.train.type
            
            # Основные расчеты
            metrics = {
                'mileage_since_to': MileageCalculationService.calculate_mileage_since_to(record),
                'mileage_to_to': MileageCalculationService.calculate_mileage_to_to(record, train_type),
                'days_since_to': MileageCalculationService.calculate_days_since_to(record),
                'avg_mileage': MileageCalculationService.calculate_average_mileage(record.train, record.record_date),
                'indicator_color': MileageCalculationService.calculate_indicator_color(record),
                'mileage_indicator_color': MileageCalculationService.calculate_mileage_indicator_color(record),
                'next_block_date': MileageCalculationService.calculate_next_block_date(record),
                'next_kp_date': MileageCalculationService.calculate_next_kp_date(record)
            }
            
            # Плановая дата ТО
            if metrics['avg_mileage'] and metrics['mileage_since_to'] is not None:
                metrics['planned_to_date'] = MileageCalculationService.calculate_planned_to_date(
                    record, metrics['avg_mileage'], train_type
                )
            
            # Специфичные для Сапсан поля
            if train_type == 'Сапсан':
                metrics.update({
                    'sapsan_mileage_from_to_l': MileageCalculationService.calculate_sapsan_mileage_from_to_l(record),
                    'sapsan_mileage_to_to_l': MileageCalculationService.calculate_sapsan_mileage_to_to_l(record),
                    'sapsan_mileage_to_to_n': MileageCalculationService.calculate_sapsan_mileage_to_to_n(record)
                })
            
            # Обновляем поля записи если нужно
            if force_recalculate:
                for field, value in metrics.items():
                    if hasattr(record, field) and value is not None:
                        setattr(record, field, value)
                record.save()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Ошибка расчета метрик для записи {record.id}: {e}")
            return {'error': str(e)} 