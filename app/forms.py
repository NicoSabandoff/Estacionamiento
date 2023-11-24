import re
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import User,Dueno,Cliente, Vehiculo

class DuenoSignUpForm(UserCreationForm):
    rut = forms.CharField(required=True)
    nombre = forms.CharField(required=True)
    apellido = forms.CharField(required=True)
    telefono = forms.CharField(required=True)


    class Meta(UserCreationForm.Meta):
        model = User
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_dueno = True
        user.rut = self.cleaned_data.get('rut')    
        user.nombre = self.cleaned_data.get('nombre')
        user.apellido = self.cleaned_data.get('apellido')
        user.telefono = self.cleaned_data.get('telefono')
        user.save()
        dueno = Dueno.objects.create(user=user)

        dueno.save()
        return user

class ClienteSignUpForm(UserCreationForm):
    rut = forms.CharField(required=True)    
    nombre = forms.CharField(required=True)
    apellido = forms.CharField(required=True)
    telefono = forms.CharField(required=True)



    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_cliente = True
        user.rut = self.cleaned_data.get('rut')         
        user.nombre = self.cleaned_data.get('nombre')
        user.apellido = self.cleaned_data.get('apellido')
        user.telefono = self.cleaned_data.get('telefono')
        user.save()
        cliente = Cliente.objects.create(user=user)
        cliente.save()
        return user
    
def validate_patente(value):
    # Verifica si la patente tiene el formato para patentes chilenas)
    pattern = re.compile(r'^[A-Z]{2}-[A-Z]{2}-\d{2}$')

    if not pattern.match(value):
        raise ValidationError('La patente debe estar en el siguiente formato: AA-BB-12')

    letras_partes = value.split('-')[:2]
    for letras in letras_partes:
        if not letras.isalpha() or not letras.isupper():
            raise ValidationError('Las letras en la patente deben ser mayúsculas.')

    numero_parte = int(value.split('-')[2])
    if not 1 <= numero_parte <= 99:
        raise ValidationError('El número en la patente debe estar entre 01 y 99.')

class RegistroVehiculoForm(forms.ModelForm):
    patente = forms.CharField(validators=[validate_patente])

    class Meta:
        model = Vehiculo
        fields = ['marca', 'modelo', 'patente']