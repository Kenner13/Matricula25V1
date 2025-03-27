from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('estudiante_pago/', views.estudiante_pago, name='estudiante_pago'),
    path('ocrac_historial/', views.ocrac_historial, name='ocrac_historial'),
    path('logout/', views.logout_view, name='logout'),
    path('terminos_condiciones/', views.terminos_condiciones, name='terminos_condiciones'),
]
