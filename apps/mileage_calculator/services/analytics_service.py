# Source Generated with Decompyle++
# File: analytics_service.cpython-312.pyc (Python 3.12)

'''
Аналитический сервис для расчета показателей пробега поездов.
'''
from datetime import date, timedelta
from typing import Dict, List, Any
from django.db.models import Avg, Sum, Count
from django.core.cache import cache
from ..models import Train, TrainDailyRecord, Depot

class AnalyticsService:
    '''Сервис для аналитики и отчетности.'''
    
    @staticmethod
    def get_train_statistics(train_id: int) -> Dict[str, Any]:
        '''Получение статистики по конкретному поезду.'''
        try:
            train = Train.objects.get(id=train_id)
            records = TrainDailyRecord.objects.filter(train=train)
            total_records = records.count()
            
            if total_records == 0:
                return {
                    'train_id': train_id,
                    'train_number': train.number,
                    'total_records': 0,
                    'avg_daily_mileage': 0,
                    'total_mileage': 0,
                    'last_record_date': None
                }
            
            avg_daily = records.aggregate(avg=Avg('daily_mileage'))['avg'] or 0
            total_mileage = records.aggregate(total=Sum('daily_mileage'))['total'] or 0
            last_record = records.order_by('-date').first()
            
            return {
                'train_id': train_id,
                'train_number': train.number,
                'total_records': total_records,
                'avg_daily_mileage': round(float(avg_daily), 2),
                'total_mileage': int(total_mileage),
                'last_record_date': last_record.date if last_record else None
            }
        except Train.DoesNotExist:
            return {
                'train_id': train_id,
                'error': 'Train not found'
            }
    
    @staticmethod
    def get_depot_statistics(depot_id: int) -> Dict[str, Any]:
        '''Получение статистики по депо.'''
        try:
            depot = Depot.objects.get(id=depot_id)
            trains = Train.objects.filter(depot=depot)
            total_trains = trains.count()
            
            if total_trains == 0:
                return {
                    'depot_id': depot_id,
                    'depot_name': depot.name,
                    'total_trains': 0,
                    'total_records': 0,
                    'avg_daily_mileage': 0
                }
            
            all_records = TrainDailyRecord.objects.filter(train__depot=depot)
            total_records = all_records.count()
            avg_daily = all_records.aggregate(avg=Avg('daily_mileage'))['avg'] or 0
            
            return {
                'depot_id': depot_id,
                'depot_name': depot.name,
                'total_trains': total_trains,
                'total_records': total_records,
                'avg_daily_mileage': round(float(avg_daily), 2)
            }
        except Depot.DoesNotExist:
            return {
                'depot_id': depot_id,
                'error': 'Depot not found'
            }
    
    @staticmethod
    def get_period_statistics(start_date: date, end_date: date) -> Dict[str, Any]:
        '''Получение статистики за период.'''
        records = TrainDailyRecord.objects.filter(date__range=[start_date, end_date])
        total_records = records.count()
        
        if total_records == 0:
            return {
                'period': f'{start_date} - {end_date}',
                'total_records': 0,
                'total_mileage': 0,
                'avg_daily_mileage': 0,
                'unique_trains': 0
            }
        
        total_mileage = records.aggregate(total=Sum('daily_mileage'))['total'] or 0
        avg_daily = records.aggregate(avg=Avg('daily_mileage'))['avg'] or 0
        unique_trains = records.values('train').distinct().count()
        
        return {
            'period': f'{start_date} - {end_date}',
            'total_records': total_records,
            'total_mileage': int(total_mileage),
            'avg_daily_mileage': round(float(avg_daily), 2),
            'unique_trains': unique_trains
        }
    
    @staticmethod
    def get_maintenance_alerts() -> List[Dict[str, Any]]:
        '''Получение уведомлений о техническом обслуживании.'''
        alerts = []
        trains = Train.objects.all()
        
        for train in trains:
            latest_record = TrainDailyRecord.objects.filter(train=train).order_by('-date').first()
            if not latest_record:
                continue
            
            days_since_to = (date.today() - latest_record.date).days
            alert_level = 'green'
            
            if days_since_to >= 56:
                alert_level = 'red'
            elif days_since_to >= 45:
                alert_level = 'yellow'
            
            if alert_level in ('yellow', 'red'):
                alerts.append({
                    'train_id': train.id,
                    'train_number': train.number,
                    'train_type': train.train_type,
                    'days_since_to': days_since_to,
                    'alert_level': alert_level,
                    'last_to_date': latest_record.date,
                    'next_to_due': latest_record.date + timedelta(days=45)
                })
        
        return sorted(alerts, key=lambda x: x['days_since_to'], reverse=True)
    
    @staticmethod
    def get_top_trains_by_mileage(limit: int = 10, period_days: int = 30) -> List[Dict[str, Any]]:
        '''Получение топ поездов по пробегу.'''
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        train_stats = []
        trains = Train.objects.all()
        
        for train in trains:
            records = TrainDailyRecord.objects.filter(
                train=train, 
                date__range=[start_date, end_date]
            )
            total_mileage = records.aggregate(total=Sum('daily_mileage'))['total'] or 0
            records_count = records.count()
            
            if total_mileage > 0:
                train_stats.append({
                    'train_id': train.id,
                    'train_number': train.number,
                    'train_type': train.train_type,
                    'total_mileage': int(total_mileage),
                    'records_count': records_count,
                    'avg_daily': round(float(total_mileage) / records_count, 2) if records_count > 0 else 0
                })
        
        sorted_stats = sorted(train_stats, key=lambda x: x['total_mileage'], reverse=True)
        return sorted_stats[:limit] if limit else sorted_stats
    
    @staticmethod
    def get_depot_comparison() -> List[Dict[str, Any]]:
        '''Сравнение депо по эффективности.'''
        depot_stats = []
        depots = Depot.objects.all()
        
        for depot in depots:
            trains = Train.objects.filter(depot=depot)
            all_records = TrainDailyRecord.objects.filter(train__depot=depot)
            total_trains = trains.count()
            total_records = all_records.count()
            
            if total_records > 0:
                avg_daily = all_records.aggregate(avg=Avg('daily_mileage'))['avg'] or 0
                total_mileage = all_records.aggregate(total=Sum('daily_mileage'))['total'] or 0
                
                depot_stats.append({
                    'depot_id': depot.id,
                    'depot_name': depot.name,
                    'total_trains': total_trains,
                    'total_records': total_records,
                    'avg_daily_mileage': round(float(avg_daily), 2),
                    'total_mileage': int(total_mileage),
                    'efficiency_score': round(float(avg_daily) * total_trains, 2)
                })
        
        return sorted(depot_stats, key=lambda x: x['efficiency_score'], reverse=True)
    
    @staticmethod
    def predict_maintenance_date(train):
        '''Прогноз даты техобслуживания для поезда.'''
        try:
            latest_record = TrainDailyRecord.objects.filter(train=train).order_by('-record_date').first()
            if not latest_record:
                return {'error': 'Нет записей для прогноза'}
            
            # Используем сервис расчетов для прогноза
            from .calculation_service import MileageCalculationService
            return MileageCalculationService.calculate_maintenance_forecast(train)
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod 
    def analyze_mileage_patterns(train, days=30):
        '''Анализ паттернов пробега поезда за период.'''
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            records = TrainDailyRecord.objects.filter(
                train=train,
                record_date__range=[start_date, end_date]
            ).order_by('record_date')
            
            if not records.exists():
                return {'error': 'Нет данных за указанный период'}
            
            daily_mileages = [r.daily_mileage or 0 for r in records]
            
            # Базовая статистика
            avg_mileage = sum(daily_mileages) / len(daily_mileages)
            max_mileage = max(daily_mileages)
            min_mileage = min(daily_mileages)
            
            # Паттерны по дням недели
            weekday_stats = {}
            for record in records:
                weekday = record.record_date.weekday()
                if weekday not in weekday_stats:
                    weekday_stats[weekday] = []
                weekday_stats[weekday].append(record.daily_mileage or 0)
            
            weekday_averages = {
                k: sum(v) / len(v) for k, v in weekday_stats.items()
            }
            
            return {
                'period_days': days,
                'total_records': len(daily_mileages),
                'avg_daily_mileage': round(avg_mileage, 2),
                'max_daily_mileage': max_mileage,
                'min_daily_mileage': min_mileage,
                'weekday_patterns': weekday_averages,
                'trend': 'stable'  # Упрощенный тренд
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_cached_analytics(cache_key: str, calculator_func, ttl: int = 3600):
        '''Получение кешированной аналитики.'''
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        fresh_data = calculator_func()
        cache.set(cache_key, fresh_data, ttl)
        return fresh_data
    
    @staticmethod
    def clear_analytics_cache():
        '''Очистка кеша аналитики.'''
        cache_keys = [
            'analytics:depot_comparison',
            'analytics:maintenance_alerts',
            'analytics:top_trains'
        ]
        cache.delete_many(cache_keys)

