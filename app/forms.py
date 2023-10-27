from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction
from .models import User,Dueno,Cliente

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
    
