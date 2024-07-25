from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=200)
    id_tg = models.CharField(max_length=200)
    phone_number = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class Salon(models.Model):
    title = models.CharField(max_length=200)
    address = models.TextField()

    def __str__(self) -> str:
        return self.title


class Specialist(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name


class Service(models.Model):
    title = models.CharField(max_length=200)
    price = models.FloatField()

    def __str__(self) -> str:
        return self.title

class TimeTable(models.Model):
    salon = models.ForeignKey(Salon, null=True, on_delete=models.CASCADE)
    specialict = models.ForeignKey(
        Specialist, null=True, on_delete=models.CASCADE
    )
    service = models.ForeignKey(Service, null=True, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    occupied = models.BooleanField(default=False)


    def __str__(self) -> str:
        return f"{self.salon.title} {self.service.title}"

class Order(models.Model):
    STATUS = [("acc", "Принят"), ("cls", "Завершен"),]
    PAYMENT = [
        ("online", "На сайте"),
        ("salon", "В салоне"),
        ("paid", "Оплачено"),
    ]

    status = models.CharField(max_length=10, choices=STATUS)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    timetable = models.ForeignKey(TimeTable, on_delete=models.CASCADE)
    payment = models.CharField(max_length=10, choices=PAYMENT)

    def __str__(self) -> str:
        return f"{self.client.name} {self.timetable.date}"
