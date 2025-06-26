"""
Конфигурация приложения калькулятора пробега.
"""
from django.apps import AppConfig


class MileageCalculatorConfig(AppConfig):
    """Конфигурация приложения калькулятора пробега."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mileage_calculator'
    verbose_name = 'VSM Калькулятор пробега' 