from django.urls import path
from .import  views

urlpatterns=[
     path('',views.index, name='index'),
     path('register/',views.register, name='register'),
     path('cliente_register/',views.cliente_register.as_view(), name='cliente_register'),
     path('dueno_register/',views.dueno_register.as_view(), name='dueno_register'),
     path('login/',views.login_request, name='login'),
     path('logout/',views.logout_view, name='logout'),
     path('buscar/',views.buscar, name='buscar'),
     path('pago_exitoso/', views.pago_exitoso, name='pago_exitoso'),
     path('arriendos/', views.arriendos, name='arriendos'),
     path('estacionamiento_dueno/', views.estacionamiento_dueno, name='estacionamiento_dueno'),
     path('editar_arrendamiento/<int:arrendamiento_id>/', views.editar_arrendamiento, name='editar_arrendamiento'),
     path('confirmar_cancelacion/', views.confirmar_cancelacion, name='confirmar_cancelacion'),
     path('cancelar_reserva/<int:arrendamiento_id>/', views.cancelar_reserva, name='cancelar_reserva'),
     path('confirmar_reserva/<int:estacionamiento_id>/<str:fecha_inicio>/<str:fecha_fin>/<str:hora_inicio>/<str:hora_fin>/', views.confirmar_reserva, name='confirmar_reserva'),
     path('deshabilitar_estacionamiento/<int:estacionamiento_id>/', views.deshabilitar_estacionamiento, name='deshabilitar_estacionamiento'),
     path('habilitar_estacionamiento/<int:estacionamiento_id>/', views.habilitar_estacionamiento, name='habilitar_estacionamiento'),
     path('error/', views.error, name='error'),
     path('calificar_dueno/<int:arrendamiento_id>/', views.calificar_dueno, name='calificar_dueno'),
     path('calificacion_duenos/', views.calificacion_duenos, name='calificacion_duenos'),
     path('reportes/',views.reportes, name='reportes'),
     path('generar_informe_pdf/', views.generar_informe_pdf, name='generar_informe_pdf'),
     path('perfil/', views.perfil, name='perfil'),
     path('registro_vehiculo/', views.registro_vehiculo, name='registro_vehiculo'),     

]