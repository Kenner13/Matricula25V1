from django.db import models
from django.utils import timezone
from TR.models import Estudiante,Programacion

# Create your models here.
class Matricula(models.Model):
    I_MatriculaID = models.AutoField(primary_key=True)
    N_CodEstudianteID = models.ForeignKey(Estudiante, on_delete=models.CASCADE, db_column='N_CodEstudianteID')
    I_ProgramacionID = models.ForeignKey(Programacion, on_delete=models.CASCADE, db_column='I_ProgramacionID')
    D_FechaMatricula = models.DateTimeField()
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()
    I_Identificador = models.IntegerField()