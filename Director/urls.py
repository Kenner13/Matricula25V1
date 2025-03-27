from django.urls import path
from . import views

urlpatterns = [
     path('eliminar_matricula/', views.eliminar_matricula, name='eliminar_matricula'),
]