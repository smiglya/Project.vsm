# Source Generated with Decompyle++
# File: tasks.cpython-312.pyc (Python 3.12)

'''
Celery задачи для калькулятора пробега.
'''
from datetime import date, timedelta
from typing import List, Dict, Any
import logging
import requests
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from .models import Train, TrainDailyRecord, Depot
from .services.calculation_service import MileageCalculationService
logger = logging.getLogger(__name__)
recalculate_train_metrics = (lambda self = None, train_id = None, start_date = shared_task(bind = True, max_retries = 3), end_date = (None, None): train = Train.objects.get(id = train_id)if start_date:
start_date = date.fromisoformat(start_date)else:
start_date = date.today() - timedelta(days = 30)if end_date:
end_date = date.fromisoformat(end_date)else:
end_date = date.today()logger.info(f'''Начинаем пересчет метрик для поезда {train.name} с {start_date} по {end_date}''')updated_count = MileageCalculationService.bulk_calculate_for_train(train, start_date, end_date)logger.info(f'''Пересчет завершен для поезда {train.name}. Обновлено записей: {updated_count}'''){
'train_id': train_id,
'train_name': train.name,
'updated_count': updated_count,
'start_date': start_date.isoformat(),
'end_date': end_date.isoformat() }# if None:  # Некорректное условиеif Train.DoesNotExist and Train.DoesNotExist:
logger.error(f'''Поезд с ID {train_id} не найден''')if None and None:
logger.error(f'''Ошибка при пересчете метрик для поезда {train_id}: {exc}''')if self.request.retries < self.max_retries:
raise self.retry(countdown = 60 * (self.request.retries + 1))del excNoneNone = Nonedel excexcept Exception as e:
        passexcept Exception as e:
        pass)()
bulk_recalculate_all_trains = (lambda self = None, depot_id = None: if depot_id:
trains = Train.objects.filter(depot_id = depot_id, is_active = True)logger.info(f'''Начинаем массовый пересчет для депо {depot_id}''')else:
trains = Train.objects.filter(is_active = True)logger.info('Начинаем массовый пересчет для всех поездов')results = []end_date = date.today()start_date = end_date - timedelta(days = 90)for train in trains:
updated_count = MileageCalculationService.bulk_calculate_for_train(train, start_date, end_date)results.append({
'train_id': train.id,
'train_name': train.name,
'updated_count': updated_count,
'status': 'success' })logger.info(f'''Поезд {train.name}: обновлено {updated_count} записей''')# if None:  # Некорректное условиеtotal_updated = (lambda .0: # if None:  # Некорректное условиеfor r in .0:
if r.get('updated_count', 0):
passr.get('updated_count', 0)# if None:  # Некорректное условиеNoneif None:
# if None:  # Некорректное условие)(results())
    logger.info(f'''Массовый пересчет завершен. Всего обновлено записей: {total_updated}''')
    return {
        'depot_id': depot_id,
        'total_trains': len(trains),
        'total_updated': total_updated,
        'results': results }
    if sum:
        pass
    try:
        exc = sum
        logger.error(f'''Ошибка при пересчете поезда {train.name}: {exc}''')
        results.append({
            'train_id': train.id,
            'train_name': train.name,
            'status': 'error',
            'error': str(exc) })
        exc = None
        del exc
        continue
        exc = None
        del exc
        except Exception as e:
        pass
    if None and None and None:
        pass
    try:
        exc = None
        logger.error(f'''Ошибка при массовом пересчете: {exc}''')
        if self.request.retries < self.max_retries:
            raise self.retry(countdown = 300)
        del exc
        return None
    None = None
    del exc
    except Exception as e:
        pass
    except Exception as e:
        pass
)()
fetch_mileage_from_external_api = (lambda self = None, train_id = None, target_date = shared_task(bind = True, max_retries = 5): train = Train.objects.get(id = train_id)if train.is_manual_mileage:
{
'message': f'''Поезд {train.name} использует ручной ввод пробега''' }if None:
target_date = date.fromisoformat(target_date)else:
target_date = date.today()existing_record = TrainDailyRecord.objects.filter(train = train, record_date = target_date).first()if existing_record:
logger.info(f'''Запись для поезда {train.name} на {target_date} уже существует'''){
'message': f'''Запись уже существует для {train.name} на {target_date}''' }api_url = None.EXTERNAL_API_URLapi_key = settings.EXTERNAL_API_KEYheaders = {
'Authorization': f'''Bearer {api_key}''',
'Content-Type': 'application/json' }params = {
'train_id': train.name,
'date': target_date.isoformat(),
'depot': train.depot.name }logger.info(f'''Запрос к API для поезда {train.name} на {target_date}''')response = requests.get(f'''{api_url}/mileage''', headers = headers, params = params, timeout = 30)if response.status_code == 200:
data = response.json()previous_record = TrainDailyRecord.objects.filter(train = train, record_date__lt = target_date).order_by('-record_date').first()daily_mileage = data.get('daily_mileage', 0)total_mileage = data.get('total_mileage')if total_mileage and previous_record:
total_mileage = previous_record.total_mileage + daily_mileageelif not total_mileage:
total_mileage = daily_mileagerecord = TrainDailyRecord.objects.create(train = train, record_date = target_date, total_mileage = total_mileage, daily_mileage = daily_mileage, last_to_mileage = previous_record.last_to_mileage if previous_record else None, last_to_date = previous_record.last_to_date if previous_record else None, last_to_type = previous_record.last_to_type if previous_record else None, next_to_type = previous_record.next_to_type if previous_record else None, last_block_date = previous_record.last_block_date if previous_record else None, last_kp_measure_date = previous_record.last_kp_measure_date if previous_record else None)MileageCalculationService.calculate_all_metrics(record, force_recalculate = True)logger.info(f'''Создана запись для поезда {train.name} на {target_date}: суточный пробег {daily_mileage} км, общий пробег {total_mileage} км'''){
'train_id': train_id,
'train_name': train.name,
'date': target_date.isoformat(),
'daily_mileage': daily_mileage,
'total_mileage': total_mileage,
'status': 'success' }if None.status_code == 404:
logger.warning(f'''Данные для поезда {train.name} на {target_date} не найдены в API'''){
'message': f'''Данные не найдены для {train.name} на {target_date}''' }None.error(f'''Ошибка API: {response.status_code} - {response.text}''')raise Exception(f'''API error: {response.status_code}''')# if None:  # Некорректное условиеif Train.DoesNotExist and Train.DoesNotExist:
logger.error(f'''Поезд с ID {train_id} не найден''')if None.RequestException and None.RequestException:
logger.error(f'''Ошибка запроса к API для поезда {train_id}: {exc}''')if self.request.retries < self.max_retries:
2 ** self.request.retries * 60 = Noneraise self.retry(countdown = countdown)del excNoneNone = Nonedel exc# if None:  # Некорректное условиеtry:
exc = Nonelogger.error(f'''Неожиданная ошибка при получении данных для поезда {train_id}: {exc}''')del excNoneNone = Nonedel excexcept Exception as e:
        passexcept Exception as e:
        pass)()
daily_mileage_sync = (lambda : logger.info('Начинаем ежедневную синхронизацию пробега')trains = Train.objects.filter(is_manual_mileage = False, is_active = True)target_date = date.today()results = []for train in trains:
task_result = fetch_mileage_from_external_api.delay(train.id, target_date.isoformat())results.append({
'train_id': train.id,
'train_name': train.name,
'task_id': task_result.id,
'status': 'queued' })# if None:  # Некорректное условиеlogger.info(f'''Запущена синхронизация для {len(trains)} поездов на {target_date}'''){
'date': target_date.isoformat(),
'total_trains': len(trains),
'results': results }# if None:  # Некорректное условиеtry:
exc = Nonelogger.error(f'''Ошибка при запуске задачи для поезда {train.name}: {exc}''')results.append({
'train_id': train.id,
'train_name': train.name,
'status': 'error',
'error': str(exc) })exc = Nonedel exccontinueexc = Nonedel excexcept Exception as e:
        passexcept Exception as e:
        pass)()
cleanup_old_cache = (lambda : logger.info('Начинаем очистку старого кеша')cache.clear()logger.info('Кеш очищен успешно'){
'status': 'success',
'message': 'Кеш очищен' }# if None:  # Некорректное условиеtry:
exc = Nonelogger.error(f'''Ошибка при очистке кеша: {exc}''')del excNoneNone = Nonedel excexcept Exception as e:
        passexcept Exception as e:
        pass)()
generate_maintenance_alerts = (lambda : logger.info('Начинаем генерацию уведомлений о ТО')alerts = []current_date = date.today()critical_records = TrainDailyRecord.objects.filter(record_date = current_date).select_related('train')for record in critical_records:
days_since_to = record.days_since_tomileage_since_to = record.mileage_since_toif days_since_to and days_since_to >= 56:
alerts.append({
'type': 'critical_days',
'train': record.train.name,
'depot': record.train.depot.name,
'message': f'''Критическое превышение дней с последнего ТО: {days_since_to} дней''',
'days_since_to': days_since_to,
'priority': 'high' })elif days_since_to:
# Некорректное сравнение, требует восстановления
passelse:
alerts.append({
'type': 'warning_days',
'train': record.train.name,
'depot': record.train.depot.name,
'message': f'''Предупреждение: {days_since_to} дней с последнего ТО''',
'days_since_to': days_since_to,
'priority': 'medium' })if not mileage_since_to:
continueif not mileage_since_to > 23000:
continuealerts.append({
'type': 'critical_mileage',
'train': record.train.name,
'depot': record.train.depot.name,
'message': f'''Критический пробег с последнего ТО: {mileage_since_to:,} км''',
'mileage_since_to': mileage_since_to,
'priority': 'high' })# if None:  # Некорректное условиеif alerts:
cache.set('maintenance_alerts', alerts, 3600)logger.info(f'''Сгенерировано {len(alerts)} уведомлений о ТО''')else:
logger.info('Критических уведомлений не найдено')# if 10:  # Некорректное условие{
'date': alerts,
'total_alerts': None,
'alerts': 10 })()
