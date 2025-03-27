import csv
import openpyxl
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from datetime import date
from TR.models import Usuario,Estudiante,PlanCurriculares
from TC.models import UsuarioRoles  # Asegúrate de importar los modelos correctos
import secrets
import string

def generar_contraseña(length=10):
    """Genera una contraseña aleatoria de longitud especificada."""
    caracteres = string.ascii_letters + string.digits + string.punctuation
    contraseña = ''.join(secrets.choice(caracteres) for _ in range(length))
    return contraseña

def cargar_usuarios_csv(request):
    contrasenas_guardadas = []  # Lista para almacenar contraseñas y usuarios para el archivo Excel

    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Por favor, sube un archivo CSV.')
            return render(request, 'cargar_usuarios_csv.html')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'El archivo subido no es un archivo CSV.')
            return render(request, 'cargar_usuarios_csv.html')

        # Leer el archivo CSV
        file_data = csv_file.read().decode('ISO-8859-1')
        lines = file_data.splitlines()
        reader = csv.DictReader(lines)

        for row in reader:
            username = row['username']
            nombre = row['nombre']
            apellido_paterno = row['apellido_paterno']
            apellido_materno = row['apellido_materno']
            rol_nombre = row['rol']
            habilitado = row.get('habilitado', 'True').lower() in ['true', '1', 'yes']  # Convierte a booleano

            # Obtener el rol correspondiente
            try:
                rol = UsuarioRoles.objects.get(T_NombreRol=rol_nombre)
            except UsuarioRoles.DoesNotExist:
                messages.error(request, f'El rol "{rol_nombre}" no existe.')
                continue  # Saltar al siguiente registro si el rol no existe

            if Usuario.objects.filter(T_NombreUsuario=username).exists():
                messages.warning(request, f'El usuario "{username}" ya existe y se omitirá.')
                continue 

            # Generar la contraseña
            contrasena = generar_contraseña()

            # Crear el nuevo usuario
            usuario = Usuario(
                T_NombreUsuario=username,
                T_Contrasenia=contrasena,  # Guardamos la contraseña en texto claro temporalmente
                T_ApelPaterno=apellido_paterno,
                T_ApelMaterno=apellido_materno,
                T_Nombre=nombre,
                I_RolID=rol,
                B_Habilitado=habilitado,
                D_DateInsert=date.today(),  # Fecha actual
                D_DateUpDate=date.today(),  # Fecha actual
                I_UsuarioID_1=1  # Valor fijo en 1
            )
            usuario.save()

            # Agregar usuario y su contraseña en texto claro a la lista
            contrasenas_guardadas.append({
                'username': username,
                'nombre': nombre,
                'apellido_paterno': apellido_paterno,
                'apellido_materno': apellido_materno,
                'rol': rol_nombre,
                'contrasena': contrasena  # Contraseña en texto claro
            })

        messages.success(request, 'Usuarios cargados exitosamente.')

    return render(request, 'cargar_usuarios_csv.html')

def generar_excel_contrasenas(request):
    # Obtener todos los usuarios con las contraseñas en texto claro desde la lista contrasenas_guardadas
    contrasenas_guardadas = []

    # Consulta para obtener todos los usuarios con su contraseña en texto claro
    usuarios = Usuario.objects.all()
    for usuario in usuarios:
        contrasenas_guardadas.append({
            'username': usuario.T_NombreUsuario,
            'nombre': usuario.T_Nombre,
            'apellido_paterno': usuario.T_ApelPaterno,
            'apellido_materno': usuario.T_ApelMaterno,
            'rol': usuario.I_RolID.T_NombreRol,
            'contrasena': usuario.T_Contrasenia  # Contraseña en texto claro
        })

    # Crear archivo Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Username', 'Nombre', 'Apellido Paterno', 'Apellido Materno', 'Rol', 'Contraseña'])  # Encabezados

    # Llenar el archivo con los usuarios y contraseñas
    for usuario in contrasenas_guardadas:
        ws.append([
            usuario['username'],
            usuario['nombre'],
            usuario['apellido_paterno'],
            usuario['apellido_materno'],
            usuario['rol'],
            usuario['contrasena']  # Contraseña en texto claro
        ])

    # Responder con el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=usuarios_con_contrasenas.xlsx'
    wb.save(response)
    return response


def cargar_estudiantes_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Por favor, sube un archivo CSV.')
            return render(request, 'cargar_estudiantes_csv.html')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'El archivo subido no es un archivo CSV.')
            return render(request, 'cargar_estudiantes_csv.html')

        # Leer el archivo CSV
        file_data = csv_file.read().decode('ISO-8859-1')
        lines = file_data.splitlines()
        reader = csv.DictReader(lines)

        for row in reader:
            # Obtener los datos del CSV
            cod_estudiante = row['CodEstudianteID']
            dni_estudiante = row['DniEstudiante']
            plan_id = int(row['PlanID'])  # Convertir el ID a entero
            anio_ingreso = int(row['AnioIngreso'])
            ulti_semestre_cursado = int(row['UltiSemestreCursado'])
            prom_ponderado = int(row['PromPonderado'])
            apel_paterno = row['ApellidoPaterno']
            apel_materno = row['ApellidoMaterno']
            nombre = row['Nombre']
            condicion_estudiante = anio_ingreso = int(row['Condicion_Estudiante'])  # Convertir el ID a entero
            email = row.get('Email', '')  # Si no existe la columna 'Email', se asigna un valor vacío

            # Obtener las claves foráneas usando los IDs
            try:
                plan = PlanCurriculares.objects.get(id=plan_id)

            except PlanCurriculares.DoesNotExist:
                messages.error(request, f"El Plan Curricular con ID {plan_id} no existe.")
                continue  # Si no existe el PlanCurricular, omite este registro

            # Crear el nuevo estudiante
            estudiante = Estudiante(
                N_CodEstudianteID=cod_estudiante,
                N_DniEstudiante=dni_estudiante,
                I_PlanID=plan,
                I_AnioIngreso=anio_ingreso,
                I_UltiSemestreCursado=ulti_semestre_cursado,
                I_PromPonderado=prom_ponderado,
                T_ApelPaterno=apel_paterno,
                T_ApelMaterno=apel_materno,
                T_Nombre=nombre,
                I_CondicionEstudianteID=condicion_estudiante,
                D_DateInsert=date.today(),  # Fecha actual
                D_DateUpDate=date.today(),  # Fecha actual
                I_UsuarioID=1,  # Valor fijo, si aplica
                T_Email=email  # Correo electrónico
            )
            estudiante.save()

        messages.success(request, 'Estudiantes cargados exitosamente.')

    return render(request, 'cargar_estudiantes_csv.html')