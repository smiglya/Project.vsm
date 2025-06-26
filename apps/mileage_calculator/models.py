# Source Generated with Decompyle++
# File: models.cpython-312.pyc (Python 3.12)

'''
Модели для системы калькулятора пробега.
'''
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import date, timedelta

class Depot(models.Model):
    '''Модель депо.'''
    name = models.CharField(max_length = 255, unique = True, verbose_name = 'Название депо', help_text = 'Уникальное название депо')
    location = models.CharField(max_length = 255, null = True, blank = True, verbose_name = 'Местоположение', help_text = 'Город или регион расположения депо')
    contact_info = models.CharField(max_length = 255, null = True, blank = True, verbose_name = 'Контактная информация', help_text = 'Email или телефон для связи с депо')
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = 'Дата создания')
    updated_at = models.DateTimeField(auto_now = True, verbose_name = 'Дата обновления')
    
    class Meta:
        verbose_name = 'Депо'
        verbose_name_plural = 'Депо'
        db_table = 'mileage_calculator_depot'
        ordering = [
            'name']

    
    def __str__(self):
        return self.name



class Train(models.Model):
    '''Модель поезда.'''
    TRAIN_TYPES = [
        ('Ласточка', 'Ласточка'),
        ('Финист', 'Финист'),
        ('Сапсан', 'Сапсан')]
    name = models.CharField(max_length = 255, unique = True, verbose_name = 'Название поезда', help_text = 'Уникальное название поезда')
    type = models.CharField(max_length = 50, choices = TRAIN_TYPES, verbose_name = 'Тип поезда', help_text = 'Тип электропоезда')
    is_manual_mileage = models.BooleanField(default = False, verbose_name = 'Ручной ввод пробега', help_text = 'Флаг ручного ввода пробега (если пробег не приходит автоматически)')
    depot = models.ForeignKey(Depot, on_delete = models.CASCADE, related_name = 'trains', verbose_name = 'Депо', help_text = 'Депо приписки поезда')
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = 'Дата создания')
    updated_at = models.DateTimeField(auto_now = True, verbose_name = 'Дата обновления')
    is_active = models.BooleanField(default = True, verbose_name = 'Активен', help_text = 'Активен ли поезд в системе')
    
    class Meta:
        verbose_name = 'Поезд'
        verbose_name_plural = 'Поезда'
        db_table = 'mileage_calculator_train'
        ordering = [
            'name']
        indexes = [
            models.Index(fields = [
                'type']),
            models.Index(fields = [
                'depot']),
            models.Index(fields = [
                'is_manual_mileage'])]

    
    def __str__(self):
        return f'''{self.name} ({self.type})'''
    
    @property
    def latest_record(self):
        """Возвращает последнюю запись пробега для поезда."""
        return self.daily_records.order_by('-record_date').first()
    
    @property
    def latest_total_mileage(self):
        """Возвращает последний общий пробег поезда."""
        latest = self.latest_record
        return latest.total_mileage if latest else None
    
    @property
    def next_block_date(self):
        """Возвращает дату следующего блока для поезда."""
        latest = self.latest_record
        if latest and latest.last_block_date:
            return latest.last_block_date + timedelta(days=45)
        return None
    
    @property
    def next_kp_date(self):
        """Возвращает дату следующего КП для поезда."""
        latest = self.latest_record
        if latest and latest.last_kp_measure_date:
            return latest.last_kp_measure_date + timedelta(days=30)
        return None
    
    @property
    def days_since_last_to(self):
        """Возвращает количество дней с последнего ТО."""
        latest = self.latest_record
        if latest and latest.last_to_date:
            return (date.today() - latest.last_to_date).days
        return None



class TrainDailyRecord(models.Model):
    '''Модель ежедневной записи пробега поезда.'''
    
    TO_TYPES = [
        ('ТО-1', 'ТО-1'),
        ('ТО-2', 'ТО-2'),
        ('ТО-3', 'ТО-3'),
        ('I1', 'I1'),
        ('I2', 'I2'),
        ('I3', 'I3'),
        ('I4', 'I4'),
        ('I5', 'I5'),
        ('I6', 'I6'),
        ('R1', 'R1'),
        ('R2', 'R2'),
        ('R3', 'R3'),
        ('R4', 'R4'),
        ('ТО-L', 'ТО-L'),
        ('ТО-N', 'ТО-N'),
        ('IS510', 'IS510'),
        ('IS520', 'IS520'),
        ('IS530', 'IS530')]
    train = models.ForeignKey(Train, on_delete = models.CASCADE, related_name = 'daily_records', verbose_name = 'Поезд')
    record_date = models.DateField(verbose_name = 'Дата записи', help_text = 'Дата записи данных')
    total_mileage = models.BigIntegerField(validators = [
        MinValueValidator(0)], verbose_name = 'Общий пробег', help_text = 'Общий пробег поезда в километрах')
    daily_mileage = models.IntegerField(null=True, blank=True, validators = [
        MinValueValidator(0)], verbose_name = 'Дневной пробег', help_text = 'Дневной пробег в километрах')
    last_to_mileage = models.BigIntegerField(null = True, blank = True, validators = [
        MinValueValidator(0)], verbose_name = 'Пробег на момент последнего ТО', help_text = 'Километраж на момент последнего технического обслуживания')
    last_to_date = models.DateField(null = True, blank = True, verbose_name = 'Дата последнего ТО')
    last_to_type = models.CharField(max_length = 10, choices = TO_TYPES, null = True, blank = True, verbose_name = 'Вид последнего ТО')
    next_to_type = models.CharField(max_length = 10, choices = TO_TYPES, null = True, blank = True, verbose_name = 'Вид следующего ТО')
    planned_to_date = models.DateField(null = True, blank = True, verbose_name = 'Плановая дата ТО')
    last_block_date = models.DateField(null = True, blank = True, verbose_name = 'Дата последнего блока')
    last_kp_measure_date = models.DateField(null = True, blank = True, verbose_name = 'Дата последних измерений КП')
    last_kp_date = models.DateField(null = True, blank = True, verbose_name = 'Дата последнего БЗКП', help_text = 'Дата последнего безотцепочного замера колесных пар')
    inspection_counter = models.IntegerField(default = 0, validators = [
        MinValueValidator(0)], verbose_name = 'Счетчик инспекций')
    to_l_mileage = models.BigIntegerField(null = True, blank = True, validators = [
        MinValueValidator(0)], verbose_name = 'Пробег для ТО-L', help_text = 'Используется для поездов типа Сапсан')
    to_n_mileage = models.BigIntegerField(null = True, blank = True, validators = [
        MinValueValidator(0)], verbose_name = 'Пробег для ТО-N', help_text = 'Используется для поездов типа Сапсан')
    is510_mileage = models.BigIntegerField(null = True, blank = True, validators = [
        MinValueValidator(0)], verbose_name = 'Километраж IS510')
    is520_mileage = models.BigIntegerField(null = True, blank = True, validators = [
        MinValueValidator(0)], verbose_name = 'Километраж IS520')
    is530_mileage = models.BigIntegerField(null = True, blank = True, validators = [
        MinValueValidator(0)], verbose_name = 'Километраж IS530')
    mileage_since_to = models.BigIntegerField(null = True, blank = True, verbose_name = 'Пробег с последнего ТО', help_text = 'Автоматически рассчитываемое поле')
    mileage_to_to = models.BigIntegerField(null = True, blank = True, verbose_name = 'Пробег до следующего ТО', help_text = 'Автоматически рассчитываемое поле')
    days_since_to = models.IntegerField(null = True, blank = True, verbose_name = 'Дней с последнего ТО', help_text = 'Автоматически рассчитываемое поле')
    avg_mileage = models.FloatField(null = True, blank = True, verbose_name = 'Средний пробег', help_text = 'Средний пробег за 3 месяца')
    manual_indicator_train = models.BooleanField(default = False, verbose_name = 'Ручная индикация поезда', help_text = 'Поезд на контроле (была замена планового вида ремонта)')
    manual_indicator_next_to = models.BooleanField(default = False, verbose_name = 'Ручная индикация следующего ТО', help_text = 'Ручная индикация для инспекций I3.I4.I5.I6.R1.R2.R3.R4')
    indicator_color = models.CharField(max_length = 20, null = True, blank = True, verbose_name = 'Цветовой индикатор')
    mileage_indicator_color = models.CharField(max_length = 20, null = True, blank = True, verbose_name = 'Индикатор по пробегу')
    next_to_indicator_color = models.CharField(max_length = 20, null = True, blank = True, verbose_name = 'Индикатор следующего ТО')
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = 'Дата создания')
    updated_at = models.DateTimeField(auto_now = True, verbose_name = 'Дата обновления')
    
    class Meta:
        verbose_name = 'Ежедневная запись'
        verbose_name_plural = 'Ежедневные записи'
        db_table = 'mileage_calculator_traindailyrecord'
        ordering = [
            '-record_date',
            'train__name']
        constraints = [
            models.UniqueConstraint(fields = [
                'train',
                'record_date'], name = 'unique_train_record_date')]
        indexes = [
            models.Index(fields = [
                'record_date']),
            models.Index(fields = [
                'train',
                'record_date']),
            models.Index(fields = [
                'train',
                '-record_date']),
            models.Index(fields = [
                'last_to_date']),
            models.Index(fields = [
                'planned_to_date'])]

    
    def __str__(self):
        return f'''{self.train.name} - {self.record_date}'''

    @property
    def next_block_date(self):
        '''Дата следующего блока (45 дней после последнего).'''
        if self.last_block_date:
            return self.last_block_date + timedelta(days = 45)
        return None

    @property
    def next_kp_date(self):
        '''Дата следующего КП (30 дней после последнего).'''
        if self.last_kp_measure_date:
            return self.last_kp_measure_date + timedelta(days = 30)
        return None

    @property
    def days_since_last_to(self):
        '''Количество дней с последнего ТО.'''
        if self.last_to_date:
            return (self.record_date - self.last_to_date).days
        return None

    @property
    def average_mileage(self):
        '''Обратная совместимость для тестов.'''
        return self.avg_mileage

    def calculate_planned_to_date(self):
        '''Рассчитывает планируемую дату ТО по формуле.'''
        if self.mileage_since_to and self.avg_mileage and self.avg_mileage > 0:
            days_to_to = (28000 - self.mileage_since_to) / self.avg_mileage
            return self.record_date + timedelta(days = int(days_to_to))
        return None

    def save(self, *args, **kwargs):
        '''Переопределяем save для автоматических расчетов.'''
        # Импорт здесь для избежания циклических импортов
        from .services.calculation_service import MileageCalculationService
        
        # Базовые расчеты
        if self.train:
            train_type = self.train.type
            
            # Расчет пробега с последнего ТО
            if self.last_to_mileage and self.total_mileage:
                self.mileage_since_to = self.total_mileage - self.last_to_mileage
            
            # Расчет остатка до ТО
            if self.mileage_since_to is not None:
                if train_type == 'Сапсан':
                    self.mileage_to_to = max(0, 25000 - self.mileage_since_to)
                else:
                    self.mileage_to_to = max(0, 25000 - self.mileage_since_to)
            
            # Расчет дней с ТО
            if self.last_to_date:
                self.days_since_to = (self.record_date - self.last_to_date).days
            
            # Расчет цветовых индикаторов
            if self.days_since_to is not None:
                if self.days_since_to < 45:
                    self.indicator_color = 'green'
                elif 45 <= self.days_since_to <= 55:
                    self.indicator_color = 'yellow'
                else:
                    self.indicator_color = 'red'
            
            if self.mileage_since_to is not None:
                if self.mileage_since_to < 23000:
                    self.mileage_indicator_color = 'green'
                elif 23000 <= self.mileage_since_to < 25000:
                    self.mileage_indicator_color = 'yellow'
                else:
                    self.mileage_indicator_color = 'red'

        super().save(*args, **kwargs)

    if None:
        __classcell__ = None

