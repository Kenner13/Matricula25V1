from django.urls import path
from . import views

urlpatterns = [
    path('', views.Estudiante_Matricula, name='estudiante_matricula'),
    path('estudiante_constancia/', views.Estudiante_Constancia, name='estudiante_constancia'),
    path('constancia/pdf/', views.Estudiante_Constancia_PDF, name='estudiante_constancia_pdf'),
]
