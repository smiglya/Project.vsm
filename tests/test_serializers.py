"""
Тесты сериализаторов VSM Калькулятора пробега.
"""
import pytest
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from datetime import date, timedelta
from io import BytesIO
from apps.mileage_calculator.models import Depot, Train, TrainDailyRecord
from apps.mileage_calculator.serializers import (
    DepotSerializer,
    TrainSerializer, 
    TrainDailyRecordSerializer,
    TrainDailyRecordDetailSerializer,
    TrainDailyRecordCreateSerializer,
    BulkRecalculateSerializer,
    ExcelImportSerializer,
    ExcelExportSerializer
)


@pytest.mark.django_db
class TestDepotSerializer:
    """Тесты сериализатора Depot."""
    
    def test_depot_serialization(self):
        """Тестирование сериализации депо."""
        depot = Depot.objects.create(name="Тестовое депо")
        
        # Создаем поезда для тестирования счетчиков
        Train.objects.create(name="Поезд 1", type="Ласточка", depot=depot, is_active=True)
        Train.objects.create(name="Поезд 2", type="Финист", depot=depot, is_active=False)
        
        serializer = DepotSerializer(depot)
        data = serializer.data
        
        assert data['id'] == depot.id
        assert data['name'] == "Тестовое депо"
        assert data['trains_count'] == 2
        assert data['active_trains_count'] == 1
    
    def test_depot_validation_empty_name(self):
        """Тестирование валидации пустого названия."""
        serializer = DepotSerializer(data={'name': ''})
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_depot_validation_long_name(self):
        """Тестирование валидации длинного названия."""
        long_name = "А" * 300
        serializer = DepotSerializer(data={'name': long_name})
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_depot_validation_whitespace_name(self):
        """Тестирование обрезки пробелов в названии."""
        serializer = DepotSerializer(data={'name': '  Депо с пробелами  '})
        assert serializer.is_valid()
        depot = serializer.save()
        assert depot.name == "Депо с пробелами"


@pytest.mark.django_db
class TestTrainSerializer:
    """Тесты сериализатора Train."""
    
    def test_train_serialization(self, depot):
        """Тестирование сериализации поезда."""
        train = Train.objects.create(
            name="ЭВС-001",
            type="Ласточка",
            depot=depot,
            is_active=True,
            is_manual_mileage=False
        )
        
        # Создаем записи для тестирования
        TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today() - timedelta(days=1),
            total_mileage=100000
        )
        TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=100500
        )
        
        serializer = TrainSerializer(train)
        data = serializer.data
        
        assert data['id'] == train.id
        assert data['name'] == "ЭВС-001"
        assert data['type'] == "Ласточка"
        assert data['depot_name'] == depot.name
        assert data['records_count'] == 2
        assert data['latest_total_mileage'] == 100500
        assert data['latest_record_date'] == date.today().isoformat()
    
    def test_train_validation_empty_name(self, depot):
        """Тестирование валидации пустого названия поезда."""
        serializer = TrainSerializer(data={
            'name': '',
            'type': 'Ласточка',
            'depot': depot.id
        })
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_train_validation_invalid_type(self, depot):
        """Тестирование валидации неверного типа поезда."""
        serializer = TrainSerializer(data={
            'name': 'Test Train',
            'type': 'Неизвестный тип',
            'depot': depot.id
        })
        assert not serializer.is_valid()
        assert 'type' in serializer.errors
    
    def test_train_serialization_no_records(self, depot):
        """Тестирование сериализации поезда без записей."""
        train = Train.objects.create(
            name="Новый поезд",
            type="Финист",
            depot=depot
        )
        
        serializer = TrainSerializer(train)
        data = serializer.data
        
        assert data['records_count'] == 0
        assert data['latest_total_mileage'] is None
        assert data['latest_record_date'] is None


@pytest.mark.django_db
class TestTrainDailyRecordSerializer:
    """Тесты сериализатора TrainDailyRecord."""
    
    def test_record_serialization(self, train):
        """Тестирование сериализации записи."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=105000,
            daily_mileage=500,
            last_to_mileage=100000,
            last_to_date=date.today() - timedelta(days=30)
        )
        
        serializer = TrainDailyRecordSerializer(record)
        data = serializer.data
        
        assert data['id'] == record.id
        assert data['train'] == train.id
        assert data['train_name'] == train.name
        assert data['train_type'] == train.type
        assert data['depot_name'] == train.depot.name
        assert data['total_mileage'] == 105000
        assert data['daily_mileage'] == 500
    
    def test_record_validation_future_date(self, train):
        """Тестирование валидации будущей даты."""
        future_date = date.today() + timedelta(days=1)
        serializer = TrainDailyRecordSerializer(data={
            'train': train.id,
            'record_date': future_date,
            'total_mileage': 100000
        })
        assert not serializer.is_valid()
        assert 'record_date' in serializer.errors
    
    def test_record_validation_negative_mileage(self, train):
        """Тестирование валидации отрицательного пробега."""
        serializer = TrainDailyRecordSerializer(data={
            'train': train.id,
            'record_date': date.today(),
            'total_mileage': -1000
        })
        assert not serializer.is_valid()
        assert 'total_mileage' in serializer.errors
    
    def test_record_validation_duplicate(self, train):
        """Тестирование валидации дублирующих записей."""
        # Создаем первую запись
        TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=100000
        )
        
        # Пытаемся создать дубликат
        serializer = TrainDailyRecordSerializer(data={
            'train': train.id,
            'record_date': date.today(),
            'total_mileage': 100500
        })
        assert not serializer.is_valid()
        assert 'record_date' in serializer.errors


@pytest.mark.django_db
class TestTrainDailyRecordCreateSerializer:
    """Тесты сериализатора создания записей."""
    
    def test_create_record_with_calculations(self, train):
        """Тестирование создания записи с автоматическими расчетами."""
        serializer = TrainDailyRecordCreateSerializer(data={
            'train': train.id,
            'record_date': date.today(),
            'total_mileage': 105000,
            'daily_mileage': 500,
            'last_to_mileage': 100000,
            'last_to_date': date.today() - timedelta(days=30)
        })
        
        assert serializer.is_valid()
        record = serializer.save()
        
        # Проверяем автоматические расчеты
        record.refresh_from_db()
        assert record.mileage_since_to == 5000
        assert record.days_since_to == 30
        assert record.indicator_color in ['green', 'yellow', 'red']


@pytest.mark.django_db
class TestTrainDailyRecordDetailSerializer:
    """Тесты детального сериализатора записей."""
    
    def test_detailed_serialization_with_metrics(self, train):
        """Тестирование детальной сериализации с метриками."""
        record = TrainDailyRecord.objects.create(
            train=train,
            record_date=date.today(),
            total_mileage=105000,
            last_to_mileage=100000
        )
        
        serializer = TrainDailyRecordDetailSerializer(record)
        data = serializer.data
        
        assert 'metrics' in data
        assert 'analytics' in data
        assert data['metrics'] is not None
        assert data['analytics'] is not None


@pytest.mark.django_db  
class TestBulkRecalculateSerializer:
    """Тесты сериализатора массового пересчета."""
    
    def test_valid_bulk_recalculate_data(self):
        """Тестирование валидных данных для массового пересчета."""
        data = {
            'train_ids': [1, 2, 3],
            'start_date': date.today() - timedelta(days=30),
            'end_date': date.today()
        }
        
        serializer = BulkRecalculateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_invalid_date_range(self):
        """Тестирование неверного диапазона дат."""
        data = {
            'start_date': date.today(),
            'end_date': date.today() - timedelta(days=30)
        }
        
        serializer = BulkRecalculateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
    
    def test_optional_fields(self):
        """Тестирование опциональных полей."""
        serializer = BulkRecalculateSerializer(data={})
        assert serializer.is_valid()


@pytest.mark.django_db
class TestExcelImportSerializer:
    """Тесты сериализатора импорта Excel."""
    
    def test_valid_excel_file(self):
        """Тестирование валидного Excel файла."""
        # Создаем mock файл
        file_content = b"fake excel content"
        file_obj = BytesIO(file_content)
        file_obj.name = "test.xlsx"
        file_obj.size = len(file_content)
        
        data = {
            'file': file_obj,
            'sheet_name': 'Sheet1',
            'skip_rows': 0,
            'update_existing': False
        }
        
        serializer = ExcelImportSerializer(data=data)
        assert serializer.is_valid()
    
    def test_invalid_file_extension(self):
        """Тестирование неверного расширения файла."""
        file_content = b"not excel content"
        file_obj = BytesIO(file_content)
        file_obj.name = "test.txt"
        file_obj.size = len(file_content)
        
        data = {'file': file_obj}
        
        serializer = ExcelImportSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file' in serializer.errors
    
    def test_file_size_validation(self):
        """Тестирование валидации размера файла."""
        # Создаем слишком большой файл
        large_content = b"x" * (11 * 1024 * 1024)  # 11 MB
        file_obj = BytesIO(large_content)
        file_obj.name = "large.xlsx"
        file_obj.size = len(large_content)
        
        data = {'file': file_obj}
        
        serializer = ExcelImportSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file' in serializer.errors


@pytest.mark.django_db
class TestExcelExportSerializer:
    """Тесты сериализатора экспорта Excel."""
    
    def test_valid_export_data(self):
        """Тестирование валидных данных для экспорта."""
        data = {
            'train_ids': [1, 2, 3],
            'depot_ids': [1],
            'start_date': date.today() - timedelta(days=30),
            'end_date': date.today(),
            'include_calculations': True,
            'format': 'xlsx'
        }
        
        serializer = ExcelExportSerializer(data=data)
        assert serializer.is_valid()
    
    def test_default_values(self):
        """Тестирование значений по умолчанию."""
        serializer = ExcelExportSerializer(data={})
        assert serializer.is_valid()
        
        validated_data = serializer.validated_data
        assert validated_data['include_calculations'] is True
        assert validated_data['format'] == 'xlsx'
    
    def test_format_choices(self):
        """Тестирование выбора формата."""
        # Тест валидного формата
        for format_choice in ['xlsx', 'xls']:
            serializer = ExcelExportSerializer(data={'format': format_choice})
            assert serializer.is_valid()
        
        # Тест неверного формата
        serializer = ExcelExportSerializer(data={'format': 'csv'})
        assert not serializer.is_valid()
        assert 'format' in serializer.errors


@pytest.mark.django_db
class TestSerializerPerformance:
    """Тесты производительности сериализаторов."""
    
    def test_bulk_serialization_performance(self, depot):
        """Тестирование производительности массовой сериализации."""
        # Создаем множество записей
        train = Train.objects.create(
            name="Performance Test Train",
            type="Ласточка",
            depot=depot
        )
        
        records = []
        for i in range(100):
            record = TrainDailyRecord.objects.create(
                train=train,
                record_date=date.today() - timedelta(days=i),
                total_mileage=100000 + i * 500
            )
            records.append(record)
        
        # Тестируем массовую сериализацию
        serializer = TrainDailyRecordSerializer(records, many=True)
        data = serializer.data
        
        assert len(data) == 100
        assert all('id' in item for item in data)


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 