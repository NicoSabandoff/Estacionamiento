from django.urls import path
from .import  views

urlpatterns=[
     path('',views.index, name='index'),
     path('register/',views.register, name='register'),
     path('cliente_register/',views.cliente_register.as_view(), name='cliente_register'),
     path('dueno_register/',views.dueno_register.as_view(), name='dueno_register'),
     path('login/',views.login_request, name='login'),
     path('logout/',views.logout_view, name='logout'),
]