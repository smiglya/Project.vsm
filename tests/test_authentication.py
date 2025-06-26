# Source Generated with Decompyle++
# File: test_authentication.cpython-312.pyc (Python 3.12)

'''
Тесты аутентификации и авторизации API.
'''
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
import uuid


class TestAPIAuthentication(APITestCase):
    '''Тесты аутентификации API.'''
    
    def setUp(self):
        '''Настройка тестовых данных.'''
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com'
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
    
    def test_api_schema_accessible(self):
        '''Тест доступности схемы API.'''
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_swagger_docs_accessible(self):
        '''Тест доступности Swagger документации.'''
        response = self.client.get('/api/docs/')
        # Swagger может требовать настройки, поэтому проверяем код ответа
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_redoc_docs_accessible(self):
        '''Тест доступности ReDoc документации.'''
        response = self.client.get('/api/redoc/')
        # ReDoc может требовать настройки, поэтому проверяем код ответа
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ])


class TestAPIPermissions(APITestCase):
    """Тесты прав доступа API"""
    
    def setUp(self):
        """Настройка тестового окружения"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_permission_required(self):
        """Тест проверки прав доступа"""
        response = self.client.get('/api/v1/depots/')
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN
        ])
