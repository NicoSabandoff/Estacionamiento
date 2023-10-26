from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_cliente = models.BooleanField(default=False)
    is_dueno = models.BooleanField(default=False)
    nombre = models.CharField(max_length=100)
    apellido= models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    rut = models.CharField(max_length=20)


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)

class Dueno(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, primary_key = True)

class Comuna(models.Model):
    comuna = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)


class Vehiculo(models.Model):
    patente = models.CharField(max_length=7)
    modelo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

class Tamano(models.Model):
    TAMAÑO_CHOICES = (
        ('pequeño', 'Pequeño'),
        ('mediano', 'Mediano'),
        ('grande', 'Grande'),
    )

    tamano = models.CharField(max_length=10, choices=TAMAÑO_CHOICES, unique=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.tamano

class Estacionamiento(models.Model):
    direccion = models.CharField(max_length=200)
    complemento = models.CharField(max_length=100, default='')
    tamano = models.ForeignKey(Tamano, on_delete=models.CASCADE, default=1)
    dueno = models.ForeignKey(Dueno, on_delete=models.CASCADE)
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE)
    costo_por_hora = models.IntegerField(default=0)


class Arrendamiento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    estacionamiento = models.ForeignKey(Estacionamiento, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    precio = models.IntegerField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

class Reporte(models.Model):
    estacionamiento = models.ForeignKey(Estacionamiento, on_delete=models.CASCADE)
    fecha = models.DateField()
    descripcion = models.TextField()
    monto_recaudado = models.DecimalField(max_digits=10, decimal_places=2)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)

