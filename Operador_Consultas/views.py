from AppLogin.decorators import rol_required,usuario_autenticado 
from django.shortcuts import render
from Operador_Horarios.views import datos_operador
from TI.models import Matricula
from django.core.paginator import Paginator
from django.http import HttpResponse
import pandas as pd


def obtener_escuela_id(request):
    # Obtener los datos del operador
    operador_datos = datos_operador(request)
    return operador_datos['escuelaid']

def filtrar_matriculas_por_escuela_y_fecha(escuela_id, fecha_desde, fecha_hasta):
    # Traemos las matrículas relacionadas con la escuela del operador
    matriculas_filtradas = Matricula.objects.filter(
        N_CodEstudianteID__I_PlanID__I_EspecialidadID__I_EscuelaID=escuela_id
    )

    # Filtrar por fechas si están presentes
    if fecha_desde:
        matriculas_filtradas = matriculas_filtradas.filter(D_FechaMatricula__gte=fecha_desde)
    if fecha_hasta:
        matriculas_filtradas = matriculas_filtradas.filter(D_FechaMatricula__lte=fecha_hasta)

    return matriculas_filtradas

def agrupar_matriculas_por_estudiante(matriculas_filtradas):
    estudiantes_matriculados = {}

    for matricula in matriculas_filtradas:
        estudiante = matricula.N_CodEstudianteID
        if estudiante.N_CodEstudianteID not in estudiantes_matriculados:
            estudiantes_matriculados[estudiante.N_CodEstudianteID] = matricula
        else:
            # Si ya existe el estudiante, verificamos cuál es la matrícula más reciente
            if matricula.D_FechaMatricula > estudiantes_matriculados[estudiante.N_CodEstudianteID].D_FechaMatricula:
                estudiantes_matriculados[estudiante.N_CodEstudianteID] = matricula

    return estudiantes_matriculados.values()


@rol_required("Operador")
@usuario_autenticado
def operador_consultas(request):
    # Obtener los datos del operador
    operador_datos = datos_operador(request)
    escuela_id = obtener_escuela_id(request)

    print(f"Escuela ID desde el contexto del operador: {escuela_id}")

    try:
        # Obtener los parámetros del filtro
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        codigo = request.GET.get('codigo')  # Captura el código del estudiante

        # Filtrar las matrículas
        matriculas_filtradas = filtrar_matriculas_por_escuela_y_fecha(escuela_id, fecha_desde, fecha_hasta)

        # Si se ingresó un código, filtramos aún más
        if codigo:
            matriculas_filtradas = [m for m in matriculas_filtradas if str(m.N_CodEstudianteID.N_CodEstudianteID) == codigo]

        print(f"Matriculas filtradas después del código: {len(matriculas_filtradas)}")

        # Agrupar por estudiante y tomar la matrícula más reciente
        matriculas_agrupadas = agrupar_matriculas_por_estudiante(matriculas_filtradas)
        matriculas_agrupadas = list(matriculas_agrupadas)

        print(f"Matrículas agrupadas: {len(matriculas_agrupadas)}")

        # Paginación
        paginator = Paginator(matriculas_agrupadas, 15)  # 15 registros por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    except Exception as e:
        print(f"Error durante la consulta: {e}")
        page_obj = []  # Evitar que la aplicación se caiga en caso de error

    # Preparar el contexto para la plantilla
    context = {
        **operador_datos,
        'page_obj': page_obj,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'codigo': codigo,  # Incluir el código en el contexto
    }
    return render(request, 'Operador/Operador_Consultas.html', context)


def descargar_matricula_excel(request):
    # Obtener código del estudiante desde GET
    codigo_estudiante = request.GET.get('codigo')

    # Filtrar matrículas
    if codigo_estudiante:
        matriculas = Matricula.objects.filter(N_CodEstudianteID=int(codigo_estudiante))
    else:
        matriculas = Matricula.objects.all()  # Cargar todas las matrículas (¡cuidado si hay muchas!)

    # Crear lista de diccionarios con los datos
    alumnos_matriculados = [
        {
            'codigo_alumno': matricula.N_CodEstudianteID.N_CodEstudianteID,
            'apellido_paterno': matricula.N_CodEstudianteID.T_ApelPaterno,
            'apellido_materno': matricula.N_CodEstudianteID.T_ApelMaterno,
            'nombre': matricula.N_CodEstudianteID.T_Nombre,
            'ingreso': matricula.N_CodEstudianteID.I_AnioIngreso,
            'facultad': matricula.N_CodEstudianteID.I_PlanID.I_EspecialidadID.I_EscuelaID.I_FacultadID.T_NombreFacultad,
            'escuela': matricula.N_CodEstudianteID.I_PlanID.I_EspecialidadID.I_EscuelaID.T_NombreEscuela,
            'especialidad': matricula.N_CodEstudianteID.I_PlanID.I_EspecialidadID.T_NombreEspecialidad,
            'quinto': matricula.N_CodEstudianteID.B_QuintoSuperior,
            'periodo': matricula.I_ProgramacionID.C_Periodo,
            'ciclo': matricula.I_ProgramacionID.I_AsignaturaID.T_Ciclo,
            'codigo_asignatura': matricula.I_ProgramacionID.I_AsignaturaID.I_CodAsignatura,
            'asignatura': matricula.I_ProgramacionID.I_AsignaturaID.T_NombreAsignatura,
            'condicion': matricula.I_ProgramacionID.I_AsignaturaID.I_CondicionAsignaturaID.T_NombreCondicion,
            'seccion': matricula.I_ProgramacionID.C_Seccion,
            'turno': matricula.I_ProgramacionID.C_Turno,
            'aula': matricula.I_ProgramacionID.T_Aula,
            'docente': f"{matricula.I_ProgramacionID.N_CodDocenteID.T_ApelPaterno} {matricula.I_ProgramacionID.N_CodDocenteID.T_ApelMaterno} {matricula.I_ProgramacionID.N_CodDocenteID.T_Nombre}",
        }
        for matricula in matriculas
    ]

    # Convertir datos en un DataFrame de pandas
    df = pd.DataFrame(alumnos_matriculados)

    # Generar la respuesta HTTP con el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=matriculados.xlsx'

    # Guardar DataFrame en la respuesta HTTP
    df.to_excel(response, index=False, engine='openpyxl')

    return response





