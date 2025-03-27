from django.urls import path
from . import views

urlpatterns = [
     path('', views.operador_horarios, name='operador_horarios'),
     path('editar_acceso_matriculas/<int:acceso_id>/', views.editar_acceso_matriculas, name='editar_acceso_matriculas'),
]