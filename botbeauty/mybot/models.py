from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Q
from django.core.exceptions import ValidationError
import datetime


class Client(models.Model):
    '''Клиент'''
    id_tg = models.UUIDField(
        'id в телеграмм',
        blank=True,
        null=True,
        unique=True
    )
    full_name = models.CharField(
        'ФИО',
        max_length=200
    )
    phone_number = PhoneNumberField(
        'Номер телефона',
        null=True,
        unique=True,
        region='RU'
    )

    def __str__(self) -> str:
        return self.full_name


class Service(models.Model):
    '''Услуга'''
    title = models.CharField('Название услуги', max_length=200)
    price = models.FloatField('Цена услуги')

    def __str__(self) -> str:
        return self.title


class Specialist(models.Model):
    '''Специалист'''
    full_name = models.CharField('ФИО', max_length=200)
    services = models.ManyToManyField(Service, verbose_name='Услуги')

    def __str__(self) -> str:
        return self.full_name


class Salon(models.Model):
    '''Салон'''
    title = models.CharField('Название салона', max_length=100)
    address = models.TextField('Адрес салона', max_length=200)

    def __str__(self) -> str:
        return self.title

class TimeSlot(models.Model):
    '''Временной промежуток'''
    start_at = models.TimeField('Начало временного промежутка')
    end_at = models.TimeField('Конец временного промежутка')

    def __str__(self) -> str:
        return f'{self.start_at} {self.end_at}'

    def clean(self, *args, **kwargs):
        TimeSlot.clean_fields(self)
        if self.start_at > self.end_at:
            raise ValidationError('Время начала промежутка меньше времени окончания')
        else:
            super(TimeSlot, self).clean()


class Order(models.Model):
    '''Счёт (статус оплаты)'''
    STATUS = [
        ("waiting", "Ожидает оплаты"),
        ("paid", "Оплачено"),
        ("cancel", "Отменено"),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    status = models.CharField('Статус заказа', max_length=14, choices=STATUS)
    receipt = models.URLField('Чек', blank=True)
    created_at = models.DateTimeField('Счёт выставлен', auto_now_add=True)
    updated_at = models.DateTimeField('Последнее обновление', auto_now=True)

    def __str__(self) -> str:
        return f"{self.updated_at} {self.client.full_name} {self.status}"


class SpecialistWorkDayInSalon(models.Model):
    '''Рабочий день сотрудника в одном из салонов'''
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE)
    time_slots = models.ManyToManyField(TimeSlot)
    workday = models.DateField()

    def __str__(self) -> str:
        return f"{self.specialist} {self.salon} {self.workday}"

    def clean(self, *args, **kwargs):
        try:
            specialists = SpecialistWorkDayInSalon.objects.filter(salon__address=self.salon.address, workday=self.workday)
            for time_slot_self in self.time_slots:
                for time_slot in specialists.time_slots:
                    if (time_slot.start_at >= time_slot_self.start_at) or (
                        time_slot.start_end <= time_slot_self.start_end) or (
                        (time_slot.start_at <= time_slot_self.start_at) and (
                            time_slot.start_end >= time_slot_self.start_end)):
                        raise ValidationError('Один из временных промежутков уже занят')
            super(SpecialistWorkDayInSalon, self).clean()
        except SpecialistWorkDayInSalon.DoesNotExist:
            super(SpecialistWorkDayInSalon, self).clean()


class Appointment(models.Model):
    '''Заказ услуги'''
    STATUSES = [("access", "Принято"), ("ended", "Завершено"), ("discard", "Отменено")]
    status = models.CharField('Статус заказа', max_length=9, choices=STATUSES)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    date = models.DateField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def clean(self, *args, **kwargs):
        try:
            SpecialistWorkDayInSalon.objects.get(time_slots__id__exact=self.time_slot.id, specialist__full_name=self.specialist.full_name, salon__address=self.salon.address, workday=self.date)
        except SpecialistWorkDayInSalon.DoesNotExist:
            raise ValidationError('Данного временного слота не существует')
        try:
            Appointment.objects.get(
                Q(time_slot__id=(self.time_slot.id)) & Q(salon__id=(self.salon.id)) & Q(specialist__id=self.specialist.id) & Q(date=self.date)
            )
            raise ValidationError('Время занято')
        except Appointment.DoesNotExist:
            super(Appointment, self).clean()
