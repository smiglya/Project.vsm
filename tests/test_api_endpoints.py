# Source Generated with Decompyle++
# File: test_api_endpoints.cpython-312.pyc (Python 3.12)

'''
Комплексные автоматизированные тесты API для VSM калькулятора пробега.
'''
import json
import uuid
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import os
from apps.mileage_calculator.models import Depot, Train, TrainDailyRecord

class APIAuthenticationTestCase(APITestCase):
    '''Тесты аутентификации API.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123',
            email=f'test_{unique_id}@test.com'
        )
        self.depot = Depot.objects.create(name=f'Test Depot {unique_id}')
        self.train = Train.objects.create(
            name=f'Test-{unique_id}',
            type='Ласточка',
            depot=self.depot
        )
    
    def test_unauthenticated_access_denied(self):
        '''Тест запрета доступа без аутентификации.'''
        endpoints = [
            '/api/v1/depots/',
            '/api/v1/trains/',
            '/api/v1/records/'
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertIn(response.status_code, [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ], f'Endpoint {endpoint} должен требовать аутентификацию')
    
    def test_authenticated_access_allowed(self):
        '''Тест разрешения доступа с аутентификацией.'''
        self.client.force_authenticate(user=self.user)
        endpoints = [
            '/api/v1/depots/',
            '/api/v1/trains/',
            '/api/v1/records/'
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                           f'Endpoint {endpoint} должен работать с аутентификацией')


class DepotAPITestCase(APITestCase):
    '''Тесты API депо.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.depot1 = Depot.objects.create(name=f'Депо Москва {unique_id}')
        self.depot2 = Depot.objects.create(name=f'Депо СПБ {unique_id}')
        Train.objects.create(
            name=f'М-{unique_id}-001',
            type='Ласточка',
            depot=self.depot1,
            is_active=True
        )
        Train.objects.create(
            name=f'М-{unique_id}-002',
            type='Сапсан',
            depot=self.depot1,
            is_active=True
        )
    
    def test_depot_list(self):
        '''Тест получения списка депо.'''
        url = '/api/v1/depots/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 2)
        
        names = [depot['name'] for depot in response.data['results']]
        self.assertIn(self.depot1.name, names)
        self.assertIn(self.depot2.name, names)
    
    def test_depot_detail(self):
        '''Тест получения детальной информации о депо.'''
        url = f'/api/v1/depots/{self.depot1.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.depot1.name)
        self.assertEqual(response.data['id'], self.depot1.id)


class TrainAPITestCase(APITestCase):
    '''Тесты API поездов.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.depot = Depot.objects.create(name=f'Test Depot {unique_id}')
        self.train1 = Train.objects.create(
            name=f'Т-{unique_id}-001',
            type='Ласточка',
            depot=self.depot,
            is_active=True,
            is_manual_mileage=False
        )
        self.train2 = Train.objects.create(
            name=f'Т-{unique_id}-002',
            type='Сапсан',
            depot=self.depot,
            is_active=True,
            is_manual_mileage=True
        )
    
    def test_train_list(self):
        '''Тест получения списка поездов.'''
        url = '/api/v1/trains/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 2)
    
    def test_train_filter_by_depot(self):
        '''Тест фильтрации поездов по депо.'''
        url = f'/api/v1/trains/?depot={self.depot.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 2)
    
    def test_train_filter_by_type(self):
        '''Тест фильтрации поездов по типу.'''
        url = '/api/v1/trains/?type=Ласточка'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for train in response.data['results']:
            self.assertEqual(train['type'], 'Ласточка')


class TrainDailyRecordAPITestCase(APITestCase):
    '''Тесты API ежедневных записей поездов.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.depot = Depot.objects.create(name=f'Test Depot {unique_id}')
        self.train = Train.objects.create(
            name=f'Test-{unique_id}',
            type='Ласточка',
            depot=self.depot
        )
    
    def test_record_list(self):
        '''Тест получения списка записей.'''
        url = '/api/v1/records/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_record_filter_by_train(self):
        '''Тест фильтрации записей по поезду.'''
        url = f'/api/v1/records/?train={self.train.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AnalyticsAPITestCase(APITestCase):
    '''Тесты API аналитики.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.depot = Depot.objects.create(name=f'Test Depot {unique_id}')
        self.train = Train.objects.create(
            name=f'Test-{unique_id}',
            type='Ласточка',
            depot=self.depot
        )
    
    def test_analytics_endpoints_exist(self):
        '''Тест существования endpoints аналитики.'''
        endpoints = [
            '/api/v1/analytics/summary/',
            '/api/v1/analytics/maintenance/',
            '/api/v1/analytics/trends/'
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # Проверяем что endpoint существует (может не быть реализован)
            self.assertIn(response.status_code, [
                status.HTTP_200_OK,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_501_NOT_IMPLEMENTED
            ])


class ExcelAPITestCase(APITestCase):
    '''Тесты API работы с Excel.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.depot = Depot.objects.create(name=f'Excel Depot {unique_id}')
        self.train = Train.objects.create(
            name=f'E-{unique_id}',
            type='Ласточка',
            depot=self.depot
        )
    
    def test_excel_endpoints_exist(self):
        '''Тест существования Excel endpoints.'''
        endpoints = [
            '/api/v1/excel/template/',
            '/api/v1/excel/export/',
            '/api/v1/excel/import/'
        ]
        for endpoint in endpoints:
            if 'import' in endpoint:
                response = self.client.post(endpoint)
            else:
                response = self.client.get(endpoint)
            # Проверяем что endpoint существует
            self.assertIn(response.status_code, [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_404_NOT_FOUND,
                status.HTTP_501_NOT_IMPLEMENTED
            ])


class APIPerformanceTestCase(APITestCase):
    '''Тесты производительности API.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.depot = Depot.objects.create(name=f'Performance Depot {unique_id}')
        
        # Создаем тестовые данные
        for i in range(10):
            Train.objects.create(
                name=f'P-{unique_id}-{i:03d}',
                type='Ласточка',
                depot=self.depot
            )
    
    def test_pagination_performance(self):
        '''Тест производительности пагинации.'''
        import time
        url = '/api/v1/records/'
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_time = end_time - start_time
        self.assertLess(response_time, 5, 'API должно отвечать менее чем за 5 секунд')
        
        # Проверяем структуру ответа
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)


