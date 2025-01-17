import datetime
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.generic import CreateView
from .forms import DuenoSignUpForm, ClienteSignUpForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Arrendamiento, Comuna, Estacionamiento, User, Cliente
import pytz
from datetime import datetime, timedelta
from django.db.models import Q

def index(request):
    return render(request, 'accounts/index.html')

def register(request):
    return render(request, 'accounts/register.html')

class dueno_register(CreateView):
    model = User
    form_class = DuenoSignUpForm
    template_name = 'accounts/dueno_register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')

class cliente_register(CreateView):
    model = User
    form_class = ClienteSignUpForm
    template_name = 'accounts/cliente_register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/')

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, "Usuario o contraseña inválida")
        else:
            messages.error(request, "Usuario o contraseña inválida")
    return render(request, 'accounts/login.html', context={'form': AuthenticationForm()})

def logout_view(request):
    logout(request)
    return redirect('/')

def lista_comunas(request):
    comunas = Comuna.objects.all()
    return render(request, 'app/buscar.html', {'comunas': comunas})






def buscar(request):
    comunas = Comuna.objects.all()

    if request.method == 'POST':
        fecha_inicio = datetime.strptime(request.POST.get('fecha_inicio'), '%Y-%m-%d')
        hora_inicio = datetime.strptime(request.POST.get('hora_inicio'), '%H:%M')
        fecha_fin = datetime.strptime(request.POST.get('fecha_fin'), '%Y-%m-%d')
        hora_fin = datetime.strptime(request.POST.get('hora_fin'), '%H:%M')
        comuna_nombre = request.POST.get('comuna_seleccionada')  # Nombre de la comuna

        # Encuentra la comuna por su nombre
        comuna = Comuna.objects.get(comuna=comuna_nombre)

        estacionamientos_disponibles = Estacionamiento.objects.filter(comuna=comuna)

        # Calcula la diferencia de tiempo en horas
        tiempo_estacionamiento = (fecha_fin - fecha_inicio).total_seconds() / 3600 + \
                                 (hora_fin - hora_inicio).total_seconds() / 3600

        # Obtiene el costo por hora de la comuna seleccionada
        costo_por_hora = comuna.estacionamiento_set.first().costo_por_hora  # Asume una relación entre Comuna y Estacionamiento

        # Calcula el costo total
        costo_total = tiempo_estacionamiento * costo_por_hora

        return render(request, 'estacionamiento/mostrar_estacionamiento.html', {
            'estacionamientos_disponibles': estacionamientos_disponibles,
            'horas_totales': tiempo_estacionamiento,
            'costo_por_hora': costo_por_hora,
            'costo_total': costo_total,  # Pasa el costo total a la plantilla
            'comunas': comunas,
        })

    return render(request, 'estacionamiento/buscar.html', {'comunas': comunas})



    
def pago_exitoso(request):
    # Lógica para la página de pago exitoso
    return render(request, 'estacionamiento/pago_exitoso.html')    



def arriendos(request):
    if request.user.is_authenticated:
        cliente = Cliente.objects.get(user=request.user)
        arrendamientos = Arrendamiento.objects.filter(cliente=cliente)
    else:
        arrendamientos = []

    return render(request, 'estacionamiento/arriendos.html', {'arrendamientos': arrendamientos})



def editar_arrendamiento(request, arrendamiento_id):
    arrendamiento = get_object_or_404(Arrendamiento, pk=arrendamiento_id)
    
    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        hora_fin = request.POST.get('hora_fin')

        # Validación de datos (debes agregar validación según tus necesidades)

        # Actualiza los datos del arrendamiento con los datos del formulario
        arrendamiento.fecha = fecha_inicio
        arrendamiento.hora_inicio = hora_inicio
        arrendamiento.fecha_fin = fecha_fin
        arrendamiento.hora_fin = hora_fin
        arrendamiento.save()

        return redirect('arriendos')
    
    return render(request, 'estacionamiento/editar_arrendamiento.html', {'arrendamiento': arrendamiento})




def confirmar_cancelacion(request):
    return render(request, 'estacionamiento/confirmacion_cancelado.html')



def cancelar_reserva(request, arrendamiento_id):
    try:
        # Obtén el objeto de arrendamiento a cancelar
        arrendamiento = Arrendamiento.objects.get(id=arrendamiento_id)
        
        # Realiza la lógica para cancelar la reserva aquí (por ejemplo, cambiar el estado de la reserva)
        # ...

        # Elimina el arrendamiento
        arrendamiento.delete()

        # Redirige a la página de confirmación de cancelación
        return redirect('confirmar_cancelacion')
    except Arrendamiento.DoesNotExist:
        # Maneja el caso en el que el arrendamiento no existe
        return redirect('error')
    
def error(request):
    return render(request, 'error.html')