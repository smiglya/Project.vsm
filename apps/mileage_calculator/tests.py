# Source Generated with Decompyle++
# File: tests.cpython-312.pyc (Python 3.12)

'''
Тесты для калькулятора пробега.
'''
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from .models import Depot, Train, TrainDailyRecord
from .services.calculation_service import MileageCalculationService
from .services.analytics_service import AnalyticsService

class ModelTestCase(TestCase):
    '''Тесты моделей.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        self.depot = Depot.objects.create(name = 'Тестовое депо')
        self.train = Train.objects.create(name = 'Тест-001', type = 'Ласточка', depot = self.depot, is_active = True)

    
    def test_depot_creation(self):
        '''Тест создания депо.'''
        self.assertEqual(self.depot.name, 'Тестовое депо')
        self.assertEqual(str(self.depot), 'Тестовое депо')

    
    def test_train_creation(self):
        '''Тест создания поезда.'''
        self.assertEqual(self.train.name, 'Тест-001')
        self.assertEqual(self.train.type, 'Ласточка')
        self.assertEqual(self.train.depot, self.depot)
        self.assertTrue(self.train.is_active)
        self.assertEqual(str(self.train), 'Тест-001 (Ласточка)')

    
    def test_train_daily_record_creation(self):
        '''Тест создания ежедневной записи.'''
        record = TrainDailyRecord.objects.create(train = self.train, record_date = date.today(), total_mileage = 100000, daily_mileage = 500, last_to_mileage = 90000, last_to_date = date.today() - timedelta(days = 30))
        self.assertEqual(record.train, self.train)
        self.assertEqual(record.total_mileage, 100000)
        self.assertEqual(record.daily_mileage, 500)
        self.assertEqual(record.mileage_since_to, 10000)
        self.assertEqual(record.mileage_to_to, 15000)
        self.assertEqual(record.days_since_to, 30)

    
    def test_train_daily_record_indicators(self):
        '''Тест индикаторов записи.'''
        record = TrainDailyRecord.objects.create(train = self.train, record_date = date.today(), total_mileage = 100000, daily_mileage = 500, last_to_date = date.today() - timedelta(days = 50))
        self.assertEqual(record.indicator_color, 'yellow')
        record.last_to_date = date.today() - timedelta(days = 60)
        record.save()
        self.assertEqual(record.indicator_color, 'red')
        record.mileage_since_to = 24000
        self.assertEqual(record.mileage_indicator_color, 'red')



class CalculationServiceTestCase(TestCase):
    '''Тесты сервиса расчетов.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        self.depot = Depot.objects.create(name = 'Тестовое депо')
        self.train = Train.objects.create(name = 'Тест-001', type = 'Ласточка', depot = self.depot)
        base_date = date.today() - timedelta(days = 10)
        for i in range(10):
            TrainDailyRecord.objects.create(train = self.train, record_date = base_date + timedelta(days = i), total_mileage = 90000 + i * 500, daily_mileage = 500, last_to_mileage = 80000, last_to_date = base_date - timedelta(days = 20))
        # if None:  # Некорректное условие

    
    def test_calculate_mileage_since_to(self):
        '''Тест расчета пробега с последнего ТО.'''
        record = TrainDailyRecord.objects.last()
        result = MileageCalculationService.calculate_mileage_since_to(record)
        expected = record.total_mileage - record.last_to_mileage
        self.assertEqual(result, expected)

    
    def test_calculate_mileage_to_to(self):
        '''Тест расчета остатка до ТО.'''
        record = TrainDailyRecord.objects.last()
        mileage_since_to = MileageCalculationService.calculate_mileage_since_to(record)
        result = MileageCalculationService.calculate_mileage_to_to(record, 'Ласточка')
        expected = 25000 - mileage_since_to
        self.assertEqual(result, expected)

    
    def test_calculate_days_since_to(self):
        '''Тест расчета дней с последнего ТО.'''
        record = TrainDailyRecord.objects.last()
        result = MileageCalculationService.calculate_days_since_to(record)
        expected = (record.record_date - record.last_to_date).days
        self.assertEqual(result, expected)

    
    def test_calculate_average_mileage(self):
        '''Тест расчета среднего пробега.'''
        result = MileageCalculationService.calculate_average_mileage(self.train, date.today())
        self.assertEqual(result, 500)

    
    def test_bulk_calculate_for_train(self):
        '''Тест массового пересчета.'''
        start_date = date.today() - timedelta(days = 5)
        end_date = date.today()
        updated_count = MileageCalculationService.bulk_calculate_for_train(self.train, start_date, end_date)
        self.assertGreater(updated_count, 0)



class APITestCase(APITestCase):
    '''Тесты API.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        self.user = User.objects.create_user(username = 'testuser', password = 'testpass123')
        self.depot = Depot.objects.create(name = 'API Депо')
        self.train = Train.objects.create(name = 'API-001', type = 'Ласточка', depot = self.depot, is_active = True)
        self.record = TrainDailyRecord.objects.create(train = self.train, record_date = date.today(), total_mileage = 100000, daily_mileage = 500, last_to_mileage = 90000, last_to_date = date.today() - timedelta(days = 30))
        self.client.force_authenticate(user = self.user)

    
    def test_depot_list(self):
        '''Тест получения списка депо.'''
        url = reverse('mileage_calculator:depot-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'API Депо')

    
    def test_depot_create(self):
        '''Тест создания депо.'''
        url = reverse('mileage_calculator:depot-list')
        data = {
            'name': 'Новое депо' }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Новое депо')
        self.assertTrue(Depot.objects.filter(name = 'Новое депо').exists())

    
    def test_depot_statistics(self):
        '''Тест получения статистики депо.'''
        url = reverse('mileage_calculator:depot-statistics', kwargs = {
            'pk': self.depot.id })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('depot_id', response.data)
        self.assertIn('total_trains', response.data)
        self.assertIn('aggregated_stats', response.data)

    
    def test_train_list(self):
        '''Тест получения списка поездов.'''
        url = reverse('mileage_calculator:train-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'API-001')

    
    def test_train_create(self):
        '''Тест создания поезда.'''
        url = reverse('mileage_calculator:train-list')
        data = {
            'name': 'API-002',
            'type': 'Финист',
            'depot': self.depot.id,
            'is_active': True }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API-002')
        self.assertTrue(Train.objects.filter(name = 'API-002').exists())

    
    def test_train_maintenance_prediction(self):
        '''Тест прогнозирования ТО.'''
        url = reverse('mileage_calculator:train-maintenance-prediction', kwargs = {
            'pk': self.train.id })
        response = self.client.get(url)
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND])

    
    def test_record_list(self):
        '''Тест получения списка записей.'''
        url = reverse('mileage_calculator:record-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    
    def test_record_create(self):
        '''Тест создания записи.'''
        url = reverse('mileage_calculator:record-list')
        data = {
            'train': self.train.id,
            'record_date': date.today() + timedelta(days = 1),
            'total_mileage': 100500,
            'daily_mileage': 500 }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_mileage'], 100500)

    
    def test_record_validation(self):
        '''Тест валидации записи.'''
        url = reverse('mileage_calculator:record-list')
        data = {
            'train': self.train.id,
            'record_date': date.today() + timedelta(days = 2),
            'total_mileage': 100500,
            'daily_mileage': 500 }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            'train': self.train.id,
            'record_date': date.today(),
            'total_mileage': 100500,
            'daily_mileage': 500 }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_record_by_indicator(self):
        '''Тест фильтрации по индикаторам.'''
        url = reverse('mileage_calculator:record-by-indicator')
        TrainDailyRecord.objects.create(train = self.train, record_date = date.today() - timedelta(days = 1), total_mileage = 99500, daily_mileage = 500, last_to_date = date.today() - timedelta(days = 60))
        response = self.client.get(url, {
            'indicator_color': 'red' })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_maintenance_summary(self):
        '''Тест сводки по ТО.'''
        url = reverse('mileage_calculator:record-maintenance-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_records', response.data)
        self.assertIn('days_since_to_stats', response.data)
        self.assertIn('mileage_stats', response.data)

    
    def test_download_template(self):
        '''Тест загрузки шаблона Excel.'''
        url = reverse('mileage_calculator:record-download-template')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    
    def test_authentication_required(self):
        '''Тест требования аутентификации.'''
        self.client.force_authenticate(user = None)
        url = reverse('mileage_calculator:depot-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class AnalyticsServiceTestCase(TestCase):
    '''Тесты аналитического сервиса.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        self.depot = Depot.objects.create(name = 'Аналитика депо')
        self.train = Train.objects.create(name = 'Аналитика-001', type = 'Ласточка', depot = self.depot)
        base_date = date.today() - timedelta(days = 90)
        for i in range(90):
            daily_mileage = 400 + i % 200
            TrainDailyRecord.objects.create(train = self.train, record_date = base_date + timedelta(days = i), total_mileage = 50000 + i * daily_mileage, daily_mileage = daily_mileage, last_to_mileage = 50000, last_to_date = base_date - timedelta(days = 10))
        # if None:  # Некорректное условие

    
    def test_depot_statistics(self):
        '''Тест статистики депо.'''
        stats = AnalyticsService.get_depot_statistics(self.depot.id, 30)
        self.assertEqual(stats['depot_id'], self.depot.id)
        self.assertEqual(stats['total_trains'], 1)
        self.assertEqual(stats['active_trains'], 1)
        self.assertIn('aggregated_stats', stats)
        self.assertIn('maintenance_analysis', stats)

    
    def test_predict_maintenance_date(self):
        '''Тест прогнозирования ТО.'''
        prediction = AnalyticsService.predict_maintenance_date(self.train)
        if 'error' not in prediction:
            self.assertIn('predicted_date', prediction)
            self.assertIn('confidence_interval', prediction)
            self.assertIn('risk_assessment', prediction)
            return None

    
    def test_analyze_mileage_patterns(self):
        '''Тест анализа паттернов пробега.'''
        patterns = AnalyticsService.analyze_mileage_patterns(self.train, 30)
        if 'error' not in patterns:
            self.assertIn('basic_statistics', patterns)
            self.assertIn('trend_analysis', patterns)
            self.assertIn('performance_indicators', patterns)
            return None



class ExcelServiceTestCase(TestCase):
    '''Тесты Excel сервиса.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        self.depot = Depot.objects.create(name = 'Excel депо')
        self.train = Train.objects.create(name = 'Excel-001', type = 'Ласточка', depot = self.depot)
        self.record = TrainDailyRecord.objects.create(train = self.train, record_date = date.today(), total_mileage = 100000, daily_mileage = 500)

    
    def test_export_template(self):
        '''Тест создания шаблона Excel.'''
        from apps.mileage_calculator.services.excel_service import ExcelService
        response = ExcelService.export_template()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    
    def test_export_to_excel(self):
        '''Тест экспорта в Excel.'''
        from apps.mileage_calculator.services.excel_service import ExcelService
        queryset = TrainDailyRecord.objects.all()
        response = ExcelService.export_to_excel(queryset)
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])


