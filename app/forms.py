from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction
from .models import User,Dueno,Cliente

class DuenoSignUpForm(UserCreationForm):
    nombre = forms.CharField(required=True)
    apellido = forms.CharField(required=True)
    telefono = forms.CharField(required=True)
    direccion = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_dueno = True
        user.nombre = self.cleaned_data.get('nombre')
        user.last_name = self.cleaned_data.get('apellido')
        user.save()
        dueno = Dueno.objects.create(user=user)
        dueno.phone_number=self.cleaned_data.get('telefono')
        dueno.location=self.cleaned_data.get('direccion')
        dueno.save()
        return user

class ClienteSignUpForm(UserCreationForm):
    nombre = forms.CharField(required=True)
    apellido = forms.CharField(required=True)
    telefono = forms.CharField(required=True)
    direccion = forms.CharField(required=True)


    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_cliente = True
        user.nombre = self.cleaned_data.get('nombre')
        user.last_name = self.cleaned_data.get('apellido')
        user.save()
        cliente = Cliente.objects.create(user=user)
        cliente.phone_number=self.cleaned_data.get('telefono')
        cliente.location=self.cleaned_data.get('direccion')
        cliente.save()
        return user