from django.db import models
# Create your models here.
class UsuarioRoles(models.Model):
    I_RolID = models.AutoField(primary_key=True)
    T_NombreRol = models.CharField(max_length=50)
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()

class CondicionAsignaturas(models.Model):
    I_CondicionAsignaturaID = models.AutoField(primary_key=True)
    T_NombreCondicion = models.CharField(max_length=50)
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()

class EntidadRecaudadoras(models.Model):
    I_EntidadID = models.AutoField(primary_key=True)
    T_NombreEntidad = models.CharField(max_length=50)
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()
    
class DepartamentoAcademicos(models.Model):
    I_DepAcademicoID = models.AutoField(primary_key=True)
    T_NombreDepAcademico = models.CharField(max_length=50)
    D_DateInsert = models.DateField()
    D_DateUpDate = models.DateField()
    I_UsuarioID = models.IntegerField()

class Facultad(models.Model):
    I_FacultadID = models.AutoField(primary_key=True)
    T_NombreFacultad = models.CharField(max_length=100)
    T_FacultadSigla = models.CharField(max_length=7)


class Dia(models.Model):
    I_DiaID = models.AutoField(primary_key=True)
    T_NombreDia = models.CharField(max_length=9)
    def __str__(self):
        return self.T_NombreDia
    
    