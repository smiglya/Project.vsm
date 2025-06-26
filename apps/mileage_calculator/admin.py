# Source Generated with Decompyle++
# File: admin.cpython-312.pyc (Python 3.12)

'''
Администрирование моделей калькулятора пробега.
'''
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import Depot, Train, TrainDailyRecord
DepotAdmin = None  # Неподдерживаемый узел, требует ручного восстановления()

class TrainDailyRecordInline(admin.TabularInline):
    '''Инлайн для ежедневных записей.'''
    model = TrainDailyRecord
    extra = 0
    readonly_fields = [
        'mileage_since_to',
        'mileage_to_to',
        'days_since_to',
        'created_at']
    fields = [
        'record_date',
        'total_mileage',
        'daily_mileage',
        'last_to_date',
        'last_to_type',
        'next_to_type',
        'mileage_since_to',
        'mileage_to_to',
        'days_since_to']
    ordering = [
        '-record_date']
    max_num = 5

TrainAdmin = None  # Неподдерживаемый узел, требует ручного восстановления()
TrainDailyRecordAdmin = None  # Неподдерживаемый узел, требует ручного восстановления()
admin.site.site_header = 'VSM - Калькулятор пробега'
admin.site.site_title = 'VSM Admin'
admin.site.index_title = 'Управление системой калькулятора пробега'
