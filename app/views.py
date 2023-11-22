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

    # Inicializa costo_total fuera del bucle
    costo_total = 0  

    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        hora_inicio = request.POST.get('hora_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        hora_fin = request.POST.get('hora_fin')
        comuna_nombre = request.POST.get('comuna_seleccionada')
        
        
        print("Fecha inicio:", fecha_inicio)
        print("Hora inicio:", hora_inicio)
        print("Fecha fin:", fecha_fin)
        print("Hora fin:", hora_fin)
        print("Costo total:", costo_total)
        

        # Encuentra la comuna por su nombre
        comuna = Comuna.objects.get(comuna=comuna_nombre)

        # Crea objetos de zona horaria para asegurarte de que se manejen correctamente las fechas y horas
        tz = pytz.timezone('America/Santiago')

        fecha_inicio = tz.localize(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
        hora_inicio = tz.localize(datetime.strptime(hora_inicio, '%H:%M'))
        fecha_fin = tz.localize(datetime.strptime(fecha_fin, '%Y-%m-%d'))
        hora_fin = tz.localize(datetime.strptime(hora_fin, '%H:%M'))

        fecha_inicio_formulario = datetime.combine(fecha_inicio.date(), hora_inicio.time()).astimezone(tz)

        # Obtén la fecha y hora actual con la misma zona horaria
        ahora = datetime.now(tz)

        # Filtra estacionamientos disponibles
        if ahora <= fecha_inicio_formulario:
            estacionamientos_disponibles = Estacionamiento.objects.exclude(
                id__in=Arrendamiento.objects.filter(
                    Q(fecha_fin__gte=fecha_inicio, fecha_inicio__lte=fecha_fin) &
                    Q(hora_fin__gte=hora_inicio, hora_inicio__lte=hora_fin)
                ).values('estacionamiento__id')
            ).filter(comuna=comuna)

            # Calcula las horas totales
            tiempo_transcurrido = fecha_fin - fecha_inicio + (hora_fin - hora_inicio)
            horas_totales = tiempo_transcurrido.total_seconds() / 3600

            for estacionamiento in estacionamientos_disponibles:
                costo_por_hora=estacionamiento.costo_por_hora
                print(horas_totales)
                print(costo_por_hora)
                costo_total = costo_por_hora * horas_totales  # Calcula el precio total para este estacionamiento            
                print(costo_total)

            # Pasa los valores calculados al contexto
            return render(request, 'estacionamiento/mostrar_estacionamiento.html', {
                'estacionamientos_disponibles': estacionamientos_disponibles,
                'horas_totales': horas_totales,
                'costo_total': costo_total,
                'fecha_inicio': fecha_inicio,
                'hora_inicio': hora_inicio,
                'fecha_fin': fecha_fin,
                'hora_fin': hora_fin,                
            })
        else:
            messages.error(request, "No hay estacionamientos disponibles en la comuna seleccionada.")

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



from django.shortcuts import get_object_or_404, redirect

def cancelar_reserva(request, arrendamiento_id):
    try:
        # Obtén el objeto de arrendamiento a cancelar
        arrendamiento = get_object_or_404(Arrendamiento, id=arrendamiento_id)
        
        # Realiza la lógica para cancelar la reserva aquí
        # Por ejemplo, cambia el estado a "eliminado"
        arrendamiento.estado = 'eliminado'
        
        # Guarda los cambios en la base de datos
        arrendamiento.save()

        # Redirige a la página de confirmación de cancelación
        return redirect('confirmar_cancelacion')
    except Arrendamiento.DoesNotExist:
        # Maneja el caso en el que el arrendamiento no existe
        return redirect('error')


    
def error(request):
    return render(request, 'error.html')



def confirmar_reserva(request, estacionamiento_id, fecha_inicio, hora_inicio, fecha_fin, hora_fin, costo_total):
    print("Entró a confirmar_reserva")

    try:
        # Formatea las fechas y horas
        tz = pytz.timezone('America/Santiago')
        fecha_inicio_obj = tz.localize(datetime.strptime(fecha_inicio, '%Y-%m-%d'))
        hora_inicio_obj = tz.localize(datetime.strptime(hora_inicio, '%H:%M'))
        fecha_fin_obj = tz.localize(datetime.strptime(fecha_fin, '%Y-%m-%d'))
        hora_fin_obj = tz.localize(datetime.strptime(hora_fin, '%H:%M'))

        # Convierte la cadena de costo_total a un número decimal
        costo_total = float(costo_total.replace(',', '.'))

        # Imprime los valores para verificar
        print("Estacionamiento ID:", estacionamiento_id)
        print("Fecha inicio:", fecha_inicio_obj)
        print("Hora inicio:", hora_inicio_obj)
        print("Fecha fin:", fecha_fin_obj)
        print("Hora fin:", hora_fin_obj)
        print("Costo total:", costo_total)

        # Resto del código para crear el objeto Arrendamiento y otras operaciones

        return redirect('estacionamiento:pago_exitoso')  # Ajusta 'pago_exitoso' según tus rutas

    except Exception as e:
        print(f"Error al confirmar reserva: {e}")
        return redirect('estacionamiento:error')  # Ajusta 'error' según tus rutas