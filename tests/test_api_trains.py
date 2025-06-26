# Source Generated with Decompyle++
# File: test_api_trains.cpython-312.pyc (Python 3.12)

'''
Тесты API для работы с поездами.
'''
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from apps.mileage_calculator.models import Depot, Train
import uuid


class TestTrainAPI(APITestCase):
    """Тесты для функциональности поездов API"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.depot = Depot.objects.create(name="Test Depot")
        self.train = Train.objects.create(
            name="Test Train",
            type="Ласточка",
            depot=self.depot,
            is_active=True
        )
    
    def test_train_list(self):
        """Тест списка поездов"""
        response = self.client.get('/api/v1/trains/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTrainFiltering(APITestCase):
    """Тесты для фильтрации поездов"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.depot = Depot.objects.create(name="Test Depot")
        self.train1 = Train.objects.create(
            name="Train 1",
            type="Ласточка",
            depot=self.depot,
            is_active=True
        )
        self.train2 = Train.objects.create(
            name="Train 2",
            type="Сапсан",
            depot=self.depot,
            is_active=True
        )
    
    def test_train_filtering(self):
        """Тест фильтрации поездов"""
        response = self.client.get('/api/v1/trains/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
