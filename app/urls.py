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
     path('editar_arrendamiento/<int:arrendamiento_id>/', views.editar_arrendamiento, name='editar_arrendamiento'),
     path('confirmar_cancelacion/', views.confirmar_cancelacion, name='confirmar_cancelacion'),
     path('cancelar_reserva/<int:arrendamiento_id>/', views.cancelar_reserva, name='cancelar_reserva'),
     
]