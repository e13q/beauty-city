from django.db import models


class Saloon(models.Model):
    name = models.CharField(max_length=256,verbose_name='название салона')
    adress = models.CharField(max_length=256, verbose_name='адресс салона ')
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Procedure(models.Model):
    name = models.CharField(max_length=100, verbose_name='название процедуры')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    saloon = models.ForeignKey(Saloon, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Master(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя мастера')
    salon = models.ForeignKey(Saloon, on_delete=models.CASCADE)
    procedurce = models.ManyToManyField(Procedure)

    def __str__(self):
        return self.name
    