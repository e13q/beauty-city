from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Q
from django.core.exceptions import ValidationError
import datetime


from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Client(models.Model):
    """Клиент"""

    id_tg = models.IntegerField(
        "id в телеграмм", blank=True, null=True, unique=True
    )
    full_name = models.CharField("ФИО", max_length=200)
    phone_number = PhoneNumberField(null=True, unique=True, region="RU")

    def __str__(self) -> str:
        return self.full_name


class Salon(models.Model):
    """Салон"""

    title = models.CharField("Название салона", max_length=100)
    address = models.TextField("Адрес салона", max_length=200)

    def __str__(self) -> str:
        return self.title


class Service(models.Model):
    """Услуга"""

    title = models.CharField("Название услуги", max_length=200)
    price = models.FloatField("Цена услуги")
    duration = models.IntegerField("Длительность услуги, мин")

    def __str__(self) -> str:
        return self.title


class Specialist(models.Model):
    """Специалист"""

    full_name = models.CharField("ФИО", max_length=200)

    def __str__(self) -> str:
        return self.full_name


class Order(models.Model):
    """Счёт (статус оплаты)"""

    STATUS = [
        ("waiting", "Ожидает оплаты"),
        ("paid", "Оплачено"),
        ("cancel", "Отменено"),
    ]
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name="Клиент"
    )
    status = models.CharField("Статус заказа", max_length=14, choices=STATUS)
    receipt = models.URLField("Чек", blank=True)
    created_at = models.DateTimeField("Счёт выставлен", auto_now_add=True)
    updated_at = models.DateTimeField("Последнее обновление", auto_now=True)

    def __str__(self) -> str:
        return f"{self.updated_at} {self.client.full_name} {self.status}"


class SpecialistWorkDayInSalon(models.Model):
    """Рабочий день сотрудника в одном из салонов"""

    workday = models.DateField()
    salon = models.ForeignKey(Salon, on_delete=models.PROTECT)
    specialist = models.ForeignKey(Specialist, on_delete=models.PROTECT)
    services = models.ManyToManyField(Service, verbose_name="Услуги")
    start_at = models.TimeField()
    end_at = models.TimeField()

    def __str__(self) -> str:
        return f"{self.specialist} {self.salon} {self.workday}"


class Appointment(models.Model):
    """Заказ услуги"""

    STATUSES = [
        ("access", "Принято"),
        ("ended", "Завершено"),
        ("discard", "Отменено"),
    ]
    status = models.CharField("Статус заказа", max_length=9, choices=STATUSES)
    date = models.DateField()
    salon = models.ForeignKey(Salon, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    specialist = models.ForeignKey(Specialist, on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    start_at = models.TimeField()
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
