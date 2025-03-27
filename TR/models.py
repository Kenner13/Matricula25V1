from django.db import models
from TC.models import UsuarioRoles,CondicionAsignaturas,DepartamentoAcademicos,Dia,EntidadRecaudadoras,Facultad
# Create your models here.
class Usuario(models.Model):
    I_UsuarioID = models.AutoField(primary_key=True)
    T_NombreUsuario = models.CharField(max_length=50)
    T_Contrasenia = models.CharField(max_length=500)
    T_ApelPaterno = models.CharField(max_length=50)
    T_ApelMaterno = models.CharField(max_length=50)
    T_Nombre = models.CharField(max_length=50)
    I_RolID = models.ForeignKey(UsuarioRoles, on_delete=models.CASCADE, db_column='I_RolID')
    B_Habilitado = models.BooleanField()
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID_1 = models.IntegerField()

class Escuela(models.Model):
    I_EscuelaID = models.AutoField(primary_key=True)
    T_NombreEscuela = models.CharField(max_length=100)
    I_FacultadID = models.ForeignKey(Facultad, on_delete=models.CASCADE, db_column='I_FacultadID')

class Especialidad(models.Model):
    I_EspecialidadID = models.AutoField(primary_key=True)
    T_NombreEspecialidad = models.CharField(max_length=100)
    I_EscuelaID = models.ForeignKey(Escuela, on_delete=models.CASCADE, db_column='I_EscuelaID')

class PlanCurriculares(models.Model):
    I_PlanID = models.AutoField(primary_key=True)
    I_AnioPlan = models.IntegerField()
    I_EspecialidadID = models.ForeignKey(Especialidad, on_delete=models.CASCADE, db_column='I_EspecialidadID')
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()

class Asignatura(models.Model):
    I_AsignaturaID = models.AutoField(primary_key=True)
    I_CodAsignatura = models.IntegerField()
    I_PlanID = models.ForeignKey(PlanCurriculares, on_delete=models.CASCADE, db_column='I_PlanID')
    T_NombreAsignatura = models.CharField(max_length=250)
    T_Ciclo = models.CharField(max_length=4)
    I_Creditos = models.IntegerField()
    I_CondicionAsignaturaID = models.ForeignKey(CondicionAsignaturas, on_delete=models.CASCADE, db_column='I_CondicionAsignaturaID')
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()
    def __str__(self):
        return self.T_Ciclo + " - " + self.T_NombreAsignatura 

class AsignaturaPreRequisitos(models.Model):
    I_AsignaturaPreRequisitoID = models.AutoField(primary_key=True)
    I_AsignaturaID = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='asignatura_principal', db_column='I_AsignaturaID')
    I_PreRequisitoID = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='asignatura_prerrequisito', db_column='I_PreRequisitoID')
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()

class Operador(models.Model):
    N_CodOperadorID = models.CharField(primary_key=True, max_length=10)
    N_DniOperador = models.CharField(max_length=10)
    T_ApelPaterno = models.CharField(max_length=50)
    T_ApelMaterno = models.CharField(max_length=50)
    T_Nombre = models.CharField(max_length=70)
    I_EspecialidadID = models.ForeignKey(Especialidad, on_delete=models.CASCADE, db_column='I_EspecialidadID')
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()
    T_Email = models.CharField(max_length=50)

class AccesoMatriculas(models.Model):
    CATEGORIAS = [
        ('quinto_superior', 'QUINTO SUPERIOR'),
        ('regulares_invictos', 'REGULARES INVICTOS'),
        ('todos', 'TODOS'),
    ]
    I_AccesoID = models.AutoField(primary_key=True)
    N_CodOperadorID = models.ForeignKey(Operador, on_delete=models.CASCADE, db_column='N_CodOperadorID')
    D_HoraApertura = models.TimeField()
    D_DiaApertura = models.DateField()
    D_DiaCierre = models.DateField()
    D_HoraCierre = models.TimeField()
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()
    T_Categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    def get_categoria_display(self):
        """Este método devuelve el nombre legible de la categoría."""
        return dict(self.CATEGORIAS).get(self.T_Categoria, 'Categoría desconocida')

class Docente(models.Model):
    N_CodDocenteID = models.CharField(primary_key=True, max_length=20)
    N_DniDocente = models.CharField(max_length=8)
    T_ApelPaterno = models.CharField(max_length=50)
    T_ApelMaterno = models.CharField(max_length=50)
    T_Nombre = models.CharField(max_length=50)
    I_DepAcademicoID = models.ForeignKey(DepartamentoAcademicos, on_delete=models.CASCADE, db_column='I_DepAcademicoID')
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()
    def __str__(self):
        return self.T_ApelPaterno + " "+ self.T_ApelMaterno+" " + self.T_Nombre

class Programacion(models.Model):
    PERIODOS = [
        ('I', 'I'),
        ('II', 'II'),
    ]
    TURNOS =[
        ('M','M'),
        ('T','T'),
        ('N','N'),
    ]
    I_ProgramacionID = models.AutoField(primary_key=True)
    I_AsignaturaID = models.ForeignKey(Asignatura, on_delete=models.CASCADE, db_column='I_AsignaturaID')
    C_Periodo = models.CharField(max_length=2,choices=PERIODOS)
    C_Turno = models.CharField(max_length=2,choices=TURNOS)
    C_Seccion = models.CharField(max_length=2)
    I_DiaID1 = models.ForeignKey(Dia, on_delete=models.CASCADE,related_name='programacion_i_dia1', blank=True, null=True,db_column='I_DiaID1')
    D_HoraInicio1 = models.TimeField(null=True, blank=True)
    D_HoraFin1 = models.TimeField(null=True, blank=True)
    I_DiaID2 = models.ForeignKey(Dia, on_delete=models.CASCADE,related_name='programacion_d_dia2', blank=True, null=True,db_column='I_DiaID2')
    D_HoraInicio2 = models.TimeField(null=True, blank=True)
    D_HoraFin2 = models.TimeField(null=True, blank=True)
    I_DiaID3 = models.ForeignKey(Dia, on_delete=models.CASCADE,related_name='programacion_d_dia3', blank=True, null=True,db_column='I_DiaID3')
    D_HoraInicio3 = models.TimeField(null=True, blank=True)
    D_HoraFin3 = models.TimeField(null=True, blank=True)
    N_CodDocenteID = models.ForeignKey(Docente, on_delete=models.CASCADE, db_column='N_CodDocenteID')
    T_Aula = models.CharField(max_length=10)
    I_Cupos = models.IntegerField()
    I_CuposFijos = models.IntegerField()
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()
    B_Habilitado = models.BooleanField()

class Estudiante(models.Model):
    N_CodEstudianteID = models.CharField(primary_key=True, max_length=10)
    N_DniEstudiante = models.CharField(max_length=10)
    I_PlanID = models.ForeignKey(PlanCurriculares, on_delete=models.CASCADE, db_column='I_PlanID')
    I_AnioIngreso = models.IntegerField()
    I_UltiSemestreCursado = models.IntegerField()
    I_PromPonderado = models.FloatField()
    T_ApelPaterno = models.CharField(max_length=50)
    T_ApelMaterno = models.CharField(max_length=50)
    T_Nombre = models.CharField(max_length=50)
    B_CondicionEstudiante = models.BooleanField()
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()
    T_Email= models.CharField(max_length=50)
    B_QuintoSuperior = models.BooleanField()
    I_Nivel = models.IntegerField()

class Pago(models.Model):
    I_ComprobanteID = models.AutoField(primary_key=True)
    N_CodEstudianteID = models.ForeignKey(Estudiante, on_delete=models.CASCADE, db_column='N_CodEstudianteID')
    T_CodLiquidacion = models.CharField(max_length=20)
    I_EntidadID = models.ForeignKey(EntidadRecaudadoras, on_delete=models.CASCADE, db_column='I_EntidadID')
    B_CondicionPago = models.BooleanField()
    D_FechaPago = models.DateField()
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()


class HistorialAcademicos(models.Model):
    I_HistorialID = models.AutoField(primary_key=True)
    N_CodEstudianteID = models.ForeignKey(Estudiante, on_delete=models.CASCADE, db_column='N_CodEstudianteID') 
    I_AsignaturaID = models.IntegerField()
    B_AsignaturaAprobada = models.BooleanField()
    I_VezLlevadoAsignatura = models.IntegerField()
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()


