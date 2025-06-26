# Source Generated with Decompyle++
# File: test_calculation_formulas.cpython-312.pyc (Python 3.12)

'''
Тесты формул расчета согласно ТЗ.
Проверка всех 12 формул автоматического расчета для калькулятора пробега.
'''
import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from apps.mileage_calculator.models import Depot, Train, TrainDailyRecord
from apps.mileage_calculator.services.calculation_service import MileageCalculationService


@pytest.mark.django_db
class TestCalculationFormulas:
    """Тесты всех 12 формул расчета."""
    
    def test_formula_1_total_mileage_calculation(self, train):
        """Формула 1: Общий пробег = Предыдущий общий пробег + Суточный пробег."""
        # Создаем базовую запись
        base_record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today() - timedelta(days=1),
            total_mileage=100000,
            daily_mileage=500
        )
        
        # Создаем новую запись
        new_record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=100500,  # Должно быть 100000 + 500
            daily_mileage=500
        )
        
        calculated = MileageCalculationService.calculate_total_mileage(
            new_record, previous_total=100000, daily_mileage=500
        )
        assert calculated == 100500
    
    def test_formula_2_daily_mileage_calculation(self, train):
        """Формула 2: Суточный пробег = Общий пробег сегодня - Общий пробег вчера."""
        yesterday_record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today() - timedelta(days=1),
            total_mileage=100000,
            daily_mileage=500
        )
        
        today_record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=100500,
            daily_mileage=0  # Будет рассчитано
        )
        
        calculated = MileageCalculationService.calculate_daily_mileage(
            today_total=100500, yesterday_total=100000
        )
        assert calculated == 500
    
    def test_formula_3_mileage_since_to(self, train):
        """Формула 3: Пробег от ТО = Общий пробег - Километраж с последнего ТО."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=105000,
            daily_mileage=500,
            last_to_mileage=100000
        )
        
        calculated = MileageCalculationService.calculate_mileage_since_to(
            total_mileage=105000, last_to_mileage=100000
        )
        assert calculated == 5000
    
    def test_formula_4_mileage_to_to(self, train):
        """Формула 4: Остаток до ТО = Лимит километража - Пробег от ТО."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=105000,
            daily_mileage=500,
            last_to_mileage=100000
        )
        
        limit = 15000  # Лимит для Ласточки
        mileage_since_to = 5000
        
        calculated = MileageCalculationService.calculate_mileage_to_to(
            limit=limit, mileage_since_to=mileage_since_to
        )
        assert calculated == 10000
    
    def test_formula_5_days_since_to(self, train):
        """Формула 5: Дней с последнего ТО."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=10000,
            daily_mileage=100,
            last_to_date=date.today() - timedelta(days=30)
        )
        
        calculated = MileageCalculationService.calculate_days_since_to(
            current_date=date.today(),
            last_to_date=date.today() - timedelta(days=30)
        )
        assert calculated == 30
    
    def test_formula_6_average_mileage(self, train):
        """Формула 6: Средний пробег за 3 месяца."""
        # Создаем записи за 90 дней
        for i in range(90):
            TrainDailyRecord.objects.create(
                train=train,
                record_date=date.today() - timedelta(days=89-i),
                daily_mileage=500,
                total_mileage=100000 + i * 500
            )
        
        calculated = MileageCalculationService.calculate_average_mileage(train, days=90)
        assert calculated == 500  # Средний суточный пробег
    
    def test_formula_7_planned_to_date(self, train):
        """Формула 7: Планируемая дата ТО."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=105000,
            daily_mileage=500,
            last_to_mileage=100000,
            last_to_date=date.today() - timedelta(days=30)
        )
        
        avg_daily = 500
        remaining_mileage = 10000
        
        calculated = MileageCalculationService.calculate_planned_to_date(
            current_date=date.today(),
            avg_daily_mileage=avg_daily,
            remaining_mileage=remaining_mileage
        )
        expected_date = date.today() + timedelta(days=20)  # 10000 / 500 = 20 дней
        assert calculated == expected_date
    
    def test_formula_8_next_block_date(self, train):
        """Формула 8: Дата следующего БЛОК (45 дней)."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=10000,
            daily_mileage=100,
            last_block_date=date.today() - timedelta(days=10)
        )
        
        calculated = MileageCalculationService.calculate_next_block_date(
            last_block_date=date.today() - timedelta(days=10)
        )
        expected_date = date.today() - timedelta(days=10) + timedelta(days=45)
        assert calculated == expected_date
    
    def test_formula_9_next_kp_date(self, train):
        """Формула 9: Дата следующего БЗКП (30 дней)."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=10000,
            daily_mileage=100,
            last_kp_measure_date=date.today() - timedelta(days=15)
        )
        
        calculated = MileageCalculationService.calculate_next_kp_date(
            last_kp_date=date.today() - timedelta(days=15)
        )
        expected_date = date.today() - timedelta(days=15) + timedelta(days=30)
        assert calculated == expected_date
    
    def test_formula_10_sapsan_mileage_from_to_l(self, depot):
        """Формула 10: Пробег от ТО-L для Сапсан."""
        sapsan_train = Train.objects.create(
            name='SAPSAN-001',
            type='Сапсан',
            depot=depot,
            is_active=True
        )
        
        record = TrainDailyRecord.objects.create(
            train=sapsan_train,
            record_date=date.today(),
            total_mileage=85000,
            daily_mileage=200,
            to_l_mileage=80000
        )
        
        calculated = MileageCalculationService.calculate_sapsan_mileage_from_to_l(
            total_mileage=85000, to_l_mileage=80000
        )
        assert calculated == 5000
    
    def test_formula_11_sapsan_mileage_to_to_l(self, depot):
        """Формула 11: Остаток до ТО-L для Сапсан."""
        limit_l = 120000  # Лимит ТО-L для Сапсан
        mileage_from_to_l = 5000
        
        calculated = MileageCalculationService.calculate_sapsan_mileage_to_to_l(
            limit=limit_l, mileage_from_to_l=mileage_from_to_l
        )
        assert calculated == 115000
    
    def test_formula_12_sapsan_mileage_to_to_n(self, depot):
        """Формула 12: Остаток до ТО-N для Сапсан."""
        sapsan_train = Train.objects.create(
            name='SAPSAN-002',
            type='Сапсан',
            depot=depot,
            is_active=True
        )
        
        record = TrainDailyRecord.objects.create(
            train=sapsan_train,
            record_date=date.today(),
            total_mileage=85000,
            daily_mileage=200,
            to_n_mileage=80000
        )
        
        limit_n = 240000  # Лимит ТО-N для Сапсан
        mileage_from_to_n = 5000
        
        calculated = MileageCalculationService.calculate_sapsan_mileage_to_to_n(
            limit=limit_n, mileage_from_to_n=mileage_from_to_n
        )
        assert calculated == 235000


@pytest.mark.django_db
class TestColorIndicators:
    """Тесты цветовых индикаторов."""
    
    def test_green_indicator(self, train):
        """Тестирование зеленого индикатора (все в норме)."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=102000,
            daily_mileage=100,
            last_to_mileage=100000,  # Пробег от ТО = 2000
        )
        
        # Заполняем поля для расчета
        record.mileage_since_to = 2000
        record.days_since_to = 10
        color = MileageCalculationService.calculate_indicator_color(record)
        assert color == 'green'
    
    def test_yellow_indicator(self, train):
        """Тестирование желтого индикатора (предупреждение)."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=112000,
            last_to_mileage=100000,  # Пробег от ТО = 12000
            last_to_date=date.today() - timedelta(days=50)  # 50 дней назад = yellow
        )
        
        # Устанавливаем нужные поля для расчета
        record.mileage_since_to = 12000
        record.days_since_to = 50
        color = MileageCalculationService.calculate_indicator_color(record)
        assert color == 'yellow'
    
    def test_red_indicator(self, train):
        """Тестирование красного индикатора (превышение лимита)."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=116000,
            daily_mileage=100,
            last_to_mileage=100000,  # Пробег от ТО = 16000
            last_to_date=date.today() - timedelta(days=60)  # 60 дней назад = red
        )
        
        # Устанавливаем нужные поля для расчета
        record.mileage_since_to = 16000
        record.days_since_to = 60
        color = MileageCalculationService.calculate_indicator_color(record)
        assert color == 'red'


@pytest.mark.django_db 
class TestIntegrationCalculations:
    """Интеграционные тесты расчетов."""
    
    def test_complete_calculation_workflow(self, train):
        """Тестирование полного рабочего процесса расчетов."""
        # Создаем базовую запись
        base_record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today() - timedelta(days=1),
            total_mileage=100000,
            daily_mileage=500,
            last_to_mileage=95000,
            last_to_date=date.today() - timedelta(days=30)
        )
        
        # Создаем новую запись
        new_record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=100500,
            daily_mileage=500,
            last_to_mileage=95000,
            last_to_date=date.today() - timedelta(days=30)
        )
        
        # Запускаем полный расчет
        metrics = MileageCalculationService.calculate_all_metrics(new_record)
        
        # Проверяем основные метрики
        assert metrics is not None
        assert new_record.mileage_since_to == 5500  # 100500 - 95000
        assert new_record.days_since_to == 30
        assert new_record.indicator_color in ['green', 'yellow', 'red']
    
    def test_edge_cases(self, train):
        """Тестирование граничных случаев."""
        # Тест с нулевым пробегом
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=0,
            daily_mileage=0
        )
        
        # Расчет не должен падать
        metrics = MileageCalculationService.calculate_all_metrics(record)
        assert record.mileage_since_to is None or record.mileage_since_to >= 0
        
        # Тест с отрицательным суточным пробегом (ошибка данных)
        record2 = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today() + timedelta(days=1),
            total_mileage=100000,
            daily_mileage=-100  # Отрицательный пробег
        )
        
        # Система должна обработать корректно - проверяем что не падает
        metrics2 = MileageCalculationService.calculate_all_metrics(record2)
        # Отрицательный пробег может быть валидным в некоторых случаях (например, корректировки)
        assert record2.daily_mileage == -100  # Оставляем как есть


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
