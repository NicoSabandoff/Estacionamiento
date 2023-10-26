from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_cliente = models.BooleanField(default=False)
    is_dueno = models.BooleanField(default=False)
    nombre = models.CharField(max_length=100)
    apellido= models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=20)


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)

class Dueno(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)
