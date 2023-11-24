import datetime
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.generic import CreateView
from .forms import DuenoSignUpForm, ClienteSignUpForm, RegistroVehiculoForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Arrendamiento, Comuna, Estacionamiento, User, Cliente, Calificacion
import pytz
from datetime import datetime, timedelta
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def index(request):
    return render(request, 'accounts/index.html')

def register(request):
    return render(request, 'accounts/register.html')

def reportes(request):
    return render(request, 'estacionamiento/reportes.html')

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

def calificacion_duenos(request):
    # Lógica para la página de pago exitoso
    return render(request, 'estacionamiento/calificacion_duenos.html')    

def arriendos(request):
    if request.user.is_authenticated:
        cliente = Cliente.objects.get(user=request.user)
        arrendamientos = Arrendamiento.objects.filter(cliente=cliente)

        # Obtener la zona horaria actual
        current_timezone = timezone.get_current_timezone()

        # Actualizar estados de arrendamientos si la fecha fin y hora fin son anteriores a la actual
        now = timezone.now()
        for arrendamiento in arrendamientos:
            fecha_fin_hora_fin = datetime.combine(
                arrendamiento.fecha_fin,
                arrendamiento.hora_fin
            ).replace(tzinfo=current_timezone)

            if fecha_fin_hora_fin < now:
                arrendamiento.estado = 'finalizado'
                arrendamiento.save()

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




def confirmar_reserva(request, estacionamiento_id, fecha_inicio, fecha_fin, hora_inicio, hora_fin):
    try:
        # Convertir las cadenas a objetos datetime sin información de la zona horaria
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S%z')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d %H:%M:%S%z')

        # Establecer explícitamente la hora en las fechas
        hora_inicio = datetime.strptime(hora_inicio, '%Y-%m-%d %H:%M:%S%z').time()
        hora_fin = datetime.strptime(hora_fin, '%Y-%m-%d %H:%M:%S%z').time()
        fecha_inicio = datetime.combine(fecha_inicio.date(), hora_inicio)
        fecha_fin = datetime.combine(fecha_fin.date(), hora_fin)

        # Obtener el usuario actual como cliente
        cliente = request.user.cliente

        # Crear una instancia del modelo Arrendamiento con los valores convertidos y el cliente
        arrendamiento = Arrendamiento(
            cliente=cliente,
            estacionamiento_id=estacionamiento_id,
            fecha_inicio=fecha_inicio.date(),
            fecha_fin=fecha_fin.date(),
            hora_inicio=fecha_inicio.time(),
            hora_fin=fecha_fin.time(),
            estado='activo'
        )

        # Calcular las horas totales de la reserva
        tiempo_transcurrido = fecha_fin - fecha_inicio
        horas_totales = tiempo_transcurrido.total_seconds() / 3600

        # Obtener el estacionamiento
        estacionamiento = Estacionamiento.objects.get(id=estacionamiento_id)

        # Calcular el precio total
        precio_total = estacionamiento.costo_por_hora * horas_totales

        # Asignar el precio total al arrendamiento
        arrendamiento.precio = precio_total

        # Guardar la instancia en la base de datos
        arrendamiento.save()

        # Resto del código...

        # Devolver una respuesta exitosa
        return redirect('pago_exitoso')

    except Exception as e:
        # Imprimir o registrar cualquier excepción para entender el problema
        print("Error en la conversión de fechas y horas:", str(e))

        # Puedes agregar un mensaje de error a la respuesta para que puedas verlo en el navegador
        return HttpResponse(f"Error en la confirmación de reserva: {str(e)}", status=500)
    
    
def estacionamiento_dueno(request):
    # Verifica si el usuario está autenticado
    if request.user.is_authenticated:
        # Obtiene el ID del usuario autenticado
        dueno_id = request.user.id

        # Filtra los estacionamientos asociados al dueño
        estacionamientos = Estacionamiento.objects.filter(dueno_id=dueno_id)

        # Renderiza la plantilla con la lista de estacionamientos
        return render(request, 'estacionamiento/estacionamiento_dueno.html', {'estacionamientos': estacionamientos})
    else:
        # Maneja el caso en el que el usuario no esté autenticado
        return render(request, 'estacionamiento/error.html', {'mensaje': 'Debes iniciar sesión para ver tus estacionamientos.'})
    
    
def deshabilitar_estacionamiento(request, estacionamiento_id):
    estacionamiento = Estacionamiento.objects.get(id=estacionamiento_id)

    # Verifica si hay arrendamientos activos
    if not Arrendamiento.objects.filter(estacionamiento=estacionamiento, fecha_fin__gte=timezone.now(), estado='activo').exists():
        estacionamiento.habilitado = False
        estacionamiento.save()
        messages.success(request, f"Estacionamiento {estacionamiento.id} deshabilitado exitosamente.")
    else:
        messages.error(request, f"No se puede deshabilitar el estacionamiento {estacionamiento.id} porque está arrendado.")

    return redirect('estacionamiento_dueno')

def habilitar_estacionamiento(request, estacionamiento_id):
    estacionamiento = Estacionamiento.objects.get(id=estacionamiento_id)

    estacionamiento.habilitado = True
    estacionamiento.save()
    messages.success(request, f"Estacionamiento {estacionamiento.id} habilitado exitosamente.")

    return redirect('estacionamiento_dueno')    



def calificar_dueno(request, arrendamiento_id):
    arrendamiento = get_object_or_404(Arrendamiento, id=arrendamiento_id)

    if request.method == 'POST':
        try:
            calificacion = request.POST.get('calificacion')
            comentario = request.POST.get('comentario')

            usuario = request.user
            estacionamiento = arrendamiento.estacionamiento
            dueno = estacionamiento.dueno

            calificacion = Calificacion(usuario=usuario,
                                        dueno=dueno,
                                        calificacion=calificacion,
                                        comentario=comentario)
            calificacion.save()

            # Redirige a la página 'calificacion_duenos'
            return redirect('calificacion_duenos')

        except Exception as e:
            # Maneja el error y devuelve una respuesta JSON con el mensaje de error
            return render(request, 'error.html', {'error_message': str(e)}, status=400)

    # Si la solicitud no es POST, devuelve un error BadRequest
    return render(request, 'error.html', {'error_message': 'Bad Request: Se esperaba una solicitud POST.'}, status=400)



def generar_informe_pdf(request):
    if request.method == 'GET':
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        # Convertir las fechas de cadena a objetos de fecha
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

        # Filtrar los arrendamientos por fecha de inicio y fin
        arrendamientos = Arrendamiento.objects.filter(
            Q(fecha_inicio__gte=fecha_inicio) & Q(fecha_fin__lte=fecha_fin)
        )

        # Puedes hacer algo con los arrendamientos, como crear un informe PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="informe.pdf"'

        # Iniciar el objeto PDF
        p = canvas.Canvas(response, pagesize=letter)

        # Encabezado del informe
        p.setFont("Helvetica-Bold", 14)  # Establecer el tamaño de la fuente
        p.drawString(100, 765, f"Informe de arrendamientos desde:")
        p.setFont("Helvetica-Bold", 12)  # Establecer el tamaño de la fuente
        p.drawString(100, 750, f"{fecha_inicio} hasta {fecha_fin}")
        
        
        p.setFont("Helvetica", 12)  # Establecer el tamaño de la fuente
        # Contenido del informe con información de los arrendamientos
        y_position = 725  # Ajusta la posición inicial del primer recuadro

        for arrendamiento in arrendamientos:

            # Agregar información dentro del recuadro
            p.drawString(110, y_position, f"Cliente: {arrendamiento.cliente.user.nombre} {arrendamiento.cliente.user.apellido}")
            p.drawString(110, y_position - 15, f"RUT: {arrendamiento.cliente.user.rut}")
            p.drawString(110, y_position - 30, f"Estacionamiento: {arrendamiento.estacionamiento.direccion}")
            p.drawString(110, y_position - 45, f"Fecha de Inicio: {arrendamiento.fecha_inicio}")
            p.drawString(110, y_position - 60, f"Fecha de Fin: {arrendamiento.fecha_fin}")
            p.drawString(110, y_position - 75, f"Valor cancelado: {arrendamiento.precio}")
            p.drawString(110, y_position - 90, f"Hora de Inicio: {arrendamiento.hora_inicio}")
            p.drawString(110, y_position - 105, f"Hora de Fin: {arrendamiento.hora_fin}")

            # Dibujar un recuadro alrededor de la información de cada arrendamiento
            p.rect(100, y_position - 115, 400, 130)  # Ajusta las dimensiones según sea necesario

            # Ajustar la posición para el próximo recuadro
            y_position -= 150  # Ajusta el espacio entre recuadros según sea necesario

        # Guardar la página y enviar la respuesta
        p.showPage()
        p.save()

        return response

    return render(request, 'estacionamiento/reportes.html')

def perfil(request):
        cliente = Cliente.objects.get(user=request.user)
        return render(request, 'accounts/perfil.html', {'cliente': cliente})

def registro_vehiculo(request):
    return render(request, 'accounts/registro_vehiculo.html')

def registro_vehiculo(request):
    if request.method == 'POST':
        form = RegistroVehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.cliente = request.user.cliente
            vehiculo.save()
            messages.success(request, 'Vehículo registrado con éxito.')
            return redirect('perfil')
        else:
            messages.error(request, 'Error en el formulario. Por favor, verifica los datos.')
    else:
        form = RegistroVehiculoForm()

    return render(request, 'accounts/registro_vehiculo.html', {'form': form})

