# Source Generated with Decompyle++
# File: load_test_data.cpython-310.pyc (Python 3.10)

'''
Команда для загрузки тестовых данных.
'''
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
import random
from apps.mileage_calculator.models import Depot, Train, TrainDailyRecord

class Command(BaseCommand):
    '''Команда для создания тестовых данных.'''
    help = 'Загружает тестовые данные для калькулятора пробега'
    
    def add_arguments(self, parser):
        parser.add_argument('--days', int, 30, 'Количество дней для генерации записей (по умолчанию 30)', **('type', 'default', 'help'))
        parser.add_argument('--clear', 'store_true', 'Очистить существующие данные перед загрузкой', **('action', 'help'))

    
    def handle(self, *args, **options):
        '''Основная логика команды.'''
        days_count = options['days']
        clear_data = options['clear']
        if clear_data:
            self.stdout.write('Очистка существующих данных...')
            TrainDailyRecord.objects.all().delete()
            Train.objects.all().delete()
            Depot.objects.all().delete()
        with transaction.atomic():
            depots = self.create_depots()
            trains = self.create_trains(depots)
            self.create_daily_records(trains, days_count)
            None(None, None, None)
        with None:
            if not None:
                if None:
                    self.stdout.write(self.style.SUCCESS(f'''Тестовые данные успешно загружены! Создано {len(depots)} депо, {len(trains)} поездов, записи за {days_count} дней.'''))
                    return None

    
    def create_depots(self):
        '''Создание депо.'''
        depots_data = [
            'ТЧ-1 Москва',
            'ТЧ-2 Санкт-Петербург',
            'ТЧ-3 Нижний Новгород',
            'ТЧ-4 Екатеринбург',
            'ТЧ-5 Новосибирск']
        depots = []
        for depot_name in depots_data:
            (depot, created) = Depot.objects.get_or_create(depot_name, **('name',))
            depots.append(depot)
            if created:
                self.stdout.write(f'''Создано депо: {depot_name}''')
        return depots

    
    def create_trains(self, depots):
        '''Создание поездов.'''
        trains_data = [
            ('ЭС1-001', 'Ласточка', False),
            ('ЭС1-002', 'Ласточка', False),
            ('ЭС1-003', 'Ласточка', True),
            ('ЭС1-004', 'Ласточка', False),
            ('ЭС1-005', 'Ласточка', True),
            ('ЭС2Г-001', 'Финист', False),
            ('ЭС2Г-002', 'Финист', False),
            ('ЭС2Г-003', 'Финист', True),
            ('ЭВС1-001', 'Сапсан', False),
            ('ЭВС1-002', 'Сапсан', False),
            ('ЭВС1-003', 'Сапсан', False)]
        trains = []
        for train_name, train_type, is_manual in enumerate(trains_data):
            depot = depots[i % len(depots)]
            (train, created) = Train.objects.get_or_create(train_name, {
                'type': train_type,
                'is_manual_mileage': is_manual,
                'depot': depot }, **('name', 'defaults'))
            trains.append(train)
            if created:
                self.stdout.write(f'''Создан поезд: {train_name} ({train_type})''')
        return trains

    
    def create_daily_records(self, trains, days_count):
        '''Создание ежедневных записей.'''
        start_date = date.today() - timedelta(days_count, **('days',))
        train_data = { }
        for train in trains:
            initial_mileage = random.randint(800000, 1200000)
            last_to_days_ago = random.randint(30, 180)
            last_to_date = start_date - timedelta(last_to_days_ago, **('days',))
            last_to_mileage = initial_mileage - random.randint(5000, 25000)
            train_data[train.id] = {
                'current_mileage': initial_mileage,
                'last_to_date': last_to_date,
                'last_to_mileage': last_to_mileage,
                'last_to_type': random.choice([
                    'ТО-1',
                    'ТО-2',
                    'I1',
                    'I2']),
                'next_to_type': random.choice([
                    'ТО-1',
                    'ТО-2',
                    'I2',
                    'I3']),
                'last_block_date': last_to_date - timedelta(random.randint(10, 30), **('days',)),
                'last_kp_date': last_to_date - timedelta(random.randint(5, 20), **('days',)),
                'inspection_counter': random.randint(1, 10) }
        records_created = 0
        for day in range(days_count):
            current_date = start_date + timedelta(day, **('days',))
            for train in trains:
                data = train_data[train.id]
                if train.type == 'Сапсан':
                    daily_mileage = random.randint(800, 1200)
                else:
                    daily_mileage = random.randint(200, 600)
                data['current_mileage'] += daily_mileage
                record = TrainDailyRecord.objects.create(train, current_date, data['current_mileage'], daily_mileage, data['last_to_mileage'], data['last_to_date'], data['last_to_type'], data['next_to_type'], data['last_block_date'], data['last_kp_date'], data['inspection_counter'], **('train', 'record_date', 'total_mileage', 'daily_mileage', 'last_to_mileage', 'last_to_date', 'last_to_type', 'next_to_type', 'last_block_date', 'last_kp_measure_date', 'inspection_counter'))
                if train.type == 'Сапсан':
                    record.to_l_mileage = data['last_to_mileage'] + random.randint(1000, 5000)
                    record.to_n_mileage = data['last_to_mileage'] + random.randint(10000, 20000)
                    record.is510_mileage = data['current_mileage'] - random.randint(500, 1500)
                    record.is520_mileage = data['current_mileage'] - random.randint(1000, 3000)
                    record.is530_mileage = data['current_mileage'] - random.randint(2000, 5000)
                    record.save()
                if random.random() < 0.1:
                    record.manual_indicator_train = True
                if record.next_to_type in ('I3', 'I4', 'I5', 'I6', 'R1', 'R2', 'R3', 'R4') and random.random() < 0.3:
                    record.manual_indicator_next_to = True
                record.save()
                records_created += 1
                if random.random() < 0.02:
                    data['last_to_date'] = current_date
                    data['last_to_mileage'] = data['current_mileage']
                    data['last_to_type'] = data['next_to_type']
                    data['next_to_type'] = random.choice([
                        'ТО-1',
                        'ТО-2',
                        'I2',
                        'I3'])
                    data['inspection_counter'] += 1
        self.stdout.write(f'''Создано {records_created} записей''')


