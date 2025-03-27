from django.urls import path
from . import views

urlpatterns = [
     path('', views.operador_asignaturas, name='operador_asignaturas'),
      path('programacion/crear/', views.crear_programacion, name='crear_programacion'),
     path('editar_programacion/<int:programacion_id>/', views.editar_programacion, name='editar_programacion'),
]