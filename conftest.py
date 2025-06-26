"""
Конфигурация pytest для всего проекта
"""
import os
import django
from django.conf import settings
from django.test.utils import get_runner

# Устанавливаем настройки для тестов
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')

def pytest_configure():
    """Настройка Django для pytest"""
    django.setup() 