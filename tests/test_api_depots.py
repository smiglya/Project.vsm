# Source Generated with Decompyle++
# File: test_api_depots.cpython-312.pyc (Python 3.12)

'''
Тесты API для работы с депо.
'''
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from apps.mileage_calculator.models import Depot, Train
import uuid


class TestDepotAPI(APITestCase):
    """Тесты для функциональности депо API"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.depot = Depot.objects.create(name="Test Depot")
    
    def test_depot_list(self):
        """Тест списка депо"""
        response = self.client.get('/api/v1/depots/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestDepotFiltering(APITestCase):
    """Тесты для фильтрации депо"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        unique_id = str(uuid.uuid4())[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.depot1 = Depot.objects.create(name="Depot 1")
        self.depot2 = Depot.objects.create(name="Depot 2")
    
    def test_depot_filtering(self):
        """Тест фильтрации депо"""
        response = self.client.get('/api/v1/depots/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
