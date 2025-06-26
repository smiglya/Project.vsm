"""
Сервис для работы с Excel файлами.
Импорт и экспорт данных калькулятора пробега.
"""
import pandas as pd
import io
from typing import Dict, Any
from django.http import HttpResponse
from django.db import transaction
from django.core.exceptions import ValidationError
import logging
from apps.mileage_calculator.models import Train, TrainDailyRecord

logger = logging.getLogger(__name__)


class ExcelService:
    """Сервис для работы с Excel файлами."""
    
    # Маппинг колонок для импорта
    IMPORT_COLUMNS_MAPPING = {
        'Поезд': 'train_name',
        'Дата': 'record_date',
        'Общий пробег': 'total_mileage',
        'Суточный пробег': 'daily_mileage',
        'Пробег последнего ТО': 'last_to_mileage',
        'Дата последнего ТО': 'last_to_date',
        'Вид последнего ТО': 'last_to_type',
        'Вид следующего ТО': 'next_to_type',
        'Дата последнего БЛОК': 'last_block_date',
        'Дата последнего БЗКП': 'last_kp_measure_date',
        'Счетчик инспекций': 'inspection_counter',
        'Пробег ТО-L': 'to_l_mileage',
        'Пробег ТО-N': 'to_n_mileage',
        'Километраж IS510': 'is510_mileage',
        'Километраж IS520': 'is520_mileage',
        'Километраж IS530': 'is530_mileage',
        'Ручная индикация поезда': 'manual_indicator_train',
        'Ручная индикация ТО': 'manual_indicator_next_to'
    }
    
    # Колонки для экспорта
    EXPORT_COLUMNS = [
        ('train__name', 'Поезд'),
        ('train__type', 'Тип поезда'),
        ('train__depot__name', 'Депо'),
        ('record_date', 'Дата'),
        ('total_mileage', 'Общий пробег'),
        ('daily_mileage', 'Суточный пробег'),
        ('last_to_mileage', 'Пробег последнего ТО'),
        ('last_to_date', 'Дата последнего ТО'),
        ('last_to_type', 'Вид последнего ТО'),
        ('next_to_type', 'Вид следующего ТО'),
        ('planned_to_date', 'Плановая дата ТО'),
        ('last_block_date', 'Дата последнего БЛОК'),
        ('last_kp_measure_date', 'Дата последнего БЗКП'),
        ('inspection_counter', 'Счетчик инспекций'),
        ('mileage_since_to', 'Пробег с последнего ТО'),
        ('mileage_to_to', 'Остаток до ТО'),
        ('days_since_to', 'Дней с последнего ТО'),
        ('avg_mileage', 'Средний пробег'),
        ('to_l_mileage', 'Пробег ТО-L'),
        ('to_n_mileage', 'Пробег ТО-N'),
        ('is510_mileage', 'Километраж IS510'),
        ('is520_mileage', 'Километраж IS520'),
        ('is530_mileage', 'Километраж IS530'),
        ('manual_indicator_train', 'Ручная индикация поезда'),
        ('manual_indicator_next_to', 'Ручная индикация ТО')
    ]

    @classmethod
    def export_to_excel(cls, queryset, filename='vsm_data.xlsx'):
        """Экспорт данных в Excel файл."""
        try:
            # Простой экспорт без сложной логики
            data = list(queryset.values(
                'train__name',
                'record_date', 
                'total_mileage',
                'daily_mileage'
            ))
            
            df = pd.DataFrame(data)
            
            # Создаем HTTP ответ
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # Записываем в буфер
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Данные VSM', index=False)
            
            response.write(buffer.getvalue())
            return response
            
        except Exception as e:
            logger.error(f'Ошибка экспорта в Excel: {e}')
            raise

    @classmethod 
    def import_from_excel(cls, file, sheet_name='Sheet1', skip_rows=0, update_existing=False):
        """
        Импорт данных из Excel файла.
        
        Args:
            file: Файл для импорта
            sheet_name: Имя листа
            skip_rows: Количество строк для пропуска
            update_existing: Обновлять ли существующие записи
            
        Returns:
            Dict с результатами импорта
        """
        try:
            # Читаем Excel файл
            df = pd.read_excel(
                file, 
                sheet_name=sheet_name, 
                skiprows=skip_rows,
                na_values=['', 'N/A', 'NULL', 'null', '-']
            )
            
            logger.info(f'Прочитано {len(df)} строк из Excel файла')
            
            # Проверяем обязательные колонки
            required_columns = ['Поезд', 'Дата', 'Общий пробег', 'Суточный пробег']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValidationError(f'Отсутствуют обязательные колонки: {missing_columns}')
            
            # Маппинг колонок
            column_mapping = {}
            for excel_col, model_field in cls.IMPORT_COLUMNS_MAPPING.items():
                if excel_col in df.columns:
                    column_mapping[excel_col] = model_field
                    
            df = df.rename(columns=column_mapping)
            
            # Очищаем данные
            df = cls._clean_import_data(df)
            
            # Импортируем записи
            results = cls._import_records(df, update_existing)
            
            logger.info(f'Импорт завершен: создано {results["created"]}, обновлено {results["updated"]}')
            return results
            
        except Exception as e:
            logger.error(f'Ошибка импорта из Excel: {e}')
            raise

    @classmethod
    def _format_dataframe(cls, df):
        """Форматирование DataFrame для экспорта."""
        # Форматируем даты
        date_columns = [
            'Дата', 'Дата последнего ТО', 'Плановая дата ТО',
            'Дата последнего БЛОК', 'Дата последнего БЗКП'
        ]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
        
        # Форматируем числовые колонки
        numeric_columns = [
            'Общий пробег', 'Суточный пробег', 'Пробег последнего ТО',
            'Пробег с последнего ТО', 'Остаток до ТО', 'Дней с последнего ТО'
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Заполняем пустые значения
        df.fillna('', inplace=True)

    @classmethod
    def _format_excel_sheet(cls, worksheet, df):
        """Форматирование Excel листа."""
        try:
            from openpyxl.styles import Font, PatternFill, Alignment
            
            # Стиль заголовков
            header_font = Font(bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            
            # Применяем стиль к заголовкам
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center')
            
            # Автоширина колонок
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
        except ImportError:
            # Если openpyxl не доступен, пропускаем форматирование
            pass
        except Exception as e:
            logger.warning(f'Ошибка форматирования Excel листа: {e}')

    @classmethod
    def _clean_import_data(cls, df):
        """Очистка данных для импорта."""
        # Удаляем пустые строки
        df = df.dropna(how='all')
        
        # Форматируем даты
        date_fields = ['record_date', 'last_to_date', 'last_block_date', 'last_kp_measure_date']
        for field in date_fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], errors='coerce').dt.date
        
        # Форматируем числовые поля
        numeric_fields = [
            'total_mileage', 'daily_mileage', 'last_to_mileage', 'inspection_counter',
            'to_l_mileage', 'to_n_mileage', 'is510_mileage', 'is520_mileage', 'is530_mileage'
        ]
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
                df[field] = df[field].clip(lower=0)  # Убираем отрицательные значения
        
        # Форматируем булевые поля
        boolean_fields = ['manual_indicator_train', 'manual_indicator_next_to']
        for field in boolean_fields:
            if field in df.columns:
                df[field] = df[field].astype(bool, errors='ignore')
        
        return df

    @classmethod
    def _import_records(cls, df, update_existing=False):
        """Импорт записей в базу данных."""
        created_count = 0
        updated_count = 0
        errors = []
        
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    train_name = row.get('train_name')
                    if not train_name:
                        errors.append(f'Строка {index + 1}: отсутствует название поезда')
                        continue
                    
                    try:
                        train = Train.objects.get(name=train_name)
                    except Train.DoesNotExist:
                        errors.append(f'Строка {index + 1}: поезд "{train_name}" не найден')
                        continue
                    
                    record_date = row.get('record_date')
                    if pd.isna(record_date):
                        errors.append(f'Строка {index + 1}: отсутствует дата записи')
                        continue
                    
                    # Подготавливаем данные записи
                    record_data = {'train': train, 'record_date': record_date}
                    
                    # Маппинг полей с типами
                    field_mapping = {
                        'total_mileage': int,
                        'daily_mileage': int,
                        'last_to_mileage': int,
                        'last_to_date': None,  # уже обработано
                        'last_to_type': str,
                        'next_to_type': str,
                        'last_block_date': None,  # уже обработано
                        'last_kp_measure_date': None,  # уже обработано
                        'inspection_counter': int,
                        'to_l_mileage': int,
                        'to_n_mileage': int,
                        'is510_mileage': int,
                        'is520_mileage': int,
                        'is530_mileage': int,
                        'manual_indicator_train': bool,
                        'manual_indicator_next_to': bool
                    }
                    
                    for field, type_converter in field_mapping.items():
                        value = row.get(field)
                        if pd.notna(value):
                            if type_converter:
                                value = type_converter(value)
                            record_data[field] = value
                    
                    # Проверяем существование записи
                    existing_record = TrainDailyRecord.objects.filter(
                        train=train, record_date=record_date
                    ).first()
                    
                    if existing_record:
                        if update_existing:
                            for field, value in record_data.items():
                                if field not in ['train', 'record_date']:
                                    setattr(existing_record, field, value)
                            existing_record.save()
                            updated_count += 1
                        else:
                            errors.append(
                                f'Строка {index + 1}: запись для поезда "{train_name}" '
                                f'на {record_date} уже существует'
                            )
                    else:
                        TrainDailyRecord.objects.create(**record_data)
                        created_count += 1
                        
                except (ValueError, TypeError) as e:
                    errors.append(f'Строка {index + 1}: ошибка данных - {str(e)}')
                    continue
                except Exception as e:
                    errors.append(f'Строка {index + 1}: ошибка импорта - {str(e)}')
                    continue
        
        return {
            'created': created_count,
            'updated': updated_count,
            'errors': errors,
            'total_processed': len(df)
        }

    @classmethod
    def export_template(cls):
        """Экспорт шаблона Excel для импорта."""
        template_data = {
            'Поезд': ['Ласточка-001', 'Финист-002'],
            'Дата': ['2024-01-01', '2024-01-01'],
            'Общий пробег': [150000, 120000],
            'Суточный пробег': [500, 400]
        }
        
        df = pd.DataFrame(template_data)
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="vsm_template.xlsx"'
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Шаблон импорта', index=False)
        
        response.write(buffer.getvalue())
        return response 