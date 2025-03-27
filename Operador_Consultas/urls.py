from django.urls import path
from . import views

urlpatterns = [
     path('', views.operador_consultas, name='operador_consultas'),
     path('descargar-excel/', views.descargar_matricula_excel, name='descargar_matricula_excel'),
]