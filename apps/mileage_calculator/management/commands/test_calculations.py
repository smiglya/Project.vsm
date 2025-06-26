# Source Generated with Decompyle++
# File: test_calculations.cpython-312.pyc (Python 3.12)

'''
Команда для тестирования всех сервисов расчетов.
'''
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.mileage_calculator.models import Train, TrainDailyRecord, Depot
from apps.mileage_calculator.services.calculation_service import MileageCalculationService
from apps.mileage_calculator.services.analytics_service import AnalyticsService
from tasks import recalculate_train_metrics, generate_maintenance_alerts

class Command(BaseCommand):
    help = 'Тестирование всех сервисов расчетов калькулятора пробега'
    
    def add_arguments(self, parser):
        parser.add_argument('--train-id', type=int, help='ID поезда для тестирования (по умолчанию - первый найденный)')
        parser.add_argument('--depot-id', type=int, help='ID депо для тестирования статистики')
        parser.add_argument('--test-analytics', action='store_true', help='Тестировать аналитические сервисы')
        parser.add_argument('--test-tasks', action='store_true', help='Тестировать Celery задачи')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧮 Начинаем тестирование сервисов расчетов'))
        
        train_id = options.get('train_id')
        try:
            if train_id:
                train = Train.objects.get(id=train_id)
            else:
                train = Train.objects.first()
                if not train:
                    self.stdout.write(self.style.ERROR('Поезда не найдены в базе данных'))
                    return
                    
            self.stdout.write(f'Тестируем поезд: {train.name} ({train.train_type})')
            
            latest_record = TrainDailyRecord.objects.filter(train=train).order_by('-record_date').first()
            if not latest_record:
                self.stdout.write(self.style.ERROR(f'Записи для поезда {train.name} не найдены'))
                return
                
            self.test_calculation_service(train, latest_record)
            
            if options['test_analytics']:
                self.test_analytics_service(train, options.get('depot_id'))
                
            # Пока отключаем тестирование Celery задач
            # if options['test_tasks']:
            #     self.test_celery_tasks(train)
                
        except Train.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Поезд с ID {train_id} не найден'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))

    def test_calculation_service(self, train, record):
        """Тестирование сервиса расчетов."""
        self.stdout.write('\n📊 Тестирование MileageCalculationService:')
        
        try:
            metrics = MileageCalculationService.calculate_all_metrics(record)
            self.stdout.write(f'  ✅ Общий пробег: {metrics.get("total_mileage", "N/A"):,} км')
            self.stdout.write(f'  ✅ Суточный пробег: {metrics.get("daily_mileage", "N/A")} км')
            self.stdout.write(f'  ✅ Пробег с последнего ТО: {metrics.get("mileage_since_to", "N/A")} км')
            self.stdout.write(f'  ✅ Остаток до ТО: {metrics.get("mileage_to_to", "N/A")} км')
            self.stdout.write(f'  ✅ Дней с последнего ТО: {metrics.get("days_since_to", "N/A")}')
            self.stdout.write(f'  ✅ Средний пробег: {metrics.get("avg_mileage", "N/A")} км/день')
            
            planned_date = metrics.get('planned_to_date')
            if planned_date:
                self.stdout.write(f'  ✅ Планируемая дата ТО: {planned_date}')
            else:
                self.stdout.write('  ⚠️  Планируемая дата ТО: не рассчитана')
                
            indicator_color = metrics.get('indicator_color')
            if indicator_color:
                self.stdout.write(f'  🔴 Цветовая индикация: {indicator_color}')
            else:
                self.stdout.write('  🟢 Цветовая индикация: нормально')
                
            if train.type == 'Сапсан':
                self.stdout.write('\n🚄 Специфичные расчеты для Сапсана:')
                sapsan_metrics = {
                    'mileage_from_to_l': MileageCalculationService.calculate_sapsan_mileage_from_to_l(record),
                    'mileage_to_to_l': MileageCalculationService.calculate_sapsan_mileage_to_to_l(record),
                    'mileage_to_to_n': MileageCalculationService.calculate_sapsan_mileage_to_to_n(record) }
                for key, value in sapsan_metrics.items():
                    '  ✅ '(f'''{key}: {value if value else 'N/A'}''')
                if self.stdout.write:
                    pass
            self.stdout.write('\n🔄 Тестирование массового пересчета:')
            end_date = date.today()
            start_date = end_date - timedelta(days = 7)
            updated_count = MileageCalculationService.bulk_calculate_for_train(train, start_date, end_date)
            self.stdout.write(f'''  ✅ Обновлено записей: {updated_count}''')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка в расчетах: {str(e)}'))

    def test_analytics_service(self, train, depot_id=None):
        """Тестирование аналитического сервиса."""
        self.stdout.write('\n📈 Тестирование AnalyticsService:')
        
        try:
            prediction = AnalyticsService.predict_maintenance_date(train)
            if 'error' in prediction:
                self.stdout.write(f'  ⚠️  Прогнозирование ТО: {prediction["error"]}')
            else:
                self.stdout.write(f'  ✅ Прогнозируемая дата ТО: {prediction["predicted_date"]}')
                
            if not depot_id:
                depot_id = train.depot.id
                
            depot_stats = AnalyticsService.get_depot_statistics(depot_id)
            self.stdout.write(f'\n🏭 Статистика депо {depot_stats["depot_id"]}:')
            self.stdout.write(f'  🚂 Всего поездов: {depot_stats["total_trains"]}')
            self.stdout.write(f'  ✅ Активных поездов: {depot_stats["active_trains"]}')
            
            agg_stats = depot_stats['aggregated_stats']
            if not agg_stats['total_mileage'] or agg_stats['total_mileage']:
                '  📊 Общий пробег: '
            None(f'''{0:,} км''')
            if not agg_stats['avg_daily_mileage'] or agg_stats['avg_daily_mileage']:
                '  📊 Средний суточный пробег: '
            None(f'''{0:.2f} км''')
            
            maintenance = depot_stats['maintenance_analysis']
            self.stdout.write(f'''  🔴 Критичных по дням: {maintenance['days_analysis']['critical']}''')
            self.stdout.write(f'''  🟡 Предупреждений по дням: {maintenance['days_analysis']['warning']}''')
            self.stdout.write(f'''  🔴 Критичных по пробегу: {maintenance['mileage_analysis']['critical']}''')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка в аналитике: {str(e)}'))

    def test_celery_tasks(self, train):
        '''Тестирование Celery задач.'''
        self.stdout.write('\n⚙️ Тестирование Celery задач:')
        end_date = date.today()
        start_date = end_date - timedelta(days = 7)
        task_result = recalculate_train_metrics.delay(train.id, start_date.isoformat(), end_date.isoformat())
        self.stdout.write(f'''  ✅ Задача пересчета запущена: {task_result.id}''')
        result = task_result.get(timeout = 30)
        if 'error' in result:
            self.stdout.write(f'''  ❌ Ошибка в задаче: {result['error']}''')
        else:
            self.stdout.write(f'''  ✅ Обновлено записей: {result['updated_count']}''')
        alerts_task = generate_maintenance_alerts.delay()
        self.stdout.write(f'''  ✅ Задача уведомлений запущена: {alerts_task.id}''')
        alerts_result = alerts_task.get(timeout = 15)
        total_alerts = alerts_result.get('total_alerts', 0)
        self.stdout.write(f'''  📢 Сгенерировано уведомлений: {total_alerts}''')
        if alerts_result.get('alerts'):
            self.stdout.write('  📋 Примеры уведомлений:')
            # if 3:  # Некорректное условие
            for alert in 3:
                self.stdout.write(f'''    • {alert['message']} (приоритет: {alert['priority']})''')
            # if None:  # Некорректное условие
        self.stdout.write(self.style.SUCCESS('\n✅ Тестирование сервисов завершено успешно!'))
        return None
        # if None:  # Некорректное условие
        try:
            e = None
            self.stdout.write(f'''  ⚠️  Таймаут или ошибка задачи: {e}''')
            e = None
            del e
            continue
            e = None
            del e
            if alerts_result['alerts'] and alerts_result['alerts']:
                pass
        if alerts_result['alerts'] and alerts_result['alerts'] and alerts_result['alerts']:
            pass
        try:
            e = alerts_result['alerts']
            self.stdout.write(f'''  ⚠️  Таймаут или ошибка задачи уведомлений: {e}''')
            e = None
            del e
            continue
            e = None
            del e
            except Exception as e:
        pass
        except Exception as e:
        pass


