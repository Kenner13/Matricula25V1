from django.urls import path
from . import views

urlpatterns = [
    path('', views.cargar_usuarios_csv, name='cargar_usuarios_csv'),
    path('descargar-excel/', views.generar_excel_contrasenas, name='generar_excel_contrasenas'),
    path('estudiantes/', views.cargar_estudiantes_csv, name='cargar_estudiantes_csv'),
]