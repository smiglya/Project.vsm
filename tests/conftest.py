# Source Generated with Decompyle++
# File: conftest.cpython-312-pytest-7.4.4.pyc (Python 3.12)

'''
Конфигурация pytest для автоматизированных тестов API.
'''
import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    django.setup()

import pytest
import uuid
import time
from datetime import date, timedelta
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.db import transaction
from apps.mileage_calculator.models import Depot, Train, TrainDailyRecord


@pytest.fixture
def clean_db():
    """Очистка базы данных для тестов."""
    with transaction.atomic():
        TrainDailyRecord.objects.all().delete()
        Train.objects.all().delete()
        Depot.objects.all().delete()
        User.objects.all().delete()


@pytest.fixture
def api_client():
    """API клиент для тестов."""
    return APIClient()


@pytest.fixture
def user():
    """Создание тестового пользователя."""
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time() * 1000)
    username = f'testuser_{unique_id}_{timestamp}'
    email = f'test_{unique_id}_{timestamp}@test.com'
    return User.objects.create_user(
        username=username,
        password='testpass123',
        email=email
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Аутентифицированный API клиент."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def depot():
    """Создание тестового депо."""
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time() * 1000)
    name = f'Test Depot {unique_id} {timestamp}'
    return Depot.objects.create(name=name)


@pytest.fixture
def train(depot):
    """Создание тестового поезда."""
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time() * 1000)
    name = f'TEST-{unique_id}-{timestamp}'
    return Train.objects.create(
        name=name,
        type='Ласточка',
        depot=depot,
        is_active=True,
        is_manual_mileage=False
    )


@pytest.fixture
def train_manual(depot):
    """Создание тестового поезда с ручным управлением."""
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time() * 1000)
    name = f'MANUAL-{unique_id}-{timestamp}'
    return Train.objects.create(
        name=name,
        type='Сапсан',
        depot=depot,
        is_active=True,
        is_manual_mileage=True
    )


@pytest.fixture
def daily_records(train):
    """Создание набора ежедневных записей."""
    records = []
    base_date = date.today() - timedelta(days=10)
    
    for i in range(10):
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=base_date + timedelta(days=i),
            total_mileage=100000 + i * 500,
            daily_mileage=500,
            last_to_mileage=90000,
            last_to_date=base_date - timedelta(days=20)
        )
        records.append(record)
    
    return records


@pytest.fixture
def sample_excel_data():
    """Тестовые данные для Excel операций."""
    return [
        {
            'train_name': 'TEST-001',
            'record_date': date.today().strftime('%Y-%m-%d'),
            'total_mileage': 100000,
            'daily_mileage': 500,
            'last_to_mileage': 90000,
            'last_to_date': (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        },
        {
            'train_name': 'TEST-001',
            'record_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'total_mileage': 100500,
            'daily_mileage': 500,
            'last_to_mileage': 90000,
            'last_to_date': (date.today() - timedelta(days=29)).strftime('%Y-%m-%d')
        }
    ]
