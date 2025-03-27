# Generated by Django 3.0.6 on 2025-02-03 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CondicionAsignaturas',
            fields=[
                ('I_CondicionAsignaturaID', models.AutoField(primary_key=True, serialize=False)),
                ('T_NombreCondicion', models.CharField(max_length=50)),
                ('D_DateInsert', models.DateField()),
                ('D_DateUpDate', models.DateField()),
                ('I_UsuarioID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DepartamentoAcademicos',
            fields=[
                ('I_DepAcademicoID', models.AutoField(primary_key=True, serialize=False)),
                ('T_NombreDepAcademico', models.CharField(max_length=50)),
                ('D_DateInsert', models.DateField()),
                ('D_DateUpDate', models.DateField()),
                ('I_UsuarioID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Dia',
            fields=[
                ('I_DiaID', models.AutoField(primary_key=True, serialize=False)),
                ('T_NombreDia', models.CharField(max_length=9)),
            ],
        ),
        migrations.CreateModel(
            name='EntidadRecaudadoras',
            fields=[
                ('I_EntidadID', models.AutoField(primary_key=True, serialize=False)),
                ('T_NombreEntidad', models.CharField(max_length=50)),
                ('D_DateInsert', models.DateField()),
                ('D_DateUpDate', models.DateField()),
                ('I_UsuarioID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Facultad',
            fields=[
                ('I_FacultadID', models.AutoField(primary_key=True, serialize=False)),
                ('T_NombreFacultad', models.CharField(max_length=100)),
                ('T_FacultadSigla', models.CharField(max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='UsuarioRoles',
            fields=[
                ('I_RolID', models.AutoField(primary_key=True, serialize=False)),
                ('T_NombreRol', models.CharField(max_length=50)),
                ('D_DateInsert', models.DateField()),
                ('D_DateUpDate', models.DateField()),
                ('I_UsuarioID', models.IntegerField()),
            ],
        ),
    ]
