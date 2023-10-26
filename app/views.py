import datetime
from django.contrib.auth import login, logout,authenticate
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.generic import CreateView
from .forms import DuenoSignUpForm, ClienteSignUpForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Arrendamiento, Comuna, Estacionamiento, User
import pytz
from datetime import datetime
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
    if request.method=='POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            print("entro")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            print(username)
            if user is not None :
                login(request,user)
                return redirect('/')
            else:
                messages.error(request,"Usuario o contraseña invalida")
        else:
                messages.error(request,"Usuario o contraseña invalida")
    return render(request, 'accounts/login.html',
    context={'form':AuthenticationForm()})

def logout_view(request):
    logout(request)
    return redirect('/')


def lista_comunas(request):
    comunas = Comuna.objects.all()
    return render(request, 'app/buscar.html', {'comunas': comunas})



def buscar(request):

    if request.method == 'POST':
        comuna = request.POST.get('comuna')
        fecha_inicio = request.POST.get('fecha_inicio')
        hora_inicio = request.POST.get('hora_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        hora_fin = request.POST.get('hora_fin')

        # Crea objetos de zona horaria para asegurarte de que se manejen correctamente las fechas y horas
        tz = pytz.timezone('America/Santiago')

        fecha_inicio = tz.localize(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
        hora_inicio = tz.localize(datetime.strptime(hora_inicio, '%H:%M'))
        fecha_fin = tz.localize(datetime.strptime(fecha_fin, '%Y-%m-%d'))
        hora_fin = tz.localize(datetime.strptime(hora_fin, '%H:%M'))

        fecha_inicio_formulario = datetime.combine(fecha_inicio.date(), hora_inicio.time()).astimezone(tz)

        print(fecha_inicio)
        print(fecha_fin)
        print(hora_inicio)
        print(hora_fin)
        print(fecha_inicio_formulario)

        # Obtén la fecha y hora actual con la misma zona horaria
        ahora = datetime.now(tz)
        print("Ahora es:", ahora)

        # Inicializa la variable estacionamientos_disponibles
        estacionamientos_disponibles = []

        tiempo_transcurrido = fecha_fin - fecha_inicio + (hora_fin - hora_inicio)
        # Calcula las horas totales
        horas_totales = tiempo_transcurrido.total_seconds() / 3600

        costo_por_hora = 0
        

        # Filtra estacionamientos disponibles
        if ahora <= fecha_inicio_formulario:
            estacionamientos_disponibles = Estacionamiento.objects.exclude(
                id__in=Arrendamiento.objects.filter(
                    Q(fecha_fin__gte=fecha_inicio, fecha_inicio__lte=fecha_fin) &
                    Q(Q(hora_fin__gte=hora_inicio, hora_inicio__lte=hora_fin) |
                    Q(hora_inicio__gte=hora_inicio, hora_inicio__lte=hora_fin))
                ).values('estacionamiento__id')
            ).filter(comuna__comuna=comuna)

            for estacionamiento in estacionamientos_disponibles:
                costo_por_hora=estacionamiento.costo_por_hora
                print(horas_totales)
                print(costo_por_hora)
                estacionamiento.precio_total = costo_por_hora * horas_totales  # Calcula el precio total para este estacionamiento

        # Pasa los valores calculados al contexto
        return render(request, 'estacionamiento/mostrar_estacionamiento.html', {
            'estacionamientos_disponibles': estacionamientos_disponibles,
            'horas_totales': horas_totales,
            'costo_por_hora': costo_por_hora,
        })
    return render(request, 'estacionamiento/buscar.html')